const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const f of ['D04_言语_答案原文册.html','D05_资料_答案册.html','/home/user/work/build/pkg2/D01_言语_答案原文册.html']) {
    const p = await b.newPage({ viewport: { width: 420, height: 900 } });
    const path = f.startsWith('/') ? f : '/home/user/work/build/pkg_r2/' + f;
    await p.goto('file://' + encodeURI(path));
    const r = await p.evaluate(() => {
      const W = document.documentElement.clientWidth; const out = [];
      for (const el of document.querySelectorAll('body *')) {
        const rc = el.getBoundingClientRect();
        if (rc.right > W + 1 && el.children.length === 0) out.push(el.tagName + '.' + el.className + ' w=' + Math.round(rc.width) + ' ' + (el.textContent || '').slice(0, 60));
      }
      return out.slice(0, 8);
    });
    console.log(f, r);
    await p.close();
  }
  await b.close();
})();
