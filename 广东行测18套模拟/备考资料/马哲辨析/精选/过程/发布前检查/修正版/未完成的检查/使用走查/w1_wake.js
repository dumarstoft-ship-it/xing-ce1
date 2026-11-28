// walk 路线1：睡醒时停在“做题页/小结页”（S.run 还在）——睡醒后的核对有没有补上
// 用法：SITEDIR=site_c|site_b|site_fix node w1_wake.js [A1,A1t,A2,A2t]
const L = require('./lib');
const SITE = process.env.SITEDIR || 'site_c';
const ONLY = (process.argv[2] || '').split(',').filter(Boolean);
const log = (...a) => console.log(...a);
const off = (d) => d.pg.evaluate(() => { window.__online = false; });
const onQuiet = (d) => d.pg.evaluate(() => { window.__online = true; });      // 网通了，但监听还没补发快照
const st = (d) => d.pg.evaluate(() => {
  const el = document.querySelector('.panel.today'); const btn = el && el.querySelector('button.primary');
  return { day: dayStr(), view: S.run ? (document.querySelector('#qcard') ? '题目页' : '小结页') : current(), btn: btn ? btn.textContent : null, disabled: btn ? btn.disabled : null,
    text: (document.querySelector('#main').innerText || '').replace(/\s+/g, ' ').slice(0, 150), cloud: S.cloud, note: S.cloudNote, waking: (typeof waking !== 'undefined') ? !!waking : '(旧版无)', nq: Object.keys(S.prog.q).length,
    plan: S.prog.plan ? { day: S.prog.plan.day, pos: S.prog.plan.pos, len: S.prog.plan.ids.length } : null,
    run: S.run ? { label: S.run.label, tkey: S.run.tkey, day: S.run.day, pos: S.run.pos, len: S.run.list.length } : null, gets: window.__gets || 0, sets: window.__sets || 0,
    countdown: document.querySelector('#countdown').innerText };
});
// 一题一题答（直接调页面函数），记下每题作答前的记录
const fastX = (pg, n, wrongEvery) => pg.evaluate(({ n, wrongEvery }) => {
  const out = [];
  for (let i = 0; i < n; i++) {
    const R = S.run; if (!R || R.pos >= R.list.length || !runState || runState.revealed) break;
    const q = R.list[R.pos]; const ok = !(wrongEvery && i % wrongEvery === 0);
    const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
    if (q.type === '判断') runState.picked = new Set([ok ? ans : (ans === '正确' ? '错误' : '正确')]);
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split('') : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
    const p = S.prog.q[q.id]; const before = p ? { d: p.d, due: p.due, b: p.b } : null;
    reveal(q); nextQ(); out.push({ id: q.id, ok, t: q.t || 3, before });
  }
  return out;
}, { n: n == null ? 1e9 : n, wrongEvery: wrongEvery || 0 });
const cloud = (store) => { const r = store.remote ? JSON.parse(store.remote) : null; return r ? { nq: Object.keys(r.q || {}).length, plan: r.plan ? { day: r.plan.day, pos: r.plan.pos, len: r.plan.ids.length } : null } : null; };
const T = {};

