// settle 的几种情形：计划做到一半去别处做了后面的题（对、错、错后重做对）；全部在别处做完；题库少题；反复重画是否反复写记录。
const H = require('./harness');
(async () => {
  const site = process.argv[2] || 'v7';
  const check = H.mkCheck();
  const startBtn = '.panel.today >> button:text-is("开始") >> nth=0';
  const wrapTouch = (pg) => pg.evaluate(() => { window.__touches = 0; const orig = window.touch; window.touch = function () { window.__touches++; return orig.apply(this, arguments); }; });
  const touches = (pg) => pg.evaluate(() => window.__touches);

  console.log('S1 计划做到一半，别处做了后面的题');
  { const d = await H.open(site, '2026-11-28T09:00:00');
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    for (let i = 0; i < 10; i++) await H.answer(d.pg, i % 5 !== 0);      // 10题里错2题
    await d.pg.evaluate(() => exitRun());
    const before = await d.pg.evaluate(() => ({ ids: S.prog.plan.ids.slice(), pos: S.prog.plan.pos, res: { ...S.prog.plan.res } }));
    // 别处：计划里第13、17、22题（下标12、16、21），分别答对、答错、答错后重做答对
    const picks = [before.ids[12], before.ids[16], before.ids[21]];
    await d.pg.evaluate((ids) => { startRun(ids.map((id) => S.q[id]), '自选练习'); }, picks);
    await H.answer(d.pg, true); await H.answer(d.pg, false); await H.answer(d.pg, false);
    await d.pg.evaluate((id) => { startRun([S.q[id]], '本组错题再做一遍', 'redo'); }, picks[2]);
    await H.answer(d.pg, true);
    await wrapTouch(d.pg);
    await d.pg.evaluate(() => exitRun());
    const t1 = await touches(d.pg);
    const st = await d.pg.evaluate(() => ({ ids: S.prog.plan.ids.slice(), pos: S.prog.plan.pos, res: { ...S.prog.plan.res }, text: document.querySelector('.panel.today .sub').textContent }));
    check('面板：已做13题，还剩37题', st.text.includes('已做13题，还剩37题'), st.text.slice(0, 30));
    check('清单仍50题、无重复，前10题不变，随后是别处做过的3题', st.ids.length === 50 && new Set(st.ids).size === 50 && st.ids.slice(0, 10).join() === before.ids.slice(0, 10).join() && st.ids.slice(10, 13).join() === picks.join(), st.ids.slice(8, 14).join());
    check('别处的结果记进了计划：对、错、最后一次答对', st.res[picks[0]] === 1 && st.res[picks[1]] === 0 && st.res[picks[2]] === 1, JSON.stringify(picks.map((id) => st.res[id])));
    check('回到今日页只写了一次记录（settle）', t1 === 1, 'touch 次数=' + t1);
    for (let i = 0; i < 5; i++) await d.pg.evaluate(() => route(true));
    check('再重画5次不再写记录', (await touches(d.pg)) === t1, 'touch 次数=' + (await touches(d.pg)));
    const rec = await d.pg.evaluate((ids) => ids.map((id) => S.prog.q[id]), picks);
    console.log('    三题的记录：', JSON.stringify(rec));
    await d.pg.click('.panel.today >> button:text-is("继续")'); await d.pg.waitForSelector('#qcard');
    const cur = await d.pg.evaluate(() => ({ pos: S.run.pos, len: S.run.list.length, cur: S.run.list[S.run.pos].id, posText: document.querySelector('.runbar .pos').textContent }));
    check('继续：从第14题开始，第14题是原来的第11题', cur.pos === 13 && cur.len === 50 && cur.cur === before.ids[10] && cur.posText === '14/50', JSON.stringify(cur));
    const seen = []; for (;;) { const id = await H.answer(d.pg, true); if (!id) break; seen.push(id); }
    check('剩下37题各出一次，没有再出别处做过的3题', seen.length === 37 && new Set(seen).size === 37 && !seen.some((id) => picks.includes(id)), 'n=' + seen.length);
    const sum = await d.pg.evaluate(() => ({ h2: document.querySelector('#main h2').textContent, wrongList: document.querySelectorAll('#main .wrongq').length, redo: (document.querySelector('#main button.primary') || {}).textContent }));
    console.log('    小结：', JSON.stringify(sum));
    check('小结：答对47/50（前10题错2，别处错1；重做答对那题按最后一次算对）', sum.h2.includes('答对47/50') && sum.wrongList === 3, sum.h2);
    await d.pg.evaluate(() => exitRun());
    const done = await d.pg.textContent('.panel.today .sub');
    check('做完面板：50题，答对47题', done.includes('50题，答对47题'), done.slice(0, 30));
    // 第二天：那道“错后重做答对”的题在①里吗
    await H.setNow(d.pg, '2026-11-29T09:00:00'); await H.reload(d.pg);
    const d2 = await d.pg.evaluate((picks) => { const p = planParts(dailyOf()); const head = p.list.slice(0, p.n.wrong).map((q) => q.id); return { n: p.n, in1: picks.map((id) => head.includes(id)) }; }, picks);
    check('第二天①：别处答错的、错后当天重做对的都在，答对的不在', d2.in1.join() === 'false,true,true' && d2.n.wrong === 4, JSON.stringify(d2));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('S2 计划剩下的题全部在别处做完');
  { const d = await H.open(site, '2026-11-28T09:00:00');
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    for (let i = 0; i < 45; i++) await H.answer(d.pg, true);
    await d.pg.evaluate(() => exitRun());
    const rest = await d.pg.evaluate(() => S.prog.plan.ids.slice(S.prog.plan.pos));
    await d.pg.evaluate((ids) => { startRun(ids.map((id) => S.q[id]), '自选练习'); }, rest);
    for (let i = 0; i < 5; i++) await H.answer(d.pg, i !== 0);
    await d.pg.evaluate(() => exitRun());
    const t = await d.pg.textContent('.panel.today');
    check('面板变成“做完了”，50题答对49题，有“再加”按钮', t.includes('今日计划：做完了') && t.includes('50题，答对49题') && /再加\d+题/.test(t), t.slice(0, 60));
    const more = await d.pg.evaluate(() => { const m = planParts(20, new Set(S.prog.plan.ids)); return { n: m.n, len: m.list.length, anyToday: m.list.filter((q) => S.prog.q[q.id] && S.prog.q[q.id].d === dayStr()).length }; });
    check('再加20题：20道，都不是今天做过的', more.len === 20 && more.anyToday === 0, JSON.stringify(more));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('S3 题库里少了题（计划、今日一组里有已经不存在的题号）');
  { const d0 = await H.open(site, '2026-11-28T09:00:00');
    await d0.pg.click(startBtn); await d0.pg.waitForSelector('#qcard');
    for (let i = 0; i < 6; i++) await H.answer(d0.pg, i !== 2);
    await d0.pg.evaluate(() => exitRun());
    const local = await d0.pg.evaluate(() => { const p = JSON.parse(JSON.stringify(S.prog)); const pl = p.plan;
      // 把已做的第3题（答错的那道）和没做的第20题换成不存在的题号
      const goneHead = pl.ids[2], goneTail = pl.ids[19]; pl.ids[2] = 'GONE-A'; pl.res['GONE-A'] = pl.res[goneHead]; delete pl.res[goneHead]; p.q['GONE-A'] = p.q[goneHead]; delete p.q[goneHead]; pl.ids[19] = 'GONE-B';
      p.today = { day: '2026-11-28', ids: ['GONE-C', ...S.qs.filter((q) => q.bank !== 'fm' && !p.q[q.id]).slice(0, 4).map((q) => q.id)], pos: 1, res: { 'GONE-C': 1 } };
      return JSON.stringify(p); });
    await d0.ctx.close();
    const d = await H.open(site, '2026-11-28T10:00:00', { local });
    const st = await d.pg.evaluate(() => ({ plan: { len: S.prog.plan.ids.length, pos: S.prog.plan.pos, hasGone: S.prog.plan.ids.some((id) => !S.q[id]) }, today: { len: S.prog.today.ids.length, pos: S.prog.today.pos }, text: document.querySelector('.panel.today .sub').textContent }));
    check('计划去掉不存在的两题：48题、已做5题', st.plan.len === 48 && st.plan.pos === 5 && !st.plan.hasGone && st.text.includes('已做5题，还剩43题'), JSON.stringify(st));
    check('分科今日一组也去掉了：4题、已做0题', st.today.len === 4 && st.today.pos === 0, JSON.stringify(st.today));
    await d.pg.click('.panel.today >> button:text-is("继续")'); await d.pg.waitForSelector('#qcard');
    const seen = []; for (;;) { const id = await H.answer(d.pg, true); if (!id) break; seen.push(id); }
    check('继续做完43题', seen.length === 43, 'n=' + seen.length);
    const h2 = await d.pg.textContent('#main h2');
    await d.pg.evaluate(() => exitRun());
    const done = await d.pg.textContent('.panel.today .sub');
    console.log('    小结标题：', h2, '｜做完面板：', done.slice(0, 24));
    const cnt = await d.pg.evaluate(() => ({ right: Object.values(S.prog.plan.res).filter(Boolean).length, len: S.prog.plan.ids.length, resKeys: Object.keys(S.prog.plan.res).length }));
    check('做完面板的“答对”不超过题数、与小结一致', cnt.right <= cnt.len && h2.includes(`答对${cnt.right}/${cnt.len}`), JSON.stringify(cnt) + ' ' + h2);
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('S4 做完计划后去分科一组；分科一组做到一半去做计划');
  { const d = await H.open(site, '2026-11-28T09:00:00');
    // 先开分科马哲一组，做5题
    await d.pg.locator('details.more', { hasText: '分科加练' }).locator('summary').click();
    await d.pg.click('.panel.today:has-text("马哲 · 今日一组") >> button:text-is("开始")'); await d.pg.waitForSelector('#qcard');
    for (let i = 0; i < 5; i++) await H.answer(d.pg, true);
    await d.pg.evaluate(() => exitRun());
    const g = await d.pg.evaluate(() => ({ ids: S.prog.today.ids.slice(), pos: S.prog.today.pos, tiers: S.prog.today.ids.map((id) => S.q[id].t || 3) }));
    console.log('    马哲一组15题的档位：', g.tiers.join(''));
    const prev = await d.pg.evaluate((gids) => { const p = planParts(dailyOf()); const ids = p.list.map((q) => q.id); return { n: p.n, overlapDone: gids.slice(0, 5).filter((id) => ids.includes(id)).length, overlapRest: gids.slice(5).filter((id) => ids.includes(id)).length }; }, g.ids);
    check('计划预览不含今天已做的5题', prev.overlapDone === 0, JSON.stringify(prev));
    console.log('    计划与马哲一组剩下10题重合：', prev.overlapRest);
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    const planIds = await d.pg.evaluate(() => S.prog.plan.ids.slice());
    for (;;) { const id = await H.answer(d.pg, true); if (!id) break; }
    await d.pg.evaluate(() => exitRun());
    const g2 = await d.pg.evaluate(() => ({ pos: S.prog.today.pos, len: S.prog.today.ids.length, text: [...document.querySelectorAll('.panel.today')].map((x) => x.querySelector('h2').textContent + '｜' + (x.querySelector('.sub') || x.querySelector('.big') || {}).textContent).join(' ## ') }));
    const expectDone = 5 + g.ids.slice(5).filter((id) => planIds.includes(id)).length;
    check('回到分科：马哲一组里在计划中做过的题算已做', g2.pos === expectDone && g2.len === 15, JSON.stringify({ pos: g2.pos, expectDone }) );
    console.log('    ', g2.text);
    // 做完计划后开政常一组：不应含今天做过的题
    await d.pg.evaluate(() => { OPEN.extra = true; route(true); });
    await d.pg.click('.panel.today:has-text("政常（非马哲）· 今日一组") >> button:text-is("开始")'); await d.pg.waitForSelector('#qcard');
    const fm = await d.pg.evaluate(() => ({ ids: S.prog.today2.ids.length, pos: S.prog.today2.pos, doneToday: S.prog.today2.ids.filter((id) => S.prog.q[id] && S.prog.q[id].d === dayStr()).length }));
    check('做完计划后新开的政常一组：15题、不含今天做过的题', fm.ids === 15 && fm.pos === 0 && fm.doneToday === 0, JSON.stringify(fm));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log(check.fails.length ? `\n有 ${check.fails.length} 项没过：${check.fails.join('；')}` : '\n全部通过');
  await H.close(); process.exit(check.fails.length ? 1 : 0);
})();
