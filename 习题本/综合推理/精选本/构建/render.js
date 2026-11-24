// Usage: node render.js in.html out.pdf meta.json
// Each .page div is one A4 sheet. Records [data-link] boxes (PDF points, origin top-left of
// the sheet) and reports any .fit box whose content overflows.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const [inHtml, outPdf, metaOut] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(inHtml), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // 流式分页：同一 data-flow 组的容器按 data-seq 排列，放不下的子元素顺延到下一个容器
  await page.evaluate(() => {
    const groups = {};
    document.querySelectorAll('[data-flow]').forEach(el => { (groups[el.dataset.flow] = groups[el.dataset.flow] || []).push(el); });
    const over = el => { const f = el.closest('.fit'); return f.scrollHeight > f.clientHeight + 1; };
    for (const g of Object.values(groups)) {
      g.sort((a, b) => (+a.dataset.seq) - (+b.dataset.seq));
      for (let i = 0; i < g.length - 1; i++) {
        const c = g[i], n = g[i + 1], min = +(c.dataset.min || 1);
        while (over(c) && c.children.length > min) n.insertBefore(c.lastElementChild, n.firstChild);
        while (c.children.length > min && c.lastElementChild.classList.contains('keep-next'))
          n.insertBefore(c.lastElementChild, n.firstChild);
      }
    }
  });
  const meta = await page.evaluate(() => {
    const PX2PT = 0.75;
    const pages = Array.from(document.querySelectorAll('.page'));
    const links = [], overflow = [];
    pages.forEach((pg, pi) => {
      const pr = pg.getBoundingClientRect();
      pg.querySelectorAll('[data-link]').forEach(el => {
        for (const r of el.getClientRects()) {
          links.push({ page: pi, target: el.dataset.link,
            x0: (r.left - pr.left) * PX2PT, top: (r.top - pr.top) * PX2PT,
            x1: (r.right - pr.left) * PX2PT, bottom: (r.bottom - pr.top) * PX2PT });
        }
      });
      pg.querySelectorAll('.fit').forEach(el => {
        if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1)
          overflow.push({ page: pi, id: el.id || '', sh: el.scrollHeight, ch: el.clientHeight });
      });
    });
    return { pageCount: pages.length, links, overflow };
  });
  fs.writeFileSync(metaOut, JSON.stringify(meta, null, 1));
  await page.pdf({ path: outPdf, printBackground: true, preferCSSPageSize: true,
                   margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await browser.close();
  if (meta.overflow.length) { console.error('OVERFLOW', JSON.stringify(meta.overflow)); process.exit(3); }
})().catch(e => { console.error(e); process.exit(1); });
