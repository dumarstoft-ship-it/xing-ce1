// 第7版修正的补充测试：睡醒后重新核对云端、零点换日、限次补写、清除、考试当天的文字、热更新带过来的做题页。
// 用法：SITE=<站点目录> node t_wake.js [只跑哪几项，如 A,C]
const L = require('./lib');
const ONLY = (process.argv[2] || '').split(',').filter(Boolean);
let fails = 0;
const ok = (cond, name, extra) => { console.log(`  ${cond ? '✓' : '✗'} ${name}${extra === undefined ? '' : '  ' + (typeof extra === 'string' ? extra : JSON.stringify(extra))}`); if (!cond) fails++; };
const off = (d) => d.pg.evaluate(() => { window.__online = false; });
const onQuiet = (d) => d.pg.evaluate(() => { window.__online = true; });          // 网通了，但监听不补发快照
const st = (d) => d.pg.evaluate(() => {
  const el = document.querySelector('.panel.today'); const btn = el && el.querySelector('button.primary');
  return { day: dayStr(), view: S.run ? (document.querySelector('#qcard') ? 'q' : 'sum') : 'today', btn: btn ? btn.textContent : null, disabled: btn ? btn.disabled : null,
    text: el ? el.innerText.replace(/\s+/g, ' ') : document.querySelector('#main').innerText.replace(/\s+/g, ' ').slice(0, 200),
    cloud: S.cloud, synced: !!S.synced, note: S.cloudNote, nq: Object.keys(S.prog.q).length, plan: S.prog.plan ? { day: S.prog.plan.day, pos: S.prog.plan.pos, len: S.prog.plan.ids.length } : null,
    run: S.run ? { tkey: S.run.tkey, day: S.run.day, pos: S.run.pos, len: S.run.list.length } : null, gets: window.__gets || 0, sets: window.__sets || 0, countdown: document.querySelector('#countdown').innerText };
});
const cloudNq = (store) => (store.remote ? Object.keys(JSON.parse(store.remote).q || {}).length : 0);
const T = {};

// A 睡醒时没网，超过10秒：先放行并提示；之后做的题，网一通（云端没有新变化、监听不补发）也要推上去
T.A = async (b) => {
  console.log('A 睡醒时没网（超过10秒），之后做题，再连上');
  const store = L.newStore(); const d = await L.device(b, { store, when: '2026-11-28T09:00:00', name: '手机' });
  await L.planBtn(d.pg, '开始').click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, 5, 0); await d.pg.click('button:text-is("退出")'); await d.pg.waitForSelector('.today'); await d.pg.waitForTimeout(1500);
  ok(cloudNq(store) === 5, '先做5题，云端5题', cloudNq(store));
  await off(d); await L.setNow(d.pg, '2026-11-28T15:00:00'); await L.wake(d.pg); await d.pg.waitForTimeout(300);
  let s = await st(d);
  ok(s.disabled === true && /正在同步云端/.test(s.text), '拿起来：“继续”先不可点，有“正在同步”的提示', { btn: s.btn, disabled: s.disabled });
  ok(s.synced === true, '这道闸不关写入（synced 仍为真）');
  await d.pg.waitForTimeout(10300); s = await st(d);
  ok(s.disabled === false, '10秒后放行', { btn: s.btn, disabled: s.disabled });
  ok(/暂时连不上/.test(s.note) && s.cloud === 'slow', '放行时有“云端暂时连不上”的提示', { cloud: s.cloud, note: s.note });
  await L.planBtn(d.pg, '继续').click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, 3, 0); await d.pg.click('button:text-is("退出")'); await d.pg.waitForSelector('.today');
  await d.pg.waitForTimeout(1500); s = await st(d);
  ok(s.nq === 8 && cloudNq(store) === 5, '没网时又做3题：本机8题，云端还是5题', { local: s.nq, cloud: cloudNq(store) });
  await onQuiet(d); let waited = 0; while (cloudNq(store) < 8 && waited < 75000) { await d.pg.waitForTimeout(1000); waited += 1000; }
  s = await st(d);
  ok(cloudNq(store) === 8, '网通后（云端没有新变化）自己把这3题推上去了', { cloud: cloudNq(store), waitedMs: waited });
  ok(s.cloud === 'ok' && !s.note, '提示消掉了', { cloud: s.cloud, note: s.note });
  ok(d.errs.length === 0, '无报错', d.errs);
  await d.ctx.close();
};

