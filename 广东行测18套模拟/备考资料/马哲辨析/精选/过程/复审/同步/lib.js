// 审查用的多设备假 db（照 db.d.ts）：
//  - 远端文档放在 Node 这边，多台“设备”（各自一个浏览器上下文、各自的 localStorage）共用；
//  - set 整份替换、后写覆盖；写入先在本机出一份 hasPendingWrites:true 的快照，latency 毫秒后落到远端，再出确认过的快照；
//  - 远端一变，其他设备的监听在 push 毫秒后收到（该设备自己有未确认写入时，看到的是自己的那份、hasPendingWrites:true）；
//  - 可以先给缓存副本（fromCache:true）；可以断网（监听收不到、set 挂起或报 unavailable）；可以让远端返回时把键排序（sortKeys）。
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');

function fakeDb(o) {
  const F = window.__F = { cb: null, err: null, pending: 0, overlay: null, online: o.online !== false, serverSeen: false, sets: 0, tries: 0, log: [], mode: o.offlineMode || 'hang', waiters: [], pushMs: o.push == null ? 5 : o.push, latency: o.latency == null ? 20 : o.latency, sortKeys: !!o.sortKeys, setError: null };
  const sortDeep = (v) => (Array.isArray(v) ? v.map(sortDeep) : v && typeof v === 'object' ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, sortDeep(v[k])])) : v);
  const parse = (s, own) => { const d = JSON.parse(s); return F.sortKeys && !(own && o.sortKeys === 'server') ? sortDeep(d) : d; };
  const snap = (body, meta) => ({ id: 'main', exists: body != null, data: () => (body == null ? undefined : parse(body, meta.hasPendingWrites || body === F.ownBody)), metadata: meta });
  const deliver = (body, meta) => { F.log.push({ t: Date.now(), n: body == null ? -1 : Object.keys(JSON.parse(body).q || {}).length, ...meta }); if (F.cb) F.cb(snap(body, meta)); };
  // 远端有变化（或刚连上）：把当前云端状态交给监听
  F.emitServer = async () => {
    if (!F.online || !F.cb) return;
    const s = await window.__remoteGet();
    if (!F.online) return;
    F.serverSeen = true;
    if (F.pending > 0) deliver(F.overlay, { fromCache: false, hasPendingWrites: true });
    else deliver(s, { fromCache: false, hasPendingWrites: false });
  };
  F.serverChanged = () => { setTimeout(F.emitServer, F.pushMs); };
  F.goOnline = () => { F.online = true; const w = F.waiters; F.waiters = []; w.forEach((f) => f()); setTimeout(F.emitServer, o.reconnect == null ? F.pushMs : o.reconnect); };
  F.goOffline = () => { F.online = false; };
  const ref = {
    id: 'main', path: 'progress/main',
    async set(d) {
      F.tries++;
      if (F.setError) { const e = F.setError; if (e.once) F.setError = null; await new Promise((r) => setTimeout(r, 5)); throw { code: e.code, message: e.code }; }
      if (!F.online) {
        if (F.mode === 'reject') { await new Promise((r) => setTimeout(r, 30)); throw { code: 'unavailable', message: 'offline' }; }
        // 挂起：本机先出一份未确认的快照，连上后再写
      }
      const body = JSON.stringify(d);
      F.pending++; F.overlay = body;
      setTimeout(() => deliver(F.overlay, { fromCache: !F.serverSeen || !F.online, hasPendingWrites: true }), 0);
      if (!F.online) await new Promise((r) => F.waiters.push(r));
      await new Promise((r) => setTimeout(r, F.latency));
      F.sets++; F.ownBody = body;
      await window.__remoteSet(body);
      F.pending--; if (F.pending === 0) F.overlay = null;
      setTimeout(F.emitServer, 1);
    },
    async get() {
      F.gets = (F.gets || 0) + 1;
      if (!F.online) { if (F.mode === 'reject') { await new Promise((r) => setTimeout(r, 30)); throw { code: 'unavailable', message: 'offline' }; } await new Promise((r) => F.waiters.push(r)); }
      const s = await window.__remoteGet(); return snap(s, { fromCache: false, hasPendingWrites: false });
    },
    onSnapshot(cb, err) {
      F.cb = cb; F.err = err;
      if (o.cached) setTimeout(() => deliver(o.cached, { fromCache: true, hasPendingWrites: false }), 1);
      if (o.cachedMissing) setTimeout(() => deliver(null, { fromCache: true, hasPendingWrites: false }), 1);
      if (o.errorAfter != null) setTimeout(() => { F.cb = null; err && err({ code: o.errorCode || 'unavailable', message: 'x' }); }, o.errorAfter);
      if (o.delay != null && o.delay >= 0) setTimeout(F.emitServer, o.delay);
      return () => { F.cb = null; };
    },
  };
  if (o.noDb) { window.claude = { use: async () => null }; return; }
  if (o.noClaude) return;
  window.claude = { use: async (name) => { if (o.useDelay) await new Promise((r) => setTimeout(r, o.useDelay)); return name === 'db' ? { doc: () => ref } : null; } };
}

async function launch() { return chromium.launch(); }

// store: { remote: string|null, sets: number, devices: [] , history: [] }
function newStore(remote) { return { t0: Date.now(), remote: remote == null ? null : (typeof remote === 'string' ? remote : JSON.stringify(remote)), sets: 0, devices: [], history: [] }; }

