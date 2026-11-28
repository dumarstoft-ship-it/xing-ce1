// 审查用的公共工具：打开站点（路由拦截）、假时钟、固定随机数、预置本机记录、程序化作答。
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const HERE = __dirname;
let browser = null;
async function launch() { if (!browser) browser = await chromium.launch(); return browser; }
async function close() { if (browser) await browser.close(); browser = null; }
// opts: { local: JSON字符串或对象, width, height, dark, seed, noSeedRandom }
async function open(site, when, opts = {}) {
  const b = await launch();
  const SITE = path.isAbsolute(site) ? site : path.join(HERE, site);
  const ctx = await b.newContext({ viewport: { width: opts.width || 390, height: opts.height || 844 }, colorScheme: opts.dark ? 'dark' : 'light', acceptDownloads: true });
  await ctx.route('http://mz.local/**', (route) => {
    const u = new URL(route.request().url());
    const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
    if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
    if (opts.patchJson && opts.patchJson[path.basename(f)]) return route.fulfill({ body: opts.patchJson[path.basename(f)](fs.readFileSync(f, 'utf8')), contentType: 'application/json; charset=utf-8' });
    return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
  });
  const pg = await ctx.newPage(); const errs = [];
  pg.on('pageerror', (e) => errs.push(e.message));
  pg.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  const local = opts.local == null ? null : (typeof opts.local === 'string' ? opts.local : JSON.stringify(opts.local));
  await pg.addInitScript(({ t, local, seed, noSeedRandom }) => {
    const Real = Date; const saved = sessionStorage.getItem('__now');
    window.__off = (saved ? Number(saved) : t) - Real.now(); window.__setNow = (ms) => { sessionStorage.setItem('__now', String(ms)); window.__off = ms - Real.now(); };
    class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + window.__off); } static now() { return Real.now() + window.__off; } }
    window.Date = Fake;
    if (!noSeedRandom) { let s = seed || 4242; Math.random = () => { s = (s * 1103515245 + 12345) % 2147483648; return s / 2147483648; }; }
    if (local && !sessionStorage.getItem('__seeded')) { sessionStorage.setItem('__seeded', '1'); localStorage.setItem('mzbx-progress-v1', local); }
  }, { t: new Date(when).getTime(), local, seed: opts.seed || 0, noSeedRandom: !!opts.noSeedRandom });
  await pg.goto('http://mz.local/index.html' + (opts.hash || '')); await pg.waitForSelector(opts.waitFor || '.today'); await pg.waitForTimeout(150);
  return { pg, errs, ctx };
}
const setNow = (pg, when) => pg.evaluate((ms) => window.__setNow(ms), new Date(when).getTime());
const reload = async (pg, sel) => { await pg.evaluate(() => { S.run = null; }); await pg.reload(); await pg.waitForSelector(sel || '.today'); await pg.waitForTimeout(150); };
// 程序化作答当前题：ok=true 答对，false 答错；返回题号，没有题时返回 null
const answer = (pg, ok, noNext) => pg.evaluate(({ ok, noNext }) => {
  const R = S.run; if (!R || R.pos >= R.list.length) return null;
  const q = R.list[R.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
  if (q.type === '判断') runState.picked = new Set([ok ? ans : (ans === '正确' ? '错误' : '正确')]);
  else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
  reveal(q); if (!noNext) nextQ(); return q.id;
}, { ok, noNext: !!noNext });
// 把当前这组做完：fn(i, id) 返回是否答对
const finish = async (pg, fn) => { let i = 0; const wrong = [], all = []; for (;;) { const ok = fn ? !!(await fn(i)) : true; const id = await answer(pg, ok); if (!id) break; all.push(id); if (!ok) wrong.push(id); i++; } return { wrong, all }; };
const prog = (pg) => pg.evaluate(() => JSON.parse(JSON.stringify(S.prog)));
const mkCheck = () => { const fails = []; const check = (label, cond, detail) => { console.log((cond ? '  ✓ ' : '  ✗ ') + label + (detail ? '  ' + detail : '')); if (!cond) fails.push(label); return cond; }; check.fails = fails; return check; };
module.exports = { launch, close, open, setNow, reload, answer, finish, prog, mkCheck, HERE };
