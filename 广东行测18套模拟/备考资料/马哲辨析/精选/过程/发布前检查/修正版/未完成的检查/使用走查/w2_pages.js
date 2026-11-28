// walk 路线1（续）：睡醒时停在卡片页、记录页、练习页、错题页、今日页（展开了分科加练）——打的字、展开的面板、滚动位置还在不在
// 用法：SITEDIR=site_c|site_b node w2_pages.js [P1,P2,...]
const L = require('./lib');
const SITE = process.env.SITEDIR || 'site_c';
const ONLY = (process.argv[2] || '').split(',').filter(Boolean);
const log = (...a) => console.log(...a);
const off = (d) => d.pg.evaluate(() => { window.__online = false; });
const onQuiet = (d) => d.pg.evaluate(() => { window.__online = true; });
const ui = (d) => d.pg.evaluate(() => {
  const q = (s) => document.querySelector(s);
  return { 页: S.run ? '做题' : current(), 日: dayStr(), 倒计时: q('#countdown').innerText, 滚动: Math.round(window.scrollY), 焦点: document.activeElement ? (document.activeElement.id || document.activeElement.tagName) : null,
    搜索框: q('#cardSearch') ? q('#cardSearch').value : undefined, 展开的卡: document.querySelectorAll('details.card[open]').length || undefined,
    导入框: q('#ioText') ? q('#ioText').value.length : undefined, 导入区展开: q('#ioText') ? !!q('#ioText').closest('details').open : undefined, 清除按钮: q('#resetBtn') ? q('#resetBtn').textContent : undefined, 清除已点一下: q('#resetBtn') ? !!q('#resetBtn').dataset.armed : undefined,
    选中的筛选: document.querySelectorAll('.filters .chip[aria-pressed="true"]').length || undefined, 分科展开: q('details.more') ? !!q('details.more.panel[open]') : undefined,
    灰的控件: [...document.querySelectorAll('#main button[disabled], #main select[disabled]')].map((e) => e.id || e.textContent.slice(0, 8)).join('、') || '无',
    提示: [...document.querySelectorAll('#main .note')].map((e) => e.textContent).filter((t) => /同步|连不上/.test(t)).join(' / ') || '无',
    本机题数: Object.keys(S.prog.q).length, 读云端: window.__gets || 0, chk: window.__chk().join('；') || undefined };
});
const j = (o) => JSON.stringify(o);
async function pair(b, startPhone) {
  const store = L.newStore();
  const ph = await L.device(b, { store, when: '2026-11-28T08:00:00', name: '手机', site: SITE });
  await L.planBtn(ph.pg, '开始').click(); await ph.pg.waitForSelector('#qcard'); await L.fastN(ph.pg, 12, 3); await ph.pg.click('button:text-is("退出")'); await ph.pg.waitForSelector('.today'); await ph.pg.waitForTimeout(1300);
  return { store, ph };
}
async function pcAdvance(b, store, when) {     // 电脑接着做8题
  const pc = await L.device(b, { store, when, name: '电脑', site: SITE });
  await L.planBtn(pc.pg, '继续').click(); await pc.pg.waitForSelector('#qcard'); await L.fastN(pc.pg, 8, 0); await pc.pg.click('button:text-is("退出")'); await pc.pg.waitForSelector('.today'); await pc.pg.waitForTimeout(1300);
  await pc.ctx.close();
}
// 一轮：在某页摆好状态 → 锁屏 → （可选）电脑推进云端 → 过一阵解锁 → 看状态
async function round(b, name, setup, { advance, wakeAt, online = 'quiet' }) {
  const { store, ph } = await pair(b);
  await setup(ph.pg); await ph.pg.waitForTimeout(200);
  const before = await ui(ph);
  await L.lock(ph.pg); await ph.pg.waitForTimeout(300); await off(ph);
  if (advance) await pcAdvance(b, store, '2026-11-28T12:00:00');
  await L.setNow(ph.pg, wakeAt); if (online !== 'off') await onQuiet(ph); await L.unlock(ph.pg);
  await ph.pg.waitForTimeout(150); const at0 = await ui(ph);
  await ph.pg.waitForTimeout(1600); const at2 = await ui(ph);
  log(`\n-- ${name}｜${advance ? '云端有新记录' : '云端没变'}｜${wakeAt.slice(5, 10) === '11-28' ? '同一天' : '隔一天'}｜${online === 'off' ? '没网' : '有网'}`);
  log('  锁屏前  ', j(before)); log('  解锁0.15秒', j(at0)); log('  解锁1.8秒 ', j(at2));
  if (online === 'off') { await ph.pg.waitForTimeout(9200); log('  解锁11秒  ', j(await ui(ph))); }
  if (ph.errs.length) log('  报错', j(ph.errs));
  await ph.ctx.close();
}
const T = {};
const cards = async (pg) => { await pg.click('#tabs a[href="#cards"]'); await pg.waitForSelector('#cardSearch'); await pg.fill('#cardSearch', '矛盾'); await pg.locator('details.card summary').nth(2).click(); await pg.evaluate(() => window.scrollTo(0, 260)); await pg.focus('#cardSearch'); };
const stats = async (pg) => { await pg.click('#tabs a[href="#stats"]'); await pg.waitForSelector('#resetBtn'); await pg.locator('summary:has-text("导出没反应")').click(); await pg.fill('#ioText', '{"v":1,"q":{},"days":{}}  '.repeat(20)); await pg.evaluate(() => window.scrollTo(0, document.body.scrollHeight)); await pg.click('#resetBtn'); };
const practice = async (pg) => { await pg.click('#tabs a[href="#practice"]'); await pg.waitForSelector('#fstart'); await pg.locator('.filters .chip').nth(1).click(); await pg.locator('.filters .chip:text-is("单选")').click(); await pg.evaluate(() => window.scrollTo(0, 300)); };
const review = async (pg) => { await pg.click('#tabs a[href="#review"]'); await pg.waitForSelector('details.card'); await pg.locator('details.card summary').first().click(); await pg.evaluate(() => window.scrollTo(0, 120)); };
const today = async (pg) => { await pg.locator('details.more summary:has-text("分科加练")').click(); await pg.evaluate(() => window.scrollTo(0, 420)); };
T.P1 = (b) => round(b, '卡片页：搜索框里打了“矛盾”、展开了一张卡、往下滚了', cards, { advance: true, wakeAt: '2026-11-28T15:00:00' });
T.P1n = (b) => round(b, '卡片页：同上', cards, { advance: false, wakeAt: '2026-11-28T15:00:00' });
T.P1d = (b) => round(b, '卡片页：同上', cards, { advance: false, wakeAt: '2026-11-29T07:00:00' });
T.P2 = (b) => round(b, '记录页：“清除全部记录”点了一下、导入框里粘了文字', stats, { advance: true, wakeAt: '2026-11-28T08:03:00' });
T.P2n = (b) => round(b, '记录页：同上', stats, { advance: false, wakeAt: '2026-11-28T08:03:00' });
T.P2d = (b) => round(b, '记录页：同上', stats, { advance: false, wakeAt: '2026-11-29T07:00:00' });
T.P2o = (b) => round(b, '记录页：同上', stats, { advance: false, wakeAt: '2026-11-28T15:00:00', online: 'off' });
T.P3 = (b) => round(b, '练习页：选了两个筛选、往下滚了', practice, { advance: true, wakeAt: '2026-11-28T15:00:00' });
T.P3o = (b) => round(b, '练习页：同上', practice, { advance: false, wakeAt: '2026-11-28T15:00:00', online: 'off' });
T.P4 = (b) => round(b, '错题页：展开了一张错题卡', review, { advance: true, wakeAt: '2026-11-28T15:00:00' });
T.P5 = (b) => round(b, '今日页：展开了“分科加练”、往下滚了', today, { advance: true, wakeAt: '2026-11-28T15:00:00' });
T.P5o = (b) => round(b, '今日页：同上', today, { advance: false, wakeAt: '2026-11-28T15:00:00', online: 'off' });
(async () => {
  const b = await L.launch();
  for (const k of Object.keys(T)) { if (ONLY.length && !ONLY.includes(k)) continue; try { await T[k](b); } catch (e) { log('  ✗ 脚本出错', k, String(e && e.stack || e).slice(0, 500)); } }
  await b.close();
})();
