// pushCloud 遇到 unavailable 的重试：断网期间每做一题多一条重试链吗？
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  const store = L.newStore(null);
  const A = await L.device(b, SITE, store, 'A', { offlineMode: 'reject' });
  await A.wait(300); await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard');
  await A.answer(true); await A.wait(1500);
  log('在线做1题：set 调用', (await A.state()).tries, '次，写成', store.sets, '次');
  await A.offline();
  const t0 = (await A.state()).tries;
  const N = 12;
  for (let i = 0; i < N; i++) { await A.answer(true); await A.wait(1500); }      // 断网中每1.5秒做一题
  const t1 = (await A.state()).tries;
  log(`断网中做${N}题（共${N * 1.5}秒）：set 调用`, t1 - t0, '次');
  await A.wait(10000);
  const t2 = (await A.state()).tries;
  log('不再做题，再等10秒：set 又调用', t2 - t1, '次（平均每秒', ((t2 - t1) / 10).toFixed(1), '次）');
  const s0 = store.sets;
  await A.online();
  await A.wait(5000);
  const t3 = (await A.state()).tries;
  log('网络恢复后5秒：set 调用', t3 - t2, '次，写成', store.sets - s0, '次；云端', L.nq(store), '题；cloud =', (await A.state()).cloud);
  const t4a = (await A.state()).tries; await A.wait(5000);
  log('再等5秒：set 调用', (await A.state()).tries - t4a, '次');
  // 如果这一阵密集调用换来的是 resource_exhausted（调用太频繁）：
  log('--- 重试期间有一次调用被拒绝为 resource_exhausted ---');
  await A.pg.evaluate(() => { window.__F.setError = { code: 'resource_exhausted', once: true }; });
  await A.answer(true); await A.wait(1500);
  const st = await A.state();
  log('cloud =', st.cloud, '；提示：', st.note);
  await A.answer(true); await A.wait(1500);
  log('之后再做1题：云端', L.nq(store), '题，本机', (await A.state()).nq, '题（这次打开期间不再写云端）');
  await A.close(); await b.close();
})();
