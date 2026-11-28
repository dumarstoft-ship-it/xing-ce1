// 两台设备交替做同一份今日计划：A 停在做题页不刷新，B 接着做，A 再继续
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  log('=== 情形1：A 做6题停在第7题；B 打开接着做3题（到第9题）；A 不刷新，继续答 ===');
  { const store = L.newStore(null);
    const A = await L.device(b, SITE, store, 'A', {});
    await A.wait(300); await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard');
    const aIds = []; for (let i = 0; i < 6; i++) aIds.push(await A.answer(true));
    await A.wait(1500);
    const B = await L.device(b, SITE, store, 'B', {});
    await B.wait(600); await B.pg.click(L.contBtn); await B.pg.waitForSelector('#qcard');
    const bIds = []; for (let i = 0; i < 3; i++) bIds.push(await B.answer(true));
    await B.wait(1500);
    const mid = await A.state();
    log('B 做完3题后：云端 plan.pos =', L.remote(store).plan.pos, '；A 本机 plan.pos =', mid.plan.pos, '，A 正在做的这组 run.pos =', mid.run.pos, '（屏幕上还是第', mid.run.pos + 1, '题）');
    const shown = await A.pg.evaluate(() => S.run.list[S.run.pos].id);
    log('A 屏幕上这道题', shown, 'B 是否已做过：', bIds.includes(shown));
    const again = []; for (let i = 0; i < 3; i++) again.push(await A.answer(true));
    await A.wait(1500);
    const end = await A.state();
    log('A 接着答3题：其中 B 已经做过的有', again.filter((id) => bIds.includes(id)).length, '题；A 本机 plan.pos =', end.plan.pos, '；云端 plan.pos =', L.remote(store).plan.pos, '（B 做到过 9）');
    log('这3题的作答次数：', JSON.stringify(await A.pg.evaluate((ids) => ids.map((id) => S.prog.q[id].n), again)), '；今天已答', JSON.stringify(end.days));
    const bs = await B.state();
    log('B（停在做题页）本机 plan.pos =', bs.plan.pos, 'run.pos =', bs.run && bs.run.pos);
    log('写云端历史', JSON.stringify(store.history.map((h) => [h.by, h.nq, h.plan])));
    log('报错', A.errs.concat(B.errs));
    await A.close(); await B.close(); }

  log('=== 情形2：云端的今日计划已做到第30题（另一台设备做的）；这台设备本机停在第10题，打开后马上点“继续”（同步的记录1.5秒后才到） ===');
  { // 先用一台设备做出30题的云端状态，同时留下做到第10题时的本机副本
    const store = L.newStore(null);
    const X = await L.device(b, SITE, store, 'X', { seedRandom: 7 });
    await X.wait(300); await X.pg.click(L.startBtn); await X.pg.waitForSelector('#qcard');
    for (let i = 0; i < 10; i++) await X.answer(true);
    await X.wait(1200);
    const at10 = await X.local();
    for (let i = 0; i < 20; i++) await X.answer(true);
    await X.wait(1500);
    log('云端 plan.pos =', L.remote(store).plan.pos, '，云端', L.nq(store), '题；本机副本 plan.pos =', at10.plan.pos);
    await X.close();
    const A = await L.device(b, SITE, store, 'A', { local: at10, delay: 1500 });
    const btn = await A.pg.evaluate(() => { const x = document.querySelector('.panel.today button'); return { text: x.textContent, disabled: x.disabled }; });
    log('打开时今日计划的按钮：', JSON.stringify(btn));
    await A.pg.click(L.contBtn); await A.pg.waitForSelector('#qcard');
    await A.wait(2500);
    const st = await A.state();
    log('记录到了以后：A 本机', st.nq, '题，plan.pos =', st.plan.pos, '，正在做的这组 run.pos =', st.run.pos);
    const redo = []; for (let i = 0; i < 20; i++) redo.push(await A.answer(true));
    const ns = await A.pg.evaluate((ids) => ids.map((id) => S.prog.q[id].n), redo);
    await A.wait(1500);
    log('A 接着做20题：其中今天已经在另一台设备做过的（作答次数变成2）有', ns.filter((n) => n >= 2).length, '题；云端 plan.pos =', L.remote(store).plan.pos, '；今天已答', JSON.stringify((await A.state()).days));
    log('报错', A.errs);
    await A.close(); }
  await b.close();
})();
