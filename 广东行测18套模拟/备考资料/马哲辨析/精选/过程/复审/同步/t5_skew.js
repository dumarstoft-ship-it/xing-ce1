// 两台设备的时钟不一致：B 的时钟快 skew 毫秒。B 先用过（留下“未来”的 updated）并开着停在今日页；之后在 A 上改设置、做题。
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  for (const skew of [5 * 60000, 3000]) {
    log(`=== B 的时钟快 ${skew / 1000} 秒 ===`);
    const store = L.newStore(null);
    const B = await L.device(b, SITE, store, 'B', { skew });
    await B.wait(300); await B.pg.click(L.startBtn); await B.pg.waitForSelector('#qcard');
    for (let i = 0; i < 5; i++) await B.answer(true);
    await B.pg.evaluate(() => exitRun()); await B.wait(1500);
    log('B 做5题后：云端 updated =', L.remote(store).updated, 'plan.pos =', L.remote(store).plan.pos);
    const A = await L.device(b, SITE, store, 'A', {});
    await A.wait(800);
    const s0 = store.sets;
    await A.pg.selectOption('#dailySel', '80');
    await A.wait(300);
    log('A 改每天题数为80：A.daily =', (await A.state()).daily, 'A.updated =', (await A.state()).updated);
    await A.wait(3500);
    log('3.5秒后：A.daily =', (await A.state()).daily, '；B.daily =', (await B.state()).daily, '；云端 daily =', L.remote(store).settings.daily, '；这期间写云端', store.sets - s0, '次', JSON.stringify(store.history.slice(s0).map((h) => h.by)));
    const s1 = store.sets;
    await A.pg.click(L.contBtn); await A.pg.waitForSelector('#qcard');
    for (let i = 0; i < 4; i++) { await A.answer(true); await A.wait(1500); }
    await A.pg.evaluate(() => exitRun());
    await A.wait(6000);
    const sa = await A.state(), sb = await B.state();
    log('A 接着做4题（每题隔1.5秒）后退出，再等6秒：A plan.pos =', sa.plan.pos, '；B plan.pos =', sb.plan.pos, '；云端 plan.pos =', L.remote(store).plan.pos, '；这期间写云端', store.sets - s1, '次', JSON.stringify(store.history.slice(s1).map((h) => h.by + h.plan)));
    const s2 = store.sets; await A.wait(5000);
    log('再空等5秒，写云端', store.sets - s2, '次');
    log('报错', A.errs.concat(B.errs));
    await A.close(); await B.close();
  }
  await b.close();
})();
