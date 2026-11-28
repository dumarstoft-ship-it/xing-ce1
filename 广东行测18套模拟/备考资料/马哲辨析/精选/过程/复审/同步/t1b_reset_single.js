// 清除全部记录：只有一台设备时的几种时序
const L = require('./lib.js');
const SITE = process.argv[2];
const { core } = L.loadCore(SITE);
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  const reset = async (dev) => { await dev.pg.evaluate(() => { location.hash = '#stats'; }); await dev.pg.waitForSelector('#resetBtn'); await dev.pg.click('#resetBtn'); await dev.pg.click('#resetBtn'); };
  const base = L.prog(core, 60, '2026-11-27', '2026-11-27T12:00:00.000Z');

  log('=== d：清除后 300 毫秒内刷新（推云端的 900 毫秒还没到） ===');
  { const store = L.newStore(base);
    const A = await L.device(b, SITE, store, 'A', { local: base });
    await A.wait(400); await reset(A); await A.wait(300);
    log('刷新前：本机', (await A.state()).nq, '题；云端', L.nq(store), '题；sets', store.sets);
    await A.pg.evaluate(() => { location.hash = '#today'; }); await A.pg.reload(); await A.pg.waitForSelector('.today'); await A.wait(2500);
    log('刷新后：本机', (await A.state()).nq, '题；云端', L.nq(store), '题；sets', store.sets);
    await A.close(); }

  log('=== e：云端一时连不上（12秒后才到），10秒后清除 ===');
  { const store = L.newStore(base);
    const A = await L.device(b, SITE, store, 'A', { local: base, delay: 12500 });
    await A.wait(10300); await reset(A); await A.wait(200);
    log('清除后：本机', (await A.state()).nq, '题；云端', L.nq(store), '题');
    await A.wait(4500);
    log('连上后：本机', (await A.state()).nq, '题；云端', L.nq(store), '题；sets', store.sets);
    await A.close(); }

  log('=== f：清除成功并推到云端；刷新时先到一份清除前的缓存副本，再到确认过的空白记录 ===');
  { const store = L.newStore(base);
    const A = await L.device(b, SITE, store, 'A', { local: base });
    await A.wait(400); await reset(A); await A.wait(1500);
    log('清除后：本机', (await A.state()).nq, '题；云端', L.nq(store), '题');
    const blank = await A.local();
    await A.close();
    const A2 = await L.device(b, SITE, store, 'A2', { local: blank, cached: base, delay: 800 });
    await A2.wait(3000);
    log('再打开：本机', (await A2.state()).nq, '题；云端', L.nq(store), '题；sets', store.sets);
    await A2.close(); }
  await b.close();
})();
