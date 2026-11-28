// 行测弱项特训：整页功能测试（本机模式、自编题、错题本、刷新、两台设备云端同步、版面）
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const SITE = path.resolve(process.argv[2] || 'site');
let fails = 0; const ok = (c, name, extra) => { console.log(`  ${c ? '✓' : '✗'} ${name}${extra === undefined ? '' : '  ' + (typeof extra === 'string' ? extra : JSON.stringify(extra))}`); if (!c) fails++; };
function sortKeys(v) { if (Array.isArray(v)) return v.map(sortKeys); if (v && typeof v === 'object') { const o = {}; for (const k of Object.keys(v).sort()) o[k] = sortKeys(v[k]); return o; } return v; }
function init({ t, cloud }) {
  const Real = Date; const saved = sessionStorage.getItem('__now');
  window.__off = (saved ? Number(saved) : t) - Real.now();
  window.__setNow = (ms) => { sessionStorage.setItem('__now', String(ms)); window.__off = ms - Real.now(); };
  class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + window.__off); } static now() { return Real.now() + window.__off; } }
  window.Date = Fake;
  if (cloud) {
    const ref = {
      async set(d) { window.__sets = (window.__sets || 0) + 1; await window.__remoteSet(JSON.stringify(d)); },
      async get() { const s = await window.__remoteGet(); const data = s ? JSON.parse(s) : null; return { exists: !!data, data: () => data, metadata: { fromCache: false, hasPendingWrites: false } }; },
      onSnapshot(cb) { ref._cb = cb; setTimeout(() => window.__emit(), 30); return () => {}; },
    };
    window.__emit = async () => { const s = await window.__remoteGet(); const data = s ? JSON.parse(s) : null; if (ref._cb) ref._cb({ exists: !!data, data: () => data, metadata: { fromCache: false, hasPendingWrites: false } }); };
    window.claude = { use: async (name) => (name === 'db' ? { doc: () => ref } : null) };
  }
  window.__chk = () => {
    const out = [];
    const w = document.documentElement.scrollWidth - window.innerWidth; if (w > 0) out.push('横向溢出 ' + w + 'px');
    const txt = document.querySelector('main').innerText;
    const m = txt.match(/.{0,12}(undefined|NaN|null|\[object Object\]).{0,12}/); if (m) out.push('怪字样: ' + m[0].replace(/\s+/g, ' '));
    return out;
  };
}
async function device(b, o) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, colorScheme: o.dark ? 'dark' : 'light' });
  await ctx.route('**/*', (route) => {
    const u = new URL(route.request().url());
    if (u.hostname !== 'xc.local') return route.abort();
    const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
    if (!fs.existsSync(f)) return route.fulfill({ status: 404, body: '' });
    if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
    return route.fulfill({ path: f });
  });
  const pg = await ctx.newPage(); const errs = [];
  pg.on('pageerror', (e) => errs.push('pageerror: ' + e.message)); pg.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push('console: ' + m.text()); });
  if (o.store) {
    const store = o.store;
    await ctx.exposeFunction('__remoteGet', () => store.remote);
    await ctx.exposeFunction('__remoteSet', (s) => { store.remote = JSON.stringify(sortKeys(JSON.parse(s))); store.sets++; for (const p of store.pages) p.evaluate(() => window.__emit && window.__emit()).catch(() => {}); });
    store.pages.push(pg);
  }
  await pg.addInitScript(init, { t: new Date(o.when || '2026-11-28T20:00:00').getTime(), cloud: !!o.store });
  await pg.goto('http://xc.local/index.html'); await pg.waitForSelector('.steps, .sets'); await pg.waitForTimeout(o.store ? 500 : 150);
  return { pg, errs, ctx };
}
const answerCur = async (pg, right) => pg.evaluate((right) => {
  const R = S.run; if (!R || R.pos >= R.list.length || !document.querySelector('#qcard')) return null;
  const q = R.list[R.pos]; const L = right ? q.answer : ['A', 'B', 'C', 'D'].find((x) => x !== q.answer);
  const btn = document.querySelector(`#qcard [data-v="${L}"]`); btn.click();
  const v = document.querySelector('.verdict'); const blocks = [...document.querySelectorAll('#qcard .blk .h')].map((x) => x.textContent);
  return { id: q.id, set: q.set, k: q.k, verdict: v && v.innerText, blocks, chk: window.__chk() };
}, right);
(async () => {
  const b = await chromium.launch();
  console.log('1 本机模式：首页、M10原题、错题本、刷新');
  {
    const d = await device(b, {}); const pg = d.pg;
    const home = await pg.evaluate(() => ({ steps: document.querySelectorAll('.step').length, h2: document.querySelector('main h2').textContent, note: [...document.querySelectorAll('.cloudNote')].map((x) => x.textContent).join(''), chk: window.__chk() }));
    ok(home.steps === 10 && /M10/.test(home.h2), '首页：标题和10步计划', home);
    ok(/只存在这台设备/.test(home.note), '本机模式有提示', home.note);
    await pg.click('.step button'); await pg.waitForSelector('#qcard');
    const res = [];
    for (let i = 0; i < 8; i++) { const r = await answerCur(pg, i % 2 === 0); res.push(r); await pg.click('#nextBtn'); }
    ok(res.every((r) => r && /答(对|错)了/.test(r.verdict)), '8道原题都能作答并出结果', res.map((r) => r && r.id));
    ok(res.every((r) => r.blocks.join() === '题眼,推导,易错'), '每题有题眼、推导、易错三段', res.map((r) => r.blocks.join('')));
    ok(res.every((r) => r.chk.length === 0), '作答后版面正常', res.flatMap((r) => r.chk));
    const sum = await pg.evaluate(() => document.querySelector('main').innerText.replace(/\s+/g, ' ').slice(0, 80));
    ok(/答对4\/8/.test(sum), '小结：答对4/8', sum);
    await pg.click('button:text-is("返回")'); await pg.waitForSelector('.steps');
    const wn = await pg.evaluate(() => document.querySelector('#wrongN').textContent);
    ok(wn === '4', '分栏“错题”显示4', wn);
    await pg.click('#tabs a[href="#wrong"]'); await pg.waitForTimeout(100);
    const wl = await pg.evaluate(() => ({ items: document.querySelectorAll('.wi').length, btn: document.querySelector('main .btn.primary').textContent }));
    ok(wl.items === 4 && /4道/.test(wl.btn), '错题本列出4道', wl);
    await pg.reload(); await pg.waitForSelector('main .panel'); await pg.waitForTimeout(150);
    const after = await pg.evaluate(() => ({ r: Object.keys(S.prog.r).length, wrong: document.querySelector('#wrongN').textContent }));
    ok(after.r === 8 && after.wrong === '4', '刷新后记录还在', after);
    // 第二天重做错题：答对后过关
    await pg.evaluate(() => window.__setNow(new Date('2026-11-29T09:00:00').getTime())); await pg.reload(); await pg.waitForSelector('main .panel');
    await pg.click('#tabs a[href="#wrong"]'); await pg.waitForTimeout(100); await pg.click('main .btn.primary'); await pg.waitForSelector('#qcard');
    for (let i = 0; i < 4; i++) { await answerCur(pg, true); await pg.click('#nextBtn'); }
    await pg.click('button:text-is("返回")'); await pg.waitForTimeout(100);
    const passed = await pg.evaluate(() => ({ wrong: document.querySelector('#wrongN').textContent, txt: document.querySelector('main').innerText.replace(/\s+/g, ' ').slice(0, 200) }));
    ok(passed.wrong === '' && /已过关（4）/.test(passed.txt), '第二天答对后4道都过关', passed);
    ok(d.errs.length === 0, '无报错', d.errs);
    await d.ctx.close();
  }
  console.log('2 各分栏、真题组、自编速练');
  {
    const d = await device(b, {}); const pg = d.pg;
    for (const [hash, name] of [['fig', '图推'], ['num', '数推'], ['data', '资料'], ['stats', '记录']]) {
      await pg.click(`#tabs a[href="#${hash}"]`); await pg.waitForTimeout(80);
      const v = await pg.evaluate(() => ({ sets: document.querySelectorAll('.set').length, cards: document.querySelectorAll('details.card').length, chk: window.__chk() }));
      ok(v.chk.length === 0 && (hash === 'stats' || v.sets > 0), `${name}页正常`, v);
    }
    // 每个真题组做完一遍
    for (const sid of ['fig-pts', 'fig-grid', 'num-frac', 'num-rec', 'num-tab', 'num-adv', 'data-pct']) {
      await pg.evaluate((sid) => startSet(sid), sid); await pg.waitForSelector('#qcard');
      const r = []; for (;;) { const x = await answerCur(pg, true); if (!x) break; r.push(x); await pg.click('#nextBtn'); }
      ok(r.length > 0 && r.every((x) => /答对了/.test(x.verdict) && x.chk.length === 0), `真题组 ${sid}：${r.length}道全部能作答、版面正常`, r.filter((x) => x.chk.length).map((x) => x.id + x.chk));
      await pg.click('button:text-is("返回")');
    }
    // 图上点标记
    await pg.evaluate(() => startSet('fig-pts')); await pg.waitForSelector('#qcard .figwrap');
    const box = await pg.locator('#qcard .figwrap').boundingBox();
    await pg.mouse.click(box.x + box.width * 0.3, box.y + box.height * 0.4); await pg.mouse.click(box.x + box.width * 0.6, box.y + box.height * 0.5);
    let mk = await pg.evaluate(() => ({ dots: document.querySelectorAll('#qcard .dot').length, txt: document.querySelector('#markN').textContent }));
    ok(mk.dots === 2 && /2/.test(mk.txt), '在题图上点两下，出现2个标记', mk);
    await pg.locator('#qcard .dot').first().click(); mk = await pg.evaluate(() => document.querySelectorAll('#qcard .dot').length);
    ok(mk === 1, '再点一下标记就取消', mk);
    await pg.click('button:text-is("退出")');
    // 自编速练：每种10题
    for (const k of ['pts', 'ptscl', 'grid', 'rec', 'tab', 'frac']) {
      await pg.evaluate((k) => startRun(newIds(k, 10), k), k); await pg.waitForSelector('#qcard');
      const r = []; for (let i = 0; i < 10; i++) { const x = await answerCur(pg, i % 3 !== 0); if (!x) break; r.push(x);
        if (k === 'pts' || k === 'ptscl') { const red = await pg.evaluate(() => document.querySelectorAll('#qcard svg circle[fill="#d23c2a"]').length); if (!red) r[r.length - 1].chk.push('答完没有红点'); }
        await pg.click('#nextBtn'); }
      ok(r.length === 10 && r.every((x) => x.chk.length === 0 && x.blocks.join() === '题眼,推导,易错'), `自编 ${k}：10题都正常`, r.filter((x) => x.chk.length).map((x) => x.chk));
      await pg.click('button:text-is("返回")');
    }
    const st = await pg.evaluate(() => ({ wrongGen: Object.keys(S.prog.r).filter((id) => id.startsWith('g:')).length, rk: Object.keys(S.prog.r).length, cnt: JSON.stringify(S.prog.cnt).length }));
    ok(st.wrongGen === 24, '自编题只记答错的（6种×4题）', st);
    await pg.click('#tabs a[href="#wrong"]'); await pg.waitForTimeout(80);
    await pg.evaluate(() => startRun(wrongList((id, p) => id.startsWith('g:') && pendingRec(p)).map((x) => x.id), '重做'));
    const re = await pg.evaluate(() => ({ n: S.run.list.length, same: S.run.list.every((q) => q.id.startsWith('g:') && q.stem !== undefined) }));
    ok(re.n === 24 && re.same, '自编错题能原样重出', re);
    await pg.click('button:text-is("退出")');
    await pg.click('#tabs a[href="#stats"]'); await pg.waitForTimeout(80);
    const sv = await pg.evaluate(() => ({ rows: document.querySelectorAll('table.st tbody tr').length, chk: window.__chk() }));
    ok(sv.rows >= 10 && sv.chk.length === 0, '记录页分类正确率表', sv);
    ok(d.errs.length === 0, '无报错', d.errs);
    await pg.screenshot({ path: path.join(__dirname, 'shot_stats.png'), fullPage: true });
    await d.ctx.close();
  }
  console.log('3 两台设备共用云端');
  {
    const store = { remote: null, sets: 0, pages: [] };
    const A = await device(b, { store, when: '2026-11-28T20:00:00' });
    await A.pg.evaluate(() => startSet('m10')); await A.pg.waitForSelector('#qcard');
    for (let i = 0; i < 3; i++) { await answerCur(A.pg, i !== 1); await A.pg.click('#nextBtn'); }
    await A.pg.waitForTimeout(1500);
    const remote1 = JSON.parse(store.remote || '{}');
    ok(remote1.r && Object.keys(remote1.r).length === 3, 'A做3题后云端有3题', remote1.r && Object.keys(remote1.r));
    const B = await device(b, { store, when: '2026-11-28T21:00:00' });
    const bseen = await B.pg.evaluate(() => ({ r: Object.keys(S.prog.r).length, wrong: document.querySelector('#wrongN').textContent }));
    ok(bseen.r === 3 && bseen.wrong === '1', 'B打开后看到A的3题和1道错题', bseen);
    await B.pg.evaluate(() => startRun(newIds('rec', 4), 'x')); await B.pg.waitForSelector('#qcard');
    for (let i = 0; i < 4; i++) { await answerCur(B.pg, false); await B.pg.click('#nextBtn'); }
    await B.pg.waitForTimeout(1500); await A.pg.waitForTimeout(800);
    const s0 = store.sets; await A.pg.waitForTimeout(4000);
    ok(store.sets === s0, '两台都静下来后不再写云端', { before: s0, after: store.sets });
    const a2 = await A.pg.evaluate(() => ({ r: Object.keys(S.prog.r).length, total: Object.values(sumCnt('d')).reduce((s, v) => s + v[0], 0) }));
    ok(a2.r === 7 && a2.total === 7, 'A收到B的4道错题，今天合计7题', a2);
    ok(A.errs.concat(B.errs).length === 0, '无报错', A.errs.concat(B.errs));
    await A.ctx.close(); await B.ctx.close();
  }
  console.log('4 深色模式、首页截图');
  {
    const d = await device(b, { dark: true }); await d.pg.screenshot({ path: path.join(__dirname, 'shot_home_dark.png'), fullPage: true });
    await d.pg.evaluate(() => startSet('fig-pts')); await d.pg.waitForSelector('#qcard'); await d.pg.screenshot({ path: path.join(__dirname, 'shot_fig_dark.png'), fullPage: true });
    await d.pg.evaluate(() => startSet('num-tab')); await d.pg.waitForSelector('#qcard'); await d.pg.screenshot({ path: path.join(__dirname, 'shot_tab_dark.png'), fullPage: true });
    ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
    const l = await device(b, {}); await l.pg.screenshot({ path: path.join(__dirname, 'shot_home.png'), fullPage: true });
    await l.pg.evaluate(() => startRun(newIds('grid', 1), '灰格')); await l.pg.waitForSelector('#qcard'); await l.pg.screenshot({ path: path.join(__dirname, 'shot_grid.png'), fullPage: true });
    await l.pg.evaluate(() => startSet('data-pct')); await l.pg.waitForSelector('#qcard'); await l.pg.screenshot({ path: path.join(__dirname, 'shot_data.png'), fullPage: true });
    await l.ctx.close();
  }
  await b.close();
  console.log(fails ? `\n有 ${fails} 项没通过` : '\n全部通过'); process.exit(fails ? 1 : 0);
})();
