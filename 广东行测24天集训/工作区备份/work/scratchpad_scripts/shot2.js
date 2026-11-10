const { chromium } = require('playwright');
(async () => {
  const [path, out, w, scrollTo] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: parseInt(w || '390'), height: 1400 } });
  await pg.goto('file://' + path); await pg.waitForTimeout(800);
  if (scrollTo) { await pg.evaluate((id) => { const e = document.getElementById(id); if (e) e.scrollIntoView(); }, scrollTo); await pg.evaluate(() => window.scrollBy(0, -700)); }
  await pg.screenshot({ path: out }); await b.close();
})();
