// 多设备随机交错测试：把页面脚本原样放进 vm（每台设备一个环境、各自的 localStorage、各自的时钟偏差），
// 共用一份假云端（照 db.d.ts：set 整份替换、后写覆盖；返回的文档键按字母排序；写入先出 hasPendingWrites 快照；
// 可以先给 fromCache 副本；可以延迟、乱序、偶尔 unavailable；可以离线）。时间是虚拟的，种子固定可重放。
'use strict';
process.env.TZ = 'Asia/Shanghai';
const vm = require('vm'), fs = require('fs'), path = require('path');
const DIR = __dirname, LS_KEY = 'mzbx-progress-v1';
const UNH = []; process.on('unhandledRejection', (e) => { UNH.push(String(e && (e.stack || e.code || e)).slice(0, 200)); });

function extract(html) { const re = /<script>([\s\S]*?)<\/script>/g; let m, best = null; while ((m = re.exec(html))) if (m[1].includes('LS_KEY')) best = m[1]; if (!best) throw new Error('no script'); return best; }
function loadSite(dir) {
  const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8'); const files = {};
  for (const f of ['cards.json', 'blocks.json', 'questions.json', 'meta.json']) { const p = path.join(dir, f); files[f] = fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : null; }
  return { script: new vm.Script(extract(html), { filename: path.basename(dir) + '.js' }), files };
}
const SITES = { new: loadSite(path.join(DIR, process.env.SITE || 'site')), old: loadSite(path.join(DIR, 'oldsite')) };
const DRIVER = new vm.Script(fs.readFileSync(path.join(DIR, 'driver.js'), 'utf8'), { filename: 'driver.js' });
const BOOT = (seed) => `(function(){ const R = Date; class D extends R { constructor(...a){ if (a.length) super(...a); else super(__now()); } static now(){ return __now(); } } globalThis.Date = D; let s = ${(seed >>> 0) % 2147483648}; Math.random = function(){ s = (s * 1103515245 + 12345) % 2147483648; return s / 2147483648; }; })();`;
const BH = new Proxy(function () {}, {
  get(t, k) { if (k === Symbol.iterator) return function* () {}; if (k === Symbol.toPrimitive) return () => ''; if (k === 'then') return undefined; if (k === 'length') return 0; if (k === 'nodeType') return 1; return BH; },
  apply() { return BH; }, construct() { return BH; }, set() { return true; }, has() { return true; }, deleteProperty() { return true; },
});
function mulberry32(a) { return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const tick = () => new Promise((r) => setImmediate(r));
function sortDeep(v) { return Array.isArray(v) ? v.map(sortDeep) : v && typeof v === 'object' ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, sortDeep(v[k])])) : v; }
const canon = (v) => JSON.stringify(sortDeep(v));
function addDays(day, n) { const [y, m, d] = day.split('-').map(Number); const x = new Date(y, m - 1, d + n); const p = (v) => String(v).padStart(2, '0'); return `${x.getFullYear()}-${p(x.getMonth() + 1)}-${p(x.getDate())}`; }
const hash = (s) => { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return (h >>> 0).toString(36); };
const gkey = (ids) => hash(ids.slice().sort().join(','));
const brief = (g) => (g ? { day: g.day, pos: g.pos, len: g.ids.length, set: gkey(g.ids), order: hash(g.ids.join(',')), nres: Object.keys(g.res || {}).length } : null);
function diffTop(a, b) {
  const out = {}; a = a || {}; b = b || {};
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
    if (canon(a[k]) === canon(b[k])) continue;
    if ((k === 'q' || k === 'days') && a[k] && b[k]) { const ids = [...new Set([...Object.keys(a[k]), ...Object.keys(b[k])])].filter((id) => canon(a[k][id]) !== canon(b[k][id])); out[k] = { n: ids.length, ex: ids.slice(0, 2).map((id) => [id, a[k][id], b[k][id]]) }; }
    else if (k === 'plan' || k === 'today' || k === 'today2') out[k] = [brief(a[k]), brief(b[k])];
    else out[k] = [a[k], b[k]];
  }
  return out;
}
const hm = (ms) => new Date(ms).toLocaleString('sv-SE', { timeZone: 'Asia/Shanghai' });

