// 键顺序：两台设备都开着时的来回写。
// 假 db 取“乐观”的那种表现：自己写入后的确认快照沿用本机写出去的那份；从云端来的（刚打开时、别的设备写入时）是按字母排过序的（真实云端读回来就是这样）。
const L = require('./lib.js');
const SITE = process.argv[2];
const { core } = L.loadCore(SITE);
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  const base = L.prog(core, 20, '2026-11-27', '2026-11-27T12:00:00.000Z');
  const store = L.newStore(base);
  const A = await L.device(b, SITE, store, 'A', { local: base, sortKeys: 'server' });
  await A.wait(3000);
  log('A 打开3秒：写云端', store.sets, '次（本机和云端内容相同）');
  // B：本机比云端旧，但多一道云端没有的题（上次关页面前900毫秒内做的）
  const bLocal = L.prog(core, 20, '2026-11-27', '2026-11-27T11:00:00.000Z');
  bLocal.q[core[30].id] = { n: 1, c: 1, l: 1, b: 1, f: '2026-11-27', d: '2026-11-27', due: '2026-11-29', f1: 1 };
  const s0 = store.sets;
  const B = await L.device(b, SITE, store, 'B', { local: bLocal, sortKeys: 'server' });
  await B.wait(15000);
  log('B 打开后15秒（两边都没有任何操作）：写云端', store.sets - s0, '次：', store.history.slice(s0).map((h) => h.by).join(''));
  log('云端', L.nq(store), '题；A', (await A.state()).nq, '题；B', (await B.state()).nq, '题；A.updated', (await A.state()).updated, 'B.updated', (await B.state()).updated);
  const s1 = store.sets;
  await B.pg.selectOption('#dailySel', '60');           // 任意一边有一次真正的操作
  await B.wait(8000);
  log('B 改了一次设置后8秒：写云端', store.sets - s1, '次：', store.history.slice(s1).map((h) => h.by).join(''));
  await A.close(); await B.close();
  await b.close();
})();