// B 睡醒时有网、云端已被另一台设备推进：面板直接变成新的进度，中间不会照旧记录开始
T.B = async (b) => {
  console.log('B 睡醒时有网，云端已被另一台设备推进');
  const store = L.newStore(); const ph = await L.device(b, { store, when: '2026-11-28T09:00:00', name: '手机' });
  await L.planBtn(ph.pg, '开始').click(); await ph.pg.waitForSelector('#qcard'); await L.fastN(ph.pg, 5, 0); await ph.pg.click('button:text-is("退出")'); await ph.pg.waitForSelector('.today'); await ph.pg.waitForTimeout(1500);
  await off(ph);                                   // 手机锁屏：收不到推送
  const pc = await L.device(b, { store, when: '2026-11-28T12:00:00', name: '电脑' });
  await L.planBtn(pc.pg, '继续').click(); await pc.pg.waitForSelector('#qcard'); await L.fastN(pc.pg, 20, 0); await pc.pg.click('button:text-is("退出")'); await pc.pg.waitForSelector('.today'); await pc.pg.waitForTimeout(1500);
  ok(cloudNq(store) === 25, '电脑接着做20题，云端25题', cloudNq(store));
  await L.setNow(ph.pg, '2026-11-28T18:00:00'); await onQuiet(ph);     // 网是通的，但监听没有补发：只能靠睡醒后主动读
  const g0 = (await st(ph)).gets; await L.wake(ph.pg); await ph.pg.waitForTimeout(600);
  const s = await st(ph);
  ok(s.gets > g0, '拿起来时主动向云端读了一次', { before: g0, after: s.gets });
  ok(s.nq === 25 && s.plan.pos === 25 && /已做25题/.test(s.text), '面板变成“已做25题”', { nq: s.nq, plan: s.plan });
  ok(s.disabled === false && s.cloud === 'ok', '读到后按钮可点', { disabled: s.disabled, cloud: s.cloud });
  ok(ph.errs.concat(pc.errs).length === 0, '无报错', ph.errs.concat(pc.errs));
  await ph.ctx.close(); await pc.ctx.close();
};

// C 电脑睡了一阵刚醒、页面一直在眼前（没有回到前台的事件）：20秒内自己发现并核对
T.C = async (b) => {
  console.log('C 没有“回到前台”的事件（电脑合盖再打开），页面自己发现');
  const store = L.newStore(); const d = await L.device(b, { store, when: '2026-11-28T09:00:00', name: '电脑' });
  const g0 = (await st(d)).gets; await L.setNow(d.pg, '2026-11-28T13:00:00');
  let waited = 0, s = await st(d); while (s.gets === g0 && waited < 24000) { await d.pg.waitForTimeout(1000); waited += 1000; s = await st(d); }
  ok(s.gets > g0, '页面自己向云端读了一次', { waitedMs: waited, gets: s.gets });
  ok(s.disabled === false && s.cloud === 'ok', '读完按钮可点', { disabled: s.disabled, cloud: s.cloud });
  const g1 = s.gets; await d.pg.waitForTimeout(22000); s = await st(d);
  ok(s.gets === g1, '之后不再重复读', { gets: s.gets });
  ok(d.errs.length === 0, '无报错', d.errs);
  await d.ctx.close();
};

