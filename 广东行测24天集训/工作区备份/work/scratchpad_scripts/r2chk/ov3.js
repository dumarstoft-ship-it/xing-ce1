const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const f of ['D04_言语_答案原文册.html','D05_资料_答案册.html']) {
    const p = await b.newPage({ viewport: { width: 420, height: 900 } });
    await p.goto('file://' + encodeURI('/home/user/work/build/pkg_r2/' + f), { waitUntil: 'load' });
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const de = document.documentElement;
      const out = [];
      for (const el of document.querySelectorAll('body *')) {
        if (el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0) out.push([el.tagName + '.' + el.className, el.scrollWidth, el.clientWidth, getComputedStyle(el).overflowX, (el.textContent||'').slice(0,40)]);
      }
      return { de: [de.scrollWidth, de.clientWidth], body: [document.body.scrollWidth, document.body.clientWidth], out: out.slice(0, 6) };
    });
    console.log(f, JSON.stringify(r));
    await p.close();
  }
  await b.close();
})();
