// 单台设备带云端、按正常手速做题：云端写几次，停手后还写不写
const L = require('./lib');
(async () => { const b = await L.launch(); const store = L.newStore(); const d = await L.device(b, { store, when: '2026-11-28T09:00:00', name: '手机' }); const pg = d.pg;
  await L.planBtn(pg, '开始').click(); await pg.waitForSelector('#qcard'); await pg.waitForTimeout(1500); const s0 = store.sets;
  for (let i = 0; i < 8; i++) { await L.answerUI(pg, i % 3 !== 0); await pg.waitForTimeout(1300); }
  const s1 = store.sets; await pg.waitForTimeout(4000); const s2 = store.sets; const g = await pg.evaluate(() => ({ sets: window.__sets, gets: window.__gets }));
  console.log(`单台设备带云端：点“开始”后写入${s0}次；隔1.3秒答一题、答完8题累计${s1}次；停手4秒后${s2}次；页面自己统计 ${JSON.stringify(g)}`);
  await pg.click('button:text-is("退出")'); await pg.waitForTimeout(2500); console.log('退出回今日页2.5秒后累计', store.sets, '| 报错', d.errs.join(';') || '无'); await b.close(); })().catch((e) => { console.error('脚本出错', e); process.exit(1); });
