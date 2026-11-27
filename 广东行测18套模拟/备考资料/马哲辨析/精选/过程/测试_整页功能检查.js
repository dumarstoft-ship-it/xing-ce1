// 新版网页功能检查：两组日课、政常题乱序与逐项解析、能讲清自评、错题重练换说法、待审区、知识块、导出导入
const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
(async () => {
  const SITE = process.argv[2], OUT = process.argv[3];
  const b = await chromium.launch(); const errs = [];
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, acceptDownloads: true });
  await ctx.route('http://mz.local/**', (route) => {
    const u = new URL(route.request().url());
    const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
    if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
    return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
  });
  const pg = await ctx.newPage();
  pg.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  await pg.goto('http://mz.local/index.html'); await pg.waitForSelector('.today'); await pg.waitForTimeout(500);
  console.log('今日面板:', (await pg.$$eval('.today h2', (els) => els.map((e) => e.textContent))).join(' | '));
  await pg.screenshot({ path: OUT + '/mz8_today.png', fullPage: true });
  for (const d of await pg.$$('details.more')) await d.evaluate((el) => { el.open = true; });
  await pg.click('section.today:has(h2:has-text("政常")) button:text-is("开始")'); await pg.waitForSelector('#qcard');
  const seen = [];
  for (let i = 0; i < 3; i++) {
    const meta = await pg.$$eval('#qcard .qmeta .pill', (els) => els.map((e) => e.textContent).join('|')); seen.push(meta);
    const tf = await pg.$('#qcard .tf .opt:nth-child(1)');
    if (tf) await tf.click(); else { const o = await pg.$('#qcard .opts .opt'); await o.click(); const sub = await pg.$('#submitMulti'); if (sub) await sub.click(); }
    await pg.waitForSelector('#nextBtn');
    if (i === 0) await pg.click('button:text-is("能讲清")');
    if (meta.includes('单选') || meta.includes('多选')) await pg.screenshot({ path: OUT + '/mz9_fm_reveal.png', fullPage: true });
    await pg.click('#nextBtn');
  }
  console.log('政常一组:', seen.join(' || '));
  const prog = await pg.evaluate(() => JSON.parse(localStorage.getItem('mzbx-progress-v1')));
  console.log('记录:', JSON.stringify(Object.fromEntries(Object.entries(prog.q).map(([k, v]) => [k, { l: v.l, f1: v.f1, e: v.e }]))), 'today2.pos:', prog.today2 && prog.today2.pos);
  await pg.goto('http://mz.local/index.html#review'); await pg.waitForTimeout(400);
  const btns = await pg.$$('button:text-is("开始重练")');
  if (btns.length) { await btns[btns.length - 1].click(); await pg.waitForSelector('#qcard'); console.log('重练第一题题干:', (await pg.textContent('#qcard .stem')).slice(0, 40)); await pg.click('button:text-is("退出")'); }
  await pg.goto('http://mz.local/index.html#pending'); await pg.waitForTimeout(400);
  console.log('待审区条数:', await pg.$$eval('#main details.card', (els) => els.length));
  await pg.goto('http://mz.local/index.html#cards'); await pg.waitForTimeout(400);
  await pg.click('button:text-is("政常全部")'); await pg.waitForTimeout(300);
  console.log('政常知识块数:', await pg.$$eval('#main details.card', (els) => els.length));
  await pg.goto('http://mz.local/index.html#stats'); await pg.waitForTimeout(400);
  const [dl] = await Promise.all([pg.waitForEvent('download', { timeout: 5000 }).catch(() => null), pg.click('button:text-is("导出记录")')]);
  console.log('导出文件:', dl ? dl.suggestedFilename() : '（无下载事件）', '|', await pg.textContent('#ioMsg'));
  await pg.click('text=导出没反应？或者想用粘贴的方式导入');
  await pg.fill('#ioText', JSON.stringify({ v: 1, q: { 'T-GD-004-1': { n: 3, c: 3, l: 1, b: 2, f: '2026-11-20', d: '2026-11-28', due: '2026-12-01', f1: 1 } }, days: {} }));
  await pg.click('button:text-is("粘贴导入")'); await pg.waitForTimeout(300);
  console.log('导入:', await pg.textContent('#ioMsg'));
  for (const r of ['today', 'practice', 'review', 'cards', 'pending', 'appendix', 'stats']) {
    await pg.goto('http://mz.local/index.html#' + r); await pg.waitForTimeout(300);
    const ov = await pg.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (ov > 0) errs.push('overflow #' + r + ': ' + ov);
  }
  console.log('errors:', errs.length ? errs.join('\n') : 'none');
  await b.close();
})();
