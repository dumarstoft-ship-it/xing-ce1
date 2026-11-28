// 路线4：两台设备轮着用（共用一份假云端）。第一天：上午手机做25题，晚上电脑做完；第二天：上午电脑做25题，晚上手机接着。
// X：手机第一天停下时点了“退出”；Y：手机第一天停在题目页就锁屏了；Z：同X，但第二天晚上手机还没连上网就点了“开始”。设备“睡着”= 断网且不触发任何事件。
const L = require('./lib'); const V = process.env.VARIANT || 'X';
(async () => {
  const b = await L.launch(); const store = L.newStore(); const PB = [];
  const off = (d) => d.pg.evaluate(() => { window.__online = false; });
  const on = (d) => d.pg.evaluate(() => { window.__online = true; window.__emit(); });
  const cloudPlan = () => { const r = store.remote ? JSON.parse(store.remote) : null; return r && r.plan ? `${r.plan.day} pos${r.plan.pos}/${r.plan.ids.length}` : 'null'; };
  const state = async (d, label) => { const s = await d.pg.evaluate(() => { const t = S.prog.plan, R = S.run, today = dayStr(), Pq = S.prog.q; const el = document.querySelector('.panel.today');
      return { now: today, view: R ? (R.pos >= R.list.length ? '小结页' : '题目页 ' + R.label + ' ' + document.querySelector('.runbar .pos').textContent) : '今日页', text: (R ? document.querySelector('#main').innerText : (el ? el.innerText : '')).replace(/\s+/g, ' ').slice(0, 120),
        plan: t ? `${t.day} pos${t.pos}/${t.ids.length}` : null, answeredToday: (S.prog.days[today] || { n: 0 }).n, distinctToday: Object.values(Pq).filter((p) => p.d === today).length, tried: Object.keys(Pq).length, cloud: S.cloud, note: S.cloudNote, countdown: document.querySelector('#countdown').innerText, chk: window.__chk() }; });
    console.log(`  [${d.name} ${label}]`, JSON.stringify(s), '| 云端计划', cloudPlan(), '| 云端写入累计', store.sets); for (const c of s.chk) PB.push(`${d.name} ${label}: ${c}`); return s; };
  const cat = (list, today) => { const c = { 没做过的: 0, 今天做过的: 0, 昨天做过的: 0, 更早做过的: 0 }; for (const x of list) { if (!x.seenDay) c.没做过的++; else if (x.seenDay === today) c.今天做过的++; else if (x.seenDay === '2026-11-28') c.昨天做过的++; else c.更早做过的++; } return JSON.stringify(c); };
  console.log(`== 变体 ${V}`);
  console.log('第一天 11-28 上午：手机');
  const phone = await L.device(b, { store, when: '2026-11-28T09:00:00', name: '手机' });
  await L.planBtn(phone.pg, '开始').click(); await phone.pg.waitForSelector('#qcard'); await L.fastN(phone.pg, 25, 4);
  if (V !== 'Y') { await phone.pg.click('button:text-is("退出")'); await phone.pg.waitForSelector('.today'); }
  await phone.pg.waitForTimeout(1500); await state(phone, '做了25题' + (V === 'Y' ? '，停在题目页锁屏' : '，退出')); await off(phone);
  console.log('第一天 11-28 晚上：电脑（第一次在这台设备上打开）');
  const pc = await L.device(b, { store, when: '2026-11-28T20:00:00', name: '电脑' }); await state(pc, '打开');
  await L.planBtn(pc.pg, '继续').click(); await pc.pg.waitForSelector('#qcard'); const pc1 = await L.fastN(pc.pg, null, 4, 25);
  const redo = pc.pg.locator('button:has-text("错题再做一遍")'); if (await redo.count()) { await redo.click(); await pc.pg.waitForSelector('#qcard'); await L.fastN(pc.pg, null, 0); }
  await pc.pg.click('button:text-is("回到今日")'); await pc.pg.waitForSelector('.today'); await pc.pg.waitForTimeout(1500); await state(pc, `接着做完（${pc1.length}题）`); await off(pc);
  console.log('第二天 11-29 上午：电脑（页面开着过夜）');
  await L.setNow(pc.pg, '2026-11-29T09:00:00'); await on(pc); await L.wake(pc.pg); await pc.pg.waitForTimeout(2000); await state(pc, '早上');
  await L.planBtn(pc.pg, '开始').click(); await pc.pg.waitForSelector('#qcard'); const pc2 = await L.fastN(pc.pg, 25, 4); await pc.pg.click('button:text-is("退出")'); await pc.pg.waitForSelector('.today'); await pc.pg.waitForTimeout(1500);
  await state(pc, '做了25题，退出'); const pcPlan = await pc.pg.evaluate(() => ({ ids: S.prog.plan.ids.slice(), pos: S.prog.plan.pos, n: S.prog.plan.n })); console.log('  电脑今天排的计划构成:', JSON.stringify(pcPlan.n)); await off(pc);
  console.log('第二天 11-29 晚上：手机（页面从昨天上午开到现在）');
  await L.setNow(phone.pg, '2026-11-29T21:00:00');
  if (V === 'Z') { await L.wake(phone.pg); await phone.pg.waitForTimeout(300); await state(phone, '拿起来，网还没连上'); const sb = L.planBtn(phone.pg, '开始');
    if ((await sb.count()) && !(await sb.isDisabled())) { await sb.click(); await phone.pg.waitForSelector('#qcard'); await L.answerUI(phone.pg, true); await on(phone); await phone.pg.waitForTimeout(2500); await state(phone, '点了开始、答了1题后网连上'); }
    else { console.log('  这时“开始/继续”点不了，页面提示：', await phone.pg.evaluate(() => [...document.querySelectorAll('.panel.today .note')].map((x) => x.innerText).filter((x) => /同步/.test(x)).join(' '))); await on(phone); await phone.pg.waitForTimeout(2500); await state(phone, '网连上之后'); } }
  else { await on(phone); await L.wake(phone.pg); await phone.pg.waitForTimeout(2500); await state(phone, '拿起来，网连上之后'); }
  const cmp = await phone.pg.evaluate((pcIds) => { const t = S.prog.plan, R = S.run; const same = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]); return { planIsPcList: same(t.ids, pcIds), runIsPcList: R ? same(R.list.map((q) => q.id), pcIds) : null, planPos: t.pos, planDay: t.day }; }, pcPlan.ids);
  console.log('  手机上现在的“今日计划”是不是电脑今天排的那份清单:', JSON.stringify(cmp));
  let done = [];
  const inRun = await phone.pg.evaluate(() => !!S.run && !!document.querySelector('#qcard'));
  if (!inRun) { const c = L.planBtn(phone.pg, '继续'); const useBtn = (await c.count()) ? c : L.planBtn(phone.pg, '开始'); await useBtn.click(); await phone.pg.waitForSelector('#qcard'); done = await L.fastN(phone.pg, null, 4, 25); }
  else { const first = await L.answerUI(phone.pg, true, PB); done = (first ? [{ id: first.id, ok: first.ok, seenDay: '?' }] : []).concat(await L.fastN(phone.pg, null, 4, 1)); }
  const sum = await L.mainText(phone.pg, 60); console.log(`  手机把眼前这组做完：又答了${done.length}题，其中 ${cat(done.filter((x) => x.seenDay !== '?'), '2026-11-29')}（第一题另计）| 小结: ${sum}`);
  await phone.pg.click('button:text-is("回到今日")'); await phone.pg.waitForSelector('.today'); await phone.pg.waitForTimeout(1500); await state(phone, '做完回到今日');
  const left = await phone.pg.evaluate((pcIds) => { const today = dayStr(), P = S.prog.q; return { pcPlanNotDoneToday: pcIds.filter((id) => !(P[id] && P[id].d === today)).length, planIsPcList: S.prog.plan.ids.length === pcIds.length && S.prog.plan.ids.every((x, i) => x === pcIds[i]) }; }, pcPlan.ids);
  console.log('  电脑今天排的50题里，今天实际没做到的还有:', left.pcPlanNotDoneToday, '道；面板上的计划还是电脑排的那份吗:', left.planIsPcList);
  console.log('第二天 11-29 深夜：再看电脑');
  await L.setNow(pc.pg, '2026-11-29T22:00:00'); await on(pc); await L.wake(pc.pg); await pc.pg.waitForTimeout(2500); await state(pc, '再看');
  const s0 = store.sets; await pc.pg.waitForTimeout(6000); console.log('  两台都开着、不操作6秒：云端写入', s0, '→', store.sets);
  console.log('页面报错：', phone.errs.concat(pc.errs).length ? phone.errs.concat(pc.errs).join(' ; ') : '无'); console.log('发现的问题：', PB.length ? '\n  ' + [...new Set(PB)].slice(0, 20).join('\n  ') : '无');
  await b.close();
})().catch((e) => { console.error('脚本出错', e); process.exit(1); });
