// 云端的几种别扭情形：没有权限的访客、get 一直不返回、set 一直挂着、use("db") 不返回、监听一直没有快照、睡醒核对时读云端报权限错
// 用法：SITE=site_v7c|site_v7b node t2_cloud_edge.js [只跑哪几项，如 V1,H2]
const L = require('./mylib'); const path = require('path');
const SITE = path.join(L.HERE, process.env.SITE || 'site_v7c'); const ONLY = (process.argv[2] || '').split(',').filter(Boolean);
const isC = !/v7b/.test(SITE);
const T = {};
const startPlan = async (d, n) => { await L.planBtn(d.pg, (await L.st(d)).btn).click(); await d.pg.waitForSelector('#qcard'); await L.fastN(d.pg, n, 0); };
const exit = async (d) => { await d.pg.click('button:text-is("退出")'); await d.pg.waitForSelector('.today'); };
const away = async (d, min) => { await d.pg.evaluate(() => window.__hide()); await d.pg.evaluate((m) => window.__addNow(m * 60000), min); await d.pg.evaluate(() => window.__show()); await d.pg.waitForTimeout(250); };

T.V1 = async (b) => {
  console.log('V1 访客：能读（云端没有文档），set() 抛 not_granted');
  const d = await L.open(b, { site: SITE, cloud: { setMode: 'throw:not_granted' } });
  let s = await L.st(d); L.ok(s.btn === '开始' && s.disabled === false, '打开后“开始”可点', { cloud: s.cloud, synced: s.synced });
  await startPlan(d, 3); await d.pg.waitForTimeout(1500); s = await L.st(d);
  L.ok(s.cloud === 'local' && /所有者/.test(s.note), '第一次写被拒后：cloud=local，提示“只有页面的所有者能把记录存到云端…”', { cloud: s.cloud, note: s.note });
  await exit(d); s = await L.st(d); L.ok(s.notesShown.length === 1 && /所有者/.test(s.notesShown[0]), '今日页上显示这句提示', s.notesShown);
  const g0 = s.gets; await away(d, 3); s = await L.st(d);
  L.ok(s.disabled === false && s.waking === false && !/正在同步/.test(s.text) && s.gets === g0, '离开3分钟再回来：不核对云端，“继续”可点', { btn: s.btn, disabled: s.disabled, waking: s.waking, gets: [g0, s.gets] });
  await startPlan(d, 2); await exit(d); await d.pg.waitForTimeout(1500); s = await L.st(d);
  const ls = await d.pg.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('mzbx-progress-v1')).q).length);
  L.ok(s.nq === 5 && ls === 5 && s.gets === g0, '接着做2题：本机5题都在，没有再去碰云端', { nq: s.nq, ls, gets: s.gets });
  L.ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
};
T.V2 = async (b) => {
  console.log('V2 访客：onSnapshot 直接走错误回调');
  const d = await L.open(b, { site: SITE, cloud: { snapMode: 'error' } });
  let s = await L.st(d);
  L.ok(s.cloud === 'local' && /连不上/.test(s.note) && s.disabled === false && !/正在同步/.test(s.text), '马上转本机：有提示，“开始”可点', { cloud: s.cloud, note: s.note, btn: s.btn, disabled: s.disabled });
  await startPlan(d, 3); await exit(d); await away(d, 5); await d.pg.waitForTimeout(1200); s = await L.st(d);
  L.ok(s.nq === 3 && s.disabled === false && s.waking === false && s.gets === 0 && s.sets === 0, '做3题、离开5分钟再回来：不读不写云端，“继续”可点', { nq: s.nq, gets: s.gets, sets: s.sets, waking: s.waking });
  L.ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
};
T.V3 = async (b) => {
  console.log('V3 用着用着权限没了：睡醒核对时 get() 抛 revoked（不是连不上）');
  const d = await L.open(b, { site: SITE, cloud: {}, beatMs: 0 });
  await startPlan(d, 3); await exit(d); await d.pg.waitForTimeout(1500);
  let s = await L.st(d); L.ok(s.remoteNq === 3 && s.cloud === 'ok', '先做3题，云端3题', { remoteNq: s.remoteNq });
  await d.pg.evaluate(() => { window.__c.getMode = 'throw:revoked'; });
  const g0 = s.gets; await away(d, 3); s = await L.st(d);
  L.info('回来时', { btn: s.btn, disabled: s.disabled, waking: s.waking, text: s.text.slice(0, 60) });
  await d.pg.waitForTimeout(10500); s = await L.st(d);
  L.info('10秒后', { cloud: s.cloud, note: s.note, disabled: s.disabled, gets: s.gets - g0 });
  const wrongNote = /暂时连不上.*自动合并/.test(s.note);
  await d.pg.waitForTimeout(40000); const s2 = await L.st(d);
  L.info('再过40秒', { cloud: s2.cloud, note: s2.note, gets: s2.gets - g0, log: await d.pg.evaluate(() => window.__c.log.slice(-8)) });
  if (isC) L.ok(!wrongNote, '权限没了时不该说“暂时连不上…连上后会自动合并”，也不该一直去读', { note: s.note, 读了几次: s2.gets - g0 });
  await startPlan(d, 1); await d.pg.waitForTimeout(1500); const s3 = await L.st(d);
  L.info('再答一题（写云端时才发现没权限）', { cloud: s3.cloud, note: s3.note });
  const g3 = s3.gets; await d.pg.waitForTimeout(33000); const s4 = await L.st(d);
  L.ok(s4.gets === g3, '转成本机后不再去读云端', { gets: [g3, s4.gets] });
  L.ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
};
T.H1 = async (b) => {
  console.log('H1 睡醒核对时 get() 一直不返回（既不成功也不失败）');
  const d = await L.open(b, { site: SITE, cloud: {} });
  await startPlan(d, 3); await exit(d); await d.pg.waitForTimeout(1500);
  await d.pg.evaluate(() => { window.__c.getMode = 'hang'; });
  await away(d, 3); let s = await L.st(d);
  if (isC) L.ok(s.disabled === true && /正在同步/.test(s.text), '回来：“继续”先不可点', { btn: s.btn, disabled: s.disabled });
  await d.pg.waitForTimeout(10400); s = await L.st(d);
  L.ok(s.disabled === false, '10秒后“继续”可点（不会一直灰着）', { btn: s.btn, disabled: s.disabled, cloud: s.cloud, note: s.note });
  await d.pg.evaluate(() => { window.__c.getMode = 'ok'; });       // 网好了，但那次挂住的 get 永远不回来
  await startPlan(d, 2); await exit(d); await d.pg.waitForTimeout(2500); s = await L.st(d);
  L.ok(s.remoteNq === 5, '之后做的2题照常推上云端（挂住的那次读不挡写）', { nq: s.nq, remoteNq: s.remoteNq, saving: s.saving });
  L.ok(s.cloud === 'ok' && !s.note, '“连不上”的提示消掉了', { cloud: s.cloud, note: s.note });
  L.ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
};
T.H2 = async (b) => {
  console.log('H2 写云端之前的那次 get() 一直不返回');
  const d = await L.open(b, { site: SITE, cloud: {} });
  await startPlan(d, 3); await d.pg.waitForTimeout(1500); let s = await L.st(d);
  L.ok(s.remoteNq === 3, '先做3题，云端3题', { remoteNq: s.remoteNq });
  await d.pg.evaluate(() => { window.__c.getMode = 'hang'; });
  await L.fastN(d.pg, 1, 0); await d.pg.waitForTimeout(1500);                     // 这一题的推送卡在 get 上
  await d.pg.evaluate(() => { window.__c.getMode = 'ok'; });                      // 网好了
  await L.fastN(d.pg, 4, 0); await exit(d); await d.pg.waitForTimeout(3000); s = await L.st(d);
  L.info('网好后又做4题、退出、等3秒', { nq: s.nq, remoteNq: s.remoteNq, saving: s.saving, again: s.again, cloud: s.cloud, note: s.note, disabled: s.disabled });
  await away(d, 3); await d.pg.waitForTimeout(3000); const s2 = await L.st(d);
  L.info('离开3分钟再回来、等3秒', { nq: s2.nq, remoteNq: s2.remoteNq, saving: s2.saving, again: s2.again, cloud: s2.cloud, note: s2.note, disabled: s2.disabled, gets: s2.gets });
  await d.pg.waitForTimeout(70000); const s3 = await L.st(d);
  L.ok(s3.remoteNq === 8, '挂住一次之后，后面做的题还能推上云端', { 本机: s3.nq, 云端: s3.remoteNq, saving: s3.saving, 页面提示: s3.note || '（无）' });
  const ls = await d.pg.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('mzbx-progress-v1')).q).length);
  L.ok(ls === 8, '本机存储里8题都在（刷新后能补推）', ls);
  await d.pg.reload(); await d.pg.waitForSelector('.today'); await d.pg.waitForTimeout(2500); const s4 = await L.st(d);
  L.ok(s4.remoteNq === 8, '刷新页面后补推上去了', { remoteNq: s4.remoteNq });
  L.ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
};
T.H3 = async (b) => {
  console.log('H3 断网：set() 一直挂着、get() 给本机副本；之后连上');
  const d = await L.open(b, { site: SITE, cloud: {} });
  await startPlan(d, 3); await d.pg.waitForTimeout(1500);
  await d.pg.evaluate(() => { window.__c.setMode = 'hang'; });
  await L.fastN(d.pg, 1, 0); await d.pg.waitForTimeout(1500);                     // 这一题的 set 挂住
  await d.pg.evaluate(() => { window.__c.getMode = 'cache'; });
  await L.fastN(d.pg, 3, 0); await exit(d); await d.pg.waitForTimeout(1200); let s = await L.st(d);
  L.ok(s.nq === 7 && s.remoteNq === 3 && s.disabled === false, '断网时做了4题：本机7题，云端还是3题，“继续”可点', { nq: s.nq, remoteNq: s.remoteNq, saving: s.saving, cloud: s.cloud, note: s.note });
  await away(d, 3); s = await L.st(d);
  if (isC) L.ok(s.disabled === true, '离开3分钟再回来：先等云端', { disabled: s.disabled });
  await d.pg.waitForTimeout(10400); s = await L.st(d);
  L.ok(s.disabled === false, '10秒后放行', { disabled: s.disabled, cloud: s.cloud, note: s.note });
  await startPlan(d, 2); await exit(d);
  await d.pg.evaluate(() => { window.__c.getMode = 'ok'; window.__c.setMode = 'ok'; window.__c.release(); });   // 连上：挂着的那次 set 完成
  let waited = 0; while ((await L.st(d)).remoteNq < 9 && waited < 70000) { await d.pg.waitForTimeout(1000); waited += 1000; }
  s = await L.st(d);
  L.ok(s.remoteNq === 9, '连上后9题都推上去了', { nq: s.nq, remoteNq: s.remoteNq, waitedMs: waited });
  L.ok(s.cloud === 'ok' && !s.note, '提示消掉', { cloud: s.cloud, note: s.note });
  L.ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
};
T.H4 = async (b) => {
  console.log('H4 use("db") 一直不返回');
  const d = await L.open(b, { site: SITE, cloud: { useMode: 'hang' } });
  let s = await L.st(d); L.ok(s.disabled === true && /正在同步/.test(s.text), '刚打开：先等云端', { disabled: s.disabled });
  await d.pg.waitForTimeout(10300); s = await L.st(d);
  L.ok(s.disabled === false && s.cloud === 'slow' && /连不上/.test(s.note), '10秒后放行、有提示', { disabled: s.disabled, cloud: s.cloud, note: s.note });
  await startPlan(d, 2); await exit(d); await away(d, 3); s = await L.st(d);
  L.ok(s.disabled === false && s.nq === 2, '做2题、离开3分钟再回来：“继续”可点', { disabled: s.disabled, nq: s.nq, waking: s.waking });
  L.ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
};
T.H5 = async (b) => {
  console.log('H5 监听一直没有快照（get 是通的）');
  const d = await L.open(b, { site: SITE, cloud: { snapMode: 'never' } });
  await d.pg.waitForTimeout(10300); let s = await L.st(d);
  L.ok(s.disabled === false && s.cloud === 'slow', '10秒后放行', { disabled: s.disabled, cloud: s.cloud, note: s.note });
  await startPlan(d, 3); await exit(d); await away(d, 3); await d.pg.waitForTimeout(2000); s = await L.st(d);
  L.info('做3题、离开3分钟再回来', { nq: s.nq, remoteNq: s.remoteNq, synced: s.synced, cloud: s.cloud, note: s.note, gets: s.gets, disabled: s.disabled });
  L.ok(s.disabled === false && s.nq === 3, '本机3题都在，“继续”可点');
  L.ok(d.errs.length === 0, '无报错', d.errs); await d.ctx.close();
};
(async () => {
  const b = await L.launch();
  console.log('站点：' + path.basename(SITE));
  for (const k of Object.keys(T)) { if (ONLY.length && !ONLY.includes(k)) continue; try { await T[k](b); } catch (e) { console.log('  ✗ 脚本出错 ' + k + ': ' + String(e && e.stack || e).slice(0, 400)); } }
  await b.close(); console.log(L.fails() ? `有 ${L.fails()} 项不符` : '全部符合'); process.exit(L.fails() ? 1 : 0);
})();
