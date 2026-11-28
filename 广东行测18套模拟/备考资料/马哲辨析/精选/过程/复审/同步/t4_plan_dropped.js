// 当天的计划（plan）跟 updated 较新的整份记录走：较新的那份没有今天的计划时，今天做到一半的计划被丢掉
// 场景：手机 A 今天做了计划的前30题（云端 plan.pos=30）。电脑 B 的本机记录停在昨天；
//       B 打开时云端一时连不上（10秒后先走本机），用户在 B 上只改了“每天题数”（或在分科加练里做了几题），之后云端连上。
const L = require('./lib.js');
const SITE = process.argv[2];
const { core } = L.loadCore(SITE);
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  const yesterday = L.prog(core, 40, '2026-11-27', '2026-11-27T12:00:00.000Z', { plan: { day: '2026-11-27', ids: core.slice(0, 40).map((x) => x.id), pos: 40, res: {}, n: {} } });
  for (const what of ['改每天题数', '在“按模块练”里做2题']) {
    log(`=== B 在连上云端之前：${what} ===`);
    const store = L.newStore(yesterday);
    const A = await L.device(b, SITE, store, 'A', { local: yesterday });
    await A.wait(400); await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard');
    for (let i = 0; i < 30; i++) await A.answer(true);
    await A.pg.evaluate(() => exitRun()); await A.wait(1500);
    log('A 做30题后：云端', L.nq(store), '题，plan =', JSON.stringify({ day: L.remote(store).plan.day, pos: L.remote(store).plan.pos }), '；A 面板：', (await A.pg.textContent('.panel.today .sub')).slice(0, 20));
    const B = await L.device(b, SITE, store, 'B', { local: yesterday, delay: 13000 });
    await B.wait(10400);
    log('B 等了10秒：cloud =', (await B.state()).cloud);
    if (what === '改每天题数') await B.pg.selectOption('#dailySel', '60');
    else { await B.pg.click('.mods .mod >> nth=0'); await B.pg.waitForSelector('#qcard'); await B.answer(true); await B.answer(true); await B.pg.evaluate(() => exitRun()); }
    await B.wait(5500);
    const r = L.remote(store), sa = await A.state(), sb = await B.state();
    log('B 连上后：云端', Object.keys(r.q).length, '题，plan =', JSON.stringify(r.plan && { day: r.plan.day, pos: r.plan.pos }), '；A 本机 plan =', JSON.stringify(sa.plan), '；B 本机 plan =', JSON.stringify(sb.plan));
    log('A 的今日面板（没刷新）：', (await A.pg.textContent('.panel.today')).slice(0, 48));
    log('B 的今日面板：', (await B.pg.textContent('.panel.today')).slice(0, 48));
    const prev = await A.pg.evaluate(() => { const p = planParts(dailyOf()); return { len: p.list.length, n: p.n }; });
    log('A 上点“开始”会新排', prev.len, '题：', JSON.stringify(prev.n), '；今天已答', JSON.stringify(sa.days['2026-11-28']));
    log('报错', A.errs.concat(B.errs));
    await A.close(); await B.close();
  }
  await b.close();
})();
