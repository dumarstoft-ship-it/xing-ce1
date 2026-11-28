// 路线3：爱逛的用户。计划做一半去自选、分科、错题重练、看卡片、改题数，再回计划；页面开着过夜（停在做完页、停在题目页）。
const L = require('./lib'); const path = require('path');
(async () => {
  const b = await L.launch(); const d = await L.device(b, { when: '2026-11-28T08:30:00', name: 'phone' }); const pg = d.pg; const PB = [];
  const shot = (name) => pg.screenshot({ path: path.join(L.DIR, 'shots', `w_${name}.png`), fullPage: true });
  const tab = async (t) => { await pg.click(`#tabs a[href="#${t}"]`); await pg.waitForTimeout(120); };
  const back = async () => { const bb = pg.locator('button:text-is("回到今日"), button:text-is("返回")').first(); console.log('  小结页的返回按钮写的是：' + await bb.textContent()); await bb.click(); await pg.waitForTimeout(120); };
  const st = async (label) => { const i = await pg.evaluate(() => { const t = S.prog.plan; const today = dayStr(); const P = S.prog.q; const el = S.run ? null : document.querySelector('.panel.today');
      return { hash: location.hash, view: S.run ? (S.run.pos >= S.run.list.length ? '小结页' : '题目页 ' + S.run.label + ' ' + document.querySelector('.runbar .pos').textContent) : (document.querySelector('#main h2') || {}).innerText, panel: el ? el.innerText.replace(/\s+/g, ' ').slice(0, 230) : null,
        plan: t ? { day: t.day, pos: t.pos, len: t.ids.length, doneToday: t.ids.filter((id) => P[id] && P[id].d === today).length, tailDone: t.ids.slice(t.pos).filter((id) => P[id] && P[id].d === today).length } : null,
        answered: (S.prog.days[today] || { n: 0 }).n, distinct: Object.values(P).filter((p) => p.d === today).length, stats: [...document.querySelectorAll('#main .stat')].map((s) => s.innerText.replace(/\s+/g, ' ')).join(' | '), countdown: document.querySelector('#countdown').innerText, chk: window.__chk() }; });
    console.log(`[${label}]`, JSON.stringify(i)); for (const c of i.chk) PB.push(`${label}: ${c}`); return i; };
  // 1
  await L.planBtn(pg, '开始').click(); await pg.waitForSelector('#qcard'); await L.fastN(pg, 25, 4); await pg.click('button:text-is("退出")'); await pg.waitForSelector('.today');
  await st('1 计划做到25题后退出');
  // 2 练习页自选核心
  await tab('practice'); await pg.click('button.chip:text-is("核心")'); await pg.waitForTimeout(80);
  const fc = await pg.textContent('#fcount'); await shot('练习页');
  await pg.click('#fstart'); await pg.waitForSelector('#qcard');
  const ov = await pg.evaluate(() => { const t = S.prog.plan; const tail = new Set(t.ids.slice(t.pos)); return { len: S.run.list.length, label: S.run.label, inPlanTail: S.run.list.filter((q) => tail.has(q.id)).length, alreadyDone: S.run.list.filter((q) => S.prog.q[q.id]).length }; });
  console.log('2 自选核心:', fc, JSON.stringify(ov));
  await tab('practice'); const stillRun = await pg.evaluate(() => !!S.run && !!document.querySelector('#qcard'));
  console.log('  做题时点“练习”分栏（这组就是从练习页开的）→', stillRun ? '没有反应，还在题目页' : '退出了这一组');
  if (!stillRun) { await pg.click('#fstart'); await pg.waitForSelector('#qcard'); }
  await L.fastN(pg, null, 3); const sumP = await L.mainText(pg, 70); await back(); const ab = await st('2 自选一组做完，点“回到今日”之后');
  console.log('  自选小结:', sumP, '| 点“回到今日”后：hash=', ab.hash, '页面标题=', ab.view);
  // 3
  await tab('today'); const s3 = await st('3 回到今日页');
  // 4 做题时点“今日”
  await L.planBtn(pg, '继续').click(); await pg.waitForSelector('#qcard'); const r4 = await pg.evaluate(() => `${S.run.pos}/${S.run.list.length} 页面显示 ${document.querySelector('.runbar .pos').textContent}`);
  await tab('today'); const still4 = await pg.evaluate(() => !!S.run && !!document.querySelector('#qcard'));
  console.log('4 点“继续”后位置:', r4, '| 做题时点“今日”分栏 →', still4 ? '没有反应，还在题目页' : '退出了这一组'); if (still4) { await pg.click('button:text-is("退出")'); await pg.waitForSelector('.today'); }
  // 5 分科加练：马哲今日一组
  await pg.locator('details.more', { hasText: '分科加练' }).locator('summary').first().click(); await pg.waitForTimeout(100); await shot('分科加练展开');
  const c5 = await pg.evaluate(() => window.__chk()); for (const c of c5) PB.push('分科加练展开: ' + c);
  await pg.locator('details.more section.panel.today', { hasText: '马哲 · 今日一组' }).locator('button:text-is("开始")').click(); await pg.waitForSelector('#qcard');
  const ov5 = await pg.evaluate(() => { const t = S.prog.plan; const tail = new Set(t.ids.slice(t.pos)); return { len: S.run.list.length, inPlanTail: S.run.list.filter((q) => tail.has(q.id)).length, tiers: S.run.list.map((q) => q.t || 3).join('') }; });
  await L.fastN(pg, null, 4); const sum5 = await L.mainText(pg, 60); await back(); console.log('5 马哲今日一组:', JSON.stringify(ov5), '| 小结:', sum5); await st('5 马哲一组做完回来');
  // 6 政常错题重练
  const redoFm = pg.locator('details.more button.entry', { hasText: '错题重练' }); console.log('6 政常“错题重练”入口:', (await redoFm.innerText()).replace(/\s+/g, ' '), '可点:', !(await redoFm.isDisabled()));
  if (!(await redoFm.isDisabled())) { await redoFm.click(); await pg.waitForSelector('#qcard'); const o6 = await pg.evaluate(() => { const t = S.prog.plan; const tail = new Set(t.ids.slice(t.pos)); return { len: S.run.list.length, label: S.run.label, neverSeen: S.run.list.filter((q) => !S.prog.q[q.id]).length, inPlanTail: S.run.list.filter((q) => tail.has(q.id)).length, tiers: S.run.list.map((q) => q.t || 3).join('') }; }); console.log('  这一组:', JSON.stringify(o6)); await L.fastN(pg, 5, 0); await pg.click('button:text-is("退出")'); await pg.waitForTimeout(120); await st('6 政常错题重练做5题退出'); }
  // 7 错题页
  await tab('review'); console.log('7 错题页:', await L.mainText(pg, 120)); const c7 = await pg.evaluate(() => window.__chk()); for (const c of c7) PB.push('错题页: ' + c); await shot('错题页');
  const rb = pg.locator('button:text-is("开始重练")').first(); if (await rb.count()) { await rb.click(); await pg.waitForSelector('#qcard'); const o7 = await pg.evaluate(() => ({ len: S.run.list.length, label: S.run.label })); await L.fastN(pg, null, 0); const sum7 = await L.mainText(pg, 70); await back(); const a7 = await st('7 错题重练做完，点“回到今日”之后'); console.log('  重练:', JSON.stringify(o7), '小结:', sum7, '| 点“回到今日”后：hash=', a7.hash, '页面标题=', a7.view); }
  // 8 卡片
  await tab('cards'); await pg.fill('#cardSearch', '实践'); await pg.waitForTimeout(150); const nCards = await pg.locator('.cardlist details.card').count(); await pg.locator('.cardlist details.card summary').first().click(); await pg.waitForTimeout(80);
  const c8 = await pg.evaluate(() => window.__chk()); for (const c of c8) PB.push('卡片页: ' + c); console.log('8 卡片页搜“实践”:', nCards, '张'); await shot('卡片页');
  // 9 记录页、改每天题数
  await tab('stats'); const c9 = await pg.evaluate(() => window.__chk()); for (const c of c9) PB.push('记录页: ' + c); await shot('记录页');
  await tab('today'); const before9 = await st('9 改题数之前'); await pg.selectOption('#dailySel', '60'); await pg.waitForTimeout(150); await st('9 进行中把“明天起每天题数”改成60');
  // 10 回计划做完
  await L.planBtn(pg, '继续').click(); await pg.waitForSelector('#qcard'); const r10 = await pg.evaluate(() => `${S.run.pos}/${S.run.list.length} 页面显示 ${document.querySelector('.runbar .pos').textContent}`);
  const rest = await L.fastN(pg, null, 4, 1); const sum10 = await L.mainText(pg, 60); await shot('计划小结');
  console.log('10 回计划:', r10, '又做了', rest.length, '题 | 小结:', sum10);
  const redoBtn = pg.locator('button:has-text("错题再做一遍")');
  if (await redoBtn.count()) { await redoBtn.focus(); await pg.keyboard.press('Enter'); await pg.waitForTimeout(150);
    const kb = await pg.evaluate(() => ({ label: S.run && S.run.label, onQ: !!document.querySelector('#qcard'), focus: document.activeElement && document.activeElement.tagName })); console.log('  小结页：焦点放在“错题再做一遍”上按回车 →', JSON.stringify(kb));
    if (!kb.onQ) { await pg.locator('button:has-text("错题再做一遍")').click(); await pg.waitForSelector('#qcard'); } await L.fastN(pg, null, 0); }
  await back(); const s10 = await st('10 计划做完'); await shot('做完');
  // 11 停在做完页过夜
  await L.setNow(pg, '2026-11-29T07:30:00'); await L.wake(pg); await st('11 做完页开着过夜，第二天早上');
  // 12 停在题目页过夜
  await L.planBtn(pg, '开始').click(); await pg.waitForSelector('#qcard'); await L.fastN(pg, 20, 4); await st('12 第二天做到20题，停在题目页');
  await L.setNow(pg, '2026-11-30T07:30:00'); await L.wake(pg); const s12 = await st('12 题目页开着过夜，第三天早上'); await shot('过夜后的题目页');
  if (s12.view && s12.view.startsWith('题目页')) {
  await L.answerUI(pg, true, PB); const m12 = await pg.evaluate(() => ({ plan: `${S.prog.plan.day} pos${S.prog.plan.pos}/${S.prog.plan.ids.length}`, answered1130: (S.prog.days['2026-11-30'] || { n: 0 }).n, countdown: document.querySelector('#countdown').innerText, pos: document.querySelector('.runbar .pos').textContent })); console.log('  在过夜的题目页上答1题:', JSON.stringify(m12));
  const more12 = await L.fastN(pg, null, 4, 1); const sum12 = await L.mainText(pg, 60); console.log('  把这组做完（又', more12.length, '题）小结:', sum12); await back(); await st('12 做完昨天那组后回到今日'); await shot('过夜做完后的今日页');
  } else console.log('  过夜后不在题目页了：旧的一组已收起，回到今日页');
  console.log('页面报错：', d.errs.length ? d.errs.join(' ; ') : '无'); console.log('发现的问题：', PB.length ? '\n  ' + [...new Set(PB)].slice(0, 30).join('\n  ') : '无');
  await b.close();
})().catch((e) => { console.error('脚本出错', e); process.exit(1); });
