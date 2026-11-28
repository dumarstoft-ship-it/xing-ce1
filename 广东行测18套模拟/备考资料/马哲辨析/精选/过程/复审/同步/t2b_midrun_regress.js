// A 停在做题页（第7题），B 把同一份计划做到第9题并关掉；A 不刷新，答1题后停一下：云端 plan.pos、res 的变化
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  const store = L.newStore(null);
  const A = await L.device(b, SITE, store, 'A', {});
  await A.wait(300); await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard');
  for (let i = 0; i < 6; i++) await A.answer(true);
  await A.wait(1500);
  const B = await L.device(b, SITE, store, 'B', {});
  await B.wait(600); await B.pg.click(L.contBtn); await B.pg.waitForSelector('#qcard');
  const bIds = []; for (let i = 0; i < 3; i++) bIds.push(await B.answer(i !== 1));     // B 做3题，第2题答错
  await B.wait(1500);
  let r = L.remote(store);
  log('B 做完：云端 plan.pos =', r.plan.pos, '，res 里', Object.keys(r.plan.res).length, '题；B 答错的那题云端记录', JSON.stringify(r.q[bIds[1]]));
  await B.close();
  const sa = await A.state();
  log('A（没刷新，仍在做题页）：本机 plan.pos =', sa.plan.pos, '；正在做的这组 run.pos =', sa.run.pos, '；A 的 run.res 和 plan.res 还是同一个对象吗：', await A.pg.evaluate(() => S.run.res === S.prog.plan.res));
  const a7 = await A.answer(true); await A.wait(1500);
  r = L.remote(store);
  log('A 答了屏幕上的题（B 已做过：', bIds.includes(a7), '）后：云端 plan.pos =', r.plan.pos, '（退回去了），res 里', Object.keys(r.plan.res).length, '题（B 的', bIds.filter((id) => id in r.plan.res).length, '/3 还在）');
  const a8 = await A.answer(true); await A.wait(1500);            // 这题 B 答错过；A 这次答对
  r = L.remote(store);
  log('A 接着又被出了 B 做过的题', bIds.includes(a8), '；B 答错、A 当天再答对的那题：', JSON.stringify(r.q[bIds[1]]));
  await A.pg.evaluate(() => exitRun()); await A.wait(1500);
  r = L.remote(store);
  log('A 退出回到今日页（这时才 settle）：云端 plan.pos =', r.plan.pos, '；面板：', (await A.pg.textContent('.panel.today .sub')).slice(0, 14));
  log('写云端历史', JSON.stringify(store.history.map((h) => [h.by, h.nq, h.plan])), '报错', A.errs);
  await A.close(); await b.close();
})();