// D 题目页开着没人动、过了零点：20秒内收起昨天那组，回到今日页（新的一天）
T.D = async (b) => {
  console.log('D 题目页开着没人动，过了零点');
  const d = await L.device(b, { when: '2026-11-28T23:59:40', name: '手机' });
  await L.planBtn(d.pg, '开始').click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, 2, 0);
  await d.pg.evaluate(() => { lastAct = Date.now() - 130000; });       // 当作已经两分多钟没碰过
  let waited = 0, s = await st(d); while (s.view !== 'today' && waited < 45000) { await d.pg.waitForTimeout(1000); waited += 1000; s = await st(d); }
  ok(s.view === 'today' && s.day === '2026-11-29', '回到了今日页，日期是29日', { view: s.view, day: s.day, waitedMs: waited });
  ok(/还有 7 天/.test(s.countdown) && s.btn === '开始', '倒计时变成7天，面板是新一天的“开始”', { countdown: s.countdown, btn: s.btn });
  ok(d.errs.length === 0, '无报错', d.errs);
  await d.ctx.close();
};

// E 一直在做题、跨过零点：不打断；过了零点答的题不再写进昨天那一组；做完回今日页是新一天的计划
T.E = async (b) => {
  console.log('E 一直在做题，跨过零点');
  const d = await L.device(b, { when: '2026-11-28T23:59:35', name: '手机' });
  await L.planBtn(d.pg, '开始').click(); await d.pg.waitForSelector('#qcard');
  const t0 = Date.now(); let n = 0, kicked = false;
  while (Date.now() - t0 < 50000) { const r = await L.answerUI(d.pg, true); if (!r) { kicked = true; break; } n++; await d.pg.waitForTimeout(1200); }
  const s = await st(d);
  ok(!kicked && s.view === 'q', `连着答了${n}题，没有被打断`, { view: s.view, run: s.run });
  const info = await d.pg.evaluate(() => ({ plan: S.prog.plan, d28: Object.values(S.prog.q).filter((p) => p.d === '2026-11-28').length, d29: Object.values(S.prog.q).filter((p) => p.d === '2026-11-29').length }));
  ok(info.d29 > 0 && info.d28 > 0, '零点前后都有作答', { d28: info.d28, d29: info.d29 });
  ok(info.plan.day === '2026-11-28' && info.plan.pos === info.d28, '昨天那一组停在零点前的位置', { planPos: info.plan.pos, d28: info.d28 });
  ok(s.run.tkey === '', '眼前这组已经和题组脱钩（当普通练习做完）', s.run);
  await d.pg.click('button:text-is("退出")'); await d.pg.waitForSelector('.today'); const s2 = await st(d);
  ok(s2.day === '2026-11-29' && s2.btn === '开始', '退出后是新一天的计划', { day: s2.day, btn: s2.btn, text: s2.text.slice(0, 60) });
  const dup = await d.pg.evaluate(() => { const p = planParts(dailyOf()); return p.list.filter((q) => S.prog.q[q.id] && S.prog.q[q.id].d === dayStr()).length; });
  ok(dup === 0, '新计划里没有今天（零点后）已经做过的题', dup);
  ok(d.errs.length === 0, '无报错', d.errs);
  await d.ctx.close();
};

// F 另一头总把云端改回旧的一份：同一份内容最多写3次就不再顶；有新改动时照常写
T.F = async (b) => {
  console.log('F 云端总被改回旧的一份（来回顶的情形）');
  const store = L.newStore(); const d = await L.device(b, { store, when: '2026-11-28T09:00:00', name: '手机' });
  await L.planBtn(d.pg, '开始').click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, 3, 0); await d.pg.waitForTimeout(1500);
  const oldDoc = store.remote;                           // 3题时的云端
  await L.fastN(d.pg, 1, 0); await d.pg.waitForTimeout(1500);
  ok(cloudNq(store) === 4, '第4题写上云端', cloudNq(store));
  let seen = store.sets, reverted = 0; const t0 = Date.now();
  while (Date.now() - t0 < 25000) {                       // 每次它写上去，就把云端改回3题的那份
    if (store.sets !== seen || cloudNq(store) === 4) { seen = store.sets; store.remote = oldDoc; reverted++; await d.pg.evaluate(() => window.__emit()); }
    await d.pg.waitForTimeout(300);
  }
  const sameWrites = store.sets;
  const quiet0 = store.sets; await d.pg.waitForTimeout(6000);
  ok(reverted >= 3 && reverted <= 4, '同一份内容写了3次后不再顶回去', { reverted, sets: store.sets });
  ok(store.sets === quiet0, '之后安静下来', { sets: store.sets });
  ok((await st(d)).nq === 4, '本机的4题都在');
  await L.fastN(d.pg, 1, 0); await d.pg.waitForTimeout(2500);
  ok(cloudNq(store) === 5 && store.sets === sameWrites + 1, '再做一题（内容变了）照常写上去', { cloud: cloudNq(store), sets: store.sets - sameWrites });
  ok(d.errs.length === 0, '无报错', d.errs);
  await d.ctx.close();
};

