const { chromium } = require('playwright');
(async () => {
  const [inp, out, label] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file://' + inp, { waitUntil: 'load' });
  await pg.waitForTimeout(500);
  await pg.pdf({ path: out, format: 'A4', printBackground: true, displayHeaderFooter: true,
    margin: { top: '16mm', bottom: '16mm', left: '14mm', right: '14mm' },
    headerTemplate: `<div style="font-size:8px;width:100%;text-align:right;padding-right:14mm;color:#666;font-family:'WenQuanYi Zen Hei',sans-serif">${label}</div>`,
    footerTemplate: `<div style="font-size:8px;width:100%;text-align:center;color:#666;font-family:'WenQuanYi Zen Hei',sans-serif"><span class="pageNumber"></span> / <span class="totalPages"></span></div>` });
  await b.close();
})();
