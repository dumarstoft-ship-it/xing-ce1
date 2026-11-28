// planParts 的不变量随机检查：用页面自己的 record() 造多天的记录（含别处做题、当天重做、漏做），每天开始时对多种题数、skip 检查。
// 用法：node t1_fuzz.js <站点> [轮数]
const H = require('./harness');
(async () => {
  const site = process.argv[2] || 'realdraft', ROUNDS = Number(process.argv[3] || 30);
  const d = await H.open(site, '2026-11-20T09:00:00');
  const res = await d.pg.evaluate((ROUNDS) => {
    const Real = Object.getPrototypeOf(Date);            // 真 Date
    const setDay = (day) => { window.__off = new Real(day + 'T09:00:00').getTime() - Real.now(); };
    let seed = 99; const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
    const pickN = (arr, n) => { const a = arr.slice(); const out = []; while (a.length && out.length < n) out.push(a.splice(Math.floor(rnd() * a.length), 1)[0]); return out; };
    const problems = []; const stats = { checks: 0, short: 0, relaxed: 0, maxWrong: 0 };
    const note = (s) => { if (problems.length < 60) problems.push(s); };
    function checkPlan(size, skip, tag) {
      const today = dayStr(), P = S.prog.q, left = daysLeft(), fin = finalDays();
      const r = planParts(size, skip); stats.checks++;
      const ids = r.list.map((q) => q.id);
      const sum = Object.values(r.n).reduce((a, x) => a + x, 0);
      if (sum !== ids.length) note(`${tag} 各类之和${sum}≠清单${ids.length}`);
      if (new Set(ids).size !== ids.length) note(`${tag} 清单有重复题`);
      if (ids.length > size) note(`${tag} 清单超过题数 ${ids.length}>${size}`);
      for (const q of r.list) {
        const p = P[q.id];
        if (paused(q)) note(`${tag} 清单里有待审题 ${q.id}`);
        if (skip && skip.has(q.id)) note(`${tag} 清单里有 skip 的题 ${q.id}`);
        if (p && p.d === today) note(`${tag} 清单里有今天已答过的题 ${q.id} ${JSON.stringify(p)}`);
        if (!inPlan(q) && !(p && !p.b && p.due <= today)) note(`${tag} 计划外的题不是“第0盒到期” ${q.id} ${JSON.stringify(p)}`);
        if (!p && left === 0) note(`${tag} 考试当天出了新题 ${q.id}`);
      }
      // ①必须排在最前，且到期的第0盒要么全进、要么清单已满
      const all = S.qs.filter((q) => !paused(q) && !(skip && skip.has(q.id)));
      const w = all.filter((q) => P[q.id] && !P[q.id].b && P[q.id].due <= today);
      stats.maxWrong = Math.max(stats.maxWrong, w.length);
      const head = ids.slice(0, r.n.wrong), wset = new Set(w.map((q) => q.id));
      if (!head.every((id) => wset.has(id))) note(`${tag} 清单开头的${r.n.wrong}题不全是①`);
      if (r.n.wrong !== Math.min(w.length, size)) note(`${tag} ①数量${r.n.wrong}，应为${Math.min(w.length, size)}`);
      // 不满时：不应还有该出的题
      const inList = new Set(ids);
      if (ids.length < size) {
        stats.short++;
        const dueLeft = all.filter((q) => P[q.id] && P[q.id].due <= today && (inPlan(q) || !P[q.id].b) && !inList.has(q.id));
        const freshCore = all.filter((q) => q.t === 1 && !P[q.id] && !inList.has(q.id));
        const freshBack = all.filter((q) => q.t === 2 && !P[q.id] && !inList.has(q.id));
        const old = all.filter((q) => inPlan(q) && P[q.id] && P[q.id].d < today && !inList.has(q.id));
        if (dueLeft.length) note(`${tag} 清单不满(${ids.length}/${size})但还有到期的 ${dueLeft.length}`);
        if (freshCore.length && left !== 0) note(`${tag} 清单不满(${ids.length}/${size})但还有核心新题 ${freshCore.length}`);
        if (old.length) note(`${tag} 清单不满(${ids.length}/${size})但还有没见的旧题 ${old.length}`);
        if (freshBack.length && left !== 0) { stats.backBlocked = (stats.backBlocked || 0) + 1; stats.backBlockedEx = `${tag} 不满(${ids.length}/${size})，备选新题还有${freshBack.length}道没出（同知识点限制）`; }
      }
      // 新题：同一知识点一天一道（核心可放宽）；备选新题不能和今天学过的新题同知识点
      const cardsToday = new Set(); for (const q of S.qs) if (P[q.id] && P[q.id].f === today) q.cards.forEach((c) => cardsToday.add(c));
      const seenCards = new Set(cardsToday); let dupCore = 0;
      for (const q of r.list) { if (P[q.id]) continue; const dup = q.cards.some((c) => seenCards.has(c)); if (dup && q.t === 2) note(`${tag} 备选新题与今天的新题同知识点 ${q.id}`); if (dup && q.t === 1) dupCore++; q.cards.forEach((c) => seenCards.add(c)); }
      if (dupCore) stats.relaxed++;
      // 核心新题在备选新题之前；新题块内按 o 升序
      const newIdx = r.list.map((q, i) => (!P[q.id] ? [i, q.t, q.o] : null)).filter(Boolean);
      const last1 = Math.max(-1, ...newIdx.filter((x) => x[1] === 1).map((x) => x[0])), first2 = Math.min(1e9, ...newIdx.filter((x) => x[1] === 2).map((x) => x[0]));
      if (first2 < last1) note(`${tag} 备选新题排到了核心新题前面`);
      // 备选新题出现时，核心新题必须已经全部进清单
      if (r.n.new2 > 0) { const rest = all.filter((q) => q.t === 1 && !P[q.id] && !inList.has(q.id)); if (rest.length) note(`${tag} 还有${rest.length}道核心新题没进清单就出了备选新题`); }
      return r;
    }
    for (let round = 0; round < ROUNDS; round++) {
      S.prog = blankProg(); S.run = null;
      const acc = 0.5 + rnd() * 0.45, doFrac = 0.3 + rnd() * 0.7, size = [20, 30, 50, 60, 80][Math.floor(rnd() * 5)];
      S.prog.settings.daily = size;
      const startOff = Math.floor(rnd() * 6);            // 11-20 之后几天开始用
      for (let k = startOff; k <= 18; k++) {             // 到 12-08
        const day = addDays('2026-11-20', k); setDay(day);
        const tag = `[轮${round} ${day} 每天${size}]`;
        // 先在别处做几道（模块练、自选）
        if (rnd() < 0.5) for (const q of pickN(S.qs.filter((q) => !paused(q)), Math.floor(rnd() * 12))) record(q, rnd() < acc);
        for (const sz of [20, 50, 80, size]) checkPlan(sz, null, tag + ` 题数${sz}`);
        const r = planParts(size);
        const nDo = rnd() < 0.15 ? 0 : Math.ceil(r.list.length * (rnd() < 0.5 ? 1 : doFrac));
        const done = r.list.slice(0, nDo); const wrong = [];
        for (const q of done) { const ok = rnd() < (S.prog.q[q.id] ? Math.min(0.97, acc + 0.15) : acc); record(q, ok); if (!ok) wrong.push(q); }
        if (rnd() < 0.6) for (const q of wrong) record(q, rnd() < 0.9);            // 当天重做
        if (rnd() < 0.3) for (const q of pickN(done, 5)) { record(q, rnd() < 0.9); if (rnd() < 0.5) setExplain(q, rnd() < 0.5); }
        // “再加20题”连点几次
        if (nDo === r.list.length && nDo > 0) {
          const skip = new Set(r.list.map((q) => q.id));
          for (let j = 0; j < 3; j++) {
            const m = checkPlan(20, skip, tag + ` 加练${j + 1}`);
            if (daysLeft() === 0) break;
            if (rnd() < 0.5) break;
            for (const q of m.list) { if (skip.has(q.id)) note(tag + ' 加练出了计划里的题'); record(q, rnd() < acc); }
          }
        }
      }
    }
    return { problems, stats };
  }, ROUNDS);
  console.log(site, JSON.stringify(res.stats));
  console.log(res.problems.length ? res.problems.join('\n') : '没有发现违反不变量的情况');
  console.log('pageerrors:', d.errs.length ? d.errs.join('; ') : 'none');
  await H.close();
})();