// G 清除全部记录：设置和它的改动时间留着，清除时间、更新时间只往后走
T.G = async (b) => {
  console.log('G 清除全部记录');
  const d = await L.device(b, { when: '2026-11-28T09:00:00', name: '手机' });
  await d.pg.evaluate(() => { S.prog.settings.daily = 80; touch(); S.prog.epoch = '2026-11-28T05:00:00.000Z'; S.prog.updated = '2026-11-28T06:00:00.000Z'; saveLocal(); });   // 另一台设备时钟快：已有的清除时间、更新时间都比本机现在晚
  await L.planBtn(d.pg, '开始').click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, 2, 0); await d.pg.click('button:text-is("退出")');
  const before = await d.pg.evaluate(() => ({ st: S.prog.st, updated: S.prog.updated, epoch: S.prog.epoch }));
  await d.pg.click('#tabs a[href="#stats"]'); await d.pg.waitForSelector('#resetBtn'); await d.pg.click('#resetBtn'); await d.pg.click('#resetBtn'); await d.pg.waitForTimeout(200);
  const a = await d.pg.evaluate(() => ({ nq: Object.keys(S.prog.q).length, st: S.prog.st, updated: S.prog.updated, epoch: S.prog.epoch, daily: S.prog.settings.daily, plan: S.prog.plan }));
  ok(a.nq === 0 && a.plan === null, '记录清空', a.nq);
  ok(a.daily === 80 && a.st === before.st && !!a.st, '设置和它的改动时间留着', { daily: a.daily, st: a.st });
  ok(a.epoch > before.epoch && a.updated > before.updated, '清除时间、更新时间都比原来的晚', { epoch: [before.epoch, a.epoch], updated: [before.updated, a.updated] });
  ok(d.errs.length === 0, '无报错', d.errs);
  await d.ctx.close();
};

// H 考试当天、考前一天的文字：不出现对不上的“明天”
T.H = async (b) => {
  console.log('H 考试当天和考前一天的文字');
  const seed = await L.device(b, { when: '2026-12-04T09:00:00', name: 'seed' });
  await L.planBtn(seed.pg, '开始').click(); await seed.pg.waitForSelector('#qcard'); await L.fastN(seed.pg, null, 4); await seed.pg.click('button:text-is("回到今日")');
  const local = await seed.pg.evaluate(() => localStorage.getItem('mzbx-progress-v1')); await seed.ctx.close();
  for (const [when, label] of [['2026-12-05T09:00:00', '考前一天'], ['2026-12-06T07:00:00', '考试当天']]) {
    const d = await L.device(b, { when, local, name: label }); const exam = label === '考试当天';
    let s = await st(d);
    ok(s.btn === '开始' && (exam ? /今天考试/.test(s.text) : /考前两天/.test(s.text)), `${label}：未开始的面板有说明`, s.text.slice(0, 90));
    await L.planBtn(d.pg, '开始').click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, 3, 2); await d.pg.click('button:text-is("退出")'); await d.pg.waitForSelector('.today'); s = await st(d);
    ok(exam ? !/明天/.test(s.text.split('核心已学')[0]) : /明天考试，不上新题/.test(s.text), `${label}：进行中的面板`, s.text.slice(0, 110));
    await L.planBtn(d.pg, '继续').click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, null, 5);
    const sum = await L.mainText(d.pg, 160);
    ok(exam ? !/明天/.test(sum) : /明天/.test(sum), `${label}：小结页`, sum.slice(0, 100));
    await d.pg.click('button:text-is("回到今日")'); await d.pg.waitForSelector('.today'); s = await st(d);
    ok(exam ? /今天考试，做到这里就可以了/.test(s.text) && /今天不再加题/.test(s.text) && !/明天/.test(s.text.split('核心已学')[0]) : /答错的明天先出（当天重做不算过关）。/.test(s.text) && !/隔2天/.test(s.text), `${label}：做完的面板`, s.text.slice(0, 120));
    if (!exam) {
      const more = await d.pg.evaluate(() => { const t = S.prog.plan; const m = planParts(20, new Set(t.ids)); const btn = [...document.querySelectorAll('.panel.today button')].find((x) => /^再加/.test(x.textContent)); return { len: m.list.length, fresh: m.list.filter((q) => !S.prog.q[q.id]).length, btn: btn ? btn.textContent : null }; });
      ok(more.btn === (more.len ? `再加${more.len}题（${more.fresh ? `新题${more.fresh}道` : '都是复习'}）` : null), '“再加”按钮上的新题数和实际清单一致', more);
    }
    ok(d.errs.length === 0, `${label}：无报错`, d.errs); await d.ctx.close();
  }
};