function makeWorld(seed, o) {
  const W = { now: o.t0, ev: [], seq: 0, errors: [], rng: mulberry32(seed), doc: null, v: 0, writes: [], hist: [], insts: new Set(), tries: 0, gets: 0, o, devs: [] };
  const rint = (a, b) => a + Math.floor(W.rng() * (b - a + 1)); W.rint = rint;
  W.delay = () => { if (o.fast) return o.fast; const r = W.rng(); return r < 0.85 ? rint(15, 250) : r < 0.97 ? rint(250, 2500) : rint(2500, 12000); };
  W.schedule = (ms, fn) => { const e = { t: W.now + Math.max(0, ms), s: W.seq++, fn, x: false }; W.ev.push(e); return e; };
  W.run = async (until) => {
    for (;;) {
      let bi = -1;
      for (let i = 0; i < W.ev.length; i++) { const e = W.ev[i]; if (e.x) continue; if (bi < 0 || e.t < W.ev[bi].t || (e.t === W.ev[bi].t && e.s < W.ev[bi].s)) bi = i; }
      if (bi < 0 || W.ev[bi].t > until) break;
      const e = W.ev[bi]; W.ev[bi] = W.ev[W.ev.length - 1]; W.ev.pop();
      W.now = e.t;
      try { e.fn(); } catch (err) { W.errors.push(String((err && err.stack) || err).slice(0, 400)); }
      await tick();
      if (W.ev.length > 400) W.ev = W.ev.filter((x) => !x.x);
    }
    W.now = until; await tick();
  };
  W.adv = (ms) => W.run(W.now + ms);
  const snap = (str, meta) => ({ id: 'main', exists: str != null, data: () => (str == null ? undefined : JSON.parse(str)), metadata: meta });
  W.apply = (str, inst) => {
    W.doc = str; W.v++; W.writes.push({ t: W.now, by: inst.dev.name, v: W.v }); W.hist.push({ by: inst.dev.name, t: W.now, str }); if (W.hist.length > 6) W.hist.shift();
    for (const x of W.insts) if (x !== inst && x.alive) { const v = W.v; W.schedule(W.delay(), () => W.push(x, str, v)); }
  };
  W.push = (x, d, v) => { if (!x.alive || !x.dev.online || !x.cb) return; if (v < x.lastV) return; if (x.pending > 0) return; x.lastV = v; x.dev.cache = d; x.cb(snap(d, { fromCache: false, hasPendingWrites: false })); };
  W.get = (inst) => new Promise((res, rej) => {
    W.gets++;
    const fail = (ms) => { W.schedule(ms, () => { if (inst.alive) rej({ code: 'unavailable', message: 'x' }); }); };
    if (!inst.dev.online) return void fail(rint(30, 3000));
    if (W.rng() < o.pFail) return void fail(rint(30, 2000));
    W.schedule(W.delay(), () => {
      if (!inst.alive) return;
      if (!inst.dev.online) return void fail(rint(30, 3000));
      const d = W.doc;
      W.schedule(W.delay(), () => { if (!inst.alive) return; if (!inst.dev.online) return void rej({ code: 'unavailable', message: 'x' }); res(snap(d, { fromCache: false, hasPendingWrites: false })); });
    });
  });
  W.set = (inst, body) => new Promise((res, rej) => {
    W.tries++;
    const fail = (ms) => { W.schedule(ms, () => { if (inst.alive) rej({ code: 'unavailable', message: 'x' }); }); };
    if (!inst.dev.online) return void fail(rint(30, 3000));
    if (W.rng() < o.pFail) return void fail(rint(30, 2000));
    const str = JSON.stringify(sortDeep(JSON.parse(JSON.stringify(body))));
    inst.pending++;
    W.schedule(0, () => { if (inst.alive && inst.cb) inst.cb(snap(str, { fromCache: false, hasPendingWrites: true })); });
    W.schedule(W.delay(), () => {
      const landed = inst.dev.online ? (inst.alive || W.rng() < 0.7) : W.rng() < 0.5;      // 请求已经发出：页面关了、网断了，也可能已经落到云端
      if (landed) W.apply(str, inst);
      W.schedule(W.delay(), () => {
        inst.pending--;
        if (!inst.alive) return;
        if (!inst.dev.online || W.rng() < o.pFail / 2) { rej({ code: 'unavailable', message: 'x' }); if (inst.dev.online && inst.pending === 0) W.push(inst, W.doc, W.v); return; }
        res(); if (inst.pending === 0) W.push(inst, W.doc, W.v);
      });
    });
  });
  W.subscribe = (inst) => {
    W.insts.add(inst);
    if (inst.dev.cache != null && W.rng() < 0.6) { const c = inst.dev.cache; W.schedule(1, () => { if (inst.alive && inst.cb) inst.cb(snap(c, { fromCache: true, hasPendingWrites: false })); }); }
    if (inst.dev.online) W.schedule(o.fast || (W.rng() < 0.06 ? rint(10500, 30000) : W.delay()), () => W.push(inst, W.doc, W.v));
  };
  W.online = (dev) => { if (dev.online) return; dev.online = true; const x = dev.inst; W.schedule(W.delay(), () => W.push(x, W.doc, W.v)); };
  W.offline = (dev) => { dev.online = false; };
  W.fire = (inst, which, type) => { for (const f of (inst[which][type] || [])) { try { f({ type }); } catch (e) { W.errors.push('fire ' + type + ': ' + String((e && e.stack) || e).slice(0, 300)); } } };
  W.newInst = (dev) => {
    const inst = { dev, alive: true, timers: new Map(), cb: null, pending: 0, lastV: -1, hd: {}, hw: {} };
    let tseq = 0;
    const ref = { id: 'main', path: 'progress/main', get: () => W.get(inst), set: (b) => W.set(inst, b), onSnapshot: (cb, err) => { inst.cb = cb; inst.err = err; W.subscribe(inst); return () => { inst.cb = null; }; } };
    const sb = {
      console, __now: () => W.now + dev.skew,
      setTimeout: (fn, ms) => { const id = ++tseq; const e = W.schedule(ms || 0, () => { inst.timers.delete(id); if (inst.alive) fn(); }); inst.timers.set(id, e); return id; },
      clearTimeout: (id) => { const e = inst.timers.get(id); if (e) { e.x = true; inst.timers.delete(id); } },
      localStorage: { getItem: (k) => (dev.ls.has(k) ? dev.ls.get(k) : null), setItem: (k, v) => { dev.ls.set(k, String(v)); }, removeItem: (k) => { dev.ls.delete(k); } },
      fetch: (f) => { const txt = SITES[dev.kind].files[f]; return Promise.resolve(txt == null ? { ok: false } : { ok: true, json: () => Promise.resolve(JSON.parse(txt)) }); },
      location: { hash: '' }, navigator: {}, scrollY: 0, scrollTo() {},
      addEventListener: (t, f) => { (inst.hw[t] = inst.hw[t] || []).push(f); }, removeEventListener() {},
      document: { hidden: false, body: BH, createElement: () => BH, createTextNode: () => BH, createDocumentFragment: () => BH, getElementById: (id) => (id === 'mz-data' ? null : BH), querySelector: () => BH, querySelectorAll: () => [],
        addEventListener: (t, f) => { (inst.hd[t] = inst.hd[t] || []).push(f); }, removeEventListener() {} },
      claude: { use: (n) => Promise.resolve(n === 'db' ? { doc: () => ref } : null) },
    };
    sb.window = sb;
    const ctx = vm.createContext(sb);
    vm.runInContext(BOOT((W.rng() * 2147483647) | 0), ctx);
    SITES[dev.kind].script.runInContext(ctx);
    DRIVER.runInContext(ctx);
    inst.sb = sb; inst.drv = sb.__drv;
    return inst;
  };
  W.addDev = (name, kind, skew) => { const dev = { name, kind, skew, online: true, ls: new Map(), cache: null, hidden: false, inst: null }; dev.inst = W.newInst(dev); W.devs.push(dev); return dev; };
  W.refresh = (dev, withHide) => { const x = dev.inst; if (withHide) W.fire(x, 'hw', 'pagehide'); x.alive = false; W.insts.delete(x); for (const e of x.timers.values()) e.x = true; dev.hidden = false; dev.inst = W.newInst(dev); };
  W.mem = (dev) => JSON.parse(dev.inst.drv.snap());
  W.cloud = () => (W.doc ? JSON.parse(W.doc) : null);
  W.writesBy = (from, to) => { const c = {}; for (const w of W.writes.slice(from, to)) c[w.by] = (c[w.by] || 0) + 1; return c; };
  return W;
}

