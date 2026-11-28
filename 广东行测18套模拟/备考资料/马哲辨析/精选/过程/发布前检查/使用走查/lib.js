// walk 的工具：打开站点（假时钟、可选假云端，云端文档按键名排序存）、像用户一样点着做题、检查版面
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const DIR = __dirname; const SITE = process.env.SITE || path.join(DIR, 'site');
function sortKeys(v) { if (Array.isArray(v)) return v.map(sortKeys); if (v && typeof v === 'object') { const o = {}; for (const k of Object.keys(v).sort()) o[k] = sortKeys(v[k]); return o; } return v; }
function pageInit({ t, local, seed, cloud, delay }) {
  const Real = Date; const saved = sessionStorage.getItem('__now');
  window.__off = (saved ? Number(saved) : t) - Real.now();
  window.__setNow = (ms) => { sessionStorage.setItem('__now', String(ms)); window.__off = ms - Real.now(); };
  class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + window.__off); } static now() { return Real.now() + window.__off; } }
  window.Date = Fake;
  if (seed) { let s = seed; Math.random = () => { s = (s * 1103515245 + 12345) % 2147483648; return s / 2147483648; }; }
  if (local && !sessionStorage.getItem('__seeded')) { sessionStorage.setItem('__seeded', '1'); localStorage.setItem('mzbx-progress-v1', local); }
  if (cloud) {
    const off = () => { const e = new Error('offline'); e.code = 'unavailable'; return e; };
    const ref = {
      async set(d) { if (!window.__online) throw off(); window.__sets = (window.__sets || 0) + 1; await window.__remoteSet(JSON.stringify(d)); },
      async get() { if (!window.__online) throw off(); window.__gets = (window.__gets || 0) + 1; const s = await window.__remoteGet(); const data = s ? JSON.parse(s) : null; return { exists: !!data, data: () => data, metadata: { fromCache: false, hasPendingWrites: false } }; },
      onSnapshot(cb) { ref._cb = cb; setTimeout(() => window.__emit(), delay); },
    };
    window.__online = !sessionStorage.getItem('__offline');
    window.__emit = async () => { if (!window.__online) return; const s = await window.__remoteGet(); const data = s ? JSON.parse(s) : null; if (ref._cb) ref._cb({ exists: !!data, data: () => data, metadata: { fromCache: false, hasPendingWrites: false } }); };
    window.claude = { use: async (name) => (name === 'db' ? { doc: () => ref } : null) };
  }
  window.__chk = () => {
    const out = [];
    const w = document.documentElement.scrollWidth - window.innerWidth; if (w > 0) out.push('横向溢出 ' + w + 'px');
    const txt = (document.querySelector('header') ? document.querySelector('header').innerText : '') + '\n' + (document.querySelector('main') ? document.querySelector('main').innerText : '');
    const m = txt.match(/.{0,14}(undefined|NaN|null|\[object Object\]).{0,14}/); if (m) out.push('怪字样: ' + m[0].replace(/\s+/g, ' '));
    for (const el of document.querySelectorAll('main *, header *')) { const r = el.getBoundingClientRect(); if (r.width && r.height && (r.right > window.innerWidth + 1 || r.left < -1)) { if (el.closest('.tbl, nav.tabs, .days, .daylbl')) continue; out.push('伸出屏幕: ' + el.tagName + '.' + el.className + ' right=' + Math.round(r.right)); break; } }
    const nav = document.querySelector('nav.tabs'); if (nav && nav.scrollWidth > nav.clientWidth + 1) out.push('分栏条要横滑 ' + nav.scrollWidth + '>' + nav.clientWidth);
    return out;
  };
}
async function device(b, o = {}) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  await ctx.route('**/*', (route) => {
    const u = new URL(route.request().url());
    if (u.hostname !== 'mz.local') return route.abort();
    const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
    if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
    return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
  });
  const pg = await ctx.newPage(); const errs = [];
  pg.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  pg.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push('console: ' + m.text()); });
  if (o.store) {
    const store = o.store;
    await ctx.exposeFunction('__remoteGet', () => store.remote);
    await ctx.exposeFunction('__remoteSet', (s) => { store.remote = JSON.stringify(sortKeys(JSON.parse(s))); store.sets++; store.log.push(o.name);
      for (const p of store.pages) if (p !== pg) p.evaluate(() => window.__emit && window.__emit()).catch(() => {}); pg.evaluate(() => setTimeout(() => window.__emit(), 5)).catch(() => {}); });
    store.pages.push(pg);
  }
  await pg.addInitScript(pageInit, { t: new Date(o.when).getTime(), local: o.local || null, seed: o.seed === undefined ? 4242 : o.seed, cloud: !!o.store, delay: o.delay == null ? 20 : o.delay });
  await pg.goto('http://mz.local/index.html'); await pg.waitForSelector('.today'); await pg.waitForTimeout(o.store ? 350 : 120);
  return { pg, errs, ctx, name: o.name || 'dev' };
}
const newStore = () => ({ remote: null, sets: 0, pages: [], log: [] });
const setNow = (pg, when) => pg.evaluate((ms) => window.__setNow(ms), new Date(when).getTime());
const wake = async (pg) => { await pg.evaluate(() => { document.dispatchEvent(new Event('visibilitychange')); window.dispatchEvent(new Event('focus')); }); await pg.waitForTimeout(120); };
const reload = async (pg) => { await pg.reload(); await pg.waitForSelector('.today, #qcard'); await pg.waitForTimeout(150); };
const planBtn = (pg, label) => pg.locator('.panel.today').first().locator(`button:text-is("${label}")`);
// 今日页的情况：面板文字、三格数字、计划、实际的核心/备选进度、估算
const todayInfo = (pg) => pg.evaluate(() => {
  const el = document.querySelector('.panel.today'); const P = S.prog.q;
  const core = S.qs.filter((q) => q.t === 1 && !paused(q)), bk = S.qs.filter((q) => q.t === 2 && !paused(q));
  const t = S.prog.plan && S.prog.plan.day === dayStr() ? S.prog.plan : null;
  const text = el ? el.innerText.replace(/\s+/g, ' ') : null; const m = text && text.match(/还差(\d+)道/);
  return { day: dayStr(), left: daysLeft(), text, short: m ? Number(m[1]) : (text && /核心还有/.test(text) ? 0 : null),
    stats: [...document.querySelectorAll('#main .stat')].map((s) => s.innerText.replace(/\s+/g, ' ')).join(' | '),
    plan: t ? { pos: t.pos, len: t.ids.length, n: t.n } : null,
    coreSeen: core.filter((q) => P[q.id]).length, coreFresh: core.filter((q) => !P[q.id]).length, bkSeen: bk.filter((q) => P[q.id]).length,
    tried: Object.keys(P).length, answeredToday: (S.prog.days[dayStr()] || { n: 0 }).n, distinctToday: Object.values(P).filter((p) => p.d === dayStr()).length,
    wrongOpen: Object.values(P).filter((p) => !p.b && p.due <= dayStr()).length, once1Due: core.filter((q) => P[q.id] && P[q.id].b === 1 && P[q.id].due <= dayStr()).length,
    countdown: document.querySelector('#countdown').innerText, wrongTab: document.querySelector('#wrongN').textContent, chk: window.__chk() };
});
const preview = (pg) => pg.evaluate(() => { const p = planParts(dailyOf()); const P = S.prog.q; const by = {}; for (const q of p.list) { const k = (P[q.id] ? '旧' : '新') + (TIER_NAME[q.t || 3]); by[k] = (by[k] || 0) + 1; } return { n: p.n, len: p.list.length, by, sum: Object.values(p.n).reduce((a, x) => a + x, 0) }; });
// 像用户一样答一题：点选项（多选再点提交），看完点“下一题”
async function answerUI(pg, ok, problems) {
  const info = await pg.evaluate((ok) => {
    const R = S.run; if (!R || R.pos >= R.list.length || !document.querySelector('#qcard')) return null;
    const q = R.list[R.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer; let picks;
    if (q.type === '判断') picks = [ok ? ans : (ans === '正确' ? '错误' : '正确')];
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); picks = ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]; }
    return { id: q.id, type: q.type, picks, t: q.t || 3, seen: !!S.prog.q[q.id], pos: R.pos, len: R.list.length, posText: document.querySelector('.runbar .pos').textContent, chk: window.__chk() };
  }, ok);
  if (!info) return null;
  for (const v of info.picks) await pg.click(`#qcard .opt[data-v="${v}"]`);
  if (info.type === '多选') await pg.click('#submitMulti');
  const after = await pg.evaluate(() => ({ verdict: (document.querySelector('.verdict') || {}).innerText || null, chk: window.__chk() }));
  if (problems) { for (const c of info.chk) problems.push(`${info.id} 题面: ${c}`); for (const c of after.chk) problems.push(`${info.id} 解析: ${c}`); if (!after.verdict) problems.push(`${info.id} 点了选项没有出结果`); if (info.posText !== `${info.pos + 1}/${info.len}`) problems.push(`${info.id} 进度显示 ${info.posText} 实际 ${info.pos + 1}/${info.len}`); }
  info.ok = /答对了/.test(after.verdict || '');
  await pg.click('#nextBtn');
  return info;
}
async function doRun(pg, okFn, limit, problems) { const done = []; for (let i = 0; i < (limit == null ? 1e9 : limit); i++) { const r = await answerUI(pg, okFn(i), problems); if (!r) break; done.push(r); } return done; }