// I 热更新（重新发布时页面自动换新版）带过来的做题页：旧版快照里没有“哪天的”，新版要认它是今天这一组并接着写
T.I = async (b) => {
  console.log('I 热更新带过来的做题页');
  const one = await L.device(b, { when: '2026-11-28T09:00:00', name: 'v7' });
  await L.planBtn(one.pg, '开始').click(); await one.pg.waitForSelector('#qcard'); await L.fastN(one.pg, 3, 0);
  const snap = await one.pg.evaluate(() => ({ local: localStorage.getItem('mzbx-progress-v1'), run: { ids: S.run.list.map((q) => q.id), pos: S.run.pos, res: S.run.res, label: S.run.label, tkey: S.run.tkey, mode: S.run.mode } }));
  await one.ctx.close();
  const two = await L.device(b, { when: '2026-11-28T09:05:00', local: snap.local, name: 'v7c', waitFor: '#qcard', init: (run) => { window.claude = window.claude || {}; window.claude.hot = { data: { run } }; }, initArg: snap.run });
  let s = await st(two);
  ok(s.view === 'q' && s.run.pos === 3 && s.run.day === '2026-11-28' && s.run.tkey === 'plan', '回到第4题，认得是今天这一组', s.run);
  await L.fastN(two.pg, 2, 0); s = await st(two);
  ok(s.plan.pos === 5 && s.run.tkey === 'plan', '接着做2题，题组位置跟到5', { plan: s.plan, run: s.run });
  ok(two.errs.length === 0, '无报错', two.errs); await two.ctx.close();
  // 自选练习的做题页（没有题组）热更新过来：换日后不该被收起
  const three = await L.device(b, { when: '2026-11-28T23:59:50', local: snap.local, name: 'v7c-练习', waitFor: '#qcard', init: (run) => { window.claude = window.claude || {}; window.claude.hot = { data: { run } }; }, initArg: { ...snap.run, tkey: '', label: '自选练习' } });
  await three.pg.evaluate(() => { lastAct = Date.now() - 130000; }); await three.pg.waitForTimeout(32000); s = await st(three);
  ok(s.view === 'q' && s.day === '2026-11-29', '自选练习的做题页过了零点还在', { view: s.view, day: s.day, run: s.run });
  ok(three.errs.length === 0, '无报错', three.errs); await three.ctx.close();
};

(async () => {
  const b = await L.launch();
  for (const k of Object.keys(T)) { if (ONLY.length && !ONLY.includes(k)) continue; try { await T[k](b); } catch (e) { fails++; console.log('  ✗ 脚本出错', String(e && e.stack || e).slice(0, 600)); } }
  await b.close();
  console.log(fails ? `\n有 ${fails} 项没通过` : '\n全部通过'); process.exit(fails ? 1 : 0);
})();
