// 用 Chromium（Playwright）把排好的 HTML 印成 PDF。
//   node render_pdf.js <html路径> <pdf路径>
// 输出最后一行为 JSON：选项排法等版面决定，供 build_print.py 写入排版日志。
const { chromium } = require('playwright');

(async () => {
  const [htmlPath, pdfPath] = process.argv.slice(2);
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto('file://' + htmlPath, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const decisions = await page.evaluate(() => (window.__layout ? window.__layout() : null));
    // 确认所有题图已解码
    await page.evaluate(async () => {
      await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
    });
    const broken = await page.evaluate(() =>
      [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src));
    if (broken.length) throw new Error('题图未能加载：' + broken.join(', '));
    await page.pdf({ path: pdfPath, preferCSSPageSize: true, printBackground: true });
    console.log(JSON.stringify({ decisions }));
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err.stack || String(err)); process.exit(1); });