// A1：同一天。手机上午做完今日计划，停在小结页锁屏；电脑中午点“再加20题”做完；手机晚上拿起来（网通了、监听还没补发），点“回到今日”再点“再加20题”
// A1t：对照——手机上午点了“回到今日”才锁屏（停在今日页）
for (const variant of ['A1', 'A1t']) T[variant] = async (b) => {
  log(`\n== ${variant} [${SITE}] 同一天：手机做完计划${variant === 'A1' ? '停在小结页' : '回到今日页'}锁屏 → 电脑“再加20题” → 手机晚上“再加20题”`);
  const store = L.newStore();
  const ph = await L.device(b, { store, when: '2026-11-28T08:00:00', name: '手机', site: SITE });
  await L.planBtn(ph.pg, '开始').click(); await ph.pg.waitForSelector('#qcard'); await fastX(ph.pg, null, 4);
  if (variant === 'A1t') { await ph.pg.click('button:text-is("回到今日")'); await ph.pg.waitForSelector('.today'); }
  await ph.pg.waitForTimeout(1500); let s = await st(ph);
  log('手机 08:xx 锁屏前:', s.view, '|', s.text.slice(0, 60), '| 云端', JSON.stringify(cloud(store)));
  await L.lock(ph.pg); await ph.pg.waitForTimeout(300); await off(ph);
  const pc = await L.device(b, { store, when: '2026-11-28T13:00:00', name: '电脑', site: SITE });
  const pcBtn = pc.pg.locator('.panel.today button.primary').first(); const pcLabel = await pcBtn.textContent(); await pcBtn.click(); await pc.pg.waitForSelector('#qcard');
  const pcDid = await fastX(pc.pg, null, 5); await pc.pg.click('button:text-is("回到今日")'); await pc.pg.waitForSelector('.today'); await pc.pg.waitForTimeout(1500);
  log(`电脑 13:00 点“${pcLabel}”做了 ${pcDid.length} 题（新题 ${pcDid.filter((x) => !x.before).length}）| 云端`, JSON.stringify(cloud(store)));
  await L.setNow(ph.pg, '2026-11-28T20:00:00'); await onQuiet(ph); const g0 = (await st(ph)).gets; await L.unlock(ph.pg); await ph.pg.waitForTimeout(700); s = await st(ph);
  log(`手机 20:00 解锁后0.7秒: 页面=${s.view} waking=${s.waking} 向云端读了 ${s.gets - g0} 次 本机题数=${s.nq}（云端 ${cloud(store).nq}）`);
  if (variant === 'A1') { await ph.pg.click('button:text-is("回到今日")'); await ph.pg.waitForSelector('.today'); await ph.pg.waitForTimeout(150); s = await st(ph);
    log(`  点“回到今日”后: 按钮“${s.btn}” disabled=${s.disabled} waking=${s.waking} 读云端累计 ${s.gets - g0} 次 本机题数=${s.nq}`); }
  else log(`  今日页: 按钮“${s.btn}” disabled=${s.disabled} 本机题数=${s.nq}`);
  const btn = ph.pg.locator('.panel.today button.primary').first(); const label = await btn.textContent(); await btn.click(); await ph.pg.waitForSelector('#qcard');
  const pcIds = new Set(pcDid.map((x) => x.id));
  const one = await fastX(ph.pg, 1, 0); await ph.pg.waitForTimeout(1800); const rest = await fastX(ph.pg, null, 0); const all = one.concat(rest);
  const dup = all.filter((x) => pcIds.has(x.id));
  log(`  手机点“${label}”，这一组 ${all.length} 题：其中电脑中午刚做过的 ${dup.length} 道（第2题起作答前已是今天做过的 ${rest.filter((x) => x.before && x.before.d === '2026-11-28' && pcIds.has(x.id)).length} 道）`);
  await ph.pg.waitForTimeout(1500); s = await st(ph);
  log('  结束:', JSON.stringify({ 今天已答: await ph.pg.evaluate(() => S.prog.days[dayStr()].n), 本机题数: s.nq, 云端: cloud(store), errs: ph.errs.concat(pc.errs) }));
  await ph.ctx.close(); await pc.ctx.close();
};

