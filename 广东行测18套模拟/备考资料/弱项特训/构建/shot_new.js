const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const SITE = path.resolve('site');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.route('**/*', (r) => { const u = new URL(r.request().url()); if (u.hostname !== 'xc.local') return r.abort(); const f = path.join(SITE, decodeURIComponent(u.pathname)); if (f.endsWith('.html')) return r.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' }); return r.fulfill({ path: f }); });
  const pg = await ctx.newPage(); const errs = []; pg.on('pageerror', (e) => errs.push(e.message));
  await pg.goto('http://xc.local/index.html'); await pg.waitForSelector('.steps');
  const ids = ['S01-Q34', 'ZJ2024-054', 'g:frac:5022', 'g:frac:5003'];
  await pg.evaluate((ids) => startRun(ids, '看看'), ids); await pg.waitForSelector('#qcard');
  for (let i = 0; i < ids.length; i++) {
    await pg.screenshot({ path: `shot_new${i}_q.png` });
    await pg.click('#qcard [data-v="A"]'); await pg.waitForTimeout(150);
    await pg.screenshot({ path: `shot_new${i}_a.png`, fullPage: true });
    if (i < ids.length - 1) await pg.click('#nextBtn');
  }
  console.log('errs', errs); await b.close();
})();
