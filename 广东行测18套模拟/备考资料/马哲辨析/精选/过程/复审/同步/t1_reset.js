// 清除全部记录 与 另一台设备 的配合
// 用法：node t1_reset.js <站点目录>
const L = require('./lib.js');
const SITE = process.argv[2];
const { core } = L.loadCore(SITE);
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  const reset = async (dev) => { await dev.pg.evaluate(() => { location.hash = '#stats'; }); await dev.pg.waitForSelector('#resetBtn'); await dev.pg.click('#resetBtn'); await dev.pg.click('#resetBtn'); };

  log('=== 情形a：A、B 都同步过（各有60题的本机记录）。B 关着，A 清除；之后 B 打开 ===');
  { const base = L.prog(core, 60, '2026-11-27', '2026-11-27T12:00:00.000Z');
    const store = L.newStore(base);
    const A = await L.device(b, SITE, store, 'A', { local: base });
    await A.wait(400);
    await reset(A); await A.wait(1500);
    log('A 清除后：A本机', (await A.state()).nq, '题；云端', L.nq(store), '题；sets', store.sets);
    const B = await L.device(b, SITE, store, 'B', { local: base });
    await B.wait(2500);
    const sb = await B.state(), sa = await A.state();
    log('B 打开后：B本机', sb.nq, '题；云端', L.nq(store), '题；A本机（没刷新）', sa.nq, '题；sets', store.sets, '历史', JSON.stringify(store.history.map((h) => [h.by, h.nq])));
    await A.close(); await B.close(); }

  log('=== 情形b：A、B 都开着；B 今天的计划做到第10题后退出停在今日页；A 清除 ===');
  { const base = L.prog(core, 60, '2026-11-27', '2026-11-27T12:00:00.000Z');
    const store = L.newStore(base);
    const B = await L.device(b, SITE, store, 'B', { local: base });
    await B.wait(300); await B.pg.click(L.startBtn); await B.pg.waitForSelector('#qcard');
    for (let i = 0; i < 10; i++) await B.answer(true);
    await B.pg.evaluate(() => exitRun()); await B.wait(1500);
    const A = await L.device(b, SITE, store, 'A', { local: base });
    await A.wait(600);
    log('清除前：A', JSON.stringify(await A.state()).slice(0, 160));
    const before = store.sets;
    await reset(A); await A.wait(4000);
    const sa = await A.state(), sb = await B.state();
    log('清除后4秒：A本机', sa.nq, '题，plan', JSON.stringify(sa.plan), '；B本机', sb.nq, '题，plan', JSON.stringify(sb.plan), '；云端', L.nq(store), '题，plan', JSON.stringify(L.remote(store).plan), '；这期间写云端', store.sets - before, '次', JSON.stringify(store.history.slice(before).map((h) => [h.by, h.nq, h.plan])));
    log('B 的今日面板：', (await B.pg.textContent('.panel.today')).slice(0, 60));
    await A.pg.evaluate(() => { location.hash = '#today'; }); await A.wait(300);
    log('A 的今日面板：', (await A.pg.textContent('.panel.today')).slice(0, 60));
    log('报错', A.errs.concat(B.errs));
    await A.close(); await B.close(); }

  log('=== 情形c：只有一台设备，清除后刷新 ===');
  { const base = L.prog(core, 60, '2026-11-27', '2026-11-27T12:00:00.000Z');
    const store = L.newStore(base);
    const A = await L.device(b, SITE, store, 'A', { local: base });
    await A.wait(400); await reset(A); await A.wait(1500);
    await A.pg.evaluate(() => { location.hash = '#today'; }); await A.pg.reload(); await A.pg.waitForSelector('.today'); await A.wait(800);
    log('刷新后：A本机', (await A.state()).nq, '题；云端', L.nq(store), '题');
    await A.close(); }
  await b.close();
})();
