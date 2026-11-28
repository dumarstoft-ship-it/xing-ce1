// 已经同步过、一直开着的页面（S.synced 为 true）落后于云端时写云端
// 场景：电脑 B 上午同步过，做到计划第5题时合上（断网、页面还开着）；手机 A 接着把计划做到第35题并关掉；
//       打开电脑，网络还没恢复时就在屏幕上那道题上作答（写入排队），网络恢复后这次写入落到云端。
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  for (const mode of ['hang', 'reject']) {
    log(`=== 断网时 set 的表现：${mode === 'hang' ? '挂起排队，连上后写入' : '报 unavailable，页面自己重试'} ===`);
    const store = L.newStore(null);
    const B = await L.device(b, SITE, store, 'B', { offlineMode: mode, reconnect: mode === 'reject' ? 4000 : 5 });
    await B.wait(300); await B.pg.click(L.startBtn); await B.pg.waitForSelector('#qcard');
    for (let i = 0; i < 5; i++) await B.answer(true);
    await B.wait(1500);
    log('B 做5题后：云端', L.nq(store), '题，plan.pos =', L.remote(store).plan.pos, '；B synced =', (await B.state()).synced);
    await B.offline();                                   // 合上电脑
    const A = await L.device(b, SITE, store, 'A', {});
    await A.wait(600); await A.pg.click(L.contBtn); await A.pg.waitForSelector('#qcard');
    const aIds = []; for (let i = 0; i < 30; i++) aIds.push(await A.answer(i % 6 !== 0));   // A 做30题，其中5题答错
    await A.wait(1500);
    log('A 接着做30题后：云端', L.nq(store), '题，plan.pos =', L.remote(store).plan.pos);
    await A.close();                                     // 手机锁屏/关掉
    const shown = await B.pg.evaluate(() => S.run.list[S.run.pos].id);
    await B.answer(true);                                // 打开电脑，网络还没恢复，先答了屏幕上这道题
    await B.wait(1200);
    log('B 断网中答了1题（这道题 A 今天', aIds.includes(shown) ? '已经做过' : '没做过', '）；B synced =', (await B.state()).synced, '，cloud =', (await B.state()).cloud);
    await B.online();                                    // 网络恢复
    await B.wait(6000);
    const r = L.remote(store), sb = await B.state();
    log('网络恢复后：云端', Object.keys(r.q).length, '题，plan.pos =', r.plan.pos, '；A 做的30题还在云端的有', aIds.filter((id) => r.q[id]).length, '题；A 答错的5题在云端的记录：', JSON.stringify(aIds.filter((_, i) => i % 6 === 0).map((id) => (r.q[id] ? r.q[id].l : '无'))));
    log('B 本机', sb.nq, '题，plan.pos =', sb.plan.pos, '；B 收到的快照：', JSON.stringify(await B.pg.evaluate(() => window.__F.log.slice(-4).map((x) => [x.n, x.fromCache ? 'cache' : 'server', x.hasPendingWrites ? 'pending' : '']))));
    const redo = []; for (let i = 0; i < 10; i++) redo.push(await B.answer(true));
    log('B 接着做10题：其中 A 今天已经做过的有', redo.filter((id) => aIds.includes(id)).length, '题');
    await B.wait(1500);
    // 手机再打开：本机还留着那30题
    log('写云端历史', JSON.stringify(store.history.map((h) => [h.by, h.nq, h.plan])));
    log('报错', B.errs);
    await B.close();
  }
  await b.close();
})();