// A2：隔天。第1天手机做计划25题、退出，又点一个模块练了3题，停在题目页锁屏；晚上电脑把计划做完；第2天上午电脑做新计划25题；
//     第2天晚上手机拿起来，网络晚 6 秒才连上（地铁里、刚解锁）：解锁后1秒点“退出”，再点今日页上的按钮
// A2t：对照——手机第1天退出到今日页才锁屏，同样的网络
const NETDELAY = Number(process.env.NETDELAY || 6000);
for (const variant of ['A2', 'A2t']) T[variant] = async (b) => {
  log(`\n== ${variant} [${SITE}] 隔天：手机第1天做25题后${variant === 'A2' ? '又进一个模块练习、停在题目页' : '停在今日页'}锁屏 → 电脑晚上做完、第2天上午做25题 → 手机第2天晚上（解锁后 ${NETDELAY / 1000} 秒网络才通）`);
  const store = L.newStore();
  const ph = await L.device(b, { store, when: '2026-11-28T08:00:00', name: '手机', site: SITE });
  await L.planBtn(ph.pg, '开始').click(); await ph.pg.waitForSelector('#qcard'); await fastX(ph.pg, 25, 4); await ph.pg.click('button:text-is("退出")'); await ph.pg.waitForSelector('.today');
  if (variant === 'A2') { await ph.pg.locator('button.mod').first().click(); await ph.pg.waitForSelector('#qcard'); await fastX(ph.pg, 3, 0); }
  await ph.pg.waitForTimeout(1500); let s = await st(ph);
  log('手机 第1天锁屏前:', s.view, s.run ? JSON.stringify(s.run) : '', '| 倒计时', s.countdown, '| 云端', JSON.stringify(cloud(store)));
  await L.lock(ph.pg); await ph.pg.waitForTimeout(300); await off(ph);
  const pc = await L.device(b, { store, when: '2026-11-28T21:00:00', name: '电脑', site: SITE });
  await L.planBtn(pc.pg, '继续').click(); await pc.pg.waitForSelector('#qcard'); const pcNight = await fastX(pc.pg, null, 4); await pc.pg.click('button:text-is("回到今日")'); await pc.pg.waitForSelector('.today'); await pc.pg.waitForTimeout(1500);
  log(`电脑 第1天21:00 接着做完计划：${pcNight.length} 题（新题 ${pcNight.filter((x) => !x.before).length}）| 云端`, JSON.stringify(cloud(store)));
  await L.setNow(pc.pg, '2026-11-29T09:00:00'); await L.unlock(pc.pg); await pc.pg.waitForTimeout(600);
  await L.planBtn(pc.pg, '开始').click(); await pc.pg.waitForSelector('#qcard'); const pcMorn = await fastX(pc.pg, 25, 4); await pc.pg.click('button:text-is("退出")'); await pc.pg.waitForSelector('.today'); await pc.pg.waitForTimeout(1500);
  const pcPlan = await pc.pg.evaluate(() => S.prog.plan.ids.slice());
  log(`电脑 第2天09:00 新计划做了 ${pcMorn.length} 题 | 云端`, JSON.stringify(cloud(store)));
  await L.setNow(ph.pg, '2026-11-29T20:00:00'); const g0 = (await st(ph)).gets; const t0 = Date.now(); await L.unlock(ph.pg);
  setTimeout(() => { onQuiet(ph).catch(() => {}); }, NETDELAY);
  await ph.pg.waitForTimeout(900); s = await st(ph);
  log(`手机 第2天20:00 解锁后1秒: 页面=${s.view} ${s.run ? s.run.label + ' ' + (s.run.pos + 1) + '/' + s.run.len : ''} 倒计时“${s.countdown}” waking=${s.waking} 本机题数=${s.nq}（云端 ${cloud(store).nq}）`);
  if (s.run) { await ph.pg.click('button:text-is("退出")'); await ph.pg.waitForSelector('.today'); await ph.pg.waitForTimeout(150); s = await st(ph); }
  log(`  今日页（解锁后 ${((Date.now() - t0) / 1000).toFixed(1)} 秒）: “${s.text.slice(0, 44)}” 按钮“${s.btn}” disabled=${s.disabled} waking=${s.waking} 本机题数=${s.nq}`);
  let waited = 0; while (s.disabled && waited < 14000) { await ph.pg.waitForTimeout(250); waited += 250; s = await st(ph); }
  if (waited) log(`  按钮灰了约 ${(waited / 1000).toFixed(1)} 秒后可点（解锁后 ${((Date.now() - t0) / 1000).toFixed(1)} 秒）: “${s.text.slice(0, 44)}” 按钮“${s.btn}” 本机题数=${s.nq} 提示“${s.note}”`);
  const label = s.btn; await L.planBtn(ph.pg, label).click(); await ph.pg.waitForSelector('#qcard');
  const nightIds = new Set(pcNight.map((x) => x.id)), mornIds = new Set(pcMorn.map((x) => x.id));
  const one = await fastX(ph.pg, 1, 0);
  let w2 = 0; while ((await st(ph)).nq < cloud(store).nq && w2 < 40000) { await ph.pg.waitForTimeout(500); w2 += 500; }      // 等网络通了、记录并进来
  await ph.pg.waitForTimeout(800); s = await st(ph);
  log(`  点“${label}”答了第1题；记录并进来后（又等了 ${(w2 / 1000).toFixed(1)} 秒）: 页面=${s.view} ${s.run ? s.run.label + ' ' + (s.run.pos + 1) + '/' + s.run.len : ''} 本机题数=${s.nq}`);
  const rest = await fastX(ph.pg, null, 0); const all = one.concat(rest);
  const again = all.filter((x) => nightIds.has(x.id)), againNotDue = rest.filter((x) => nightIds.has(x.id) && x.before && x.before.due > '2026-11-29');
  log(`  手机这一组实际答了 ${all.length} 题：电脑昨晚做过的 ${again.length} 道（其中作答前记录已显示“今天不到期”的 ${againNotDue.length} 道）、电脑今天上午做过的 ${all.filter((x) => mornIds.has(x.id)).length} 道`);
  await ph.pg.waitForTimeout(1800); await pc.pg.waitForTimeout(300);
  const fin = await ph.pg.evaluate((pcPlan) => { const t = S.prog.plan; const P = S.prog.q; return { 手机面板计划: t ? `${t.pos}/${t.ids.length}` : null, 还是电脑排的那份: t ? pcPlan.every((id) => t.ids.includes(id)) : null, 电脑那份里今天没做到的: pcPlan.filter((id) => !(P[id] && P[id].d === dayStr())).length, 今天已答: S.prog.days[dayStr()].n,
    核心已学: S.qs.filter((q) => q.t === 1 && P[q.id]).length }; }, pcPlan);
  log('  结束:', JSON.stringify(fin), '| 云端', JSON.stringify(cloud(store)), '| errs', JSON.stringify(ph.errs.concat(pc.errs)));
  await ph.ctx.close(); await pc.ctx.close();
};

(async () => {
  const b = await L.launch();
  for (const k of Object.keys(T)) { if (ONLY.length && !ONLY.includes(k)) continue; try { await T[k](b); } catch (e) { log('  ✗ 脚本出错', String(e && e.stack || e).slice(0, 700)); } }
  await b.close();
})();
