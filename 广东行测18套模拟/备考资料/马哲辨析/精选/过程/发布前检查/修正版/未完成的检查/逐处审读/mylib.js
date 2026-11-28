// 检查人 read 的小工具：真浏览器里开页面（站点目录或单文件），假时钟、可调的假云端（页面内）、可模拟转后台。
// 假云端的开关都在 window.__c 上：
//   getMode / setMode: 'ok' | 'hang'（一直不返回） | 'cache'（get 给 fromCache 副本） | 'throw:<code>'
//   snapMode: 'ok' | 'never'（监听一直没有快照） | 'error'（直接走错误回调） | 'cacheOnly'
//   remote: 云端文档（字符串，键排过序）；__emit() 把当前云端发给监听；gets / sets 计数；log 记录每次调用
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const HERE = __dirname;
function sortKeys(v) { if (Array.isArray(v)) return v.map(sortKeys); if (v && typeof v === 'object') { const o = {}; for (const k of Object.keys(v).sort()) o[k] = sortKeys(v[k]); return o; } return v; }

function pageInit(o) {
  const Real = Date; const saved = sessionStorage.getItem('__now');
  window.__off = (saved ? Number(saved) : o.t) - Real.now();
  window.__setNow = (ms) => { sessionStorage.setItem('__now', String(ms)); window.__off = ms - Real.now(); };
  window.__addNow = (ms) => { window.__setNow(Real.now() + window.__off + ms); };
  class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + window.__off); } static now() { return Real.now() + window.__off; } }
  window.Date = Fake;
  if (o.seed) { let s = o.seed; Math.random = () => { s = (s * 1103515245 + 12345) % 2147483648; return s / 2147483648; }; }
  if (o.local && !sessionStorage.getItem('__seeded')) { sessionStorage.setItem('__seeded', '1'); localStorage.setItem('mzbx-progress-v1', o.local); }
  // 心跳 20 秒可以调快（只改恰好 20000 毫秒的定时器），别的定时器照原样
  const st = window.setTimeout.bind(window);
  window.__timers = 0;
  window.setTimeout = (fn, ms, ...a) => { window.__timers++; return st(fn, ms === 20000 && o.beatMs ? o.beatMs : ms, ...a); };
  // 模拟转后台
  window.__hidden = false;
  try { Object.defineProperty(document, 'hidden', { configurable: true, get: () => window.__hidden }); Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => (window.__hidden ? 'hidden' : 'visible') }); } catch (e) {}
  window.__hide = () => { window.__hidden = true; document.dispatchEvent(new Event('visibilitychange')); };
  window.__show = (noFocus) => { window.__hidden = false; document.dispatchEvent(new Event('visibilitychange')); if (!noFocus) window.dispatchEvent(new Event('focus')); };
  if (o.cloud) {
    const sortKeys = (v) => { if (Array.isArray(v)) return v.map(sortKeys); if (v && typeof v === 'object') { const x = {}; for (const k of Object.keys(v).sort()) x[k] = sortKeys(v[k]); return x; } return v; };
    const c = window.__c = { getMode: 'ok', setMode: 'ok', snapMode: o.cloud.snapMode || 'ok', remote: o.cloud.remote || null, gets: 0, sets: 0, log: [], cb: null, err: null, useMode: o.cloud.useMode || 'ok', hung: [] };
    if (o.cloud.getMode) c.getMode = o.cloud.getMode; if (o.cloud.setMode) c.setMode = o.cloud.setMode;
    const mk = (code) => { const e = new Error(code); e.code = code; return e; };
    const snap = (str, meta) => ({ id: 'main', exists: str != null, data: () => (str == null ? undefined : JSON.parse(str)), metadata: meta });
    const lag = (ms) => new Promise((r) => st(r, ms));
    const ref = {
      id: 'main', path: 'progress/main',
      async get() {
        c.gets++; const m = c.getMode; c.log.push('get:' + m + '@' + new Real(Real.now() + window.__off).toISOString().slice(11, 19));
        if (m === 'hang') return new Promise((res) => { c.hung.push(() => res(snap(c.remote, { fromCache: false, hasPendingWrites: false }))); });
        await lag(o.cloud.lag == null ? 30 : o.cloud.lag);
        if (m === 'cache') return snap(c.remote, { fromCache: true, hasPendingWrites: false });
        if (m.startsWith('throw:')) throw mk(m.slice(6));
        return snap(c.remote, { fromCache: false, hasPendingWrites: false });
      },
      async set(d) {
        const m = c.setMode; c.log.push('set:' + m + '@' + new Real(Real.now() + window.__off).toISOString().slice(11, 19));
        if (m === 'hang') return new Promise((res) => { c.hung.push(() => { c.remote = JSON.stringify(sortKeys(JSON.parse(JSON.stringify(d)))); c.sets++; res(); st(() => c.emit(), 5); }); });
        await lag(o.cloud.lag == null ? 30 : o.cloud.lag);
        if (m.startsWith('throw:')) throw mk(m.slice(6));
        c.remote = JSON.stringify(sortKeys(JSON.parse(JSON.stringify(d)))); c.sets++;
        st(() => c.emit(), 5);
      },
      onSnapshot(cb, err) {
        c.cb = cb; c.err = err;
        if (c.snapMode === 'error') { st(() => err && err(mk(o.cloud.snapErr || 'not_granted')), 20); return () => {}; }
        if (c.snapMode === 'cacheOnly') { st(() => cb(snap(c.remote, { fromCache: true, hasPendingWrites: false })), 20); return () => {}; }
        if (c.snapMode === 'never') return () => {};
        st(() => c.emit(), o.cloud.firstSnap == null ? 20 : o.cloud.firstSnap);
        return () => { c.cb = null; };
      },
    };
    c.emit = () => { if (c.cb && c.snapMode === 'ok') c.cb(snap(c.remote, { fromCache: false, hasPendingWrites: false })); };
    c.release = () => { const h = c.hung; c.hung = []; for (const f of h) f(); };
    const useDb = async () => { if (c.useMode === 'hang') return new Promise(() => {}); if (c.useMode === 'throw') throw mk('capability_disabled'); if (c.useMode === 'none') return null; return { doc: () => ref }; };
    window.claude = { use: async (name) => (name === 'db' ? useDb() : null) };
    if (o.hot) { if (o.hot.mode === 'ready') window.claude.hot = { ready: (fn) => st(() => fn(o.hot.data), 30), snapshot: (fn) => { window.__hotSnap = fn; } }; else window.claude.hot = { data: o.hot.data, snapshot: (fn) => { window.__hotSnap = fn; } }; }
  } else if (o.hot) {
    window.claude = { hot: o.hot.mode === 'ready' ? { ready: (fn) => st(() => fn(o.hot.data), 30), snapshot: (fn) => { window.__hotSnap = fn; } } : { data: o.hot.data, snapshot: (fn) => { window.__hotSnap = fn; } } };
  }
  window.__chk = () => {
    const out = [];
    const w = document.documentElement.scrollWidth - window.innerWidth; if (w > 0) out.push('横向溢出 ' + w + 'px');
    const txt = (document.querySelector('header') ? document.querySelector('header').innerText : '') + '\n' + (document.querySelector('main') ? document.querySelector('main').innerText : '');
    const m = txt.match(/.{0,14}(undefined|NaN|null|\[object Object\]).{0,14}/); if (m) out.push('怪字样: ' + m[0].replace(/\s+/g, ' '));
    const nav = document.querySelector('nav.tabs'); if (nav && nav.scrollWidth > nav.clientWidth + 1) out.push('分栏条要横滑 ' + nav.scrollWidth + '>' + nav.clientWidth);
    return out;
  };
}

