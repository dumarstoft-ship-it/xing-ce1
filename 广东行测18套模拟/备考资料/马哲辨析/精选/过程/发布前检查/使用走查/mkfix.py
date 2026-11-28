# 在我自己的目录里做一份带修改建议的副本，验证建议可行（不改 v7b）。fixed = P1–P7；fixed8 = 再加 P8。
import os, shutil, sys
src = open('site/index.html', encoding='utf8').read()
def rep(s, old, new, label):
    assert s.count(old) == 1, (label, s.count(old))
    return s.replace(old, new)
s = src
# P1 前一天留下的一组（今日计划、今日一组）不再去改今天的题组；页面回到前台发现换了日，就把它收起来
s = rep(s, 'label: "今日计划", tkey: "plan", mode: "" };', 'label: "今日计划", tkey: "plan", day: t.day, mode: "" };', 'P1a')
s = rep(s, 'tkey: todayKey(bank), mode: "" };', 'tkey: todayKey(bank), day: t.day, mode: "" };', 'P1b')
s = rep(s, '  const R = S.run; if (!R || !R.tkey) return;\n  const today = dayStr(), P = S.prog.q;\n', '  const R = S.run; if (!R || !R.tkey) return;\n  const today = dayStr(), P = S.prog.q;\n  if (R.day && R.day !== today) return;      // 眼前这组是前一天的：不去动今天的题组\n', 'P1c')
s = rep(s, '  if (R.tkey && S.prog[R.tkey]) { S.prog[R.tkey].pos = R.pos; S.prog[R.tkey].res = R.res; touch(); }', '  if (R.tkey && S.prog[R.tkey] && (!R.day || S.prog[R.tkey].day === R.day)) { S.prog[R.tkey].pos = R.pos; S.prog[R.tkey].res = R.res; touch(); }', 'P1d')
s = rep(s, 'function dayRolled() { if (S.prog && shownDay && shownDay !== dayStr() && !S.run) route(); }',
 'function dayRolled() {\n  if (!S.prog || !shownDay || shownDay === dayStr()) return;\n  if (S.run && S.run.tkey && S.run.day && S.run.day !== dayStr()) S.run = null;   // 眼前是前一天的今日计划（或今日一组）：收起来，没做的照规则排进今天\n  if (!S.run) route();\n}', 'P1e')
s = rep(s, 'tkey: hot.run.tkey || "", mode: hot.run.mode || "" };', 'tkey: hot.run.tkey || "", day: hot.run.day, mode: hot.run.mode || "" };', 'P1f')
s = rep(s, 'tkey: S.run.tkey, mode: S.run.mode } : null }));', 'tkey: S.run.tkey, day: S.run.day, mode: S.run.mode } : null }));', 'P1g')
# P2 估算：明天的第一次复习要算上已经过期、今天排不进去的
s = rep(s, 'function coreShort(size, newToday, done) {', 'function coreShort(size, newToday, done, pending) {', 'P2a')
s = rep(s, '    const firstDue = core.filter((q) => P[q.id] && P[q.id].b === 1 && P[q.id].due === tomorrow).length;',
 '    const pend = new Set(pending || []);     // 今天计划里还没做的题今天会做掉，不算到明天头上\n    const firstDue = core.filter((q) => !pend.has(q.id) && P[q.id] && P[q.id].b === 1 && P[q.id].due <= tomorrow).length;   // 含已经过期、今天排不进去的', 'P2b')
