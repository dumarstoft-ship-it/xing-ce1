// 真浏览器复现：电脑停在昨天“今日计划”的做题页（没作答的题上），手机今天排了新计划。
// A：两台同时开着；B：电脑夜里断网（休眠），白天手机做了几题后回到今日页，电脑再连上。
const L = require('./lib.js'); const path = require('path');
const SITE = path.join(__dirname, process.argv[2] || 'site');
const sameSet = (a, b) => !!a && !!b && a.length === b.length && a.slice().sort().join() === b.slice().sort().join();
const panel = (d) => d.pg.evaluate(() => { const p = document.querySelector('.panel.today'); if (!p) return null; const h2 = p.querySelector('h2'), sub = p.querySelector('.sub'); return (h2 ? h2.textContent : '') + ' | ' + (sub ? sub.textContent : ''); });
const planOf = (d) => d.pg.evaluate(() => (S.prog.plan ? { day: S.prog.plan.day, pos: S.prog.plan.pos, ids: S.prog.plan.ids.slice(), res: { ...S.prog.plan.res } } : null));
const runOf = (d) => d.pg.evaluate(() => (S.run ? { tkey: S.run.tkey, pos: S.run.pos, len: S.run.list.length, revealed: !!(runState && runState.revealed) } : null));
const out = (o) => console.log(JSON.stringify(o));

async function day1(browser, store) {
  const o = { when: '2026-11-28T20:00:00', sortKeys: true, latency: 30, push: 10 };
  const pc = await L.device(browser, SITE, store, 'PC', { ...o, seedRandom: 7 });
  const ph = await L.device(browser, SITE, store, 'PHONE', { ...o, seedRandom: 9 });
  await pc.pg.waitForFunction(() => S.synced); await pc.pg.click(L.startBtn);
  for (let i = 0; i < 30; i++) await pc.answer(i % 5 !== 0);      // 30题里答错6题
  await pc.wait(2500);
  const y = await planOf(pc);
  return { pc, ph, y, wrong: Object.keys(y.res).filter((id) => y.res[id] === 0) };
}
async function phoneStartsDay2(ph) {
  await ph.pg.reload(); await ph.pg.waitForSelector('.today'); await ph.pg.waitForFunction(() => S.synced);
  await ph.pg.click(L.startBtn); await ph.wait(200);
  return planOf(ph);
}

(async () => {
  const browser = await L.launch();
  // ---------- A ----------
  {
    const store = L.newStore(null); const { pc, ph, y, wrong } = await day1(browser, store);
    out({ A: '第一天', pcRun: await runOf(pc), yesterdayLen: y.ids.length, pos: y.pos, wrongYesterday: wrong.length, sets: store.sets });
    await pc.setNow('2026-11-29T08:00:00'); await ph.setNow('2026-11-29T08:00:00');
    const t = await phoneStartsDay2(ph);
    out({ A: '第二天手机点开始', day: t.day, len: t.ids.length, sameAsYesterday: sameSet(t.ids, y.ids), wrongOnesInToday: wrong.filter((id) => t.ids.includes(id)).length });
    await ph.answer(true); const s0 = store.sets, h0 = store.history.length; await ph.wait(20000);
    const by = {}; for (const x of store.history.slice(h0)) by[x.by] = (by[x.by] || 0) + 1;
    const cp = L.remote(store).plan;
    out({ A: '手机停在第2题20秒', cloudWrites: store.sets - s0, by, cloudPlanIsToday: sameSet(cp.ids, t.ids), cloudPlanIsYesterday: sameSet(cp.ids, y.ids), pcRun: await runOf(pc), phoneRun: await runOf(ph) });
    for (let i = 0; i < 4; i++) { await ph.answer(true); await ph.wait(1500); }
    await ph.pg.evaluate(() => exitRun()); await ph.wait(4000);
    const pp = await planOf(ph), cp2 = L.remote(store).plan;
    out({ A: '手机做了5题后退出到今日页', panel: await panel(ph), phonePlanIsToday: sameSet(pp.ids, t.ids), phonePlanIsYesterday: sameSet(pp.ids, y.ids), phonePos: pp.pos, cloudPlanIsYesterday: sameSet(cp2.ids, y.ids), totalCloudWrites: store.sets - s0, pcErrs: pc.errs.slice(0, 2), phErrs: ph.errs.slice(0, 2) });
    const s1 = store.sets; await ph.wait(8000); out({ A: '手机不在做题页后的8秒', cloudWrites: store.sets - s1 });
    await pc.close(); await ph.close();
  }
  // ---------- B ----------
  {
    const store = L.newStore(null); const { pc, ph, y, wrong } = await day1(browser, store);
    await pc.offline();
    await pc.setNow('2026-11-29T08:00:00'); await ph.setNow('2026-11-29T08:00:00');
    const t = await phoneStartsDay2(ph);
    const done = []; for (let i = 0; i < 2; i++) { done.push(await ph.answer(true)); await ph.wait(1300); }
    await ph.pg.evaluate(() => exitRun()); await ph.wait(2500);
    const before = await panel(ph); const cp = L.remote(store).plan; const s0 = store.sets;
    out({ B: '电脑断网时手机做了2题', panel: before, cloudPlanIsToday: sameSet(cp.ids, t.ids), wrongOnesStillPending: wrong.filter((id) => t.ids.includes(id) && !done.includes(id)).length });
    await pc.online(); await ph.wait(5000);
    const cp2 = L.remote(store).plan, pp = await planOf(ph);
    out({ B: '电脑连上之后', cloudWrites: store.sets - s0, cloudPlanIsToday: sameSet(cp2.ids, t.ids), cloudPlanIsYesterday: sameSet(cp2.ids, y.ids), phonePlanIsYesterday: sameSet(pp.ids, y.ids), panel: await panel(ph), pcRun: await runOf(pc) });
    await ph.pg.click(L.contBtn); await ph.wait(300);
    const rest = await ph.pg.evaluate(() => S.run.list.slice(S.run.pos).map((q) => q.id));
    const shouldRemain = t.ids.filter((id) => !done.includes(id));
    const dropped = shouldRemain.filter((id) => !rest.includes(id));
    out({ B: '手机点“继续”', runRemaining: rest.length, todayShouldRemain: shouldRemain.length, droppedFromToday: dropped.length, droppedWrongReviews: dropped.filter((id) => wrong.includes(id)).length, notInTodaysPlan: rest.filter((id) => !t.ids.includes(id)).length });
    await pc.close(); await ph.close();
  }
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
