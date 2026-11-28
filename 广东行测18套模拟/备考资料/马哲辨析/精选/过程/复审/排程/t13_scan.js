// 各页面、做题页、小结页有没有漏出 null / undefined / NaN / [object Object] 这样的字
const H = require('./harness');
(async () => {
  for (const site of ['v7_noplan', 'realdraft', 'old_noplan']) {
    const d = await H.open(site, '2026-11-28T09:00:00'); const pg = d.pg; const hits = [];
    const scan = async (where) => {
      const r = await pg.evaluate(() => {
        const t = document.body.innerText;
        const re = new RegExp('.{0,25}(\\bnull\\b|undefined|NaN|\\[object Object\\]).{0,15}', 'g');
        const m = t.match(re); return m ? m.map((x) => x.replace(/\s+/g, ' ')) : [];
      });
      for (const x of r) hits.push(where + '：' + x);
    };
    await scan('今日（未开始）');
    const btn = (await pg.$$('button:text-is("开始")'))[0];
    await pg.evaluate(() => { for (const x of document.querySelectorAll('details.more')) x.open = true; });
    await scan('今日（展开）');
    await btn.click(); await pg.waitForSelector('#qcard'); await scan('做题');
    for (let i = 0; i < 6; i++) { await H.answer(pg, i % 2 === 0, true); await scan('揭晓'); await pg.evaluate(() => nextQ()); }
    await pg.evaluate(() => exitRun()); await scan('今日（进行中）');
    await pg.evaluate(() => { const t = S.prog.plan || S.prog.today; S.run = { list: t.ids.map((id) => S.q[id]), pos: t.pos, res: t.res, label: 'x', tkey: S.prog.plan ? 'plan' : 'today', mode: '' }; route(); });
    for (;;) { const id = await H.answer(pg, true); if (!id) break; }
    await scan('小结');
    await pg.evaluate(() => exitRun()); await scan('今日（做完）');
    for (const r of ['practice', 'review', 'cards', 'pending', 'appendix', 'stats']) { await pg.evaluate((r) => { location.hash = '#' + r; }, r); await pg.waitForTimeout(200); await scan('#' + r); }
    await H.setNow(pg, '2026-12-06T08:00:00'); await pg.evaluate(() => { location.hash = '#today'; }); await H.reload(pg); await scan('考试当天今日页');
    console.log(site, hits.length ? '\n  ' + [...new Set(hits)].slice(0, 12).join('\n  ') : '没有', '| errors:', d.errs.join('; ') || 'none');
    await d.ctx.close();
  }
  await H.close();
})();