s = rep(s, '  let newToday = 0;         // 今天的计划里还没做的核心新题数', '  let newToday = 0, pending = [];         // 今天的计划里还没做的核心新题数、还没做的题', 'P2c')
s = rep(s, "    newToday = t.ids.slice(t.pos).filter((id) => S.q[id] && S.q[id].t === 1 && !S.prog.q[id]).length;", "    newToday = t.ids.slice(t.pos).filter((id) => S.q[id] && S.q[id].t === 1 && !S.prog.q[id]).length; pending = t.ids.slice(t.pos);", 'P2d')
s = rep(s, '    newToday = prev.n.new1;', '    newToday = prev.n.new1; pending = prev.list.map((q) => q.id);', 'P2e')
s = rep(s, 'const short = coreShort(size, newToday, done), last', 'const short = coreShort(size, newToday, done, pending), last', 'P2f')
# P3 页面睡了一阵再回来：先向云端读一次，读到之前（最多10秒）不让开始
s = rep(s, 'document.addEventListener("visibilitychange", () => { if (document.hidden) flushCloud(); else dayRolled(); });\nwindow.addEventListener("pagehide", flushCloud);\nwindow.addEventListener("focus", dayRolled);\n',
 '''let lastAlive = Date.now(), resyncTimer = 0;
setInterval(() => { lastAlive = Date.now(); }, 20000);
async function resync() {   // 页面睡了一阵再回来（合上电脑、锁屏、隔天）：云端可能已被另一台设备推进。先读一次确认过的记录，读到之前（最多10秒）不让开始
  const gap = Date.now() - lastAlive; lastAlive = Date.now();
  if (gap < 120000 || !S.ref || S.cloud === "local" || !S.synced || S.run) return;
  S.synced = false; S.cloud = "connecting"; S.cloudNote = "";
  clearTimeout(resyncTimer);
  resyncTimer = setTimeout(() => { if (S.cloud === "connecting" && !S.synced) { S.cloud = "slow"; S.cloudNote = "云端记录暂时连不上，先存在这台设备上，连上后会自动合并。"; cloudSettled(false); } }, 10000);
  route(true);
  try {
    const cur = await S.ref.get();
    if (cur.metadata && cur.metadata.fromCache) return;
    const r = cur.exists ? cur.data() : null;
    let took = 0, ahead = 0;
    if (r && r.v === 1) ({ took, ahead } = mergeProg(JSON.parse(JSON.stringify(r))));
    if (took) { normalize(S.prog); saveLocal(); }
    clearTimeout(resyncTimer); S.synced = true; S.cloud = "ok"; S.cloudNote = "";
    if (ahead) scheduleCloud();
    cloudSettled(took > 0);
  } catch (e) {}      // 读不到：等快照到，或者10秒后先走本机
}
document.addEventListener("visibilitychange", () => { if (document.hidden) flushCloud(); else { dayRolled(); resync(); } });
window.addEventListener("pagehide", flushCloud);
window.addEventListener("focus", () => { dayRolled(); resync(); });
document.getElementById("tabs").addEventListener("click", (e) => {   // P5 做题时点当前所在的分栏：地址不变、不会触发 hashchange，这里补上退出
  const a = e.target.closest("a"); if (a && S.run && a.getAttribute("href") === (location.hash || "#today")) { e.preventDefault(); exitRun(); }
});
''', 'P3')
# P4 小结页回到页顶
s = rep(s, '  if (R.pos >= R.list.length) { main.replaceChildren(runSummary()); return; }', '  if (R.pos >= R.list.length) { main.replaceChildren(runSummary()); window.scrollTo(0, 0); return; }', 'P4')
# P6 小结页的返回按钮：不在今日页开的组，不叫“回到今日”
s = rep(s, '    h("button", { class: "btn", onclick: exitRun }, "回到今日")));', '    h("button", { class: "btn", onclick: exitRun }, current() === "today" ? "回到今日" : "返回")));', 'P6')
# P7 小结页不拦回车、空格
s = rep(s, '  if (!S.run || !runState || /INPUT|SELECT|TEXTAREA/.test(e.target.tagName) || e.metaKey || e.ctrlKey || e.altKey) return;', '  if (!S.run || !runState || !$("#qcard") || /INPUT|SELECT|TEXTAREA/.test(e.target.tagName) || e.metaKey || e.ctrlKey || e.altKey) return;', 'P7')
def out(d, text):
    os.makedirs(d, exist_ok=True)
    for f in ['blocks.json', 'cards.json', 'meta.json', 'questions.json']: shutil.copy('site/' + f, d + '/' + f)
    open(d + '/index.html', 'w', encoding='utf8').write(text)
out('fixed', s)
# P8 同一份内容不连着写第二次（两台设备对同一处各执一词时不来回顶）
s8 = rep(s, '    const body = JSON.parse(JSON.stringify(S.prog));\n    if (!r || canon(body) !== canon(r)) await S.ref.set(body); // 内容一样就不写',
 '    const body = JSON.parse(JSON.stringify(S.prog)), cb = canon(body);\n    if (!r || cb !== canon(r)) { if (r && cb === lastWrote) { /* 这份上次已经写过、又被别的设备改了回去：不再顶回去 */ } else { await S.ref.set(body); lastWrote = cb; } } // 内容一样就不写', 'P8a')
s8 = rep(s8, 'let cloudTimer = 0, retryTimer = 0, retryWait = 0;', 'let cloudTimer = 0, retryTimer = 0, retryWait = 0, lastWrote = "";', 'P8b')
out('fixed8', s8)
print('ok', len(src), len(s), len(s8))
