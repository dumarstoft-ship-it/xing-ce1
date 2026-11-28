// 等同步的那几秒里改一个设置（控件没有禁用）：本机 updated 变成“现在”，云端那份的设置和当天的题组整份输给本机
// 场景：云端是另一台设备今天做到第30题的记录，设置改过（每组20题、先写错因、每天40题）。这台设备打开（本机空白，或是昨天的旧记录），记录2秒后才到；这2秒里把“每天题数”改成60。
const L = require('./lib.js');
const SITE = process.argv[2];
const log = (...a) => console.log(...a);
(async () => {
  const b = await L.launch();
  // 先用一台设备造出云端状态
  const store = L.newStore(null);
  const X = await L.device(b, SITE, store, 'X', {});
  await X.wait(300);
  await X.pg.evaluate(() => { S.prog.settings.size = 20; S.prog.settings.why = true; S.prog.settings.daily = 40; touch(); });
  await X.pg.evaluate(() => { route(); }); await X.pg.click(L.startBtn); await X.pg.waitForSelector('#qcard');
  for (let i = 0; i < 30; i++) await X.answer(true);
  await X.pg.evaluate(() => exitRun()); await X.wait(1500);
  const cloud0 = L.remote(store);
  log('云端：', Object.keys(cloud0.q).length, '题，plan.pos =', cloud0.plan.pos, '/', cloud0.plan.ids.length, '，设置', JSON.stringify(cloud0.settings));
  for (const kind of ['本机空白（新设备）', '本机是这台设备今天早些时候的记录（做到第10题）']) {
    store.remote = JSON.stringify(cloud0);
    let local = null;
    if (kind.startsWith('本机是')) { local = JSON.parse(JSON.stringify(cloud0)); const keep = local.plan.ids.slice(0, 10); for (const id of Object.keys(local.q)) if (!keep.includes(id)) delete local.q[id]; local.plan.pos = 10; local.plan.res = Object.fromEntries(keep.map((id) => [id, 1])); local.days['2026-11-28'] = { n: 10, c: 10 }; local.updated = '2026-11-28T00:30:00.000Z'; }
    log(`=== ${kind} ===`);
    const A = await L.device(b, SITE, store, 'A', { local, delay: 2000 });
    await A.wait(300);
    log('同步前：“每天题数”可改吗：', !(await A.pg.isDisabled('#dailySel')), '；面板：', (await A.pg.textContent('.panel.today')).includes('正在同步') ? '正在同步…' : (await A.pg.textContent('.panel.today .sub')).slice(0, 14));
    await A.pg.selectOption('#dailySel', '60');
    await A.wait(4500);
    const r = L.remote(store), st = await A.state();
    log('同步后：云端设置', JSON.stringify(r.settings), '；云端 plan =', JSON.stringify(r.plan && { pos: r.plan.pos, len: r.plan.ids.length }), '；本机', st.nq, '题；X（另一台，开着）plan =', JSON.stringify((await X.state()).plan));
    log('A 的今日面板：', (await A.pg.textContent('.panel.today')).slice(0, 40));
    await A.close();
  }
  await X.close(); await b.close();
})();
