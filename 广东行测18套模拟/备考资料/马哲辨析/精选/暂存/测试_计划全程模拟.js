// 每日计划的全程模拟：从起始日到12月5日，每天把“今日计划”做完，按给定正确率作答。
// 用法：node plan_sim.js <站点目录> <起始日 2026-11-28> <首次正确率 0.75> <复习正确率 0.9> [每天做到第几题就停，默认做完]
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const SITE = process.argv[2], START = process.argv[3] || '2026-11-28';
  const PNEW = Number(process.argv[4] || 0.75), PREV = Number(process.argv[5] || 0.9), STOP = Number(process.argv[6] || 0);
  let seed = 12345; const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const b = await chromium.launch(); const errs = [];
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.route('http://mz.local/**', (route) => {
    const u = new URL(route.request().url());
    const f = path.join(SITE, decodeURIComponent(u.pathname === '/' ? '/index.html' : u.pathname));
    if (f.endsWith('.html')) return route.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(f, 'utf8') + '</body></html>', contentType: 'text/html; charset=utf-8' });
    return route.fulfill({ path: f, contentType: 'application/json; charset=utf-8' });
  });
  const days = []; for (let d = new Date(START + 'T09:00:00'); d < new Date('2026-12-06T00:00:00'); d = new Date(d.getTime() + 86400000)) days.push(new Date(d));
  for (const day of days) {
    const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(day.toISOString().slice(0, 10) + ' ' + e.message));
    await pg.addInitScript((t) => {
      const Real = Date, off = t - Real.now();
      class Fake extends Real { constructor(...a) { if (a.length) super(...a); else super(Real.now() + off); } static now() { return Real.now() + off; } }
      window.Date = Fake;
    }, day.getTime());
    await pg.goto('http://mz.local/index.html'); await pg.waitForSelector('.today'); await pg.waitForTimeout(150);
    const head = await pg.textContent('.today');
    const startBtn = await pg.$('.today button:text-is("开始")');
    if (!startBtn) { console.log(day.toISOString().slice(5, 10), '没有开始按钮：', head.slice(0, 60)); await pg.close(); continue; }
    await startBtn.click(); await pg.waitForSelector('#qcard');
    let n = 0, right = 0;
    for (;;) {
      const info = await pg.evaluate(() => { const R = S.run; if (!R || R.pos >= R.list.length) return null; const q = R.list[R.pos]; const pres = runState.pres; const p = S.prog.q[q.id];
        return { type: q.type, answer: pres ? pres.answer : q.answer, letters: pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(), seen: !!p }; });
      if (!info) break;
      const ok = rnd() < (info.seen ? PREV : PNEW);
      if (info.type === '判断') { const v = ok ? info.answer : (info.answer === '正确' ? '错误' : '正确'); await pg.click(`#qcard .tf .opt[data-v="${v}"]`); }
      else if (info.type === '单选') { const L = ok ? info.answer : info.letters.find((x) => x !== info.answer); await pg.click(`#qcard .opts .opt[data-v="${L}"]`); }
      else { const pick = ok ? info.answer.split('') : [info.letters.find((x) => !info.answer.includes(x)) || info.answer[0]]; for (const L of pick) await pg.click(`#qcard .opts .opt[data-v="${L}"]`); await pg.click('#submitMulti'); }
      await pg.waitForSelector('#nextBtn'); n++; right += ok ? 1 : 0;
      if (STOP && n >= STOP) break;
      await pg.click('#nextBtn');
    }
    const st = await pg.evaluate(() => { const P = S.prog.q, pl = S.prog.plan; const t1 = S.qs.filter((q) => q.t === 1), t2 = S.qs.filter((q) => q.t === 2);
      return { n: pl && pl.n, len: pl && pl.ids.length, pos: pl && pl.pos, core: t1.filter((q) => P[q.id]).length, coreAll: t1.length, back: t2.filter((q) => P[q.id]).length,
        out: Object.keys(P).filter((id) => !S.q[id].t).length }; });
    console.log(day.toISOString().slice(5, 10), `做${n}题 对${right}`, JSON.stringify(st.n), `核心${st.core}/${st.coreAll} 备选${st.back} 计划外${st.out}`);
    if (day === days[days.length - 1]) {
      const fin = await pg.evaluate(() => { const P = S.prog.q; const plan = S.qs.filter((q) => (q.t === 1 || q.t === 2) && P[q.id]); const ex = {}; for (const q of plan) ex[P[q.id].n] = (ex[P[q.id].n] || 0) + 1;
        const lastWeek = plan.filter((q) => P[q.id].d >= '2026-12-03').length;
        return { seen: plan.length, exposures: ex, avg: plan.reduce((a, q) => a + P[q.id].n, 0) / plan.length, weak: plan.filter((q) => !P[q.id].l).length, everWrongNotRefreshed: plan.filter((q) => P[q.id].c < P[q.id].n && P[q.id].d < '2026-12-04').length, seenLast3Days: lastWeek }; });
      console.log('结束时：', JSON.stringify(fin));
    }
    await pg.close();
  }
  console.log('errors:', errs.length ? errs.join('\n') : 'none'); await b.close();
})();
