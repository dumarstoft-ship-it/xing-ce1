const { chromium } = require('playwright');
(async () => {
  const [path, out, w] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: parseInt(w || '390'), height: 1300 } });
  await pg.goto('file://' + path); await pg.screenshot({ path: out }); await b.close();
})();