// o: { site: 站点目录 | single: 单文件路径, when, local, cloud: {...}|null, hot, beatMs, width, tz }
async function open(b, o = {}) {
  const ctx = await b.newContext({ viewport: { width: o.width || 390, height: o.height || 844 }, deviceScaleFactor: 1, isMobile: o.mobile !== false, hasTouch: o.mobile !== false, timezoneId: o.tz || 'Asia/Shanghai' });
  const SITE = o.site || path.join(HERE, 'site_v7c');
  await ctx.route('**/*', (route) => {
    const u = new URL(route.request().url());
    if (u.hostname !== 'mz.local') return route.abort();
    if (o.single) return route.fulfill({ body: fs.readFileSync(o.single, 'utf8'), contentType: 'text/html; charset=utf-8' });
    const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
    if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
    if (o.failData) return route.abort();
    return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
  });
  const pg = await ctx.newPage(); const errs = [];
  pg.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  pg.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource|net::ERR/.test(m.text())) errs.push('console: ' + m.text()); });
  await pg.addInitScript(pageInit, { t: new Date(o.when || '2026-11-28T09:00:00+08:00').getTime(), local: o.local || null, seed: o.seed === undefined ? 4242 : o.seed, cloud: o.cloud || null, hot: o.hot || null, beatMs: o.beatMs || 0 });
  await pg.goto(o.url || 'http://mz.local/index.html' + (o.hash || '')); await pg.waitForSelector(o.waitFor || '.today, #qcard'); await pg.waitForTimeout(o.settle == null ? 200 : o.settle);
  return { pg, errs, ctx };
}
const st = (d) => d.pg.evaluate(() => {
  const el = document.querySelector('.panel.today'); const btn = el && el.querySelector('button.primary');
  const notes = [...document.querySelectorAll('#main .note')].map((x) => (x.hidden ? '' : x.innerText.replace(/\s+/g, ' '))).filter((t) => /云端|同步|设备|连不上|所有者/.test(t));
  return { now: new Date().toISOString(), day: dayStr(), view: S.run ? (document.querySelector('#qcard') ? 'q' : 'sum') : (location.hash || '#today'), btn: btn ? btn.textContent : null, disabled: btn ? btn.disabled : null,
    text: el ? el.innerText.replace(/\s+/g, ' ').slice(0, 260) : document.querySelector('#main').innerText.replace(/\s+/g, ' ').slice(0, 200),
    cloud: S.cloud, synced: !!S.synced, saving: !!S.saving, again: !!S.again, note: S.cloudNote, notesShown: notes, waking: typeof waking === 'undefined' ? null : !!waking,
    nq: S.prog ? Object.keys(S.prog.q).length : null, plan: S.prog && S.prog.plan ? { day: S.prog.plan.day, pos: S.prog.plan.pos, len: S.prog.plan.ids.length } : null,
    run: S.run ? { tkey: S.run.tkey, day: S.run.day, pos: S.run.pos, len: S.run.list.length, label: S.run.label } : null,
    gets: window.__c ? window.__c.gets : null, sets: window.__c ? window.__c.sets : null, remoteNq: window.__c && window.__c.remote ? Object.keys(JSON.parse(window.__c.remote).q || {}).length : null,
    countdown: document.querySelector('#countdown').innerText, chk: window.__chk() };
});
// 像用户一样答一题
async function answerUI(pg, ok) {
  const info = await pg.evaluate((ok) => {
    const R = S.run; if (!R || R.pos >= R.list.length || !document.querySelector('#qcard')) return null;
    const q = R.list[R.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer; let picks;
    if (q.type === '判断') picks = [ok ? ans : (ans === '正确' ? '错误' : '正确')];
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); picks = ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]; }
    return { id: q.id, type: q.type, picks, pos: R.pos, len: R.list.length };
  }, ok);
  if (!info) return null;
  for (const v of info.picks) await pg.click(`#qcard .opt[data-v="${v}"]`);
  if (info.type === '多选') await pg.click('#submitMulti');
  await pg.waitForSelector('#nextBtn');
  await pg.click('#nextBtn');
  return info;
}
const fastN = (pg, n, wrongEvery, offset) => pg.evaluate(({ n, wrongEvery, offset }) => {
  const out = [];
  for (let i = 0; i < n; i++) {
    const R = S.run; if (!R || R.pos >= R.list.length || !runState || runState.revealed) break;
    const q = R.list[R.pos]; const ok = !(wrongEvery && (i + offset) % wrongEvery === 0);
    const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
    if (q.type === '判断') runState.picked = new Set([ok ? ans : (ans === '正确' ? '错误' : '正确')]);
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
    reveal(q); nextQ(); out.push({ id: q.id, ok });
  }
  return out;
}, { n: n == null ? 1e9 : n, wrongEvery: wrongEvery || 0, offset: offset || 0 });
const planBtn = (pg, label) => pg.locator('.panel.today').first().locator(`button:text-is("${label}")`);
let fails = 0;
const ok = (cond, name, extra) => { console.log(`  ${cond ? '✓' : '✗'} ${name}${extra === undefined ? '' : '  ' + (typeof extra === 'string' ? extra : JSON.stringify(extra))}`); if (!cond) fails++; return cond; };
const info = (name, extra) => console.log(`  · ${name}${extra === undefined ? '' : '  ' + (typeof extra === 'string' ? extra : JSON.stringify(extra))}`);
module.exports = { chromium, HERE, open, st, answerUI, fastN, planBtn, ok, info, sortKeys, fails: () => fails, launch: () => chromium.launch() };
