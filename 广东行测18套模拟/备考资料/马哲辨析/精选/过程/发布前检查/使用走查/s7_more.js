// Y2：手机第一天停在题目页，晚上电脑把计划做完；第二天早上先拿起手机（另一台设备今天还没动）。
// 另：错题重练里判断题的答案分布；计划外的题答错后进不进今日计划。
const L = require('./lib'); const ONLY = (process.env.ONLY || 'Y2,P1,P2').split(',');
(async () => {
  const b = await L.launch();
  if (ONLY.includes('Y2')) { const store = L.newStore();
    const off = (d) => d.pg.evaluate(() => { window.__online = false; }); const on = (d) => d.pg.evaluate(() => { window.__online = true; window.__emit(); });
    const state = async (d, label) => { const s = await d.pg.evaluate(() => { const t = S.prog.plan, R = S.run, today = dayStr(), Pq = S.prog.q; const el = document.querySelector('.panel.today');
      return { now: today, view: R ? (R.pos >= R.list.length ? '小结页' : '题目页 ' + R.label + ' ' + document.querySelector('.runbar .pos').textContent) : '今日页', text: (R ? document.querySelector('#main').innerText : (el ? el.innerText : '')).replace(/\s+/g, ' ').replace(' 20题 30题 40题 50题 60题 80题', '').slice(0, 110), plan: t ? `${t.day} pos${t.pos}/${t.ids.length}` : null, answeredToday: (S.prog.days[today] || { n: 0 }).n, coreSeen: S.qs.filter((q) => q.t === 1 && Pq[q.id]).length, countdown: document.querySelector('#countdown').innerText }; }); console.log(`  [${d.name} ${label}]`, JSON.stringify(s), '| 云端写入累计', store.sets); return s; };
    console.log('Y2 第一天：手机上午做25题停在题目页；电脑晚上接着做完');
    const phone = await L.device(b, { store, when: '2026-11-28T09:00:00', name: '手机' }); await L.planBtn(phone.pg, '开始').click(); await phone.pg.waitForSelector('#qcard'); await L.fastN(phone.pg, 25, 4); await phone.pg.waitForTimeout(1500); await off(phone);
    const pc = await L.device(b, { store, when: '2026-11-28T20:00:00', name: '电脑' }); await L.planBtn(pc.pg, '继续').click(); await pc.pg.waitForSelector('#qcard'); await L.fastN(pc.pg, null, 4, 25);
    await pc.pg.click('button:text-is("回到今日")'); await pc.pg.waitForSelector('.today'); await pc.pg.waitForTimeout(1500); await state(pc, '晚上做完'); await off(pc);
    console.log('   第二天早上先拿起手机');
    await L.setNow(phone.pg, '2026-11-29T08:00:00'); await on(phone); await L.wake(phone.pg); await phone.pg.waitForTimeout(2500); const s = await state(phone, '拿起来');
    if (s.view.startsWith('题目页')) { const first = await L.answerUI(phone.pg, true); const rest = await L.fastN(phone.pg, null, 4, 1); const sum = await L.mainText(phone.pg, 40);
      console.log(`  接着眼前这组做完：共答${rest.length + 1}题，其中昨晚在电脑上刚做过的 ${rest.filter((x) => x.seenDay === '2026-11-28').length + (first && first.seen ? 1 : 0)} 道、没做过的 ${rest.filter((x) => !x.seenDay).length} 道 | 小结: ${sum}`);
      await phone.pg.click('button:text-is("回到今日")'); await phone.pg.waitForSelector('.today'); await phone.pg.waitForTimeout(1200); await state(phone, '点“回到今日”'); }
    else console.log('  不在题目页：直接看到今天的计划');
    console.log('  页面报错：', phone.errs.concat(pc.errs).join(' ; ') || '无'); await phone.ctx.close(); await pc.ctx.close(); }
  if (ONLY.includes('P1')) { const d = await L.device(b, { when: '2026-11-28T08:30:00' }); const pg = d.pg;
    await L.planBtn(pg, '开始').click(); await pg.waitForSelector('#qcard'); await L.fastN(pg, null, 1);   // 50题全答错
    await pg.click('button:has-text("错题再做一遍")'); await pg.waitForSelector('#qcard');
    const tally = {}; for (;;) { const x = await pg.evaluate(() => { const R = S.run; if (!R || R.pos >= R.list.length) return null; const q = R.list[R.pos], pres = runState.pres; return { k: (q.bank === 'fm' ? '政常' : '马哲') + q.type, ans: q.type === '判断' ? (pres ? pres.answer : q.answer) : '-', orig: q.answer, flip: !!(pres && pres.flip) }; }); if (!x) break; const key = x.k + (x.k.endsWith('判断') ? ` 原答案${x.orig}→这次${x.ans}` : ''); tally[key] = (tally[key] || 0) + 1; await L.fastN(pg, 1, 0); }
    console.log('P1 计划50题全答错后点“错题再做一遍”，这一遍各题型及判断题的答案:', JSON.stringify(tally)); await d.ctx.close(); }
  if (ONLY.includes('P2')) { const d = await L.device(b, { when: '2026-11-28T08:30:00' }); const pg = d.pg;
    await pg.click('#tabs a[href="#practice"]'); await pg.click('button.chip:has-text("扩展（计划外）")'); await pg.selectOption('#size-mz', '30'); await pg.waitForTimeout(100); await pg.click('#fstart'); await pg.waitForSelector('#qcard'); const n1 = await L.fastN(pg, null, 1);
    await pg.click('#tabs a[href="#today"]'); await pg.waitForTimeout(100); await L.setNow(pg, '2026-11-29T08:30:00'); await L.reload(pg);
    const r = await pg.evaluate(() => { const p = planParts(dailyOf()); const tiers = {}; for (const q of p.list) tiers[TIER_NAME[q.t || 3]] = (tiers[TIER_NAME[q.t || 3]] || 0) + 1; return { n: p.n, tiers, panel: document.querySelector('.panel.today').innerText.replace(/\s+/g, ' ').replace(' 20题 30题 40题 50题 60题 80题', '').slice(0, 170), about: (document.querySelector('#main').innerText.match(/今日计划只用[^。]*。/) || [''])[0] }; });
    console.log(`P2 第一天只在“练习”里做了${n1.length}道计划外的题（全错），第二天的今日计划:`, JSON.stringify(r)); await d.ctx.close(); }
  await b.close();
})().catch((e) => { console.error('脚本出错', e); process.exit(1); });
