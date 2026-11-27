// 每日计划改动的检查（当天重做、别处做过的题、再加20题、跨零点、考前与考试当天、折叠面板、溢出）。
// 用法：node v7_plan_test.js <站点目录>
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const SITE = process.argv[2];
const fails = [];
const check = (label, cond, detail) => { console.log((cond ? '  ✓ ' : '  ✗ ') + label + (detail ? '  ' + detail : '')); if (!cond) fails.push(label); };
(async () => {
  const b = await chromium.launch();
  async function open(when, local) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    await ctx.route('http://mz.local/**', (route) => {
      const u = new URL(route.request().url());
      const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
      if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
      return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
    });
    const pg = await ctx.newPage(); const errs = [];
    pg.on('pageerror', (e) => errs.push(e.message));
    await pg.addInitScript(({ t, local }) => {
      const Real = Date; const saved = sessionStorage.getItem('__now');   // 刷新后沿用上次设定的“现在”
      window.__off = (saved ? Number(saved) : t) - Real.now(); window.__setNow = (ms) => { sessionStorage.setItem('__now', String(ms)); window.__off = ms - Real.now(); };
      class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + window.__off); } static now() { return Real.now() + window.__off; } }
      window.Date = Fake;
      let seed = 4242; Math.random = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
      if (local && !sessionStorage.getItem('__seeded')) { sessionStorage.setItem('__seeded', '1'); localStorage.setItem('mzbx-progress-v1', local); }
    }, { t: new Date(when).getTime(), local: local || null });
    await pg.goto('http://mz.local/index.html'); await pg.waitForSelector('.today'); await pg.waitForTimeout(150);
    return { pg, errs, ctx };
  }
  const setNow = (pg, when) => pg.evaluate((ms) => window.__setNow(ms), new Date(when).getTime());
  const reload = async (pg) => { await pg.evaluate(() => { S.run = null; }); await pg.reload(); await pg.waitForSelector('.today'); await pg.waitForTimeout(150); };
  const answer = (pg, ok) => pg.evaluate((ok) => {
    const R = S.run; if (!R || R.pos >= R.list.length) return null;
    const q = R.list[R.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
    if (q.type === '判断') runState.picked = new Set([ok ? ans : (ans === '正确' ? '错误' : '正确')]);
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
    reveal(q); nextQ(); return q.id;
  }, ok);
  const startBtn = '.panel.today >> button:text-is("开始") >> nth=0';
  const doPlan = async (pg, wrongEvery) => { let i = 0; const wrong = []; for (;;) { const ok = !(wrongEvery && i % wrongEvery === 0); const id = await answer(pg, ok); if (!id) break; if (!ok) wrong.push(id); i++; } return wrong; };
  const exportLocal = (pg) => pg.evaluate(() => localStorage.getItem('mzbx-progress-v1'));

  console.log('A 当天重做错题并答对，第二天仍然先出');
  { const d = await open('2026-11-28T09:00:00');
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    const wrong = await doPlan(d.pg, 5);                     // 每5题错1题：共错10题
    check('第一天50题、错10题', wrong.length === 10);
    check('小结页写了“当天重做不算过关”', (await d.pg.textContent('#main')).includes('当天重做不算过关'));
    await d.pg.click('button:has-text("错题再做一遍")'); await d.pg.waitForSelector('#qcard');
    await doPlan(d.pg, 0);
    const rec = await d.pg.evaluate((ids) => ids.map((id) => S.prog.q[id]), wrong);
    check('重做答对后：上次答对、盒子仍是0、到期日是明天', rec.every((p) => p.l === 1 && p.b === 0 && p.due === '2026-11-29' && p.n === 2 && !p.x), JSON.stringify(rec[0]));
    check('错题页不再列这些题', (await d.pg.evaluate(() => wrongCards().length)) === 0);
    await d.pg.evaluate(() => exitRun());
    check('做完面板写了当天重做不算过关', (await d.pg.textContent('.panel.today')).includes('当天重做不算过关'));
    const more = await d.pg.evaluate(() => { const t = S.prog.plan; const m = planParts(20, new Set(t.ids)); const P = S.prog.q; const todayCards = new Set(); for (const q of S.qs) if (P[q.id] && P[q.id].f === dayStr()) q.cards.forEach((c) => todayCards.add(c));
      return { n: m.list.length, sameCard: m.list.filter((q) => q.cards.some((c) => todayCards.has(c))).length, o: m.list.map((q) => q.o).slice(0, 8) }; });
    check('“再加20题”有20道', more.n === 20, JSON.stringify(more));
    console.log('    再加的20题里与今天已学新题同知识点的：', more.sameCard, '（核心不够分散时才会放宽）');
    await setNow(d.pg, '2026-11-29T09:00:00'); await reload(d.pg);
    const day2 = await d.pg.evaluate((ids) => { const p = planParts(dailyOf()); const inList = new Set(p.list.map((q) => q.id)); return { n: p.n, wrongIn: ids.filter((id) => inList.has(id)).length, first10: p.list.slice(0, 10).filter((q) => ids.includes(q.id)).length }; }, wrong);
    check('第二天①里有昨天错的10题，排在最前', day2.n.wrong === 10 && day2.wrongIn === 10 && day2.first10 === 10, JSON.stringify(day2));
    check('第二天有保底的核心新题', day2.n.new1 >= 20, JSON.stringify(day2.n));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('B 同一天答对两次不连升；计划开始后在别处做过的题不再出');
  { const d = await open('2026-11-28T09:00:00');
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    for (let i = 0; i < 10; i++) await answer(d.pg, true);
    await d.pg.evaluate(() => exitRun());
    const st = await d.pg.evaluate(() => {
      const rest = S.prog.plan.ids.slice(S.prog.plan.pos);
      const g = pickGroup(mzPool(), 15); const overlap = g.filter((q) => rest.includes(q.id)).length;
      // 模拟在别处把计划里剩下的前3题做了（答对）
      const took = rest.slice(0, 3); for (const id of took) record(S.q[id], true);
      const before = took.map((id) => ({ ...S.prog.q[id] }));
      for (const id of took) record(S.q[id], true);          // 同一天再答对一次
      const after = took.map((id) => ({ ...S.prog.q[id] }));
      return { overlap, took, before, after, restLen: rest.length };
    });
    console.log('    分科一组与计划剩余题重合：', st.overlap, '题（不再排除，回计划时算作已做）');
    check('同一天答对两次不连升', st.after.every((p, i) => p.b === st.before[i].b && p.due === st.before[i].due && p.b === 1 && p.n === 2), JSON.stringify(st.after[0]));
    await d.pg.click('.panel.today >> button:text-is("继续")'); await d.pg.waitForSelector('#qcard');
    const run = await d.pg.evaluate((took) => ({ len: S.run.list.length, pos: S.run.pos, has: S.run.list.slice(S.run.pos).filter((q) => took.includes(q.id)).length, planLen: S.prog.plan.ids.length }), st.took);
    check('回到计划：别处做过的3题算作已做、不再出，清单仍是50题', run.has === 0 && run.len === 50 && run.pos === 13 && run.planLen === 50, JSON.stringify(run));
    await doPlan(d.pg, 0);
    await d.pg.evaluate(() => exitRun());
    check('做完后面板显示“做完了”', (await d.pg.textContent('.panel.today')).includes('今日计划：做完了'));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('C 页面开着过了零点');
  { const d = await open('2026-11-28T23:50:00');
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
    for (let i = 0; i < 5; i++) await answer(d.pg, i !== 0);
    await d.pg.evaluate(() => exitRun());
    check('零点前面板是“继续”', (await d.pg.textContent('.panel.today')).includes('已做5题'));
    await setNow(d.pg, '2026-11-29T00:10:00');
    await d.pg.click('.panel.today >> button:text-is("继续")'); await d.pg.waitForTimeout(200);
    const t1 = await d.pg.textContent('.panel.today');
    check('过零点点“继续”：换成新一天的计划', t1.includes('开始') && !t1.includes('已做5题'), t1.slice(0, 40));
    check('倒计时也换了', (await d.pg.textContent('#countdown')).includes('7'));
    await setNow(d.pg, '2026-11-30T08:00:00');
    await d.pg.evaluate(() => { document.dispatchEvent(new Event('visibilitychange')); });
    await d.pg.waitForTimeout(200);
    check('页面重新可见时自动换日', (await d.pg.textContent('#countdown')).includes('6'));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('D 折叠面板里改设置不收起、不跳回页顶');
  { const d = await open('2026-11-28T09:00:00');
    const det = d.pg.locator('details.more', { hasText: '分科加练' });
    await det.locator('summary').click();
    await d.pg.locator('#size-mz').scrollIntoViewIfNeeded();
    const y0 = await d.pg.evaluate(() => window.scrollY);
    await d.pg.selectOption('#size-mz', '20');
    await d.pg.waitForTimeout(150);
    const st = await d.pg.evaluate(() => ({ open: [...document.querySelectorAll('details.more')].map((x) => x.open), y: window.scrollY, size: S.prog.settings.size, focus: document.activeElement && document.activeElement.id }));
    check('改每组题数后面板仍展开、位置不变、焦点还在', st.open.includes(true) && Math.abs(st.y - y0) < 4 && st.size === 20 && st.focus === 'size-mz', JSON.stringify(st) + ` y0=${y0}`);
    await d.pg.check('#fmC'); await d.pg.waitForTimeout(150);
    const st2 = await d.pg.evaluate(() => ({ open: [...document.querySelectorAll('details.more')].map((x) => x.open), fmC: S.prog.settings.fmC, vis: !!document.querySelector('#fmC') && document.querySelector('#fmC').checked }));
    check('勾“含C档”后面板仍展开', st2.open.includes(true) && st2.fmC === true && st2.vis, JSON.stringify(st2));
    await d.pg.selectOption('#dailySel', '60'); await d.pg.waitForTimeout(150);
    check('改每天题数后计划是60题', (await d.pg.textContent('.panel.today .big')).includes('60'));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('E 考前两天与考试当天');
  { // 先造一份做到12-03的记录：每天做完计划，每4题错1题
    const d = await open('2026-11-28T09:00:00');
    for (const day of ['2026-11-28', '2026-11-29', '2026-11-30', '2026-12-01', '2026-12-02', '2026-12-03', '2026-12-04', '2026-12-05']) {
      await setNow(d.pg, day + 'T09:00:00'); await reload(d.pg);
      const prev = await d.pg.evaluate(() => { const p = planParts(dailyOf()); const sum = Object.values(p.n).reduce((a, x) => a + x, 0); return { n: p.n, len: p.list.length, sum, fin: finalDays(), chips: document.querySelector('.panel.today .mix') ? document.querySelector('.panel.today .mix').textContent : '' }; });
      if (day >= '2026-12-04') {
        check(`${day.slice(5)} 是考前模式，各类之和等于总数`, prev.fin && prev.sum === prev.len, JSON.stringify(prev.n));
        const nums = (prev.chips.match(/(复习|考前回顾|核心新题|备选新题) (\d+)/g) || []).map((x) => Number(x.split(' ')[1])).reduce((a, x) => a + x, 0);
        check(`${day.slice(5)} 面板上各项数字加起来等于总题数`, nums === prev.len, `${prev.chips} → ${nums}/${prev.len}`);
        check(`${day.slice(5)} 面板有考前说明`, (await d.pg.textContent('.panel.today')).includes('考前两天'));
      }
      await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard');
      await doPlan(d.pg, 4);
      await d.pg.evaluate(() => exitRun());
    }
    const end = await d.pg.evaluate(() => { const P = S.prog.q; const core = S.qs.filter((q) => q.t === 1); return { seen: core.filter((q) => P[q.id]).length, total: core.length, missedNotRefreshed: core.filter((q) => P[q.id] && P[q.id].c < P[q.id].n && P[q.id].d < '2026-12-04').length }; });
    console.log('    到12-05：', JSON.stringify(end));
    check('答错过的核心题考前两天都再见过', end.missedNotRefreshed === 0, JSON.stringify(end));
    await setNow(d.pg, '2026-12-06T07:30:00'); await reload(d.pg);
    const exam = await d.pg.evaluate(() => { const p = planParts(dailyOf()); return { n: p.n, text: document.querySelector('.panel.today').textContent }; });
    check('考试当天不上新题', exam.n.new1 === 0 && exam.n.new2 === 0, JSON.stringify(exam.n));
    check('考试当天有说明', exam.text.includes('今天考试'));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log('F 390px 下做题页不横向溢出（含长的真题来源标签）');
  { const d = await open('2026-11-28T09:00:00');
    const over = await d.pg.evaluate(async () => { const out = []; for (const q of S.qs.filter((x) => x.src === '真题')) { S.run = { list: [q], pos: 0, res: {}, label: '测', tkey: '', mode: '' }; route(); await new Promise((r) => setTimeout(r, 10)); const w = document.documentElement.scrollWidth - window.innerWidth; if (w > 0) out.push([q.id, w]); } S.run = null; route(); return out; });
    check('真题做题页无横向溢出', over.length === 0, JSON.stringify(over));
    check('无报错', d.errs.length === 0, d.errs.join('; ')); await d.ctx.close(); }

  console.log(fails.length ? `\n有 ${fails.length} 项没过：${fails.join('；')}` : '\n全部通过');
  await b.close(); process.exit(fails.length ? 1 : 0);
})();
