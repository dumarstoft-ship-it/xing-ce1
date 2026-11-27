// 今日计划页面截图（新开一个没有记录的浏览器），可指定日期
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const SITE = process.argv[2], OUT = process.argv[3], DAY = process.argv[4] || '2026-11-28';
  const b = await chromium.launch(); const errs = [];
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await ctx.route('http://mz.local/**', (route) => {
    const u = new URL(route.request().url());
    const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
    if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
    return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
  });
  const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(e.message));
  await pg.addInitScript((t) => { const Real = Date, off = t - Real.now(); class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + off); } static now() { return Real.now() + off; } } window.Date = Fake; }, new Date(DAY + 'T09:00:00').getTime());
  await pg.goto('http://mz.local/index.html'); await pg.waitForSelector('.today'); await pg.waitForTimeout(300);
  for (const d of await pg.$$('details.more')) await d.evaluate((el) => { el.open = true; });
  await pg.screenshot({ path: OUT + '/plan_today.png', fullPage: true });
  await pg.click('.today button:text-is("开始")'); await pg.waitForSelector('#qcard');
  await pg.screenshot({ path: OUT + '/plan_q.png' });
  const ov = await pg.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  console.log('overflow', ov, 'errors:', errs.length ? errs.join('\n') : 'none'); await b.close();
})();
