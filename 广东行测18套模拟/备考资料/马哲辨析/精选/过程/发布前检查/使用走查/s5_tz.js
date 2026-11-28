// 两台设备对“今天是几号”看法不同（比如电脑时区设成了别处，慢8小时）：各自都有“今天”的计划时，会不会来回写云端
const L = require('./lib');
(async () => {
  const b = await L.launch(); const store = L.newStore();
  const show = async (d, label) => { const s = await d.pg.evaluate(() => ({ now: dayStr(), plan: S.prog.plan ? `${S.prog.plan.day} pos${S.prog.plan.pos}/${S.prog.plan.ids.length}` : null, panel: document.querySelector('.panel.today').innerText.replace(/\s+/g, ' ').slice(0, 50), sets: window.__sets || 0, gets: window.__gets || 0 })); const r = store.remote ? JSON.parse(store.remote) : null; console.log(`  [${d.name} ${label}]`, JSON.stringify(s), '| 云端计划', r && r.plan ? `${r.plan.day} pos${r.plan.pos}` : null, '| 云端写入累计', store.sets); };
  const pc = await L.device(b, { store, when: '2026-11-28T16:30:00', name: '电脑(日期慢)' });
  await L.planBtn(pc.pg, '开始').click(); await pc.pg.waitForSelector('#qcard'); await L.fastN(pc.pg, 10, 4); await pc.pg.click('button:text-is("退出")'); await pc.pg.waitForTimeout(1500); await show(pc, '做了10题');
  const phone = await L.device(b, { store, when: '2026-11-29T00:30:00', name: '手机' }); await show(phone, '过了零点打开');
  await L.planBtn(phone.pg, '开始').click(); await phone.pg.waitForSelector('#qcard'); await L.fastN(phone.pg, 5, 0); await phone.pg.click('button:text-is("退出")'); await phone.pg.waitForTimeout(1500);
  await show(phone, '开始新一天的计划做了5题'); await show(pc, '此时');
  const s0 = store.sets; const n0 = store.log.length; await pc.pg.waitForTimeout(12000);
  console.log(`  两台都不操作12秒：云端写入 ${s0} → ${store.sets}；这期间写入的设备依次是：${store.log.slice(n0).join('、') || '（无）'}`);
  await show(phone, '12秒后'); await show(pc, '12秒后');
  console.log('页面报错：', phone.errs.concat(pc.errs).join(' ; ') || '无');
  await b.close();
})().catch((e) => { console.error('脚本出错', e); process.exit(1); });
