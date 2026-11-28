// 离线单文件版（照 build_single.py 用 v7c 打的）：做题、切后台再回来、电脑睡醒、过零点，看新加的心跳和睡醒核对出不出错、有没有奇怪的提示
// 用法：node t1_single.js
const L = require('./mylib'); const path = require('path');
const SINGLE = path.join(L.HERE, 'single', 'v7c_single.html');
(async () => {
  const b = await L.launch();
  console.log('一、单文件版（经 http 路由打开），23:40 开始');
  const d = await L.open(b, { single: SINGLE, when: '2026-11-28T23:40:00+08:00', beatMs: 1500 });
  let s = await L.st(d);
  L.ok(s.cloud === 'local' && /只存在这台设备/.test(s.note), '没有云端：cloud=local，提示是“只存在这台设备的浏览器里”', { cloud: s.cloud, note: s.note });
  L.ok(s.btn === '开始' && s.disabled === false && !/正在同步/.test(s.text), '“开始”可点，没有“正在同步”', { btn: s.btn, disabled: s.disabled });
  L.ok(s.chk.length === 0, '版面无怪字样、无横向溢出', s.chk);
  await L.planBtn(d.pg, '开始').click(); await d.pg.waitForSelector('#qcard');
  for (let i = 0; i < 3; i++) await L.answerUI(d.pg, i !== 1);
  s = await L.st(d); L.ok(s.view === 'q' && s.run.pos === 3 && s.plan.pos === 3, '点着做了3题（题组位置跟着走）', { run: s.run, plan: s.plan });
  // 切后台5分钟再回来（做题中）
  await d.pg.evaluate(() => window.__hide()); await d.pg.evaluate(() => window.__addNow(5 * 60000)); await d.pg.evaluate(() => window.__show()); await d.pg.waitForTimeout(300);
  s = await L.st(d); L.ok(s.view === 'q' && s.run.pos === 3 && s.cloud === 'local' && s.waking === false, '做题中切后台5分钟再回来：还在第4题，没有进入“核对云端”', { view: s.view, run: s.run, waking: s.waking });
  await d.pg.click('button:text-is("退出")'); await d.pg.waitForSelector('.today');
  // 今日页切后台3分钟再回来
  await d.pg.evaluate(() => window.__hide()); await d.pg.evaluate(() => window.__addNow(3 * 60000)); await d.pg.evaluate(() => window.__show()); await d.pg.waitForTimeout(300);
  s = await L.st(d);
  L.ok(s.btn === '继续' && s.disabled === false && s.waking === false && !/正在同步/.test(s.text), '今日页切后台3分钟再回来：“继续”可点，没有“正在同步”', { btn: s.btn, disabled: s.disabled, waking: s.waking, text: s.text.slice(0, 80) });
  L.ok(s.notesShown.length === 1 && /只存在这台设备/.test(s.notesShown[0]), '页面上和云端有关的提示只有原来那一句', s.notesShown);
  // 电脑合盖4分钟（没有任何事件），靠心跳发现
  await d.pg.evaluate(() => window.__addNow(4 * 60000)); await d.pg.waitForTimeout(3500);
  s = await L.st(d);
  L.ok(s.btn === '继续' && s.disabled === false && s.waking === false && s.cloud === 'local', '合盖4分钟后（心跳发现）：没有变化、没有提示', { btn: s.btn, disabled: s.disabled, cloud: s.cloud, now: s.now });
  // 做题页开着没人动、过零点（此时 23:52 左右，再拨到次日 00:03）
  await L.planBtn(d.pg, '继续').click(); await d.pg.waitForSelector('#qcard'); await L.answerUI(d.pg, true);
  const before = await L.st(d);
  await d.pg.evaluate(() => window.__setNow(new Date('2026-11-29T00:03:00+08:00').getTime())); await d.pg.waitForTimeout(3500);
  s = await L.st(d);
  L.ok(s.view === '#today' && s.day === '2026-11-29' && s.btn === '开始' && /7/.test(s.countdown), '做题页开着过了零点（心跳发现）：收起昨天那组，今日页是29日的“开始”', { view: s.view, day: s.day, btn: s.btn, countdown: s.countdown, runBefore: before.run });
  L.ok(s.nq === 4 && s.plan && s.plan.day === '2026-11-28' && s.plan.pos === 4, '昨天做的4题都在，题组停在第4题', { nq: s.nq, plan: s.plan });
  const ls = await d.pg.evaluate(() => { const p = JSON.parse(localStorage.getItem('mzbx-progress-v1')); return { nq: Object.keys(p.q).length, updated: p.updated }; });
  L.ok(ls.nq === 4, '本机存储里也是4题', ls);
  // 新的一天开始做，做完一组小的自选练习，再过一天（停在别的页）
  await L.planBtn(d.pg, '开始').click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, 5, 3);
  await d.pg.click('#tabs a[href="#stats"]'); await d.pg.waitForSelector('#resetBtn');
  await d.pg.evaluate(() => window.__setNow(new Date('2026-11-30T00:01:00+08:00').getTime())); await d.pg.waitForTimeout(3500);
  s = await L.st(d);
  L.ok(s.view === '#stats' && /6/.test(s.countdown), '停在“记录”页过零点：倒计时自己变成6天，仍在记录页', { view: s.view, countdown: s.countdown });
  // 时钟往回拨一天、再拨回来
  await d.pg.evaluate(() => window.__setNow(new Date('2026-11-29T10:00:00+08:00').getTime())); await d.pg.evaluate(() => window.__show()); await d.pg.waitForTimeout(3500);
  s = await L.st(d); L.ok(s.day === '2026-11-29' && /7/.test(s.countdown), '时钟往回拨一天：页面跟着显示29日，不报错', { day: s.day, countdown: s.countdown });
  await d.pg.click('#tabs a[href="#today"]'); await d.pg.waitForSelector('.today'); s = await L.st(d);
  L.info('往回拨后今日页', { btn: s.btn, text: s.text.slice(0, 70), plan: s.plan });
  // 定时器有没有越积越多：静置 9 秒（心跳调成1.5秒一次），应当只有心跳自己那几次
  const t0 = await d.pg.evaluate(() => window.__timers); await d.pg.waitForTimeout(9000); const t1 = await d.pg.evaluate(() => window.__timers);
  L.ok(t1 - t0 <= 8, '静置9秒，新开的定时器只有心跳自己的（≤8个）', { added: t1 - t0 });
  L.ok(d.errs.length === 0, '全程无报错', d.errs);
  await d.ctx.close();

  console.log('二、单文件版直接用 file:// 打开');
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, offline: true, timezoneId: 'Asia/Shanghai' }); const pg = await ctx.newPage(); const errs = [];
  pg.on('pageerror', (e) => errs.push('pageerror: ' + e.message)); pg.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource|net::ERR/.test(m.text())) errs.push('console: ' + m.text()); });
  await pg.goto('file://' + SINGLE); await pg.waitForSelector('.today'); await pg.waitForTimeout(300);
  const f = await pg.evaluate(() => ({ cloud: S.cloud, note: S.cloudNote, btn: document.querySelector('.panel.today button.primary').textContent, nqs: S.qs.length, hasPlan: hasPlan() }));
  L.ok(f.cloud === 'local' && f.btn === '开始' && f.hasPlan, 'file:// 打开正常', f);
  await pg.click('.panel.today button.primary'); await pg.waitForSelector('#qcard');
  const r = await pg.evaluate(() => { const q = S.run.list[S.run.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer; runState.picked = new Set(q.type === '判断' ? [ans] : ans.split('')); reveal(q); nextQ(); return { nq: Object.keys(S.prog.q).length, ls: !!localStorage.getItem('mzbx-progress-v1') }; });
  L.ok(r.nq === 1 && r.ls, 'file:// 下答一题，记录存进了本机', r);
  await pg.evaluate(() => { document.dispatchEvent(new Event('visibilitychange')); window.dispatchEvent(new Event('focus')); window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true })); window.dispatchEvent(new Event('pagehide')); }); await pg.waitForTimeout(200);
  L.ok(errs.length === 0, 'file:// 下各种事件无报错', errs);
  await ctx.close();
  await b.close();
  console.log(L.fails() ? `有 ${L.fails()} 项不符` : '全部符合'); process.exit(L.fails() ? 1 : 0);
})().catch((e) => { console.error('脚本出错', e); process.exit(2); });
