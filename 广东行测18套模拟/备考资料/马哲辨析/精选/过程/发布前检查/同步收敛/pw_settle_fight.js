// 真浏览器复现（同一天、同一份计划）：手机停在今日计划的做题页；电脑在别的练习里做了计划后面的两道题，然后回到今日页。
const L = require('./lib.js'); const path = require('path');
const SITE = path.join(__dirname, process.argv[2] || 'site');
(async () => {
  const browser = await L.launch(); const store = L.newStore(null);
  const o = { when: '2026-11-28T09:00:00', sortKeys: true, latency: 30, push: 10 };
  const ph = await L.device(browser, SITE, store, 'PHONE', { ...o, seedRandom: 9 });
  const pc = await L.device(browser, SITE, store, 'PC', { ...o, seedRandom: 7 });
  await ph.pg.waitForFunction(() => S.synced); await ph.pg.click(L.startBtn);
  for (let i = 0; i < 2; i++) { await ph.answer(true); await ph.wait(1200); }
  await ph.wait(2500);
  const ids = await ph.pg.evaluate(() => S.prog.plan.ids.slice());
  await pc.pg.waitForFunction(() => S.synced && S.prog.plan && S.prog.plan.pos === 2);
  await pc.pg.evaluate((two) => startRun(two.map((id) => S.q[id]), '练习'), [ids[10], ids[11]]);
  for (let i = 0; i < 2; i++) { await pc.answer(true); await pc.wait(1200); }
  await pc.wait(1500);
  const s0 = store.sets, h0 = store.history.length; await pc.pg.evaluate(() => exitRun());
  await pc.wait(20000);
  const by = {}; for (const x of store.history.slice(h0)) by[x.by] = (by[x.by] || 0) + 1;
  console.log(JSON.stringify({ site: process.argv[2] || 'site', writesIn20sAfterPcBackToToday: store.sets - s0, by, phoneRun: await ph.pg.evaluate(() => ({ pos: S.run.pos, revealed: runState.revealed })), pcView: await pc.pg.evaluate(() => (S.run ? 'run' : 'today')), errs: [...pc.errs, ...ph.errs].slice(0, 2) }));
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
