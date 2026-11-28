// 关页面前 900 毫秒内的作答：本机已存，云端没有；之后的几种走向
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  const store = L.newStore(null);
  const A = await L.device(b, SITE, store, 'A', {});
  await A.wait(300); await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard');
  const ids = [];
  ids.push(await A.answer(true)); ids.push(await A.answer(true)); await A.wait(1500);
  ids.push(await A.answer(false));                       // 第3题答错
  await A.wait(300);
  const aLocal = await A.local();
  await A.close();                                       // 300 毫秒后关页面
  log('A 关页面时：本机', Object.keys(aLocal.q).length, '题，plan.pos =', aLocal.plan.pos, '；云端', L.nq(store), '题，plan.pos =', L.remote(store).plan.pos);
  // 走向一：先在另一台设备 B 上接着做
  const B = await L.device(b, SITE, store, 'B', {});
  await B.wait(600);
  log('B 打开：面板', (await B.pg.textContent('.panel.today .sub')).slice(0, 12), '；A 答错的第3题在 B 上', (await B.pg.evaluate((id) => !!S.prog.q[id], ids[2])) ? '有记录' : '没有记录');
  await B.pg.click(L.contBtn); await B.pg.waitForSelector('#qcard');
  const again = await B.answer(true);                    // B 上这道题答对了
  await B.answer(true); await B.wait(1500);
  log('B 接着做的第一题就是 A 最后答错的那题：', again === ids[2], '；B 上答对后记录', JSON.stringify(await B.pg.evaluate((id) => S.prog.q[id], ids[2])));
  // 走向二：A 再打开（本机留着那条答错的记录）
  const A2 = await L.device(b, SITE, store, 'A2', { local: aLocal });
  await A2.wait(2500);
  const r = L.remote(store);
  log('A 再打开后：云端', Object.keys(r.q).length, '题，plan.pos =', r.plan.pos, '；第3题云端的记录', JSON.stringify(r.q[ids[2]]), '；写云端历史', JSON.stringify(store.history.map((h) => [h.by, h.nq, h.plan])));
  log('报错', B.errs.concat(A2.errs));
  await B.close(); await A2.close();
  // 走向三：只用这一台，重新打开能补推
  const store2 = L.newStore(null);
  const C = await L.device(b, SITE, store2, 'C', {});
  await C.wait(300); await C.pg.click(L.startBtn); await C.pg.waitForSelector('#qcard');
  await C.answer(true); await C.wait(1500); await C.answer(true); await C.wait(200);
  const cLocal = await C.local(); await C.close();
  log('只用一台：关页面时云端', L.nq(store2), '题，本机', Object.keys(cLocal.q).length, '题');
  const C2 = await L.device(b, SITE, store2, 'C2', { local: cLocal });
  await C2.wait(2500);
  log('重新打开后云端', L.nq(store2), '题，plan.pos =', L.remote(store2).plan.pos);
  await C2.close();
  await b.close();
})();
