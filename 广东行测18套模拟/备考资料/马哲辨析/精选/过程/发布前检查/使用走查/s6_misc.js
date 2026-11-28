// 小结页打开时的位置；上一轮留下的真实云端文档在新版上的第一天
const L = require('./lib'); const fs = require('fs'); const path = require('path');
const REAL = path.join(L.DIR, '..', 'rev2_sync', 'realdoc', 'progress', 'main.json'); const TAG = process.env.TAG || 'o';
(async () => {
  const b = await L.launch();
  { const d = await L.device(b, { when: '2026-11-28T08:30:00' }); const pg = d.pg;
    await L.planBtn(pg, '开始').click(); await pg.waitForSelector('#qcard'); await L.fastN(pg, 46, 4); await L.doRun(pg, (i) => i % 2 === 0, null);
    const m = await pg.evaluate(() => { const h2 = document.querySelector('#main h2'), hd = document.querySelector('header.top'); const r = h2.getBoundingClientRect(), hr = hd.getBoundingClientRect(); return { title: h2.innerText, scrollY: Math.round(window.scrollY), titleTop: Math.round(r.top), titleBottom: Math.round(r.bottom), headerBottom: Math.round(hr.bottom), docH: document.documentElement.scrollHeight, vh: window.innerHeight, wrongListed: document.querySelectorAll('.wrongq').length }; });
    console.log('小结页（计划最后几题像用户一样点完）:', JSON.stringify(m), m.titleBottom <= m.headerBottom ? '→ 标题（答对几题）整行被顶栏盖住' : (m.titleTop < m.headerBottom ? '→ 标题被顶栏盖住一部分' : '→ 标题看得见'));
    await pg.screenshot({ path: path.join(L.DIR, 'shots', TAG + '_小结页视口.png') }); await d.ctx.close(); }
  { const real = fs.readFileSync(REAL, 'utf8'); const o = JSON.parse(real); console.log('真实文档: v=', o.v, '题数', Object.keys(o.q || {}).length, '字段', Object.keys(o).join(','), 'settings', JSON.stringify(o.settings), 'updated', o.updated);
    const d = await L.device(b, { when: '2026-11-28T08:30:00', local: real }); const i = await L.todayInfo(d.pg); const pv = await L.preview(d.pg);
    const ids = await d.pg.evaluate(() => Object.keys(S.prog.q).map((id) => ({ id, inBank: !!S.q[id], t: S.q[id] ? (S.q[id].t || 3) : null })));
    console.log('  本机有这份记录，11-28 面板:', i.text.replace(/ 20题 30题 40题 50题 60题 80题/, '')); console.log('  三格:', i.stats, '| 构成', JSON.stringify(pv.n), '| 记录里的题:', JSON.stringify(ids), '| 检查', JSON.stringify(i.chk), '| 报错', d.errs.join(';') || '无'); await d.ctx.close();
    const store = L.newStore(); store.remote = JSON.stringify(L.sortKeys(o)); const d2 = await L.device(b, { when: '2026-11-28T08:30:00', store, name: '新设备' }); await d2.pg.waitForTimeout(2500); const i2 = await L.todayInfo(d2.pg);
    console.log('  云端有这份记录、新设备打开:', i2.text.slice(0, 60), '| 云端写入次数', store.sets, '| 报错', d2.errs.join(';') || '无');
    await L.planBtn(d2.pg, '开始').click(); await d2.pg.waitForSelector('#qcard'); await L.fastN(d2.pg, 3, 0); await d2.pg.waitForTimeout(2500); const w1 = store.sets; await d2.pg.waitForTimeout(4000); console.log('  做3题后云端写入次数', w1, '；再等4秒', store.sets); await d2.ctx.close(); }
  await b.close();
})().catch((e) => { console.error('脚本出错', e); process.exit(1); });
