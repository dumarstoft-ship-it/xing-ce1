// 没发现问题的几条路径（假 db 保持键顺序）：两边离线各做一段后先后打开；error 回调；db 为 null；没有 window.claude；只有缓存副本；文档不存在
const L = require('./lib.js');
const SITE = process.argv[2];
const { core } = L.loadCore(SITE);
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  log('=== b：两边离线各做一段（各自排了当天的计划，有重合的题、结果不同），再先后打开 ===');
  { const base = L.prog(core, 0, '2026-11-27', '');
    // 用两台“离线”设备各自做题，取它们的本机记录
    const mk = async (name, n, wrongEvery, when) => { const st = L.newStore(null); const d = await L.device(b, SITE, st, name, { noDb: true, when, seedRandom: name === 'A' ? 11 : 22 }); await d.wait(200); await d.pg.click(L.startBtn); await d.pg.waitForSelector('#qcard'); const ids = []; for (let i = 0; i < n; i++) ids.push([await d.answer(!(wrongEvery && i % wrongEvery === 0)), !(wrongEvery && i % wrongEvery === 0)]); await d.wait(100); const loc = await d.local(); await d.close(); return { loc, ids }; };
    const a = await mk('A', 20, 4, '2026-11-28T09:00:00'), bb = await mk('B', 10, 0, '2026-11-28T10:00:00');
    const overlap = a.ids.filter(([id]) => bb.ids.some(([x]) => x === id));
    log('A 离线做20题（错5题），B 离线做10题（全对）；两边都做过的题', overlap.length, '道，其中 A 答错、B 答对的', overlap.filter(([, ok]) => !ok).length, '道');
    const store = L.newStore(null); store.t0 = Date.now() - 2 * 3600e3;   // 之后打开时已是 11:00 以后
    const A = await L.device(b, SITE, store, 'A', { local: a.loc }); await A.wait(2000);
    log('A 先打开：云端', L.nq(store), '题，plan.pos =', L.remote(store).plan.pos, '，sets', store.sets);
    await A.close();
    const B = await L.device(b, SITE, store, 'B', { local: bb.loc }); await B.wait(3000);
    const r = L.remote(store), union = new Set([...a.ids.map((x) => x[0]), ...bb.ids.map((x) => x[0])]).size;
    log('B 再打开：云端', Object.keys(r.q).length, '题（两边合起来应为', union, '），plan.pos =', r.plan.pos, '/', r.plan.ids.length, '，今天作答数', JSON.stringify(r.days['2026-11-28']), '，sets', store.sets, JSON.stringify(store.history.map((h) => [h.by, h.nq, h.plan])));
    log('重合且结果不同的题，云端留的是：', JSON.stringify(overlap.filter(([, ok]) => !ok).map(([id]) => r.q[id].l)), '（B 的整份记录较新，跟 B：1=答对）');
    log('B 面板：', (await B.pg.textContent('.panel.today .sub')).slice(0, 16), '；计划里剩下的题有没有今天做过的：', await B.pg.evaluate(() => S.prog.plan.ids.slice(S.prog.plan.pos).filter((id) => S.prog.q[id] && S.prog.q[id].d === dayStr()).length));
    const s0 = store.sets; await B.wait(4000); log('再等4秒，又写', store.sets - s0, '次；报错', B.errs);
    await B.close(); }

  log('=== e：监听报错（error 回调） ===');
  { const store = L.newStore(L.prog(core, 30, '2026-11-27', '2026-11-27T12:00:00.000Z'));
    const A = await L.device(b, SITE, store, 'A', { delay: -1, errorAfter: 500, errorCode: 'revoked' });
    await A.wait(1200);
    const st = await A.state();
    log('cloud =', st.cloud, '；提示：', st.note, '；“开始”可点：', !(await A.pg.isDisabled(L.startBtn)));
    await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard'); await A.answer(true); await A.wait(1500);
    log('做1题后：写云端', store.sets, '次；本机', (await A.state()).nq, '题；报错', A.errs);
    await A.close(); }

  log('=== f：db 为 null / 没有 window.claude（离线单文件版） ===');
  for (const o of [{ noDb: true }, { noClaude: true }]) {
    const store = L.newStore(null);
    const A = await L.device(b, SITE, store, 'A', o);
    await A.wait(300);
    const st = await A.state();
    log(JSON.stringify(o), 'cloud =', st.cloud, '；“开始”可点：', !(await A.pg.isDisabled(L.startBtn)), '；提示：', st.note.slice(0, 20));
    await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard'); await A.answer(true); await A.wait(1200);
    log('  做1题：本机', (await A.local()).plan.pos, '；报错', A.errs);
    await A.close(); }

  log('=== c：只有缓存副本，确认过的记录一直不来 ===');
  { const store = L.newStore(L.prog(core, 100, '2026-11-27', '2026-11-27T12:00:00.000Z'));
    const A = await L.device(b, SITE, store, 'A', { delay: -1, cached: L.prog(core, 50, '2026-11-26', '2026-11-26T12:00:00.000Z') });
    await A.wait(500);
    log('0.5秒：本机', (await A.state()).nq, '题，synced', (await A.state()).synced, '，“开始”可点：', !(await A.pg.isDisabled(L.startBtn)));
    await A.wait(10000);
    log('10秒后：cloud =', (await A.state()).cloud, '，“开始”可点：', !(await A.pg.isDisabled(L.startBtn)));
    await A.pg.click(L.startBtn); await A.pg.waitForSelector('#qcard'); await A.answer(true); await A.answer(true); await A.wait(1500);
    log('做2题：写云端', store.sets, '次（应为0），云端仍', L.nq(store), '题');
    await A.pg.evaluate(() => window.__F.emitServer()); await A.wait(2500);
    log('确认过的记录终于到了：云端', L.nq(store), '题（100＋新做的），写', store.sets, '次，cloud =', (await A.state()).cloud, '；报错', A.errs);
    await A.close(); }

  log('=== d：缓存副本说“没有文档”，确认过的也是“没有文档” ===');
  { const store = L.newStore(null);
    const A = await L.device(b, SITE, store, 'A', { cachedMissing: true, delay: 800, local: L.prog(core, 5, '2026-11-27', '2026-11-27T12:00:00.000Z') });
    await A.wait(400); log('0.4秒：synced', (await A.state()).synced, '，写', store.sets, '次');
    await A.wait(2500); log('之后：synced', (await A.state()).synced, '，云端', L.nq(store), '题，写', store.sets, '次');
    await A.close(); }
  await b.close();
})();
