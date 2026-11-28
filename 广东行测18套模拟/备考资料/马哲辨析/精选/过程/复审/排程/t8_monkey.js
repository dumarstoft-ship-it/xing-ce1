// 随机操作检查：在页面上随机地开始/继续计划、分科一组、模块练、错题重练、自选、加练、改题数、跨天、刷新，每步之后检查状态是否自洽。
// 用法：node t8_monkey.js <站点> [种子] [步数]
const H = require('./harness');
(async () => {
  const site = process.argv[2] || 'v7', SEED = Number(process.argv[3] || 1), STEPS = Number(process.argv[4] || 400);
  let seed = SEED * 7919 + 13; const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const pick = (arr) => arr[Math.floor(rnd() * arr.length)];
  const d = await H.open(site, '2026-11-27T08:00:00', { seed: SEED });
  const pg = d.pg; let now = new Date('2026-11-27T08:00:00').getTime();
  const problems = []; const trace = [];
  const note = (s) => { problems.push(`[步${trace.length}] ${s}  ← 最近操作：${trace.slice(-6).join(' → ')}`); };
  const answerSome = async (k, pRight) => { let n = 0; for (let i = 0; i < k; i++) { const id = await H.answer(pg, rnd() < pRight); if (!id) break; n++; } return n; };
  const clickText = (sel) => pg.evaluate((sel) => { const [css, text] = sel; const el = [...document.querySelectorAll(css)].find((x) => x.textContent.trim().startsWith(text) && !x.disabled); if (!el) return false; el.click(); return true; }, sel);
  const inRun = () => pg.evaluate(() => !!S.run);
  const exit = async () => { if (await inRun()) await pg.evaluate(() => exitRun()); };
  const actions = {
    plan: async () => { await exit(); await pg.evaluate(() => { if (current() !== 'today') { location.hash = '#today'; } }); await pg.waitForTimeout(30);
      if (!(await clickText(['.panel.today button', '开始'])) && !(await clickText(['.panel.today button', '继续']))) return 'plan:无按钮';
      if (!(await inRun())) return 'plan:没进入';
      const k = pick([1, 3, 10, 25, 60]); const n = await answerSome(k, 0.75); return `plan:答${n}`; },
    more: async () => { await exit(); if (!(await clickText(['.panel.today button', '再加']))) return 'more:无'; const n = await answerSome(pick([3, 20]), 0.7); return `more:答${n}`; },
    group: async () => { await exit(); const bank = pick(['马哲 · 今日一组', '政常（非马哲）· 今日一组']);
      const ok = await pg.evaluate((bank) => { const p = [...document.querySelectorAll('.panel.today')].find((x) => x.querySelector('h2').textContent.startsWith(bank)); if (!p) return false; const b = [...p.querySelectorAll('button.primary')].find((x) => !x.disabled); if (!b) return false; b.click(); return true; }, bank);
      if (!ok || !(await inRun())) return 'group:无'; const n = await answerSome(pick([2, 8, 20]), 0.7); return `group(${bank.slice(0, 2)}):答${n}`; },
    module: async () => { await exit(); const ok = await pg.evaluate((r) => { const m = [...document.querySelectorAll('.mod')]; if (!m.length) return false; m[Math.floor(r * m.length)].click(); return true; }, rnd()); if (!ok || !(await inRun())) return 'module:无'; const n = await answerSome(pick([2, 6, 15]), 0.7); return `module:答${n}`; },
    redoSummary: async () => { if (!(await inRun())) return 'redoSum:不在做题'; await answerSome(100, 0.7); if (!(await clickText(['#main button', '错题再做一遍']))) return 'redoSum:无错题'; const n = await answerSome(pick([2, 30]), 0.9); return `redoSum:答${n}`; },
    redoBank: async () => { await exit(); const bank = pick(['mz', 'fm']); const ok = await pg.evaluate((bank) => { if (!wrongPool(bank).length) return false; startRedo(bank); return true; }, bank); if (!ok) return 'redoBank:无'; const n = await answerSome(pick([3, 30]), 0.85); return `redoBank(${bank}):答${n}`; },
    practiceWrong: async () => { await exit(); const ok = await pg.evaluate(() => { F.scope = 'wrong'; const pool = filtered(); F.scope = 'all'; if (!pool.length) return false; startRun(spread(shuffle(pool)).slice(0, 15), '自选练习', 'redo'); return true; }); if (!ok) return 'pracWrong:无'; const n = await answerSome(20, 0.85); return `pracWrong:答${n}`; },
    practiceTier: async () => { await exit(); await pg.evaluate((t) => { const pool = S.qs.filter((q) => !paused(q) && String(tierOf(q)) === t); startRun(pickGroup(pool, 15, { reviewCap: 15 }), '自选练习'); }, pick(['1', '2', '3'])); const n = await answerSome(pick([4, 15]), 0.7); return `pracTier:答${n}`; },
    daily: async () => { await exit(); const v = pick(['20', '30', '40', '50', '60', '80']); const ok = await pg.evaluate((v) => { const s = document.querySelector('#dailySel'); if (!s) return false; s.value = v; s.dispatchEvent(new Event('change')); return true; }, v); return ok ? `daily=${v}` : 'daily:无'; },
    exit: async () => { await exit(); return 'exit'; },
    reload: async () => { await H.reload(pg); return 'reload'; },
    hours: async () => { const hrs = pick([1, 3, 5, 9, 14]); now += hrs * 3600000; await H.setNow(pg, now); await pg.evaluate(() => { document.dispatchEvent(new Event('visibilitychange')); }); return `+${hrs}h(${new Date(now).toISOString().slice(5, 16)})`; },
    tab: async () => { const r = pick(['review', 'stats', 'cards', 'practice', 'today', 'today']); await pg.evaluate((r) => { location.hash = '#' + r; }, r); await pg.waitForTimeout(40); await pg.evaluate(() => { location.hash = '#today'; }); await pg.waitForTimeout(40); return `tab:${r}`; },
  };
  const weights = { plan: 9, more: 3, group: 3, module: 2, redoSummary: 3, redoBank: 2, practiceWrong: 1, practiceTier: 2, daily: 1, exit: 3, reload: 1, hours: 4, tab: 1 };
  const bag = Object.entries(weights).flatMap(([k, w]) => Array(w).fill(k));
  for (let step = 0; step < STEPS; step++) {
    const name = pick(bag);
    let r; try { r = await actions[name](); } catch (e) { r = name + ':异常 ' + e.message.slice(0, 80); note(r); }
    trace.push(r);
    const bad = await pg.evaluate(() => {
      const out = []; const today = dayStr(), P = S.prog.q;
      for (const [id, p] of Object.entries(P)) {
        if (!(p.n >= 1 && p.c >= 0 && p.c <= p.n && (p.l === 0 || p.l === 1) && Number.isInteger(p.b) && p.b >= 0 && p.b <= 5)) out.push(`记录异常 ${id} ${JSON.stringify(p)}`);
        else if (p.due !== addDays(p.d, p.b ? INTERVALS[p.b] : 1)) out.push(`到期日与盒子不符 ${id} ${JSON.stringify(p)}`);
        else if (!p.l && p.b) out.push(`最近答错但不在第0盒 ${id} ${JSON.stringify(p)}`);
        if (p.d > today || p.f > p.d) out.push(`日期异常 ${id} ${JSON.stringify(p)}`);
      }
      const onToday = !S.run && current() === 'today';
      for (const key of ['plan', 'today', 'today2']) {
        const t = S.prog[key]; if (!t || t.day !== today) continue;
        if (new Set(t.ids).size !== t.ids.length) out.push(`${key} 有重复题`);
        if (t.ids.some((id) => !S.q[id])) out.push(`${key} 有不存在的题`);
        if (!(t.pos >= 0 && t.pos <= t.ids.length)) out.push(`${key} pos 越界 ${t.pos}/${t.ids.length}`);
        const head = t.ids.slice(0, t.pos), tail = t.ids.slice(t.pos);
        const noRes = head.filter((id) => t.res[id] !== 0 && t.res[id] !== 1); if (noRes.length) out.push(`${key} 已做的题没有结果 ${noRes.length}`);
        const notDone = head.filter((id) => !P[id] || P[id].d !== today); if (notDone.length) out.push(`${key} 算作已做的题今天其实没答过 ${notDone.length}: ${notDone.slice(0, 3)}`);
        if (onToday) { const doneElse = tail.filter((id) => P[id] && P[id].d === today); if (doneElse.length) out.push(`${key} 没轮到的题里有今天已答过的 ${doneElse.length}`); }
        if (S.run && S.run.tkey === key) { if (S.run.list.map((q) => q.id).join() !== t.ids.join()) out.push(`${key} 做题清单与题组不一致`); if (S.run.pos !== t.pos) out.push(`${key} 做题位置${S.run.pos}≠题组位置${t.pos}`); if (S.run.res !== t.res) out.push(`${key} res 不是同一份`); }
      }
      if (onToday && hasPlan()) {
        const p = document.querySelector('.panel.today'), txt = p.innerText.replace(/\s+/g, ' '), t = S.prog.plan && S.prog.plan.day === today ? S.prog.plan : null;
        if (t && t.pos < t.ids.length && !txt.includes(`已做${t.pos}题，还剩${t.ids.length - t.pos}题`)) out.push('面板与计划进度不符：' + txt.slice(0, 40));
        if (t && t.pos >= t.ids.length && !txt.includes('今日计划：做完了')) out.push('计划做完但面板不是“做完了”：' + txt.slice(0, 40));
        if (!t) { const r = planParts(dailyOf()); if (!txt.includes(`今日计划 ${r.list.length}题`)) out.push('面板题数与 planParts 不符：' + txt.slice(0, 40));
          const nums = (txt.match(/(复习|考前回顾|核心新题|备选新题) (\d+)/g) || []).map((x) => Number(x.split(' ')[1])).reduce((a, x) => a + x, 0); if (nums !== r.list.length) out.push(`面板各项之和${nums}≠${r.list.length}`);
          if (r.list.some((q) => P[q.id] && P[q.id].d === today)) out.push('预览清单里有今天答过的题'); }
        const c1 = S.qs.filter((q) => q.t === 1 && !paused(q)); if (!txt.includes(`${c1.filter((q) => P[q.id]).length}/${c1.length} 核心已学`)) out.push('核心已学数字不符');
      }
      const dn = Object.values(P).filter((p) => p.d === today).length, dd = (S.prog.days[today] || { n: 0 }).n; if (dd < dn) out.push(`今天答题数${dd}小于今天答过的题数${dn}`);
      const doms = document.querySelectorAll('#dailySel').length; if (doms > 1) out.push('页面上有多个 dailySel');
      if (document.querySelector('#main') && /\bnull\b|undefined|NaN/.test(document.querySelector('#main').innerText)) out.push('页面文字里出现 null/undefined/NaN：' + document.querySelector('#main').innerText.match(/.{0,20}(\bnull\b|undefined|NaN).{0,10}/)[0].replace(/\s+/g, ' '));
      return out;
    });
    for (const b of bad) note(b);
    if (d.errs.length) { note('页面报错：' + d.errs.join('; ')); d.errs.length = 0; }
    if (problems.length >= 12) break;
  }
  console.log(`${site} 种子${SEED}：${trace.length}步，结束于 ${new Date(now).toISOString().slice(0, 16)}`);
  console.log(problems.length ? problems.join('\n') : '没有发现问题');
  if (process.env.TRACE) console.log(trace.join(' → '));
  await H.close();
})();
