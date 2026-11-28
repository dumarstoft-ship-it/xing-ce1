// walk 路线1（续）：题目页睡醒（选了选项没提交、看着解析）、连着锁屏解锁好几次（没网）、网很慢
// 用法：SITEDIR=site_c|site_b|site_fix node w3_more.js [Q1,Q2,...]
const L = require('./lib');
const SITE = process.env.SITEDIR || 'site_c';
const ONLY = (process.argv[2] || '').split(',').filter(Boolean);
const log = (...a) => console.log(...a); const j = (o) => JSON.stringify(o);
const off = (d) => d.pg.evaluate(() => { window.__online = false; });
const onQuiet = (d) => d.pg.evaluate(() => { window.__online = true; });
const onLive = (d) => d.pg.evaluate(() => { window.__online = true; return window.__emit(); });
const ui = (d) => d.pg.evaluate(() => {
  const q = (s) => document.querySelector(s); const el = q('.panel.today'); const btn = el && el.querySelector('button.primary');
  return { 页: S.run ? (q('#qcard') ? '题目页' : '小结页') : current(), 日: dayStr(), 倒计时: q('#countdown').innerText.replace(/\s+/g, ''), 位置: S.run ? `${S.run.label} ${q('.runbar .pos') ? q('.runbar .pos').textContent : '完'}` : undefined,
    题号: S.run && S.run.list[runState && runState.revealed ? S.run.pos - 1 : S.run.pos] ? S.run.list[runState && runState.revealed ? S.run.pos - 1 : S.run.pos].id : undefined,
    已选: q('#qcard') ? [...document.querySelectorAll('#qcard .opt.sel')].map((e) => e.dataset.v).join('') : undefined, 已出解析: q('#qcard') ? !!q('.verdict') : undefined, 展开的卡: document.querySelectorAll('details.card[open]').length || undefined,
    错因框: q('#whyIn') ? q('#whyIn').value : undefined, 滚动: Math.round(window.scrollY),
    按钮: btn ? btn.textContent + (btn.disabled ? '(灰)' : '') : undefined, 面板: el ? el.innerText.replace(/\s+/g, ' ').slice(0, 46) : undefined,
    提示: [...document.querySelectorAll('#main .note')].map((e) => e.textContent).filter((t) => /同步|连不上/.test(t)).join(' / ') || '无',
    cloud: S.cloud, 本机题数: Object.keys(S.prog.q).length, 读云端: window.__gets || 0, 写云端: window.__sets || 0 };
});
const cloudNq = (store) => (store.remote ? Object.keys(JSON.parse(store.remote).q || {}).length : 0);
const T = {};
async function toMulti(pg) {      // 一直答到眼前是一道多选题
  for (let i = 0; i < 49; i++) { const t = await pg.evaluate(() => S.run.list[S.run.pos].type); if (t === '多选') return true; await L.fastN(pg, 1, 0); }
  return false;
}
// Q1 多选题选了两项没提交 → 锁屏 → 同一天解锁；之后电脑做了别的题（监听送到）；再之后电脑做了眼前这道题
T.Q1 = async (b) => {
  log(`\n== Q1 [${SITE}] 题目页：多选题选了两项还没提交，锁屏，同一天再拿起来`);
  const store = L.newStore(); const ph = await L.device(b, { store, when: '2026-11-28T08:00:00', name: '手机', site: SITE });
  await L.planBtn(ph.pg, '开始').click(); await ph.pg.waitForSelector('#qcard'); const found = await toMulti(ph.pg); if (!found) { log('  计划里没有多选题，跳过'); await ph.ctx.close(); return; }
  const opts = ph.pg.locator('#qcard .opts .opt'); await opts.nth(0).click(); await opts.nth(2).click(); await ph.pg.waitForTimeout(1300);
  log('  锁屏前    ', j(await ui(ph))); const cur = await ph.pg.evaluate(() => S.run.list[S.run.pos].id);
  await L.lock(ph.pg); await off(ph); await L.setNow(ph.pg, '2026-11-28T14:00:00'); await onQuiet(ph); await L.unlock(ph.pg); await ph.pg.waitForTimeout(1500);
  log('  解锁1.5秒  ', j(await ui(ph)));
  // 电脑做计划里后面的3题（不含眼前这道）：直接改云端文档，再让监听送到
  const bump = async (ids) => { const r = JSON.parse(store.remote); for (const id of ids) r.q[id] = { n: 1, c: 1, l: 1, b: 1, f: '2026-11-28', d: '2026-11-28', due: '2026-11-30', f1: 1 }; r.days['2026-11-28'].n += ids.length; r.days['2026-11-28'].c += ids.length; r.updated = new Date(new Date(r.updated).getTime() + 5000).toISOString(); store.remote = JSON.stringify(L.sortKeys(r)); await ph.pg.evaluate(() => window.__emit()); await ph.pg.waitForTimeout(400); };
  const later = await ph.pg.evaluate(() => S.run.list.slice(S.run.pos + 3, S.run.pos + 6).map((q) => q.id));
  await bump(later); log('  电脑做了后面3题、监听送到', j(await ui(ph)));
  await bump([cur]); log('  电脑做了眼前这道题、监听送到', j(await ui(ph)));
  if (ph.errs.length) log('  报错', j(ph.errs)); await ph.ctx.close();
};
// Q2 看着解析（展开了相关卡片、往下滚）→ 锁屏 → 同一天解锁、云端有新记录；隔天解锁
T.Q2 = async (b) => {
  log(`\n== Q2 [${SITE}] 题目页：答完看着解析（展开了一张相关卡片），锁屏`);
  for (const [wakeAt, label] of [['2026-11-28T14:00:00', '同一天'], ['2026-11-29T07:30:00', '隔一天']]) {
    const store = L.newStore(); const ph = await L.device(b, { store, when: '2026-11-28T08:00:00', name: '手机', site: SITE });
    await L.planBtn(ph.pg, '开始').click(); await ph.pg.waitForSelector('#qcard'); await L.fastN(ph.pg, 4, 0); await L.answerUI(ph.pg, true).catch(() => {});
    // answerUI 会点“下一题”；这里再答一题但不点下一题
    const info = await ph.pg.evaluate(() => { const q = S.run.list[S.run.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer; return { type: q.type, picks: q.type === '判断' ? [ans] : ans.split('') }; });
    for (const v of info.picks) await ph.pg.click(`#qcard .opt[data-v="${v}"]`); if (info.type === '多选') await ph.pg.click('#submitMulti');
    const det = ph.pg.locator('#afterArea details.card summary').first(); if (await det.count()) await det.click(); await ph.pg.evaluate(() => window.scrollTo(0, 200)); await ph.pg.waitForTimeout(1300);
    log(`  [${label}] 锁屏前   `, j(await ui(ph)));
    await L.lock(ph.pg); await off(ph);
    const r = JSON.parse(store.remote); const extra = await ph.pg.evaluate(() => S.run.list.slice(S.run.pos + 2, S.run.pos + 5).map((q) => q.id)); for (const id of extra) r.q[id] = { n: 1, c: 1, l: 1, b: 1, f: '2026-11-28', d: '2026-11-28', due: '2026-11-30', f1: 1 }; r.updated = new Date(new Date(r.updated).getTime() + 5000).toISOString(); store.remote = JSON.stringify(L.sortKeys(r));
    await L.setNow(ph.pg, wakeAt); await onLive(ph); await L.unlock(ph.pg); await ph.pg.waitForTimeout(1500);
    log(`  [${label}] 解锁1.5秒 `, j(await ui(ph)));
    if (ph.errs.length) log('  报错', j(ph.errs)); await ph.ctx.close();
  }
};
// Q5 今日页，没网，连着锁屏、解锁3次（每次隔3分钟）；之后网通了；再做3题
T.Q5 = async (b) => {
  log(`\n== Q5 [${SITE}] 今日页：没网时连着锁屏、解锁3次（每次隔3分钟），之后网通了，再做3题`);
  const store = L.newStore(); const ph = await L.device(b, { store, when: '2026-11-28T08:00:00', name: '手机', site: SITE });
  await L.planBtn(ph.pg, '开始').click(); await ph.pg.waitForSelector('#qcard'); await L.fastN(ph.pg, 5, 0); await ph.pg.click('button:text-is("退出")'); await ph.pg.waitForSelector('.today'); await ph.pg.waitForTimeout(1300);
  let now = new Date('2026-11-28T08:00:30').getTime();
  for (let k = 1; k <= 3; k++) {
    await L.lock(ph.pg); await off(ph); now += 180000; await L.setNow(ph.pg, now); const t0 = Date.now(); await L.unlock(ph.pg); await ph.pg.waitForTimeout(200);
    let s = await ui(ph); const first = s; let grey = 0; while (/灰/.test(s.按钮 || '') && Date.now() - t0 < 13000) { await ph.pg.waitForTimeout(250); s = await ui(ph); grey = Date.now() - t0; }
    log(`  第${k}次解锁: 刚解锁 按钮=${first.按钮} 提示=“${first.提示}”；灰了约 ${(grey / 1000).toFixed(1)} 秒；放行后 按钮=${s.按钮} 提示=“${s.提示}” cloud=${s.cloud} 读云端=${s.读云端}`);
    now += Date.now() - t0;
  }
  // 没网时做2题
  await L.planBtn(ph.pg, '继续').click(); await ph.pg.waitForSelector('#qcard'); await L.fastN(ph.pg, 2, 0); await ph.pg.click('button:text-is("退出")'); await ph.pg.waitForSelector('.today'); await ph.pg.waitForTimeout(1200);
  log(`  没网时做2题: 本机 ${(await ui(ph)).本机题数} 云端 ${cloudNq(store)}`);
  await onQuiet(ph); const t1 = Date.now(); let s = await ui(ph); while ((s.cloud !== 'ok' || cloudNq(store) < 7) && Date.now() - t1 < 70000) { await ph.pg.waitForTimeout(500); s = await ui(ph); }
  log(`  网通后 ${((Date.now() - t1) / 1000).toFixed(1)} 秒: cloud=${s.cloud} 提示=“${s.提示}” 云端题数 ${cloudNq(store)}（本机 ${s.本机题数}）`);
  await L.planBtn(ph.pg, '继续').click(); await ph.pg.waitForSelector('#qcard'); await L.fastN(ph.pg, 3, 0); await ph.pg.click('button:text-is("退出")'); await ph.pg.waitForSelector('.today'); await ph.pg.waitForTimeout(1500); s = await ui(ph);
  log(`  再做3题: 本机 ${s.本机题数} 云端 ${cloudNq(store)} 面板“${s.面板}” 写云端累计 ${s.写云端} 次`);
  await ph.pg.waitForTimeout(5000); log(`  静置5秒后写云端累计 ${(await ui(ph)).写云端} 次`);
  if (ph.errs.length) log('  报错', j(ph.errs)); await ph.ctx.close();
};
// Q6 网很慢：云端每次读写要 3 秒 / 12 秒
T.Q6 = async (b) => {
  for (const lag of [3000, 12000]) {
    log(`\n== Q6 [${SITE}] 今日页：睡醒后网很慢（云端每次读写 ${lag / 1000} 秒），电脑中间做了20题`);
    const store = L.newStore(); const ph = await L.device(b, { store, when: '2026-11-28T08:00:00', name: '手机', site: SITE });
    await L.planBtn(ph.pg, '开始').click(); await ph.pg.waitForSelector('#qcard'); await L.fastN(ph.pg, 5, 0); await ph.pg.click('button:text-is("退出")'); await ph.pg.waitForSelector('.today'); await ph.pg.waitForTimeout(1300);
    await L.lock(ph.pg); await off(ph);
    const pc = await L.device(b, { store, when: '2026-11-28T12:00:00', name: '电脑', site: SITE }); await L.planBtn(pc.pg, '继续').click(); await pc.pg.waitForSelector('#qcard'); await L.fastN(pc.pg, 20, 0); await pc.pg.click('button:text-is("退出")'); await pc.pg.waitForTimeout(1400); await pc.ctx.close();
    await L.setNow(ph.pg, '2026-11-28T18:00:00'); await ph.pg.evaluate((lag) => { window.__lag = lag; window.__online = true; }, lag); const t0 = Date.now(); await L.unlock(ph.pg);
    let last = '', s; while (Date.now() - t0 < lag + 4000) { s = await ui(ph); const line = `按钮=${s.按钮} 面板“${s.面板}” 提示=“${s.提示}” cloud=${s.cloud}`; if (line !== last) { log(`  解锁后 ${((Date.now() - t0) / 1000).toFixed(1)} 秒: ${line}`); last = line; } await ph.pg.waitForTimeout(250); }
    if (ph.errs.length) log('  报错', j(ph.errs)); await ph.ctx.close();
  }
};
(async () => {
  const b = await L.launch();
  for (const k of Object.keys(T)) { if (ONLY.length && !ONLY.includes(k)) continue; try { await T[k](b); } catch (e) { log('  ✗ 脚本出错', k, String(e && e.stack || e).slice(0, 500)); } }
  await b.close();
})();
