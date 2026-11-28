// 界面：390px 下今日计划面板三种状态（未开始、进行中、做完）、深色模式、横向溢出、“每天题数”在三种状态下改动后的表现。
const H = require('./harness');
(async () => {
  const site = process.argv[2] || 'realdraft';
  const check = H.mkCheck();
  const startBtn = '.panel.today >> button:text-is("开始") >> nth=0';
  const overflow = (pg) => pg.evaluate(() => { const w = document.documentElement.scrollWidth - window.innerWidth; const bad = []; if (w > 0) for (const el of document.querySelectorAll('#main *')) { const r = el.getBoundingClientRect(); if (r.right > window.innerWidth + 0.5) bad.push(el.tagName + '.' + el.className + ':' + Math.round(r.right)); } return { w, bad: bad.slice(0, 5) }; });
  const panel = (pg) => pg.evaluate(() => { const p = document.querySelector('.panel.today'); return { text: p.innerText.replace(/\s+/g, ' ').trim(), sel: (p.querySelector('#dailySel') || {}).value, label: (p.querySelector('label[for=dailySel]') || {}).textContent, focus: document.activeElement && document.activeElement.id, y: window.scrollY }; });
  for (const dark of [false, true]) {
    const tag = dark ? 'dark' : 'light';
    console.log(`== ${tag}`);
    const d = await H.open(site, '2026-11-28T09:00:00', { dark });
    const pg = d.pg;
    // 未开始
    let p = await panel(pg); console.log('  未开始：', p.text.slice(0, 200));
    check(`${tag} 未开始无横向溢出`, (await overflow(pg)).w <= 0, JSON.stringify(await overflow(pg)));
    await pg.locator('.panel.today').first().screenshot({ path: `out/ui_${tag}_1_notstarted.png` });
    for (const k of ['20', '80', '50']) {
      await pg.selectOption('#dailySel', k); await pg.waitForTimeout(120);
      p = await panel(pg);
      const big = await pg.textContent('.panel.today .big');
      const prev = await pg.evaluate(() => { const r = planParts(dailyOf()); return { len: r.list.length, n: r.n }; });
      check(`${tag} 未开始改成${k}题：面板显示${k}题、焦点留在下拉框、设置已存`, big === `${k}题` && p.focus === 'dailySel' && p.sel === k && prev.len === Number(k), JSON.stringify({ big, focus: p.focus, sel: p.sel, prev }));
      console.log('     ', p.text.slice(0, 160));
    }
    // 进行中
    await pg.click(startBtn); await pg.waitForSelector('#qcard');
    for (let i = 0; i < 12; i++) await H.answer(pg, i % 4 !== 0);
    await pg.evaluate(() => exitRun());
    p = await panel(pg); console.log('  进行中：', p.text.slice(0, 260));
    check(`${tag} 进行中无横向溢出`, (await overflow(pg)).w <= 0, JSON.stringify(await overflow(pg)));
    await pg.locator('.panel.today').first().screenshot({ path: `out/ui_${tag}_2_inprogress.png` });
    check(`${tag} 进行中：标签是“明天起每天题数”`, p.label === '明天起每天题数', p.label);
    await pg.selectOption('#dailySel', '80'); await pg.waitForTimeout(120);
    p = await panel(pg);
    const pl = await pg.evaluate(() => ({ len: S.prog.plan.ids.length, pos: S.prog.plan.pos, daily: S.prog.settings.daily }));
    check(`${tag} 进行中改成80题：今天的清单不变（50题、已做12），设置=80，焦点保留`, pl.len === 50 && pl.pos === 12 && pl.daily === 80 && p.focus === 'dailySel' && p.text.includes('已做12题，还剩38题'), JSON.stringify(pl) + ' ' + p.focus);
    console.log('     改80后：', p.text.slice(0, 300));
    await pg.selectOption('#dailySel', '50'); await pg.waitForTimeout(120);
    // 做完
    await pg.click('.panel.today >> button:text-is("继续")'); await pg.waitForSelector('#qcard');
    for (;;) { const id = await H.answer(pg, true); if (!id) break; }
    await pg.screenshot({ path: `out/ui_${tag}_summary.png`, fullPage: true });
    check(`${tag} 小结页无横向溢出`, (await overflow(pg)).w <= 0, JSON.stringify(await overflow(pg)));
    await pg.evaluate(() => exitRun());
    p = await panel(pg); console.log('  做完：', p.text.slice(0, 300));
    check(`${tag} 做完无横向溢出`, (await overflow(pg)).w <= 0, JSON.stringify(await overflow(pg)));
    await pg.locator('.panel.today').first().screenshot({ path: `out/ui_${tag}_3_done.png` });
    await pg.selectOption('#dailySel', '20'); await pg.waitForTimeout(120);
    p = await panel(pg);
    const pl2 = await pg.evaluate(() => ({ len: S.prog.plan.ids.length, pos: S.prog.plan.pos, daily: S.prog.settings.daily }));
    check(`${tag} 做完后改成20题：今天的记录不变，设置=20，仍是“做完了”`, pl2.len === 50 && pl2.pos === 50 && pl2.daily === 20 && p.text.includes('今日计划：做完了') && p.focus === 'dailySel', JSON.stringify(pl2));
    console.log('     改20后：', p.text.slice(0, 300));
    await pg.screenshot({ path: `out/ui_${tag}_today_full.png`, fullPage: true });
    // 记录页的每天题数
    await pg.goto('http://mz.local/index.html#stats'); await pg.waitForSelector('#dailySel');
    await pg.selectOption('#dailySel', '60'); await pg.waitForTimeout(120);
    const st = await pg.evaluate(() => ({ daily: S.prog.settings.daily, focus: document.activeElement && document.activeElement.id, sel: document.querySelector('#dailySel').value, n: document.querySelectorAll('#dailySel').length }));
    check(`${tag} 记录页改每天题数=60`, st.daily === 60 && st.focus === 'dailySel' && st.sel === '60' && st.n === 1, JSON.stringify(st));
    check(`${tag} 记录页无横向溢出`, (await overflow(pg)).w <= 0, JSON.stringify(await overflow(pg)));
    check(`${tag} 无报错`, d.errs.length === 0, d.errs.join('; '));
    await d.ctx.close();
  }
  // 窄屏 320px 再看一眼
  { const d = await H.open(site, '2026-11-28T09:00:00', { width: 320 });
    check('320px 未开始无横向溢出', (await overflow(d.pg)).w <= 0, JSON.stringify(await overflow(d.pg)));
    await d.pg.click(startBtn); await d.pg.waitForSelector('#qcard'); for (;;) { const id = await H.answer(d.pg, true); if (!id) break; } await d.pg.evaluate(() => exitRun());
    check('320px 做完无横向溢出', (await overflow(d.pg)).w <= 0, JSON.stringify(await overflow(d.pg)));
    await d.pg.locator('.panel.today').first().screenshot({ path: 'out/ui_320_done.png' });
    await d.ctx.close(); }
  console.log(check.fails.length ? `\n有 ${check.fails.length} 项没过：${check.fails.join('；')}` : '\n全部通过');
  await H.close();
})();