// ---------------- 随机交错 ----------------
async function fuzzRound(seed, steps, F) {
  const prng = mulberry32((seed * 2654435761) >>> 0); const rnd = () => prng(); const ri = (a, b) => a + Math.floor(rnd() * (b - a + 1));
  const late = F.midnight ? true : (F.noday ? false : rnd() < 0.12);
  const W = makeWorld(seed, { t0: Date.parse(late ? '2026-11-28T23:40:00+08:00' : '2026-11-28T09:00:00+08:00'), pFail: F.nofail ? 0 : 0.04 });
  const nDev = F.ndev || (rnd() < 0.5 ? 2 : 3);
  const SK = [0, 0, 1500, -2500, 40000, -70000, 170000, -120000];
  for (let i = 0; i < nDev; i++) W.addDev('D' + i, i < (F.old || 0) ? 'old' : 'new', F.noskew ? 0 : SK[ri(0, SK.length - 1)]);
  const devs = W.devs; await tick(); await tick();
  const pReset = F.noreset ? 0 : (F.reset ? 0.02 : (rnd() < 0.4 ? 0.012 : 0)), pDay = F.noday ? 0 : 0.012;
  const log = { answers: [], resets: [], groups: { plan: {}, today: {}, today2: {} }, ops: [], foreign: null, days: 0 };
  const note = (k, res) => { if (res && res.r === 'created' && res.ids) { const m = log.groups[k]; (m[res.day] = m[res.day] || new Set()).add(gkey(res.ids)); } };
  await W.adv(ri(300, 3000));
  const POOL = devs[0].inst.drv.pool(36);
  const call = (dev, name, ...a) => { try { return dev.inst.drv[name](...a); } catch (e) { W.errors.push(name + ': ' + String((e && e.stack) || e).slice(0, 400)); return null; } };
  const OPS = [['answer', 46], ['next', 6], ['rate', 5], ['setting', 5], ['exit', 3], ['offline', 4], ['online', 7], ['refresh', 3], ['hide', 3], ['idle', 8], ['reset', pReset * 100]];
  const total = OPS.reduce((s, x) => s + x[1], 0);
  for (let i = 0; i < steps; i++) {
    const dev = devs[ri(0, devs.length - 1)]; let r = rnd() * total, op = 'idle';
    for (const [n, w] of OPS) { if (r < w) { op = n; break; } r -= w; }
    let s = call(dev, 'info'); if (!s || !s.ready) { await W.adv(50); continue; }
    if (op === 'answer') {
      if (s.run && s.run.revealed) { call(dev, 'next'); s = call(dev, 'info'); }
      if (s.run && s.run.pos >= s.run.len) { call(dev, 'exit'); s = call(dev, 'info'); }
      if (!s.run) {
        const x = rnd();
        if (x < 0.55) note('plan', call(dev, 'startPlan'));
        else if (x < 0.70) note('today', call(dev, 'startBank', 'mz'));
        else if (x < 0.78) note('today2', call(dev, 'startBank', 'fm'));
        else if (x < 0.90) { const ids = []; for (let k = ri(2, 5); k > 0; k--) ids.push(POOL[ri(0, POOL.length - 1)]); call(dev, 'practice', [...new Set(ids)], ''); }
        else { const t = call(dev, 'todayIds') || []; if (t.length) call(dev, 'practice', t.slice(ri(0, Math.max(0, t.length - 4))).slice(0, 4), 'redo'); }
        s = call(dev, 'info');
      }
      if (s.run && s.run.pos >= s.run.len) call(dev, 'exit');
      else if (s.run) { const a = call(dev, 'answer', rnd() < 0.7); if (a) log.answers.push({ t: W.now, dev: dev.name, kind: dev.kind, id: a.id, ok: a.correct, day: a.day, epoch: a.epoch, n: a.n }); }
    } else if (op === 'next') call(dev, 'next');
    else if (op === 'rate') call(dev, 'rate', rnd() < 0.5 ? 1 : 0);
    else if (op === 'setting') { const k = ['daily', 'size', 'size2', 'fmB', 'fmC', 'why'][ri(0, 5)]; const v = k === 'daily' ? [30, 40, 50, 60][ri(0, 3)] : k.startsWith('size') ? [10, 12, 15, 20][ri(0, 3)] : rnd() < 0.5; call(dev, 'setting', k, v); }
    else if (op === 'exit') call(dev, 'exit');
    else if (op === 'offline') W.offline(dev);
    else if (op === 'online') W.online(dev);
    else if (op === 'refresh') { W.refresh(dev, rnd() < 0.7); await tick(); await tick(); }
    else if (op === 'hide') { dev.hidden = !dev.hidden; dev.inst.sb.document.hidden = dev.hidden; W.fire(dev.inst, 'hd', 'visibilitychange'); if (!dev.hidden) W.fire(dev.inst, 'hw', 'focus'); }
    else if (op === 'reset') { if (dev.kind === 'new' || F.oldreset) { const e = call(dev, 'reset'); log.resets.push({ t: W.now, dev: dev.name, kind: dev.kind, epoch: e }); } }
    log.ops.push(dev.name + ':' + op);
    const x = rnd();
    if (x < pDay && log.days < 3) { log.days++; const nd = new Date(W.now); nd.setDate(nd.getDate() + 1); nd.setHours(ri(7, 22), ri(0, 59), 0, 0); await W.run(nd.getTime()); log.ops.push('DAY'); }
    else await W.adv(x < 0.6 ? ri(300, 4000) : x < 0.9 ? ri(4000, 30000) : ri(30000, 300000));
    if (!log.foreign) for (const d of devs) {      // 当天的题组不该变成“当天没人排过”的名单
      const st = call(d, 'info'); if (!st || !st.ready) continue;
      for (const k of ['plan', 'today', 'today2']) { const g = call(d, 'group', k); if (g && g.day === st.day && log.groups[k][g.day] && !log.groups[k][g.day].has(gkey(g.ids))) { log.foreign = { step: i, dev: d.name, kind: d.kind, k, day: g.day, pos: g.pos, len: g.ids.length, lastOps: log.ops.slice(-8) }; } }
    }
  }
  // 静置：全部上线
  for (const dev of devs) { W.online(dev); if (dev.hidden) { dev.hidden = false; dev.inst.sb.document.hidden = false; W.fire(dev.inst, 'hd', 'visibilitychange'); } if (F.focus) W.fire(dev.inst, 'hw', 'focus'); }
  if (F.exit) for (const dev of devs) call(dev, 'exit');
  const inRun = devs.map((d) => { const s = call(d, 'info'); return s && s.run ? (s.run.tkey || 'free') + (s.run.revealed ? ':revealed' : '') : '-'; });
  const a = W.writes.length; await W.adv(10 * 60000); const b = W.writes.length; await W.adv(5 * 60000); const c = W.writes.length;
  const V = [];
  if (c - b > 0) { const h = W.hist.slice(-3).map((x) => ({ by: x.by, at: hm(x.t) })); const hh = W.hist.slice(-2).map((x) => JSON.parse(x.str)); V.push({ type: 'writes-never-stop', quiet5min: c - b, first10min: b - a, by: W.writesBy(b, c), inRun, last: h, diffLast2: hh.length === 2 ? diffTop(hh[0], hh[1]) : null }); }
  const fin = W.cloud() || { q: {}, days: {} }; const fe = fin.epoch || '';
  const mems = devs.map((d) => W.mem(d));
  devs.forEach((d, i) => {
    const dm = diffTop(mems[i], fin); if (Object.keys(dm).length) V.push({ type: (d.kind === 'old' ? 'old-' : '') + 'device-differs-from-cloud:' + Object.keys(dm).sort().join('+'), dev: d.name, diff: dm });
    else { const ls = JSON.parse(d.ls.get(LS_KEY) || 'null'); const dl = diffTop(ls, fin); const ks = Object.keys(dl).filter((k) => k !== 'updated' && k !== 'st'); if (ks.length) V.push({ type: 'localStorage-differs:' + ks.sort().join('+'), dev: d.name, diff: dl }); }
  });
  const cutDay = fe ? new Date(fe).toLocaleDateString('sv-SE', { timeZone: 'Asia/Shanghai' }) : '';
  const inEra = log.answers.filter((x) => x.epoch === fe || (F.keepLater && x.epoch < fe && x.day > cutDay)); const byQ = new Map();
  for (const x of inEra) { if (!byQ.has(x.id)) byQ.set(x.id, []); byQ.get(x.id).push(x); }
  for (const [id, list] of byQ) {
    const D = list.reduce((m, x) => (x.day > m ? x.day : m), ''); const has = (p) => !!p && (p.d || '') >= D; const p = fin.q[id];
    if (!has(p)) { const any = mems.some((m) => has(m.q[id])); V.push({ type: any ? 'answer-missing-in-cloud' : 'answer-lost-everywhere', id, by: [...new Set(list.map((x) => x.dev + '/' + x.kind))], D, cloud: p || null }); }
    else if (list.some((x) => x.day === D && !x.ok) && !(p.d === D && p.b === 0 && p.due === addDays(D, 1))) V.push({ type: 'wrong-answer-overridden', id, D, rec: p, answers: list.filter((x) => x.day === D).map((x) => x.dev + (x.ok ? ':对' : ':错') + '(n=' + x.n + ')') });
  }
  for (const id of Object.keys(fin.q)) if (!byQ.has(id)) V.push({ type: 'pre-reset-record-survived', id, rec: fin.q[id] });
  const fr = log.resets.find((x) => x.epoch === fe);
  if (fr) { const lost = log.answers.filter((x) => x.epoch !== fe && x.t > fr.t && !(fin.q[x.id] && fin.q[x.id].d >= x.day)); if (lost.length) V.push({ type: 'answers-after-reset-wiped(stale-device)', n: lost.length, ex: lost.slice(0, 2).map((x) => ({ dev: x.dev, id: x.id, at: hm(x.t), resetAt: hm(fr.t), resetBy: fr.dev })) }); }
  const lr = log.resets[log.resets.length - 1];
  if (lr && lr.epoch !== fe) V.push({ type: 'later-reset-overridden', last: { dev: lr.dev, at: hm(lr.t), epoch: lr.epoch }, finalEpoch: fe });
  if (log.foreign) V.push({ type: 'today-group-replaced-by-foreign-list', ...log.foreign });
  if (F.trace) console.log(JSON.stringify({ resets: log.resets.map((r) => ({ dev: r.dev, at: hm(r.t), epoch: r.epoch })), finalEpoch: fe, lost: V.filter((v) => v.type.startsWith('answer-')).map((v) => log.answers.filter((x) => x.id === v.id).map((x) => ({ dev: x.dev, at: hm(x.t), epoch: x.epoch, day: x.day, ok: x.ok }))) }));
  return { seed, nDev, kinds: devs.map((d) => d.kind[0]).join(''), skews: devs.map((d) => d.skew), steps, answers: log.answers.length, resets: log.resets.length, days: log.days, writes: W.writes.length, tries: W.tries, gets: W.gets, settle10: b - a, quiet5: c - b, errors: W.errors.slice(0, 3), nerr: W.errors.length, V };
}

