// 跨设备时“当天的题组”和“清除全部记录”的表现（假 db，写法照 v7_cloud_test.js；多台设备共用一份云端，写入会推给所有在线设备）。
// 用法：node t9_cross.js <站点>
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const SITE = path.resolve(__dirname, process.argv[2] || 'v7');
function fakeDb({ delay, online }) {
  const ref = {
    async set(d) { if (!window.__online) { const e = new Error('offline'); e.code = 'unavailable'; throw e; } window.__sets = (window.__sets || 0) + 1; await window.__remoteSet(JSON.stringify(d)); },
    async get() { if (!window.__online) { const e = new Error('offline'); e.code = 'unavailable'; throw e; } const s = await window.__remoteGet(); const data = s ? JSON.parse(s) : null; return { exists: !!data, data: () => data, metadata: { fromCache: false, hasPendingWrites: false } }; },
    onSnapshot(cb) { ref._cb = cb; setTimeout(() => window.__emit(), delay); },
  };
  window.__online = online !== false;
  window.__emit = async () => { if (!window.__online) return; const s = await window.__remoteGet(); const data = s ? JSON.parse(s) : null; if (ref._cb) ref._cb({ exists: !!data, data: () => data, metadata: { fromCache: false, hasPendingWrites: false } }); };
  window.claude = { use: async (name) => (name === 'db' ? { doc: () => ref } : null) };
}
const ONLY = (process.env.ONLY || 'X1,X2,X3').split(',');
const fails = [];
const check = (label, cond, detail) => { console.log((cond ? '  ✓ ' : '  ✗ ') + label + (detail ? '  ' + detail : '')); if (!cond) fails.push(label); };
(async () => {
  const b = await chromium.launch();
  async function device(store, { delay, local, when, online }) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    await ctx.route('http://mz.local/**', (route) => {
      const u = new URL(route.request().url());
      const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
      if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
      return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
    });
    const pg = await ctx.newPage(); const errs = [];
    await ctx.exposeFunction('__remoteGet', () => store.remote);
    await ctx.exposeFunction('__remoteSet', (s) => { store.remote = s; store.sets++; for (const p of store.pages) if (p !== pg) p.evaluate(() => window.__emit && window.__emit()).catch(() => {}); pg.evaluate(() => setTimeout(() => window.__emit(), 5)).catch(() => {}); });
    store.pages.push(pg);
    pg.on('pageerror', (e) => errs.push(e.message));
    await pg.addInitScript(({ t, local }) => {
      const Real = Date; window.__off = t - Real.now();
      class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + window.__off); } static now() { return Real.now() + window.__off; } }
      window.Date = Fake;
      if (local && !sessionStorage.getItem('__seeded')) { sessionStorage.setItem('__seeded', '1'); localStorage.setItem('mzbx-progress-v1', local); }
    }, { t: new Date(when).getTime(), local: local || null });
    await pg.addInitScript(fakeDb, { delay, online });
    await pg.goto('http://mz.local/index.html'); await pg.waitForSelector('.today');
    return { pg, errs, ctx };
  }
  const startBtn = '.panel.today >> button:text-is("开始") >> nth=0';
  const answer = (pg, ok) => pg.evaluate((ok) => {
    const R = S.run; if (!R || R.pos >= R.list.length) return null; const q = R.list[R.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
    if (q.type === '判断') runState.picked = new Set([ok ? ans : (ans === '正确' ? '错误' : '正确')]);
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
    reveal(q); nextQ(); return q.id;
  }, ok);
  const panel = (pg) => pg.evaluate(() => document.querySelector('.panel.today').innerText.replace(/\s+/g, ' ').slice(0, 70));
  const remotePlan = (store) => { const r = store.remote ? JSON.parse(store.remote) : null; return r && r.plan ? `${r.plan.day} pos${r.plan.pos}/${r.plan.ids.length}` : 'null'; };

  if (ONLY.includes('X1')) console.log('X1 手机A今天把计划做到第30题；电脑B留着昨天的页面、断网时改了一下“每天题数”，再连上网');
  if (ONLY.includes('X1')) { const store = { remote: null, sets: 0, pages: [] };
    // 昨天（11-28）：B 做完当天计划并同步
    const B = await device(store, { delay: 20, when: '2026-11-28T20:00:00' });
    await B.pg.waitForTimeout(300); await B.pg.click(startBtn); await B.pg.waitForSelector('#qcard');
    for (let i = 0; i < 50; i++) await answer(B.pg, true);
    await B.pg.evaluate(() => exitRun()); await B.pg.waitForTimeout(1500);
    const yesterday = store.remote;
    // 今天（11-29）早上：B 断网放着；A 打开，做到第30题
    await B.pg.evaluate(() => { window.__online = false; });
    const A = await device(store, { delay: 20, when: '2026-11-29T08:00:00', local: yesterday });
    await A.pg.waitForTimeout(300); await A.pg.click(startBtn); await A.pg.waitForSelector('#qcard');
    for (let i = 0; i < 30; i++) await answer(A.pg, true);
    await A.pg.evaluate(() => exitRun()); await A.pg.waitForTimeout(1500);
    check('A：今日计划已做30题，云端也是', (await panel(A.pg)).includes('已做30题') && remotePlan(store) === '2026-11-29 pos30/50', `${await panel(A.pg)} | 云端计划 ${remotePlan(store)}`);
    // 今天晚些：B 的时钟到今天，仍断网，改了每天题数；然后连上
    await B.pg.evaluate((ms) => { window.__off = ms - Object.getPrototypeOf(Date).now(); document.dispatchEvent(new Event('visibilitychange')); }, new Date('2026-11-29T12:00:00').getTime());
    await B.pg.selectOption('#dailySel', '60'); await B.pg.selectOption('#dailySel', '50');
    await B.pg.evaluate(() => { window.__online = true; window.__emit(); }); await B.pg.waitForTimeout(3500);
    const bq = await B.pg.evaluate(() => Object.keys(S.prog.q).length), aq = await A.pg.evaluate(() => Object.keys(S.prog.q).length);
    console.log('    连上后：B面板=', await panel(B.pg), '| A面板=', await panel(A.pg), '| 云端计划', remotePlan(store), `| 题数 A${aq} B${bq}`);
    check('做题记录没有丢（两边都是80题）', aq === 80 && bq === 80, `A${aq} B${bq}`);
    check('A今天做到第30题的计划还在', (await panel(A.pg)).includes('已做30题'), await panel(A.pg));
    check('无报错', A.errs.length + B.errs.length === 0, A.errs.concat(B.errs).join('; ')); await A.ctx.close(); await B.ctx.close(); }

  if (ONLY.includes('X2')) console.log('X2 两台设备都有记录；在A上“清除全部记录”，之后打开B');
  if (ONLY.includes('X2')) { const store = { remote: null, sets: 0, pages: [] };
    const A = await device(store, { delay: 20, when: '2026-11-28T09:00:00' });
    await A.pg.waitForTimeout(300); await A.pg.click(startBtn); await A.pg.waitForSelector('#qcard');
    for (let i = 0; i < 20; i++) await answer(A.pg, i % 4 !== 0);
    await A.pg.evaluate(() => exitRun()); await A.pg.waitForTimeout(1500);
    const snap = store.remote;
    // B 的本机里有同一份记录（上次打开时同步下来的），现在关着
    await A.pg.evaluate(() => { location.hash = '#stats'; }); await A.pg.waitForSelector('#resetBtn');
    await A.pg.click('#resetBtn'); await A.pg.click('#resetBtn'); await A.pg.waitForTimeout(1500);
    const afterReset = { a: await A.pg.evaluate(() => Object.keys(S.prog.q).length), remote: Object.keys(JSON.parse(store.remote).q).length };
    check('A清除后：本机0题、云端0题', afterReset.a === 0 && afterReset.remote === 0, JSON.stringify(afterReset));
    const B = await device(store, { delay: 300, when: '2026-11-28T12:00:00', local: snap });
    await B.pg.waitForTimeout(2500);
    const end = { a: await A.pg.evaluate(() => Object.keys(S.prog.q).length), b: await B.pg.evaluate(() => Object.keys(S.prog.q).length), remote: Object.keys(JSON.parse(store.remote).q).length };
    check('打开B之后记录仍然是清空的', end.a === 0 && end.b === 0 && end.remote === 0, JSON.stringify(end));
    check('无报错', A.errs.length + B.errs.length === 0, A.errs.concat(B.errs).join('; ')); await A.ctx.close(); await B.ctx.close(); }

  if (ONLY.includes('X3')) console.log('X3 一台设备：云端连得慢（先走本机）时“清除全部记录”，之后云端连上');
  if (ONLY.includes('X3')) { const store = { remote: null, sets: 0, pages: [] };
    const A0 = await device(store, { delay: 20, when: '2026-11-28T09:00:00' });
    await A0.pg.waitForTimeout(300); await A0.pg.click(startBtn); await A0.pg.waitForSelector('#qcard');
    for (let i = 0; i < 20; i++) await answer(A0.pg, true);
    await A0.pg.evaluate(() => exitRun()); await A0.pg.waitForTimeout(1500);
    const snap = store.remote; await A0.ctx.close(); store.pages.length = 0;
    const A = await device(store, { delay: 14000, when: '2026-11-28T12:00:00', local: snap });
    await A.pg.waitForTimeout(10500);
    await A.pg.evaluate(() => { location.hash = '#stats'; }); await A.pg.waitForSelector('#resetBtn');
    await A.pg.click('#resetBtn'); await A.pg.click('#resetBtn'); await A.pg.waitForTimeout(300);
    const mid = await A.pg.evaluate(() => ({ q: Object.keys(S.prog.q).length, cloud: S.cloud }));
    await A.pg.waitForTimeout(5500);
    const end = { a: await A.pg.evaluate(() => Object.keys(S.prog.q).length), remote: Object.keys(JSON.parse(store.remote).q).length };
    check('清除时本机0题（云端还没连上）', mid.q === 0 && mid.cloud === 'slow', JSON.stringify(mid));
    check('云端连上后记录仍然是清空的', end.a === 0 && end.remote === 0, JSON.stringify(end));
    await A.ctx.close(); }

  if (ONLY.includes('X4')) console.log('X4 电脑B的页面从昨天开到今天（昨天已同步过）；手机A今天把计划做到第30题；打开电脑，网络还没恢复就点了“开始”');
  if (ONLY.includes('X4')) { const store = { remote: null, sets: 0, pages: [] };
    const B = await device(store, { delay: 20, when: '2026-11-28T20:00:00' });
    await B.pg.waitForTimeout(300); await B.pg.click(startBtn); await B.pg.waitForSelector('#qcard');
    for (let i = 0; i < 50; i++) await answer(B.pg, i % 5 !== 0);
    await B.pg.evaluate(() => exitRun()); await B.pg.waitForTimeout(1500);
    const yesterday = store.remote;
    await B.pg.evaluate(() => { window.__online = false; });            // 合上电脑
    const A = await device(store, { delay: 20, when: '2026-11-29T08:00:00', local: yesterday });
    await A.pg.waitForTimeout(300); await A.pg.click(startBtn); await A.pg.waitForSelector('#qcard');
    const aDone = []; for (let i = 0; i < 30; i++) aDone.push(await answer(A.pg, true));
    await A.pg.evaluate(() => exitRun()); await A.pg.waitForTimeout(1500);
    // 中午打开电脑：页面换成新一天，网络还没连上
    await B.pg.evaluate((ms) => { window.__off = ms - Object.getPrototypeOf(Date).now(); document.dispatchEvent(new Event('visibilitychange')); }, new Date('2026-11-29T12:00:00').getTime());
    await B.pg.waitForTimeout(200);
    const pre = await B.pg.evaluate(() => { const x = [...document.querySelectorAll('.panel.today button')].find((y) => y.textContent === '开始'); return { text: document.querySelector('.panel.today').innerText.replace(/\s+/g, ' ').slice(0, 60), disabled: x && x.disabled, hint: document.querySelector('#main').innerText.includes('正在同步'), synced: S.synced, cloud: S.cloud, note: S.cloudNote }; });
    console.log('    打开电脑时：', JSON.stringify(pre));
    check('这时“开始”可点、没有任何“还没同步”的提示', pre.disabled === false && !pre.hint && !pre.note, JSON.stringify(pre));
    await B.pg.click(startBtn); await B.pg.waitForSelector('#qcard');
    const first = await answer(B.pg, true);
    await B.pg.evaluate(() => { window.__online = true; window.__emit(); }); await B.pg.waitForTimeout(3500);      // 网络恢复，云端记录到了
    const st = await B.pg.evaluate((aDone) => { const today = dayStr(), R = S.run; const rest = R.list.slice(R.pos); const P = S.prog.q;
      return { pos: R.pos, len: R.list.length, firstWasDoneOnA: null, restAlreadyDoneToday: rest.filter((q) => P[q.id] && P[q.id].d === today).length, restAlreadyDoneOnA: rest.filter((q) => aDone.includes(q.id)).length, days: S.prog.days[today] }; }, aDone);
    console.log('    云端记录合并进来后，B正在做的这组：', JSON.stringify(st), '第一题A也做过：', aDone.includes(first));
    check('B这组接下来的题里没有今天已经在手机上做过的', st.restAlreadyDoneToday === 0, `还会再出 ${st.restAlreadyDoneToday} 道今天已做过的题`);
    let repeated = 0; for (let i = 0; i < 49; i++) { const was = await B.pg.evaluate(() => { const R = S.run; if (!R || R.pos >= R.list.length) return null; const p = S.prog.q[R.list[R.pos].id]; return !!(p && p.d === dayStr()); }); if (was === null) break; if (was) repeated++; await answer(B.pg, true); }
    await B.pg.evaluate(() => exitRun()); await B.pg.waitForTimeout(2500);
    const end = await B.pg.evaluate(() => ({ answeredToday: (S.prog.days[dayStr()] || {}).n, distinctToday: Object.values(S.prog.q).filter((p) => p.d === dayStr()).length, panel: document.querySelector('.panel.today').innerText.replace(/\s+/g, ' ').slice(0, 40) }));
    console.log(`    B把这50题做完：其中 ${repeated} 道是今天在手机上已经做过的；`, JSON.stringify(end), '| A面板：', await panel(A.pg));
    check('无报错', A.errs.length + B.errs.length === 0, A.errs.concat(B.errs).join('; ')); await A.ctx.close(); await B.ctx.close(); }

  console.log(fails.length ? `\n有 ${fails.length} 项没过：${fails.join('；')}` : '\n全部通过');
  await b.close();
})();
