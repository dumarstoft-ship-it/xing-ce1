// mergeProg 用 JSON.stringify 比较两份记录是否相同，结果依赖对象里键的先后顺序。
// 假 db 加一个开关：云端返回文档时把键按字母排序（内容不变，只是顺序变了）。只用一台设备。
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  for (const sortKeys of [false, true]) {
    log(`=== 云端返回的键顺序：${sortKeys ? '按字母排序（和写入时不同）' : '和写入时一样'} ===`);
    const store = L.newStore(null);
    const A = await L.device(b, SITE, store, 'A', { sortKeys });
    await A.wait(300); await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard');
    for (let i = 0; i < 3; i++) await A.answer(true);
    await A.pg.evaluate(() => exitRun());
    await A.wait(2000);
    const s0 = store.sets;
    await A.wait(15000);
    const st = await A.state();
    log('做3题后先等2秒（这时已写', s0, '次），再空等15秒：又写云端', store.sets - s0, '次；cloud =', st.cloud);
    log('本机的一条记录键顺序：', await A.pg.evaluate(() => Object.keys(Object.values(S.prog.q)[0]).join(',')), '；云端返回的：', await A.pg.evaluate(async () => Object.keys(Object.values((await S.ref.get()).data().q)[0]).join(',')));
    log('报错', A.errs);
    await A.close();
  }
  await b.close();
})();
