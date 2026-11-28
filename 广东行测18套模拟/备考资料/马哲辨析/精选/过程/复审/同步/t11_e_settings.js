// mergeProg 的两条分支：同一天同次数但内容不同（只改了自评 e）；设置只在一边改过
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  log('=== 只改了自评 e：B 没同步上去（断网/关页面前900毫秒内）时点了“还讲不清”，之后 A 做了别的题 ===');
  { const store = L.newStore(null);
    const A = await L.device(b, SITE, store, 'A', {});
    await A.wait(300); await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard');
    const q1 = await A.answer(true); await A.wait(1500);
    const B = await L.device(b, SITE, store, 'B', {});
    await B.wait(600);
    await B.pg.evaluate((id) => { setExplain(S.q[id], 0); }, q1);       // B 上给这道题点“还讲不清”
    await B.wait(200);
    const bLocal = await B.local(); await B.close();                    // 没等到推云端就关了
    log('B 本机这道题：', JSON.stringify(bLocal.q[q1]), '；云端：', JSON.stringify(L.remote(store).q[q1]));
    await A.answer(true); await A.wait(1500);                           // A 之后又做了一题（云端的整份记录变得更新）
    const B2 = await L.device(b, SITE, store, 'B2', { local: bLocal });
    await B2.wait(2500);
    log('B 再打开后：本机这道题', JSON.stringify(await B2.pg.evaluate((id) => S.prog.q[id], q1)), '；云端', JSON.stringify(L.remote(store).q[q1]), '（自评 e 没了）');
    await A.close(); await B2.close(); }

  log('=== 设置只在一边改过：B 断网时把“每天题数”改成80、勾了“先写错因”；之后 A 做了一题；B 再连上 ===');
  { const store = L.newStore(null);
    const A = await L.device(b, SITE, store, 'A', {});
    await A.wait(300); await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard'); await A.answer(true); await A.wait(1500);
    const B = await L.device(b, SITE, store, 'B', {});
    await B.wait(600);
    await B.pg.evaluate(() => { S.prog.settings.daily = 80; S.prog.settings.why = true; touch(); });
    await B.wait(200);
    const bLocal = await B.local(); await B.close();
    await A.answer(true); await A.wait(1500);
    const B2 = await L.device(b, SITE, store, 'B2', { local: bLocal });
    await B2.wait(2500);
    log('B 再打开后：本机设置', JSON.stringify((await B2.local()).settings), '；云端', JSON.stringify(L.remote(store).settings));
    await A.close(); await B2.close(); }
  await b.close();
})();