// ---------------- 定向情形 ----------------
const out = (o) => console.log(JSON.stringify(o));
async function prep(W, n = 2) { await tick(); await tick(); await W.adv(1500); }
const SC = {
  // 一台设备停在昨天的“今日计划”做题页（没作答的题上），另一台今天排了新计划
  async s1(F) {
    const W = makeWorld(11, { t0: Date.parse('2026-11-28T20:00:00+08:00'), pFail: 0, fast: 40 });
    const pc = W.addDev('PC', F.pcold ? 'old' : 'new', 0), ph = W.addDev('PHONE', 'new', 0); await prep(W);
    const r1 = pc.inst.drv.startPlan(); const k1 = gkey(r1.ids);
    for (let i = 0; i < 30; i++) { pc.inst.drv.answer(true); await W.adv(3000); pc.inst.drv.next(); await W.adv(1000); }
    await W.adv(10000);
    out({ step: '第一天晚上', pc: pc.inst.drv.info().run, pcPlan: brief(W.mem(pc).plan), phonePlan: brief(W.mem(ph).plan), writes: W.writes.length });
    await W.run(Date.parse('2026-11-29T08:00:00+08:00'));
    const w0 = W.writes.length;
    W.fire(ph.inst, 'hd', 'visibilitychange');
    const r2 = ph.inst.drv.startPlan(); const k2 = gkey(r2.ids);
    out({ step: '第二天手机开始今日计划', r: r2.r, day: r2.day, len: r2.ids.length, set: k2, yesterdaySet: k1, overlap: r2.ids.filter((id) => r1.ids.includes(id)).length });
    ph.inst.drv.answer(true); await W.adv(4000); ph.inst.drv.next();
    const seen = []; for (let i = 0; i < 12; i++) { await W.adv(10000); seen.push([W.writes.length - w0, brief(W.mem(ph).plan).set === k2 ? 'phone:今天的' : 'phone:昨天的', brief(W.cloud().plan).set === k2 ? 'cloud:今天的' : 'cloud:昨天的'].join(' ')); }
    out({ step: '手机停在第2题不动的120秒', writes: W.writes.length - w0, by: W.writesBy(w0), every10s: seen });
    const w1 = W.writes.length; let n = 1;
    for (;;) { const s = ph.inst.drv.info(); if (!s.run || s.run.pos >= s.run.len) break; ph.inst.drv.answer(true); n++; await W.adv(4000); ph.inst.drv.next(); await W.adv(1000); }
    out({ step: '手机做完全部' + n + '题', seconds: (n - 1) * 5, writes: W.writes.length - w1, by: W.writesBy(w1), phoneRun: ph.inst.drv.info().run });
    ph.inst.drv.exit(); await W.adv(60000);
    const pm = W.mem(ph).plan, cm = W.cloud().plan;
    out({ step: '手机回到今日页', panel: ph.inst.drv.panel(), phonePlan: brief(pm), isTodaysList: gkey(pm.ids) === k2, isYesterdaysList: gkey(pm.ids) === k1, cloudPlan: brief(cm), cloudIsYesterdaysList: gkey(cm.ids) === k1, totalWrites: W.writes.length - w0, errors: W.errors.slice(0, 2) });
    W.refresh(ph, false); await tick(); await tick(); await W.adv(5000);
    out({ step: '手机刷新后', panel: ph.inst.drv.panel(), plan: brief(W.mem(ph).plan) });
  },
  // 同一天、同一份计划：电脑停在做题页，手机接着做
  async s1same() {
    const W = makeWorld(12, { t0: Date.parse('2026-11-28T09:00:00+08:00'), pFail: 0, fast: 40 });
    const pc = W.addDev('PC', 'new', 0), ph = W.addDev('PHONE', 'new', 0); await prep(W);
    pc.inst.drv.startPlan(); for (let i = 0; i < 10; i++) { pc.inst.drv.answer(true); await W.adv(3000); pc.inst.drv.next(); await W.adv(1000); }
    await W.adv(60000); const w0 = W.writes.length;
    const r = ph.inst.drv.startPlan();
    for (let i = 0; i < 10; i++) { ph.inst.drv.answer(i % 3 !== 0); await W.adv(6000); ph.inst.drv.next(); await W.adv(2000); }
    await W.adv(60000);
    out({ step: '手机接着做10题', r: r.r, writes: W.writes.length - w0, by: W.writesBy(w0), pcRun: pc.inst.drv.info().run, same: canon(W.mem(pc)) === canon(W.cloud()) && canon(W.mem(ph)) === canon(W.cloud()) });
    const w1 = W.writes.length; await W.adv(300000); out({ step: '再静置5分钟', writes: W.writes.length - w1 });
  },
  // 两次清除，先清的那台时钟快3分钟
  async epoch() {
    const W = makeWorld(13, { t0: Date.parse('2026-11-28T09:00:00+08:00'), pFail: 0, fast: 40 });
    const A = W.addDev('A', 'new', 180000), B = W.addDev('B', 'new', 0); await prep(W);
    const pool = A.inst.drv.pool(10);
    A.inst.drv.practice(pool.slice(0, 3), ''); for (let i = 0; i < 3; i++) { A.inst.drv.answer(true); await W.adv(2000); A.inst.drv.next(); } A.inst.drv.exit(); await W.adv(5000);
    const e1 = A.inst.drv.reset(); await W.adv(5000);
    out({ step: 'A（时钟快3分钟）清除', epochA: e1, B: { nq: B.inst.drv.info().nq, epoch: B.inst.drv.info().epoch } });
    B.inst.drv.practice(pool.slice(3, 6), ''); for (let i = 0; i < 3; i++) { B.inst.drv.answer(true); await W.adv(2000); B.inst.drv.next(); } B.inst.drv.exit(); await W.adv(54000);
    out({ step: 'B做了3题', Bnq: B.inst.drv.info().nq, cloudNq: Object.keys(W.cloud().q).length });
    const e2 = B.inst.drv.reset(); const right = B.inst.drv.info().nq; await W.adv(30000);
    out({ step: 'B在A清除约1分钟后再清除', epochB: e2, olderThanExisting: e2 < e1, BnqRightAfterClick: right, Bnq30sLater: B.inst.drv.info().nq, Bepoch: B.inst.drv.info().epoch, cloudNq: Object.keys(W.cloud().q).length, Anq: A.inst.drv.info().nq });
  },
  // 新版设备清除过；旧版页面的记录较新
  async oldloop() {
    const W = makeWorld(14, { t0: Date.parse('2026-11-28T09:00:00+08:00'), pFail: 0, fast: 40 });
    const N = W.addDev('NEW', 'new', 0), O = W.addDev('OLD', 'old', 0); await prep(W);
    const pool = N.inst.drv.pool(12);
    N.inst.drv.practice(pool.slice(0, 5), ''); for (let i = 0; i < 5; i++) { N.inst.drv.answer(true); await W.adv(2000); N.inst.drv.next(); } N.inst.drv.exit(); await W.adv(5000);
    out({ step: '两台同步好', Nnq: N.inst.drv.info().nq, Onq: O.inst.drv.info().nq });
    W.offline(O); N.inst.drv.reset(); await W.adv(3000);
    N.inst.drv.practice(pool.slice(5, 7), ''); for (let i = 0; i < 2; i++) { N.inst.drv.answer(true); await W.adv(2000); N.inst.drv.next(); } N.inst.drv.exit(); await W.adv(5000);
    O.inst.drv.practice(pool.slice(7, 8), ''); O.inst.drv.answer(true); await W.adv(2000); O.inst.drv.next(); O.inst.drv.exit(); await W.adv(2000);
    const w0 = W.writes.length; W.online(O); await W.adv(60000); const w1 = W.writes.length; await W.adv(300000); const w2 = W.writes.length;
    out({ step: '旧版页面上线后', first60s: w1 - w0, next5min: w2 - w1, by: W.writesBy(w1), Nnq: N.inst.drv.info().nq, Onq: O.inst.drv.info().nq, cloudNq: Object.keys(W.cloud().q).length, cloudEpoch: W.cloud().epoch || '' });
  },
  // 同一天同一题：A答错一次；B答对两次（或 A错后重做对、B对两次）
  async wrong() {
    for (const variant of [1, 2]) {
      const W = makeWorld(15, { t0: Date.parse('2026-11-28T09:00:00+08:00'), pFail: 0, fast: 40 });
      const A = W.addDev('A', 'new', 0), B = W.addDev('B', 'new', 0); await prep(W);
      const q = A.inst.drv.pool(3)[0];
      W.offline(A);
      A.inst.drv.practice([q], ''); A.inst.drv.answer(false); await W.adv(2000); A.inst.drv.next(); A.inst.drv.exit();
      if (variant === 2) { A.inst.drv.practice([q], 'redo'); A.inst.drv.answer(true); await W.adv(2000); A.inst.drv.next(); A.inst.drv.exit(); }
      const ra = A.inst.drv.rec(q);
      for (let i = 0; i < 2; i++) { B.inst.drv.practice([q], ''); B.inst.drv.answer(true); await W.adv(2000); B.inst.drv.next(); B.inst.drv.exit(); await W.adv(3000); }
      const rb = B.inst.drv.rec(q);
      W.online(A); await W.adv(120000);
      out({ step: 'wrong 变体' + variant, q, A: ra, B: rb, final: W.cloud().q[q], Afinal: A.inst.drv.rec(q), expect: { b: 0, due: '2026-11-29' } });
    }
  },
  // 同一天两台各答一题，一对一错：days 的 n 一样、c 不一样
  async days() {
    const W = makeWorld(16, { t0: Date.parse('2026-11-28T09:00:00+08:00'), pFail: 0, fast: 40 });
    const A = W.addDev('A', 'new', 0), B = W.addDev('B', 'new', 0); await prep(W);
    const p = A.inst.drv.pool(3);
    W.offline(A); A.inst.drv.practice([p[0]], ''); A.inst.drv.answer(true); await W.adv(2000); A.inst.drv.next(); A.inst.drv.exit();
    B.inst.drv.practice([p[1]], ''); B.inst.drv.answer(false); await W.adv(2000); B.inst.drv.next(); B.inst.drv.exit(); await W.adv(5000);
    W.online(A); await W.adv(600000); const w = W.writes.length; await W.adv(300000);
    out({ step: 'days', A: A.inst.drv.days(), B: B.inst.drv.days(), cloud: W.cloud().days, nq: [A.inst.drv.info().nq, B.inst.drv.info().nq, Object.keys(W.cloud().q).length], quietWrites: W.writes.length - w });
    W.refresh(A, false); await tick(); await tick(); await W.adv(60000); W.refresh(B, false); await tick(); await tick(); await W.adv(60000);
    out({ step: 'days 两台都刷新后', A: A.inst.drv.days(), B: B.inst.drv.days(), cloud: W.cloud().days });
  },
  // 零点前后：B 的时钟快2分钟，先进入第二天并排了新计划
  async midnight() {
    const W = makeWorld(17, { t0: Date.parse('2026-11-28T23:40:00+08:00'), pFail: 0, fast: 40 });
    const A = W.addDev('A', 'new', 0), B = W.addDev('B', 'new', 120000); await prep(W);
    A.inst.drv.startPlan(); for (let i = 0; i < 3; i++) { A.inst.drv.answer(true); await W.adv(2000); A.inst.drv.next(); } A.inst.drv.exit(); await W.adv(10000);
    await W.run(Date.parse('2026-11-28T23:58:20+08:00'));
    const w0 = W.writes.length; W.fire(B.inst, 'hd', 'visibilitychange');
    const r = B.inst.drv.startPlan(); B.inst.drv.answer(true); await W.adv(2000); B.inst.drv.next(); B.inst.drv.exit();
    await W.run(Date.parse('2026-11-28T23:59:58+08:00')); const w1 = W.writes.length;
    out({ step: 'B（快2分钟）已是29日并开始了新计划；A还在28日', r: r.r, day: r.day, writesIn96s: w1 - w0, by: W.writesBy(w0, w1), Aplan: brief(W.mem(A).plan), Bplan: brief(W.mem(B).plan) });
    await W.run(Date.parse('2026-11-29T00:05:00+08:00')); const w2 = W.writes.length; await W.adv(300000);
    out({ step: 'A也过了零点', writesAfter: w2 - w1, quiet5min: W.writes.length - w2, Aplan: brief(W.mem(A).plan), Bplan: brief(W.mem(B).plan), same: canon(W.mem(A)) === canon(W.cloud()) && canon(W.mem(B)) === canon(W.cloud()) });
  },
  // 同一天同一份计划：手机停在做题页；电脑在别的练习里做了计划后面的两道题，然后回到今日页
  async settlefight() {
    const W = makeWorld(19, { t0: Date.parse('2026-11-28T09:00:00+08:00'), pFail: 0, fast: 40 });
    const ph = W.addDev('PHONE', 'new', 0), pc = W.addDev('PC', 'new', 0); await prep(W);
    const r = ph.inst.drv.startPlan(); for (let i = 0; i < 2; i++) { ph.inst.drv.answer(true); await W.adv(3000); ph.inst.drv.next(); await W.adv(1000); }
    await W.adv(10000); const w0 = W.writes.length;
    pc.inst.drv.practice([r.ids[10], r.ids[11]], ''); for (let i = 0; i < 2; i++) { pc.inst.drv.answer(true); await W.adv(3000); pc.inst.drv.next(); await W.adv(1000); }
    const w1 = W.writes.length; pc.inst.drv.exit(); await W.adv(60000); const w2 = W.writes.length; await W.adv(300000); const w3 = W.writes.length;
    out({ step: '电脑回到今日页后', duringPractice: w1 - w0, first60s: w2 - w1, next5min: w3 - w2, by: W.writesBy(w2), phoneRun: ph.inst.drv.info().run, pcPlan: brief(W.mem(pc).plan), phonePlan: brief(W.mem(ph).plan), cloudPlan: brief(W.cloud().plan) });
    const w4 = W.writes.length; for (let i = 0; i < 3; i++) { ph.inst.drv.answer(true); await W.adv(3000); ph.inst.drv.next(); await W.adv(1000); } await W.adv(120000);
    const w5 = W.writes.length; await W.adv(120000);
    out({ step: '手机再做3题后静置', writes: w5 - w4, quiet2min: W.writes.length - w5, phoneRun: ph.inst.drv.info().run, same: canon(W.mem(pc)) === canon(W.cloud()) && canon(W.mem(ph)) === canon(W.cloud()) });
  },
  // 清除没有及时到云端（离线时清除），之后别的设备照常做题
  async latereset() {
    const W = makeWorld(18, { t0: Date.parse('2026-11-28T09:00:00+08:00'), pFail: 0, fast: 40 });
    const A = W.addDev('PHONE', 'new', 0), B = W.addDev('PC', 'new', 0); await prep(W);
    const pool = A.inst.drv.pool(20);
    B.inst.drv.practice(pool.slice(0, 4), ''); for (let i = 0; i < 4; i++) { B.inst.drv.answer(true); await W.adv(2000); B.inst.drv.next(); } B.inst.drv.exit(); await W.adv(5000);
    W.offline(A); const e = A.inst.drv.reset(); await W.adv(5000);
    out({ step: '手机离线时清除', epoch: e, phoneNq: A.inst.drv.info().nq, cloudNq: Object.keys(W.cloud().q).length });
    await W.run(Date.parse('2026-11-29T10:00:00+08:00'));
    B.inst.drv.practice(pool.slice(4, 12), ''); for (let i = 0; i < 8; i++) { B.inst.drv.answer(true); await W.adv(2000); B.inst.drv.next(); } B.inst.drv.exit(); await W.adv(5000);
    out({ step: '第二天电脑又做了8题', pcNq: B.inst.drv.info().nq, cloudNq: Object.keys(W.cloud().q).length });
    W.online(A); await W.adv(120000);
    out({ step: '手机连上网', phoneNq: A.inst.drv.info().nq, pcNq: B.inst.drv.info().nq, cloudNq: Object.keys(W.cloud().q).length, pcDays: B.inst.drv.days() });
  },
};

