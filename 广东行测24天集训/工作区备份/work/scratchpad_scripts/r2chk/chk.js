const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const dir = '/home/user/work/build/pkg_r2/';
  const files = require('fs').readdirSync(dir).filter(f => f.endsWith('.html'));
  for (const f of files) {
    const p = await b.newPage({ viewport: { width: 420, height: 900 } });
    await p.goto('file://' + dir + encodeURI(f), { waitUntil: 'load' });
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const imgs = [...document.images];
      const broken = imgs.filter(i => !i.complete || i.naturalWidth === 0).length;
      const qs = document.querySelectorAll('.q, section.q, div.q').length;
      const sw = document.documentElement.scrollWidth;
      return { imgs: imgs.length, broken, qs, sw, h: document.body.scrollHeight };
    });
    console.log(f, JSON.stringify(r));
    if (f.startsWith('D06_判断_题目册') || f.startsWith('D05_资料_题目册')) await p.screenshot({ path: f.replace('.html', '.png') });
    await p.close();
  }
  await b.close();
})();
