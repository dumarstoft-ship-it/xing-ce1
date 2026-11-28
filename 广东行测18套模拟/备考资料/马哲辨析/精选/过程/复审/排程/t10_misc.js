// 杂项：考前两天/考试当天/考试之后的顺序；老记录（缺 b、due，b 很大）；数据不配套（题目有精选标记、meta 没有 plan）；跨零点。
const H = require('./harness');
(async () => {
  const site = process.argv[2] || 'realdraft';
  const check = H.mkCheck();
  const startBtn = '.panel.today >> button:text-is("开始") >> nth=0';
  // 造一份记录：核心前 100 道在不同日期学过，各种盒子
  const mk = async () => {
    const d = await H.open(site, '2026-11-28T09:00:00');
    const local = await d.pg.evaluate(() => {
      const core = S.qs.filter((q) => q.t === 1).sort((a, b) => a.o - b.o), back = S.qs.filter((q) => q.t === 2).sort((a, b) => a.o - b.o), out = S.qs.filter((q) => !q.t && !paused(q));
      const p = blankProg(); const Q = p.q;
      const rec = (q, o) => { Q[q.id] = { n: 1, c: 1, l: 1, b: 1, f: '2026-11-28', d: '2026-11-28', due: '2026-11-30', f1: 1, ...o }; };
      core.slice(0, 10).forEach((q) => rec(q, { n: 2, c: 0, l: 0, b: 0, d: '2026-12-03', due: '2026-12-04', f1: 0 }));                       // 答错待过关
      core.slice(10, 20).forEach((q) => rec(q, { n: 2, c: 1, l: 1, b: 1, d: '2026-12-02', due: '2026-12-04', f1: 0, x: 1 }));              // 错过、只隔天答对一次、到期
      core.slice(20, 40).forEach((q) => rec(q, { n: 1, c: 1, l: 1, b: 1, d: '2026-12-02', due: '2026-12-04' }));                              // 只答对一次、到期
      core.slice(40, 50).forEach((q) => rec(q, { n: 3, c: 2, l: 1, b: 2, d: '2026-12-01', due: '2026-12-05', f1: 0, x: 1 }));              // 错过、没到期、两天没见
      core.slice(50, 60).forEach((q) => rec(q, { n: 2, c: 2, l: 1, b: 2, d: '2026-11-30', due: '2026-12-04', x: 1 }));                        // 答对两次、到期
      core.slice(60, 70).forEach((q) => rec(q, { n: 2, c: 2, l: 1, b: 2, d: '2026-12-01', due: '2026-12-05', x: 1, e: 0 }));                  // 讲不清、没到期
      core.slice(70, 100).forEach((q) => rec(q, { n: 2, c: 2, l: 1, b: 2, d: '2026-12-02', due: '2026-12-06', x: 1 }));                       // 没到期
      back.slice(0, 6).forEach((q) => rec(q, { n: 1, c: 1, l: 1, b: 1, d: '2026-12-02', due: '2026-12-04' }));                                // 备选到期
      back.slice(6, 9).forEach((q) => rec(q, { n: 1, c: 0, l: 0, b: 0, d: '2026-12-03', due: '2026-12-04', f1: 0 }));                         // 备选答错
      out.slice(0, 4).forEach((q) => rec(q, { n: 1, c: 0, l: 0, b: 0, d: '2026-12-02', due: '2026-12-03', f1: 0 }));                          // 计划外答错
      out.slice(4, 8).forEach((q) => rec(q, { n: 1, c: 1, l: 1, b: 1, d: '2026-12-01', due: '2026-12-03' }));                                 // 计划外答对到期：不该进计划
      p.updated = '2026-12-03T12:00:00.000Z';
      return JSON.stringify(p);
    });
    await d.ctx.close(); return local;
  };
  const local = await mk();
  const classify = (pg, size, skip) => pg.evaluate(({ size, skip }) => {
    const P = S.prog.q, today = dayStr(), cut = addDays(today, -1);
    const r = planParts(size, skip ? new Set(skip) : undefined);
    const kind = (q) => { const p = P[q.id]; if (!p) return q.t === 1 ? 'N1' : 'N2'; const due = p.due <= today; const missed = p.c < p.n;
      if (!p.b && due) return q.t ? 'W' : 'Wout'; if (q.t === 1 && p.b === 1 && due) return missed ? 'F!' : 'F'; if (q.t === 1 && p.b >= 2 && due) return 'L'; if (q.t === 2 && due) return 'L2';
      if (q.t === 1 && p.d < cut && (missed || p.e === 0)) return 'K'; return q.t === 1 ? 'X' : 'X2'; };
    const seq = r.list.map(kind); const runs = []; for (const k of seq) { if (runs.length && runs[runs.length - 1][0] === k) runs[runs.length - 1][1]++; else runs.push([k, 1]); }
    return { n: r.n, len: r.list.length, runs: runs.map((x) => x.join('×')).join(' '), text: document.querySelector('.panel.today').innerText.replace(/\s+/g, ' ').replace(/20题 30题 40题 50题 60题 80题 /, '').slice(0, 230) };
  }, { size, skip: skip || null });

  for (const [day, label] of [['2026-12-03', '平日（12-03）'], ['2026-12-04', '考前两天（12-04）'], ['2026-12-05', '考前一天（12-05）'], ['2026-12-06', '考试当天'], ['2026-12-07', '考试之后']]) {
    const d = await H.open(site, day + 'T08:00:00', { local });
    for (const size of [50, 80]) { const c = await classify(d.pg, size); console.log(`${label} 每天${size}：`, JSON.stringify(c.n).replace(/"/g, ''), '\n     顺序：', c.runs); if (size === 50) console.log('     面板：', c.text); }
    if (day === '2026-12-06') {
      const btn = await d.pg.$(startBtn); check('考试当天“开始”可点', btn && !(await btn.isDisabled()));
      await btn.click(); await d.pg.waitForSelector('#qcard'); for (;;) { const id = await H.answer(d.pg, true); if (!id) break; } await d.pg.evaluate(() => exitRun());
      const t = await d.pg.textContent('.panel.today'); check('考试当天做完后没有“再加”，有说明', !/再加\d+题/.test(t) && t.includes('今天不再加题'), t.slice(0, 80));
      check('考试当天倒计时文字', (await d.pg.textContent('#countdown')).includes('今天省考'));
    }
    if (day === '2026-12-07') { check('考试之后倒计时文字', (await d.pg.textContent('#countdown')).includes('省考已结束')); const t = await d.pg.textContent('.panel.today'); check('考试之后面板没有估算文字、没有考前说明', !t.includes('核心还有') && !t.includes('考前两天') && !t.includes('今天考试'), t.slice(-60)); }
    check(`${label} 无报错`, d.errs.length === 0, d.errs.join('; ')); await d.ctx.close();
  }

  console.log('老记录：缺 b、缺 due、b 很大');
  { const d = await H.open(site, '2026-11-28T09:00:00', { local: await (async () => { const p = JSON.parse(local); return p; })() });
    const r = await d.pg.evaluate(() => {
      const core = S.qs.filter((q) => q.t === 1).sort((a, b) => a.o - b.o);
      const [a, b2, c, e] = core.slice(110, 114);
      S.prog.q = {}; S.prog.plan = null;
      S.prog.q[a.id] = { n: 1, c: 1, l: 1, f: '2026-11-20', d: '2026-11-20' };                          // 没有 b、due
      S.prog.q[b2.id] = { n: 1, c: 0, l: 0, f: '2026-11-20', d: '2026-11-20' };                         // 没有 b、due，上次答错
      S.prog.q[c.id] = { n: 6, c: 6, l: 1, b: 5, f: '2026-11-20', d: '2026-11-20', due: '2026-12-20', f1: 1 };   // b 很大（旧规则当天连对几次）
      S.prog.q[e.id] = { n: 9, c: 9, l: 1, b: 9, f: '2026-11-20', d: '2026-11-20', due: '2026-11-25', f1: 1 };   // b 超出范围
      const before = planParts(50); const where = (q) => before.list.findIndex((x) => x.id === q.id);
      const pos = { noB_right: where(a), noB_wrong: where(b2), b5: where(c), b9: where(e), n: before.n };
      record(a, true); record(b2, true); record(c, true); record(e, true);
      return { pos, after: [a, b2, c, e].map((q) => S.prog.q[q.id]) };
    });
    console.log('   ', JSON.stringify(r.pos)); console.log('    作答后：', JSON.stringify(r.after));
    for (const h of ['today', 'review', 'cards', 'stats', 'practice']) { await d.pg.evaluate((h) => { location.hash = '#' + h; }, h); await d.pg.waitForTimeout(150); }
    check('老记录下各页无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('数据不配套：questions.json 带精选标记，meta.json 的 plan 是 null（比如只有一个文件走了旧缓存）');
  { let err = '';
    try { const d = await H.open(site, '2026-11-28T09:00:00', { patchJson: { 'meta.json': (s) => { const m = JSON.parse(s); m.plan = null; return JSON.stringify(m); } }, waitFor: '#main' });
      await d.pg.waitForTimeout(600);
      const st = await d.pg.evaluate(() => ({ main: document.querySelector('#main').innerText.slice(0, 40), hasPlan: hasPlan() }));
      console.log('   ', JSON.stringify(st), '| 报错：', d.errs.join('; '));
      check('页面能正常显示今日页', !st.main.includes('正在载入') && d.errs.length === 0, st.main);
      await d.ctx.close(); } catch (e) { err = e.message; console.log('    打开失败：', err.slice(0, 200)); } }

  console.log('跨零点：做题中过了零点；分科一组的“继续”');
  { const d = await H.open(site, '2026-11-28T23:40:00');
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    const w = []; for (let i = 0; i < 10; i++) { const id = await H.answer(d.pg, i >= 3); if (i < 3) w.push(id); }
    await H.setNow(d.pg, '2026-11-29T00:05:00');
    const after = []; for (let i = 0; i < 5; i++) after.push(await H.answer(d.pg, i !== 0));
    // 零点后把零点前答错的3题“再做一遍”
    await d.pg.evaluate((ids) => { startRun(ids.map((id) => S.q[id]), '本组错题再做一遍', 'redo'); }, w);
    for (let i = 0; i < 3; i++) await H.answer(d.pg, true);
    const rec = await d.pg.evaluate((ids) => ids.map((id) => S.prog.q[id]), w);
    console.log('    零点前答错、零点后几分钟重做答对：', JSON.stringify(rec[0]));
    await d.pg.evaluate(() => exitRun());
    const t = await d.pg.textContent('.panel.today');
    const st = await d.pg.evaluate((after) => { const r = planParts(dailyOf()); const ids = new Set(r.list.map((q) => q.id)); return { n: r.n, afterIn: after.filter((id) => ids.has(id)).length, days: S.prog.days, planDay: S.prog.plan.day, planPos: S.prog.plan.pos }; }, after);
    console.log('    退出后面板：', t.replace(/\s+/g, ' ').slice(0, 60), JSON.stringify(st));
    check('零点后退出：显示新一天的计划，零点后做的题不再排进去', t.includes('开始') && st.afterIn === 0, JSON.stringify(st));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log(check.fails.length ? `\n有 ${check.fails.length} 项没过：${check.fails.join('；')}` : '\n全部通过');
  await H.close();
})();
