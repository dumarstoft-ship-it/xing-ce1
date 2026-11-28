// 路线1：正常用户。每天早上打开，做完当天计划（每4题错1题），错的点“错题再做一遍”，11-28 到 12-08。
const L = require('./lib'); const path = require('path'); const fs = require('fs');
const DAILY = Number(process.env.DAILY || 50); const WRONG = Number(process.env.WRONG || 4); const TAG = process.env.TAG || 'n50';
(async () => {
  const b = await L.launch(); const d = await L.device(b, { when: '2026-11-28T08:30:00', name: 'phone' }); const pg = d.pg;
  const shot = (name) => pg.screenshot({ path: path.join(L.DIR, 'shots', `${TAG}_${name}.png`), fullPage: true });
  const problems = []; const est = []; const rows = [];
  const note = (info, state) => { for (const c of info.chk) problems.push(`${info.day} ${state}: ${c}`); est.push({ day: info.day, state, coreFresh: info.coreFresh, short: info.short }); };
  if (DAILY !== 50) { await pg.selectOption('#dailySel', String(DAILY)); await pg.waitForTimeout(100); }
  for (const day of ['2026-11-28', '2026-11-29', '2026-11-30', '2026-12-01', '2026-12-02', '2026-12-03', '2026-12-04', '2026-12-05', '2026-12-06', '2026-12-07', '2026-12-08']) {
    await L.setNow(pg, day + 'T08:30:00'); await L.reload(pg);
    const pre = await L.todayInfo(pg), pv = await L.preview(pg); note(pre, '未开始');
    console.log(`\n== ${day}（${pre.countdown}）`);
    console.log('  未开始 面板:', pre.text); console.log('  三格:', pre.stats, '| 错题角标', JSON.stringify(pre.wrongTab));
    console.log('  构成 n=', JSON.stringify(pv.n), '共', pv.len, '按新旧/层级', JSON.stringify(pv.by), `| 开工前：答错待过关${pre.wrongOpen} 第一次复习到期${pre.once1Due}`);
    if (pv.sum !== pv.len) problems.push(`${day} 各类之和 ${pv.sum} ≠ 总数 ${pv.len}`);
    const big = pre.text.match(/今日计划 (\d+)题/); if (!big || Number(big[1]) !== pv.len) problems.push(`${day} 面板题数与计划不一致: ${pre.text.slice(0, 30)} vs ${pv.len}`);
    const chipSum = (pre.text.match(/(复习|考前回顾|核心新题|备选新题) (\d+)/g) || []).map((x) => Number(x.split(' ')[1])).reduce((a, x) => a + x, 0); if (chipSum !== pv.len) problems.push(`${day} 面板各项之和 ${chipSum} ≠ ${pv.len}`);
    if (['2026-11-28', '2026-12-04', '2026-12-06', '2026-12-07'].includes(day)) await shot(day.slice(5) + '_a未开始');
    const start = L.planBtn(pg, '开始');
    if (!(await start.count()) || await start.isDisabled()) { console.log('  “开始”不可点或没有'); continue; }
    await start.click(); await pg.waitForSelector('#qcard');
    if (day === '2026-11-28') await shot('11-28_b题面');
    const okFn = (i) => i % WRONG !== 0;
    const first = await L.doRun(pg, okFn, 10, problems);
    if (day === '2026-11-28') { await pg.click('#qcard .opt >> nth=0'); if (await pg.locator('#submitMulti').count()) await pg.click('#submitMulti'); await shot('11-28_c解析'); await pg.click('#nextBtn'); first.push({ ok: null }); }
    await pg.click('button:text-is("退出")'); await pg.waitForSelector('.today');
    const mid = await L.todayInfo(pg); note(mid, '进行中'); console.log('  进行中 面板:', mid.text.slice(0, 200));
    const mm = mid.text.match(/已做(\d+)题，还剩(\d+)题/); if (!mm || Number(mm[1]) !== mid.plan.pos || Number(mm[1]) + Number(mm[2]) !== mid.plan.len) problems.push(`${day} 进行中数字不对: ${mid.text.slice(0, 40)} plan=${JSON.stringify(mid.plan)}`);
    if (day === '2026-11-28' || day === '2026-12-04') await shot(day.slice(5) + '_d进行中');
    await L.planBtn(pg, '继续').click(); await pg.waitForSelector('#qcard');
    const rest = await L.doRun(pg, (i) => okFn(i + first.length), null, problems);
    const sum1 = await L.mainText(pg, 160); const chkS = await pg.evaluate(() => window.__chk()); for (const c of chkS) problems.push(`${day} 小结: ${c}`);
    if (day === '2026-11-28') await shot('11-28_e小结');
    const redoBtn = pg.locator('button:has-text("错题再做一遍")'); let redo = [], sum2 = '';
    if (await redoBtn.count()) { const lbl = await redoBtn.textContent(); await redoBtn.click(); await pg.waitForSelector('#qcard'); redo = await L.doRun(pg, () => true, null, problems); sum2 = await L.mainText(pg, 120); console.log('  小结:', sum1.slice(0, 60), '| 按钮:', lbl, '| 重做后:', sum2); }
    else console.log('  小结:', sum1);
    await pg.click('button:text-is("回到今日")'); await pg.waitForSelector('.today');
    const post = await L.todayInfo(pg); note(post, '做完'); console.log('  做完 面板:', post.text); console.log('  三格:', post.stats, '| 错题角标', JSON.stringify(post.wrongTab), `| 今天答题${post.answeredToday}次、${post.distinctToday}道不同的题`);
    const dm = post.text.match(/(\d+)题，答对(\d+)题/); const right = first.concat(rest).filter((x) => x.ok).length; if (dm && (Number(dm[1]) !== pv.len)) problems.push(`${day} 做完面板题数 ${dm[1]} ≠ ${pv.len}`);
    if (['2026-11-28', '2026-12-05', '2026-12-06'].includes(day)) await shot(day.slice(5) + '_f做完');
    rows.push({ day, n: pv.n, len: pv.len, coreSeen: post.coreSeen, bkSeen: post.bkSeen, redo: redo.length });
    if (day === '2026-11-28' || day === '2026-12-04') { for (const tab of ['practice', 'review', 'cards', 'pending', 'appendix', 'stats', 'today']) { await pg.click(`#tabs a[href="#${tab}"]`); await pg.waitForTimeout(80); const c = await pg.evaluate(() => window.__chk()); for (const x of c) problems.push(`${day} 分栏${tab}: ${x}`); if (tab === 'stats' && day === '2026-12-04') await shot('12-04_g记录'); } }
  }
  console.log('\n估算对照（每天面板上“还差X道”，没有这句记0；实际 = 12-03 做完后核心还没学的）：');
  const actual = est.find((e) => e.day === '2026-12-03' && e.state === '做完'); for (const e of est) if (e.day <= '2026-12-03') console.log(`  ${e.day} ${e.state}: 核心没学${e.coreFresh} 面板估算还差${e.short}`); console.log('  12-03 做完后实际还没学的核心：', actual && actual.coreFresh);
  console.log('\n每天构成：'); for (const r of rows) console.log('  ', r.day, JSON.stringify(r.n), '共', r.len, '核心已学', r.coreSeen, '备选已学', r.bkSeen, '重做', r.redo);
  console.log('\n页面报错：', d.errs.length ? d.errs.join(' ; ') : '无'); console.log('发现的问题：', problems.length ? '\n  ' + [...new Set(problems)].slice(0, 40).join('\n  ') : '无');
  fs.writeFileSync(path.join(L.DIR, 'out', `${TAG}_final.json`), await pg.evaluate(() => localStorage.getItem('mzbx-progress-v1')));
  await b.close();
})().catch((e) => { console.error('脚本出错', e); process.exit(1); });
