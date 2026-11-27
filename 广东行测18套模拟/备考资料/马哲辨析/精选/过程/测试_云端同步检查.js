// 云端同步改动的检查：用假的 db（接口照 db.d.ts：set 整份替换、onSnapshot 先给缓存副本再给确认过的记录）。
// 用法：node v7_cloud_test.js <站点目录>
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const SITE = process.argv[2];
const qs = JSON.parse(fs.readFileSync(path.join(SITE, 'questions.json'), 'utf8'));
const core = qs.filter((x) => x.t === 1).sort((a, b) => a.o - b.o);
function prog(n, day, updated, extra = {}) {
  const q = {}; core.slice(0, n).forEach((x) => { q[x.id] = { n: 1, c: 1, l: 1, b: 1, f: day, d: day, due: '2026-11-28', f1: 1 }; });
  return { v: 1, q, days: { [day]: { n, c: n } }, settings: { size: 15, size2: 15, daily: 50, why: false, fmB: true, fmC: false }, today: null, today2: null, plan: null, updated, ...extra };
}
// 假 db：remote 存在 Node 这边（多台“设备”共用）；delay 毫秒后给第一份确认过的记录；cached 不为空时先立刻给一份缓存副本
function fakeDb({ delay, cached }) {
  const ref = {
    async set(d) { window.__sets = (window.__sets || 0) + 1; await window.__remoteSet(JSON.stringify(d)); setTimeout(() => emit(false), 5); },
    onSnapshot(cb) { ref._cb = cb; if (cached) setTimeout(() => cb({ exists: true, data: () => JSON.parse(cached), metadata: { fromCache: true, hasPendingWrites: false } }), 1); setTimeout(() => emit(false), delay); },
  };
  async function emit() { const s = await window.__remoteGet(); const data = s ? JSON.parse(s) : null; if (ref._cb) ref._cb({ exists: !!data, data: () => data, metadata: { fromCache: false, hasPendingWrites: false } }); }
  window.claude = { use: async (name) => (name === 'db' ? { doc: () => ref } : null) };
}
const fails = [];
const check = (label, cond, detail) => { console.log((cond ? '  ✓ ' : '  ✗ ') + label + (detail ? '  ' + detail : '')); if (!cond) fails.push(label); };
(async () => {
  const b = await chromium.launch();
  const when = new Date('2026-11-28T09:00:00').getTime();
  async function device(store, { delay, local, cached }) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    await ctx.route('http://mz.local/**', (route) => {
      const u = new URL(route.request().url());
      const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
      if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
      return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
    });
    await ctx.exposeFunction('__remoteGet', () => store.remote);
    await ctx.exposeFunction('__remoteSet', (s) => { store.remote = s; store.sets++; });
    const pg = await ctx.newPage(); const errs = [];
    pg.on('pageerror', (e) => errs.push(e.message));
    await pg.addInitScript(({ t, local }) => {
      const Real = Date, off = t - Real.now();
      class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + off); } static now() { return Real.now() + off; } }
      window.Date = Fake;
      if (local && !sessionStorage.getItem('__seeded')) { sessionStorage.setItem('__seeded', '1'); localStorage.setItem('mzbx-progress-v1', local); }
    }, { t: when, local: local ? JSON.stringify(local) : null });
    await pg.addInitScript(fakeDb, { delay, cached: cached ? JSON.stringify(cached) : null });
    await pg.goto('http://mz.local/index.html'); await pg.waitForSelector('.today');
    return { pg, errs, ctx };
  }
  const nq = (store) => (store.remote ? Object.keys(JSON.parse(store.remote).q).length : -1);
  const startBtn = '.panel.today >> button:text-is("开始") >> nth=0';
  const answer = (pg, ok) => pg.evaluate((ok) => {
    const R = S.run; const q = R.list[R.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
    if (q.type === '判断') runState.picked = new Set([ok ? ans : (ans === '正确' ? '错误' : '正确')]);
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
    reveal(q); nextQ(); return q.id;
  }, ok);

  console.log('1 本机空白，云端有100题，记录2秒后才到；这之前点“开始”、改每天题数');
  { const store = { remote: JSON.stringify(prog(100, '2026-11-26', '2026-11-26T12:00:00.000Z')), sets: 0 };
    const d = await device(store, { delay: 2000 });
    await d.pg.waitForTimeout(200);
    check('同步前“开始”不可点', await d.pg.isDisabled(startBtn));
    check('同步前有“正在同步”的提示', (await d.pg.textContent('.panel.today')).includes('正在同步'));
    await d.pg.selectOption('#dailySel', '60');
    await d.pg.waitForTimeout(1300);
    check('同步前没有写云端', store.sets === 0, `sets=${store.sets}`);
    await d.pg.waitForTimeout(2500);
    const st = await d.pg.evaluate(() => ({ local: Object.keys(S.prog.q).length, daily: S.prog.settings.daily, synced: S.synced, cloud: S.cloud }));
    check('同步后本机有100题', st.local === 100, JSON.stringify(st));
    check('云端仍是100题', nq(store) === 100, `云端${nq(store)}题`);
    check('刚改的每天题数保住并推到云端', st.daily === 60 && JSON.parse(store.remote).settings.daily === 60);
    check('同步后“开始”可点', !(await d.pg.isDisabled(startBtn)));
    check('今日面板显示核心已学100', (await d.pg.textContent('.panel.today')).includes('100/160'));
    check('没有反复写云端', store.sets <= 2, `sets=${store.sets}`);
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('2 本机是11-24的旧记录（40题），云端100题；同步前在“练习”里做了2题');
  { const store = { remote: JSON.stringify(prog(100, '2026-11-26', '2026-11-26T12:00:00.000Z')), sets: 0 };
    const d = await device(store, { delay: 2500, local: prog(40, '2026-11-24', '2026-11-24T12:00:00.000Z') });
    await d.pg.evaluate(() => { location.hash = '#practice'; }); await d.pg.waitForSelector('#fstart');
    await d.pg.click('#fstart'); await d.pg.waitForSelector('#qcard');
    const a1 = await answer(d.pg, true), a2 = await answer(d.pg, false);
    await d.pg.waitForTimeout(1200);
    check('同步前没有写云端', store.sets === 0, `sets=${store.sets}`);
    await d.pg.waitForTimeout(3000);
    const r = JSON.parse(store.remote);
    const expect = new Set([...core.slice(0, 100).map((x) => x.id), a1, a2]).size;
    check('云端是合并结果（原100题＋刚做的）', Object.keys(r.q).length === expect, `云端${Object.keys(r.q).length}题，应为${expect}`);
    check('刚做的两题在云端', !!r.q[a1] && !!r.q[a2] && r.q[a2].l === 0);
    check('本机与云端题数一致', (await d.pg.evaluate(() => Object.keys(S.prog.q).length)) === expect);
    check('没有反复写云端', store.sets <= 3, `sets=${store.sets}`);
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('3 第一次使用：云端没有记录');
  { const store = { remote: null, sets: 0 };
    const d = await device(store, { delay: 300 });
    await d.pg.waitForTimeout(800);
    check('同步后“开始”可点', !(await d.pg.isDisabled(startBtn)));
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    for (let i = 0; i < 3; i++) await answer(d.pg, true);
    await d.pg.waitForTimeout(1500);
    check('云端有3题', nq(store) === 3, `云端${nq(store)}题`);
    check('云端带着今天的计划', !!(JSON.parse(store.remote).plan && JSON.parse(store.remote).plan.pos === 3));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('4 云端12秒后才连上（先走本机）；这期间开始了计划并做了5题');
  { const store = { remote: JSON.stringify(prog(100, '2026-11-26', '2026-11-26T12:00:00.000Z')), sets: 0 };
    const d = await device(store, { delay: 12500 });
    await d.pg.waitForTimeout(10400);
    check('10秒后改为先存本机，“开始”可点', !(await d.pg.isDisabled(startBtn)) && (await d.pg.evaluate(() => S.cloud)) === 'slow');
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    const ids = []; for (let i = 0; i < 5; i++) ids.push(await answer(d.pg, true));
    check('连上之前没有写云端', store.sets === 0, `sets=${store.sets}`);
    await d.pg.waitForTimeout(3500);
    const r = JSON.parse(store.remote);
    const expect = new Set([...core.slice(0, 100).map((x) => x.id), ...ids]).size;
    check('连上后云端是合并结果', Object.keys(r.q).length === expect, `云端${Object.keys(r.q).length}题，应为${expect}`);
    check('做题没有被打断', await d.pg.evaluate(() => !!S.run && S.run.pos === 5));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('5 先到一份缓存副本（50题），再到确认过的记录（100题）');
  { const full = prog(100, '2026-11-26', '2026-11-26T12:00:00.000Z'); full.days['2026-11-25'] = { n: 50, c: 50 };   // 云端的记录包含缓存副本里的那一天
    const store = { remote: JSON.stringify(full), sets: 0 };
    const d = await device(store, { delay: 1500, cached: prog(50, '2026-11-25', '2026-11-25T12:00:00.000Z') });
    await d.pg.waitForTimeout(500);
    const mid = await d.pg.evaluate(() => ({ local: Object.keys(S.prog.q).length, synced: S.synced }));
    check('缓存副本先并进本机，但还不算同步完', mid.local === 50 && mid.synced === false, JSON.stringify(mid));
    check('这时“开始”仍不可点', await d.pg.isDisabled(startBtn));
    await d.pg.waitForTimeout(1800);
    check('确认过的记录到后本机100题', (await d.pg.evaluate(() => Object.keys(S.prog.q).length)) === 100);
    check('没有写云端（本机没有更新的东西）', store.sets === 0, `sets=${store.sets}`);
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('6 两台设备：A做6题；B打开后马上点“开始”；B再做3题；A刷新');
  { const store = { remote: null, sets: 0 };
    const A = await device(store, { delay: 20 });
    await A.pg.waitForTimeout(300); await A.pg.click(startBtn); await A.pg.waitForSelector('#qcard');
    for (let i = 0; i < 6; i++) await answer(A.pg, true);
    await A.pg.waitForTimeout(1500);
    check('A做6题后云端6题', nq(store) === 6, `云端${nq(store)}题`);
    const B = await device(store, { delay: 4000 });
    const early = await B.pg.evaluate(() => { const x = document.querySelector('.panel.today button'); const st = { text: x.textContent, disabled: x.disabled, syncing: syncing() }; x.click(); return st; });
    check('B打开时计划的“开始”不可点', early.text === '开始' && early.disabled && early.syncing, JSON.stringify(early));
    await B.pg.waitForTimeout(5500);
    check('B同步前的点击没有生效，云端还是6题', nq(store) === 6 && (await B.pg.evaluate(() => !S.run)), `云端${nq(store)}题`);
    check('B显示A的进度（继续，已做6题）', (await B.pg.textContent('.panel.today')).includes('已做6题'));
    await B.pg.click('.panel.today >> button:text-is("继续")'); await B.pg.waitForSelector('#qcard');
    for (let i = 0; i < 3; i++) await answer(B.pg, true);
    await B.pg.waitForTimeout(1500);
    check('B再做3题后云端9题', nq(store) === 9, `云端${nq(store)}题`);
    await A.pg.evaluate(() => { S.run = null; }); await A.pg.reload(); await A.pg.waitForSelector('.today'); await A.pg.waitForTimeout(900);   // 假 db 不会把B的写入推给A，刷新A来取
    check('A刷新后有9题', (await A.pg.evaluate(() => Object.keys(S.prog.q).length)) === 9);
    check('A的今日计划位置跟到9', (await A.pg.evaluate(() => S.prog.plan.pos)) === 9);
    check('A的面板显示已做9题', (await A.pg.textContent('.panel.today')).includes('已做9题'));
    check('写云端的次数正常', store.sets <= 4, `sets=${store.sets}`);
    check('无报错', A.errs.length + B.errs.length === 0, A.errs.concat(B.errs).join('; ')); await A.ctx.close(); await B.ctx.close(); }

  console.log('7 两台设备各有对方没有的记录（A在线做了4题没来得及同步到B，B离线做了2题）');
  { const base = prog(20, '2026-11-27', '2026-11-27T12:00:00.000Z');
    const aDoc = JSON.parse(JSON.stringify(base)); core.slice(20, 24).forEach((x) => { aDoc.q[x.id] = { n: 1, c: 0, l: 0, b: 0, f: '2026-11-28', d: '2026-11-28', due: '2026-11-29', f1: 0 }; }); aDoc.updated = '2026-11-28T00:30:00.000Z';
    const bLocal = JSON.parse(JSON.stringify(base)); core.slice(30, 32).forEach((x) => { bLocal.q[x.id] = { n: 1, c: 1, l: 1, b: 1, f: '2026-11-28', d: '2026-11-28', due: '2026-11-30', f1: 1 }; }); bLocal.updated = '2026-11-28T00:50:00.000Z';
    const store = { remote: JSON.stringify(aDoc), sets: 0 };
    const B = await device(store, { delay: 300, local: bLocal });
    await B.pg.waitForTimeout(2200);
    const r = JSON.parse(store.remote);
    check('合并后云端26题（20＋4＋2）', Object.keys(r.q).length === 26, `云端${Object.keys(r.q).length}题`);
    check('A答错的4题保住了', core.slice(20, 24).every((x) => r.q[x.id] && r.q[x.id].l === 0));
    check('写云端一次就收敛', store.sets === 1, `sets=${store.sets}`);
    check('无报错', B.errs.length === 0, B.errs.join('; ')); await B.ctx.close(); }

  console.log(fails.length ? `\n有 ${fails.length} 项没过：${fails.join('；')}` : '\n全部通过');
  await b.close(); process.exit(fails.length ? 1 : 0);
})();