// 快速答题（直接调页面里的 reveal/nextQ，一次答 n 题；wrongEvery=4 表示每4题错1题）
const fastN = (pg, n, wrongEvery, offset) => pg.evaluate(({ n, wrongEvery, offset }) => {
  const out = [];
  for (let i = 0; i < n; i++) {
    const R = S.run; if (!R || R.pos >= R.list.length || !runState || runState.revealed) break;
    const q = R.list[R.pos]; const ok = !(wrongEvery && (i + offset) % wrongEvery === 0);
    const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
    if (q.type === '判断') runState.picked = new Set([ok ? ans : (ans === '正确' ? '错误' : '正确')]);
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
    const seenDay = S.prog.q[q.id] ? S.prog.q[q.id].d : null;
    reveal(q); nextQ(); out.push({ id: q.id, ok, t: q.t || 3, seenDay });
  }
  return out;
}, { n: n == null ? 1e9 : n, wrongEvery: wrongEvery || 0, offset: offset || 0 });
const mainText = (pg, n) => pg.evaluate((n) => document.querySelector('#main').innerText.replace(/\s+/g, ' ').slice(0, n || 400), n);
async function sheet(b, files, out) {   // 把几张截图拼成一张
  const ctx = await b.newContext({ viewport: { width: files.length * 400 + 10, height: 900 } }); const pg = await ctx.newPage();
  const imgs = files.map((f) => `<figure style="margin:0 5px;width:390px"><figcaption style="font:12px sans-serif">${path.basename(f)}</figcaption><img src="data:image/png;base64,${fs.readFileSync(f).toString('base64')}" style="width:390px;border:1px solid #999"></figure>`).join('');
  await pg.setContent(`<body style="margin:5px;display:flex;align-items:flex-start;background:#ccc">${imgs}</body>`); await pg.waitForTimeout(200);
  await pg.screenshot({ path: out, fullPage: true }); await ctx.close();
}
module.exports = { chromium, DIR, SITE, device, newStore, setNow, wake, reload, planBtn, todayInfo, preview, answerUI, doRun, fastN, mainText, sheet, sortKeys, launch: () => chromium.launch() };