(async () => {
  const [mode, ...rest] = process.argv.slice(2);
  const F = {}; const pos = []; for (const a of rest) { const m = /^(\w+)=(.*)$/.exec(a); if (m) F[m[1]] = isNaN(Number(m[2])) ? m[2] : Number(m[2]); else pos.push(a); }
  if (mode === 'scen') { for (const n of pos) { console.log('== ' + n); await SC[n](F); } if (UNH.length) console.log('unhandled', UNH.slice(0, 3)); return; }
  const seed0 = Number(pos[0] || 1), count = Number(pos[1] || 10), steps = Number(pos[2] || 120);
  const agg = { rounds: 0, steps: 0, answers: 0, resets: 0, writes: 0, tries: 0, gets: 0, maxSettle10: 0, nerr: 0, types: {}, clean: 0 }; const ex = {}; const errs = new Set();
  const t0 = Date.now();
  for (let s = seed0; s < seed0 + count; s++) {
    const r = await fuzzRound(s, steps, F);
    agg.rounds++; agg.steps += r.steps; agg.answers += r.answers; agg.resets += r.resets; agg.writes += r.writes; agg.tries += r.tries; agg.gets += r.gets; agg.maxSettle10 = Math.max(agg.maxSettle10, r.settle10); agg.nerr += r.nerr; r.errors.forEach((e) => errs.add(e));
    const seen = new Set();
    for (const v of r.V) { const t = v.type; if (!seen.has(t)) { seen.add(t); (agg.types[t] = agg.types[t] || []).push(s); } if (!ex[t]) ex[t] = { seed: s, nDev: r.nDev, kinds: r.kinds, skews: r.skews, ...v }; }
    if (!r.V.length) agg.clean++;
    if (F.verbose) console.log(JSON.stringify({ seed: s, kinds: r.kinds, skews: r.skews, answers: r.answers, resets: r.resets, days: r.days, writes: r.writes, settle10: r.settle10, quiet5: r.quiet5, types: [...seen] }));
  }
  const types = {}; for (const [k, v] of Object.entries(agg.types)) types[k] = { rounds: v.length, seeds: v.slice(0, 12).join(',') };
  console.log(JSON.stringify({ flags: F, seeds: seed0 + '..' + (seed0 + count - 1), ...agg, types, sec: Math.round((Date.now() - t0) / 1000) }, null, 1));
  for (const [k, v] of Object.entries(ex)) console.log('EXAMPLE ' + k + ' ' + JSON.stringify(v).slice(0, 1500));
  if (errs.size) console.log('PAGE ERRORS', [...errs].slice(0, 5));
  if (UNH.length) console.log('unhandled', UNH.slice(0, 3));
})();