async function device(browser, SITE, store, name, opts = {}) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.route('http://mz.local/**', (route) => {
    const u = new URL(route.request().url());
    const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
    if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
    return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
  });
  const dev = { name, ctx, errs: [], closed: false };
  await ctx.exposeFunction('__remoteGet', () => store.remote);
  await ctx.exposeFunction('__remoteSet', (s) => {
    store.remote = s; store.sets++; store.history.push({ by: name, at: Date.now(), nq: Object.keys(JSON.parse(s).q || {}).length, updated: JSON.parse(s).updated, plan: JSON.parse(s).plan ? JSON.parse(s).plan.pos : null });
    for (const d of store.devices) if (d !== dev && !d.closed) d.pg.evaluate(() => window.__F && window.__F.serverChanged()).catch(() => {});
  });
  const pg = dev.pg = await ctx.newPage();
  pg.on('pageerror', (e) => dev.errs.push(e.message));
  await pg.addInitScript(({ t, local, seedRandom, t0, skew }) => {
    // 所有设备共用一条时间线：假时间 = t + (真实时间 - t0) + skew；刷新后沿用
    const Real = Date; const saved = sessionStorage.getItem('__off');
    window.__off = saved != null ? Number(saved) : (t - t0 + skew); window.__setNow = (ms) => { window.__off = ms - Real.now(); sessionStorage.setItem('__off', String(window.__off)); };
    class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + window.__off); } static now() { return Real.now() + window.__off; } }
    window.Date = Fake;
    if (seedRandom) { let seed = seedRandom; Math.random = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }; }
    if (local && !sessionStorage.getItem('__seeded')) { sessionStorage.setItem('__seeded', '1'); localStorage.setItem('mzbx-progress-v1', local); }
  }, { t: new Date(opts.when || '2026-11-28T09:00:00').getTime(), local: opts.local ? (typeof opts.local === 'string' ? opts.local : JSON.stringify(opts.local)) : null, seedRandom: opts.seedRandom || 0, t0: store.t0, skew: opts.skew || 0 });
  const dbOpts = { delay: opts.delay == null ? 30 : opts.delay, cached: opts.cached ? (typeof opts.cached === 'string' ? opts.cached : JSON.stringify(opts.cached)) : null, cachedMissing: !!opts.cachedMissing,
    latency: opts.latency, push: opts.push, online: opts.online, offlineMode: opts.offlineMode, sortKeys: opts.sortKeys, errorAfter: opts.errorAfter, errorCode: opts.errorCode, noDb: opts.noDb, noClaude: opts.noClaude, useDelay: opts.useDelay, reconnect: opts.reconnect };
  await pg.addInitScript(fakeDb, dbOpts);
  store.devices.push(dev);
  await pg.goto('http://mz.local/index.html'); await pg.waitForSelector('.today');
  dev.close = async () => { dev.closed = true; await ctx.close(); };
  dev.state = () => pg.evaluate(() => ({ nq: Object.keys(S.prog.q).length, updated: S.prog.updated, plan: S.prog.plan ? { day: S.prog.plan.day, pos: S.prog.plan.pos, len: S.prog.plan.ids.length, nres: Object.keys(S.prog.plan.res).length } : null, synced: S.synced, cloud: S.cloud, note: S.cloudNote, run: S.run ? { pos: S.run.pos, len: S.run.list.length, tkey: S.run.tkey } : null, sets: window.__F ? window.__F.sets : 0, tries: window.__F ? window.__F.tries : 0, daily: S.prog.settings.daily, days: S.prog.days }));
  dev.answer = (ok = true) => pg.evaluate((ok) => {
    const R = S.run; if (!R || R.pos >= R.list.length) return null;
    const q = R.list[R.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
    if (q.type === '判断') runState.picked = new Set([ok ? ans : (ans === '正确' ? '错误' : '正确')]);
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
    reveal(q); nextQ(); return q.id;
  }, ok);
  dev.setNow = (when) => pg.evaluate((ms) => window.__setNow(ms), new Date(when).getTime());
  dev.online = () => pg.evaluate(() => window.__F.goOnline());
  dev.offline = () => pg.evaluate(() => window.__F.goOffline());
  dev.wait = (ms) => pg.waitForTimeout(ms);
  dev.local = () => pg.evaluate(() => JSON.parse(localStorage.getItem('mzbx-progress-v1') || 'null'));
  return dev;
}
const startBtn = '.panel.today >> button:text-is("开始") >> nth=0';
const contBtn = '.panel.today >> button:text-is("继续") >> nth=0';
const remote = (store) => (store.remote ? JSON.parse(store.remote) : null);
const nq = (store) => (store.remote ? Object.keys(JSON.parse(store.remote).q).length : -1);
function loadCore(SITE) { const qs = JSON.parse(fs.readFileSync(path.join(SITE, 'questions.json'), 'utf8')); return { qs, core: qs.filter((x) => x.t === 1).sort((a, b) => a.o - b.o), backup: qs.filter((x) => x.t === 2).sort((a, b) => a.o - b.o) }; }
function prog(core, n, day, updated, extra = {}) {
  const q = {}; core.slice(0, n).forEach((x) => { q[x.id] = { n: 1, c: 1, l: 1, b: 1, f: day, d: day, due: '2026-11-28', f1: 1 }; });
  return { v: 1, q, days: { [day]: { n, c: n } }, settings: { size: 15, size2: 15, daily: 50, why: false, fmB: true, fmC: false }, today: null, today2: null, plan: null, updated, ...extra };
}
module.exports = { launch, newStore, device, startBtn, contBtn, remote, nq, loadCore, prog };
