// 路线2：偷懒用户。A：两天只做20题、一天没做、一天做完又点两次“再加20题”；B、C：缺一两天后照常做，对照“还差X道”的估算。
const L = require('./lib'); const V = process.env.VARIANT || 'A';
const PLAN = {
  A: { '2026-11-28': 'full', '2026-11-29': 20, '2026-11-30': 'skip', '2026-12-01': 20, '2026-12-02': 'full+2', '2026-12-03': 'full', '2026-12-04': 'full', '2026-12-05': 20, '2026-12-06': 10, '2026-12-07': 'full' },
  B: { '2026-11-28': 'full', '2026-11-29': 'full', '2026-11-30': 'skip', '2026-12-01': 'skip', '2026-12-02': 'full', '2026-12-03': 'full', '2026-12-04': 'full' },
  C: { '2026-11-28': 'full', '2026-11-29': 'full', '2026-11-30': 'skip', '2026-12-01': 'full', '2026-12-02': 'full', '2026-12-03': 'full', '2026-12-04': 'full' },
}[V];
(async () => {
  const b = await L.launch(); const d = await L.device(b, { when: '2026-11-28T08:30:00', name: 'phone' }); const pg = d.pg; const problems = [], est = [];
  const info = async (state) => { const i = await L.todayInfo(pg); for (const c of i.chk) problems.push(`${i.day} ${state}: ${c}`); est.push({ day: i.day, state, coreFresh: i.coreFresh, short: i.short }); return i; };
  for (const [day, what] of Object.entries(PLAN)) {
    if (what === 'skip') { console.log(`\n== ${day} 这天没打开`); continue; }
    await L.setNow(pg, day + 'T08:30:00'); await L.reload(pg);
    const pre = await info('未开始'), pv = await L.preview(pg);
    console.log(`\n== ${day}（${pre.countdown}）这天：${what}`); console.log('  未开始:', pre.text); console.log('  三格:', pre.stats);
    console.log('  构成', JSON.stringify(pv.n), '共', pv.len, JSON.stringify(pv.by), `| 答错待过关${pre.wrongOpen} 第一次复习到期${pre.once1Due}`);
    await L.planBtn(pg, '开始').click(); await pg.waitForSelector('#qcard');
    if (typeof what === 'number') { await L.fastN(pg, what, 4); await pg.click('button:text-is("退出")'); await pg.waitForSelector('.today'); const mid = await info(`做了${what}题停下`); console.log('  停下:', mid.text); console.log('  三格:', mid.stats); continue; }
    await L.fastN(pg, null, 4);
    const redo = pg.locator('button:has-text("错题再做一遍")'); if (await redo.count()) { await redo.click(); await pg.waitForSelector('#qcard'); await L.fastN(pg, null, 0); }
    await pg.click('button:text-is("回到今日")'); await pg.waitForSelector('.today');
    const post = await info('做完'); console.log('  做完:', post.text); console.log('  三格:', post.stats);
    if (what === 'full+2') for (const k of [1, 2]) {
      const more = await pg.evaluate(() => { const m = planParts(20, new Set(S.prog.plan.ids)); return { n: m.n, len: m.list.length }; });
      const btn = pg.locator('.panel.today').first().locator('button.primary'); const lbl = await btn.textContent(); await btn.click(); await pg.waitForSelector('#qcard');
      const run = await pg.evaluate(() => ({ len: S.run.list.length, label: S.run.label, pos: document.querySelector('.runbar .pos').textContent })); await L.fastN(pg, null, 5); const sum = await L.mainText(pg, 110);
      await pg.click('button:text-is("回到今日")'); await pg.waitForSelector('.today'); const p2 = await info('加练' + k);
      console.log(`  加练${k}: 按钮“${lbl}” 实际${run.len}题（${run.label} ${run.pos}） 构成${JSON.stringify(more.n)} | 小结: ${sum}`); console.log('    之后:', p2.text); console.log('    三格:', p2.stats);
    }
  }
  console.log('\n估算对照（面板上“还差X道”，没有这句记0，核心学完后为null）：');
  for (const e of est) if (e.day <= '2026-12-03') console.log(`  ${e.day} ${e.state}: 核心没学${e.coreFresh} 面板估算到12-03还差${e.short}`);
  const last = est.filter((e) => e.day === '2026-12-03').pop(); console.log('  12-03 当天最后实际还没学的核心：', last && last.coreFresh);
  console.log('页面报错：', d.errs.length ? d.errs.join(' ; ') : '无'); console.log('发现的问题：', problems.length ? '\n  ' + [...new Set(problems)].slice(0, 30).join('\n  ') : '无');
  await b.close();
})().catch((e) => { console.error('脚本出错', e); process.exit(1); });
