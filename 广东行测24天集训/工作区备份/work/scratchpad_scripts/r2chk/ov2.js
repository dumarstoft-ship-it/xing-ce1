const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const f of ['D04_言语_答案原文册.html','D05_资料_答案册.html']) {
    const p = await b.newPage({ viewport: { width: 420, height: 900 } });
    await p.goto('file://' + encodeURI('/home/user/work/build/pkg_r2/' + f));
    const r = await p.evaluate(() => {
      const W = document.documentElement.clientWidth; const out = [];
      for (const el of document.querySelectorAll('body *')) {
        const rc = el.getBoundingClientRect();
        if (rc.right > W + 1) out.push([Math.round(rc.right), el.tagName + '.' + el.className, (el.textContent || '').slice(0, 50), getComputedStyle(el).whiteSpace]);
      }
      out.sort((a,b)=>b[0]-a[0]);
      return {W, n: out.length, top: out.slice(0, 6)};
    });
    console.log(f, JSON.stringify(r, null, 0));
    await p.close();
  }
  await b.close();
})();
