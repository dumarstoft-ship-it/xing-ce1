# 政常辨析日课 第7版修正：把发布前检查（同步收敛、使用走查两路）查出的问题一次改完。
# 用法：python3 patch_v7c.py <第7版的 index.html>     （原地改写；每一处都要求原文恰好出现一次，对不上就报错、不写文件）
import sys

p = sys.argv[1]
s = open(p, encoding="utf8").read()
done = []


def sub(tag, old, new):
    global s
    n = s.count(old)
    assert n == 1, (tag, n, old[:80])
    s = s.replace(old, new)
    done.append(tag)


def block(tag, start, end, new):
    """把 start（含）到 end（不含）之间整段换成 new"""
    global s
    assert s.count(start) == 1 and s.count(end) == 1, (tag, s.count(start), s.count(end))
    a, b = s.index(start), s.index(end)
    assert a < b, tag
    s = s[:a] + new + s[b:]
    done.append(tag)


# ---------- 一、写云端：同一份内容不连着写第二次 ----------
sub("写云端-变量", 'let cloudTimer = 0, retryTimer = 0, retryWait = 0;', 'let cloudTimer = 0, retryTimer = 0, retryWait = 0, lastWrote = "", wroteSame = 0;')
sub("写云端-不顶回去", '''    const body = JSON.parse(JSON.stringify(S.prog));
    if (!r || canon(body) !== canon(r)) await S.ref.set(body); // 内容一样就不写
    S.cloud = "ok"; retryWait = 0;
''', '''    const body = JSON.parse(JSON.stringify(S.prog)), cb = canon(body);
    if (!r || cb !== canon(r)) {                              // 内容一样就不写
      // 同一份内容写上去又被别的设备改回去：再写两次还这样，就不顶了，等下一次真有改动再写。
      // 头两次要补写，是因为两台设备同时写时后到的会盖掉先到的；一直顶下去，就成了两边各执一词来回写
      if (cb !== lastWrote) { lastWrote = cb; wroteSame = 0; }
      if (!r || wroteSame < 3) { await S.ref.set(body); wroteSame++; }
    }
    if (S.cloud === "slow") { S.cloudNote = ""; renderCloudNote(); }
    S.cloud = "ok"; retryWait = 0;
''')

# ---------- 二、合并规则 ----------
block("合并", '// 把另一份记录并进本机。返回 took', 'const syncing = () =>', '''// 把另一份记录并进本机。返回 took（采用了对方几处）和 ahead（本机有几处比对方新，需要推回云端）。
// 规则：同一道题留最近练过的那份（同一天取作答次数多的；同一天只要有一边答错过，就照答错处理，明天再出），每天的作答数取多的，
// 当天定好的题组留今天的那份，设置跟最后改它的一边，其余拿不准的地方跟较新的整份记录。
// “清除全部记录”：清除时间较晚的一边算数，另一边在清除当天及之前的记录作废；清除之后的日子里做的题留下（清除迟到时不连累后来做的题）。
function mergeProg(inc) {
  const ie = inc.epoch || "", me = S.prog.epoch || "";
  let took = 0, ahead = 0;
  if (ie !== me) {
    const hi = ie > me ? ie : me, cut = dayStr(new Date(hi)), old = ie > me ? S.prog : inc;
    old.q = Object.fromEntries(Object.entries(old.q || {}).filter(([, p]) => (p.d || "") > cut));
    old.days = Object.fromEntries(Object.entries(old.days || {}).filter(([d]) => d > cut));
    for (const k of ["today", "today2", "plan"]) if (old[k] && !(old[k].day > cut)) old[k] = null;
    old.epoch = hi;
    if (ie > me) took++; else ahead++;
  }
  const mine = S.prog, iq = inc.q || {}, idays = inc.days || {};
  const iu = inc.updated || "", mu = mine.updated || "";
  const incWins = (a, b) => iu > mu || (iu === mu && canon(b) > canon(a));     // 一样新时按内容定一个固定的先后，两台设备不会各执一词来回写
  const newer = (a, b) => (a.d || "") > (b.d || "") || ((a.d || "") === (b.d || "") && (a.n || 0) > (b.n || 0));
  for (const [id, p] of Object.entries(iq)) {
    const m = mine.q[id];
    let u;
    if (!m || newer(p, m)) u = p;
    else if (newer(m, p)) u = m;
    else if (sameRec(p, m)) continue;
    // 同一天、同样的作答次数但内容不同：一边答错一边答对的，以答错的为准；否则冲突的跟较新的一份。只有一边有的字段（如“能讲清”的自评）留着
    else u = ((p.l === 0) !== (m.l === 0) ? p.l === 0 : incWins(m, p)) ? { ...m, ...p } : { ...p, ...m };
    // 同一天两边都做过、有一边答错过：不管留的是哪份，都照答错处理（明天再出）
    if (m && u.d && (m.d || "") === (p.d || "") && (m.b === 0 || p.b === 0) && u.b !== 0) u = { ...u, b: 0, due: addDays(u.d, 1) };
    if (!m || !sameRec(u, m)) { mine.q[id] = u; took++; }
    if (!sameRec(u, p)) ahead++;
  }
  for (const id in mine.q) if (!iq[id]) ahead++;
  const big = (x, y) => (x.n || 0) > (y.n || 0) || ((x.n || 0) === (y.n || 0) && (x.c || 0) > (y.c || 0));
  for (const [d, v] of Object.entries(idays)) {
    const m = mine.days[d];
    if (!m || big(v, m)) { mine.days[d] = v; took++; } else if (big(m, v)) ahead++;
  }
  for (const d in mine.days) if (!idays[d]) ahead++;
  const day = dayStr(), isToday = (g) => !!g && g.day === day;
  for (const k of ["today", "today2", "plan"]) {       // 只有一边是今天的题组：留今天的；否则跟较新的整份记录
    const a = mine[k] || null, b = inc[k] || null;
    if (canon(a) === canon(b)) continue;
    // 对方题组的日期比本机的今天还晚：对方的时钟（或时区）走在前面。留自己的，但不为这个推回去，免得两边各认各的“今天”来回写
    if (isToday(a) !== isToday(b)) { if (isToday(b)) { mine[k] = b; took++; } else if (!(b && b.day > day)) ahead++; }
    else if (incWins(a, b)) { mine[k] = b; took++; } else ahead++;
  }
  const iset = { ...DEFAULT_SETTINGS, ...(inc.settings || {}) }, ist = inc.st || "", mst = mine.st || "";
  if (canon(mine.settings) !== canon(iset)) {          // 设置跟最后改它的一边；都没记改动时间的老记录，跟较新的整份记录
    if (ist !== mst ? ist > mst : incWins(mine.settings, iset)) { mine.settings = iset; mine.st = ist; S.setSeen = canon(iset); took++; } else ahead++;
  } else if (ist > mst) { mine.st = ist; took++; } else if (mst > ist) ahead++;
  if (iu > mu) mine.updated = iu; else if (mu > iu) ahead++;
  if (me > ie && iu >= mu) {       // 本机清除过、对方还是清除前的，而且对方的记录更新：把本机的更新时间提到对方之后再推，还开着的旧版页面才会收下，不会来回写
    const t = new Date(iu).getTime();
    if (!isNaN(t)) mine.updated = new Date(t + 1).toISOString();
  }
  return { took, ahead };
}
let waking = 0;      // 页面睡了一阵再回来、正在向云端核对的那几秒（见 resync）
''')
sub("等云端", 'const syncing = () => S.cloud === "connecting" && !S.synced;   // 还在等云端的记录：这时先不让开始，免得照着空白记录排计划',
    'const syncing = () => (S.cloud === "connecting" && !S.synced) || !!waking;   // 还在等云端的记录：这时先不让开始，免得照着空白的或过时的记录排计划')
sub("同步后重画", '  if (changed || current() === "today") route(true); else updateTabs();\n}',
    '''  if (changed || current() === "today") route(true);
  else { updateTabs(); for (const el of document.querySelectorAll("#dailySel, #size-mz, #size-fm")) el.disabled = syncing(); }   // 别的页不重画，只把题数选择放开
}''')

# ---------- 三、做题页只往“自己那一组”里写 ----------
sub("计划-开做", 'pos: t.pos, res: t.res, label: "今日计划", tkey: "plan", mode: "" };', 'pos: t.pos, res: { ...t.res }, label: "今日计划", tkey: "plan", mode: "", day: t.day };')
sub("分科-开做", 'pos: t.pos, res: t.res, label: bank === "fm" ? "政常 · 今日一组" : "马哲 · 今日一组", tkey: todayKey(bank), mode: "" };',
    'pos: t.pos, res: { ...t.res }, label: bank === "fm" ? "政常 · 今日一组" : "马哲 · 今日一组", tkey: todayKey(bank), mode: "", day: t.day };')
block("做题页与题组", '// 当天定好的题组做到一半时并进了别处的记录：', '// 粗算：照现在的量', '''// 做题页手里这一组，还是不是记录里当天的那一组（隔了一天，或者别的设备另排了一组，就不是了）
function ownGroup(R) {
  const t = R && R.tkey ? S.prog[R.tkey] : null;
  if (!t || t.day !== dayStr() || t.day !== R.day || t.ids.length !== R.list.length || !R.list.every((q) => t.ids.includes(q.id))) return null;
  return t;
}
// 把做题页的进度写回题组：只写自己那一组，而且只在比记录里的靠前（多做了题）时才写。已经不是自己那一组的，眼前这组当普通练习做完，作答照样记录
function saveRun() {
  const R = S.run; if (!R || !R.tkey) return;
  const t = ownGroup(R); if (!t) { R.tkey = ""; return; }
  if (R.pos > t.pos || Object.keys(R.res).some((id) => !(id in t.res))) { t.ids = R.list.map((q) => q.id); t.pos = R.pos; t.res = { ...t.res, ...R.res }; touch(); }
}
// 当天定好的题组做到一半时并进了别处的记录：接下来的题如果今天已经在别处做过，算作已做、不再出一遍
function syncRun() {
  const R = S.run; if (!R || !R.tkey) return;
  if (!ownGroup(R)) { R.tkey = ""; return; }
  const today = dayStr(), P = S.prog.q;
  while (R.pos < R.list.length) { const id = R.list[R.pos].id; if (!(id in R.res) && P[id] && P[id].d === today) { R.res[id] = P[id].l; R.pos++; } else break; }
  saveRun();
}
''')
sub("作答后写回", '  if (R.tkey && S.prog[R.tkey]) { S.prog[R.tkey].pos = R.pos; S.prog[R.tkey].res = R.res; touch(); }', '  saveRun();')
sub("热更新-恢复", 'tkey: hot.run.tkey || "", mode: hot.run.mode || "" };', 'tkey: hot.run.tkey || "", mode: hot.run.mode || "", day: hot.run.day || (hot.run.tkey ? dayStr() : "") };')
sub("热更新-快照", 'tkey: S.run.tkey, mode: S.run.mode } : null }));', 'tkey: S.run.tkey, mode: S.run.mode, day: S.run.day } : null }));')

# ---------- 四、估算：明天的第一次复习要算上已经过期、今天排不进去的 ----------
sub("估算-参数", 'function coreShort(size, newToday, done) {', 'function coreShort(size, newToday, done, pending) {')
sub("估算-明天", '''  if (after >= 1) {       // 明天：今天答错的次日再出，加上明天到期的第一次复习，剩下的位置给新题（不少于保底）；再往后按保底算
    const tomorrow = addDays(today, 1);
    const firstDue = core.filter((q) => P[q.id] && P[q.id].b === 1 && P[q.id].due === tomorrow).length;''',
    '''  if (after >= 1) {       // 明天：今天答错的次日再出，加上明天及以前到期的第一次复习（缺过几天后会积压），剩下的位置给新题（不少于保底）；再往后按保底算
    const tomorrow = addDays(today, 1), pend = new Set(pending || []);     // 今天计划里还没做的题今天会做掉，不算到明天头上
    const firstDue = core.filter((q) => !pend.has(q.id) && P[q.id] && P[q.id].b === 1 && P[q.id].due <= tomorrow).length;''')
sub("面板-待做", '  let newToday = 0;         // 今天的计划里还没做的核心新题数', '  let newToday = 0, pending = [];   // 今天的计划里还没做的核心新题数、还没做的题')
sub("面板-做完", '''    box.append(h("div", null, h("h2", { text: "今日计划：做完了" }), h("p", { class: "sub", text: `${t.ids.length}题，答对${right}题。答错的明天先出（当天重做不算过关），答对的隔2天、4天再出。` })),
      h("div", { class: "row" }, more.list.length ? h("button", { class: "btn primary", onclick: () => startRun(more.list, "计划加练") }, `再加${more.list.length}题`) : h("span", { class: "note", text: "计划里今天没有该做的题了。" }),
        ...daily("明天起每天题数")));''',
    '''    const moreNew = more.list.length ? more.n.new1 + more.n.new2 : 0;
    box.append(h("div", null, h("h2", { text: "今日计划：做完了" }), h("p", { class: "sub", text: `${t.ids.length}题，答对${right}题。` + (left === 0 ? "今天考试，做到这里就可以了。" : left === 1 ? "答错的明天先出（当天重做不算过关）。" : "答错的明天先出（当天重做不算过关），答对的隔2天、4天再出。") })),
      h("div", { class: "row" }, more.list.length ? h("button", { class: "btn primary", disabled: wait, onclick: () => startRun(more.list, "计划加练") }, `再加${more.list.length}题（${moreNew ? `新题${moreNew}道` : "都是复习"}）`) : h("span", { class: "note", text: left === 0 ? "今天不再加题。" : "计划里今天没有该做的题了。" }),
        ...daily(left === 0 ? "每天题数" : "明天起每天题数")));
    if (wait && more.list.length) box.append(h("p", { class: "note", text: "正在同步云端的做题记录，同步好就能加题（最多等10秒）。" }));''')
sub("面板-进行中", '''`已做${t.pos}题，还剩${t.ids.length - t.pos}题。前面是该复习的和排在前面的新题，中途停下，没做的明天接着排。` })),
      h("div", { class: "row" }, h("button", { class: "btn primary", disabled: wait, onclick: resumePlan }, "继续"), ...daily("明天起每天题数")));''',
    '''`已做${t.pos}题，还剩${t.ids.length - t.pos}题。` + (left === 0 ? "" : left === 1 ? "没做完的复习题明天接着排；明天考试，不上新题。" : "前面是该复习的和排在前面的新题，中途停下，没做的明天接着排。") })),
      h("div", { class: "row" }, h("button", { class: "btn primary", disabled: wait, onclick: resumePlan }, "继续"), ...daily(left === 0 ? "每天题数" : "明天起每天题数")));''')
sub("面板-待做1", "    newToday = t.ids.slice(t.pos).filter((id) => S.q[id] && S.q[id].t === 1 && !S.prog.q[id]).length;",
    "    pending = t.ids.slice(t.pos);\n    newToday = pending.filter((id) => S.q[id] && S.q[id].t === 1 && !S.prog.q[id]).length;")
sub("面板-待做2", "    newToday = prev.n.new1;", "    newToday = prev.n.new1; pending = prev.list.map((q) => q.id);")
sub("面板-估算", "const short = coreShort(size, newToday, done), last", "const short = coreShort(size, newToday, done, pending), last")
sub("面板-提示", "核心大约还差${short}道学不到；做完后点“再加20题”补上，或者把每天题数调高一档。`", "核心大约还差${short}道学不到；可以把每天题数调高一档，或者每天做完后点“再加20题”（按钮上标着其中几道是新题）。`")

# ---------- 五、换日、页面睡醒 ----------
block("换日与睡醒", 'function dayRolled() {', 'window.addEventListener("hashchange"', '''let rollSeen = "";
function dayRolled() {      // 换了日：前一天开的今日计划（或今日一组）收起来，没做的照规则排进今天；今日页重画成新的一天
  const today = dayStr();
  if (!S.prog || !shownDay || shownDay === today) return;
  if (S.run && S.run.day && S.run.day !== today) S.run = null;
  if (rollSeen !== today) { rollSeen = today; scheduleCloud(); }      // 题组“是不是今天的”变了：和云端再对一次
  if (!S.run) route(current() !== "today");      // 别的页原地重画，不跳回页顶
}
// 页面睡了一阵再回来（切到别处、锁屏、电脑合盖超过2分钟）：云端可能已经被另一台设备推进了。先向云端读一次，读到之前（最多10秒）不让开始。
// 这里只管今日页的按钮，不拦写入：写云端之前本来就会先读一遍并进来。
const AWAY = 120000;
let wakeSeq = 0;
async function resync() {
  if (!S.ref || S.cloud === "local" || !S.synced || S.run || waking) return;
  const my = ++wakeSeq; let open = true;
  waking = setTimeout(() => {
    open = false; waking = 0;
    if (S.cloud === "ok") { S.cloud = "slow"; S.cloudNote = "云端记录暂时连不上，先存在这台设备上，连上后会自动合并。"; }
    cloudSettled(false);
  }, 10000);
  cloudSettled(false);
  for (let wait = 1000; ; wait = Math.min(wait * 2, 30000)) {
    try {
      const cur = await S.ref.get();
      if (!(cur.metadata && cur.metadata.fromCache)) {
        const r = cur.exists ? cur.data() : null;
        let took = 0, ahead = 0;
        if (r && r.v === 1) ({ took, ahead } = mergeProg(JSON.parse(JSON.stringify(r))));
        if (took) { normalize(S.prog); saveLocal(); }
        if (open) { open = false; clearTimeout(waking); waking = 0; }
        if (S.cloud === "slow" && S.synced) { S.cloud = "ok"; S.cloudNote = ""; }
        if (ahead) scheduleCloud();
        cloudSettled(took > 0);
        return;
      }
    } catch (e) {}
    // 没读到。10秒内接着试；10秒到了已经放行，之后只要页面还显示“连不上”，就隔一阵再读（间隔逐次加长到30秒），读到为止
    if (my !== wakeSeq || (!open && S.cloud !== "slow")) return;
    await new Promise((go) => setTimeout(go, wait));
    if (my !== wakeSeq || (!open && S.cloud !== "slow")) return;
  }
}
let lastAlive = Date.now(), hiddenAt = 0, lastAct = Date.now();
function back() {           // 页面回到眼前（切回来、解锁、电脑唤醒）：换了日就换成新的一天；离开超过2分钟，先向云端核对一次
  const now = Date.now(), gap = Math.max(now - lastAlive, hiddenAt ? now - hiddenAt : 0);
  lastAlive = now; hiddenAt = 0;
  dayRolled();
  if (gap >= AWAY) resync();
}
(function beat() {          // 每20秒看一眼：电脑睡了一阵刚醒（页面一直在眼前，没有“回到前台”的事件）；或者页面开着没人动、过了零点
  const now = Date.now();
  if (!document.hidden && now - lastAlive >= AWAY) back();
  else { lastAlive = now; if (!document.hidden && now - lastAct >= AWAY) dayRolled(); }
  setTimeout(beat, 20000);
})();
for (const ev of ["pointerdown", "keydown"]) document.addEventListener(ev, () => { lastAct = Date.now(); }, true);
document.addEventListener("visibilitychange", () => { if (document.hidden) { hiddenAt = Date.now(); flushCloud(); } else back(); });
window.addEventListener("pagehide", () => { if (!hiddenAt) hiddenAt = Date.now(); flushCloud(); });
window.addEventListener("pageshow", (e) => { if (e.persisted) back(); });
window.addEventListener("focus", back);
document.getElementById("tabs").addEventListener("click", (e) => {      // 做题时点当前所在的分栏：地址不变、不会触发 hashchange，这里补上退出
  const a = e.target.closest("a");
  if (a && S.run && a.getAttribute("href") === (location.hash || "#today")) { e.preventDefault(); exitRun(); }
});
''')

# ---------- 六、做题页的几处小毛病 ----------
sub("小结回页顶", '  if (R.pos >= R.list.length) { main.replaceChildren(runSummary()); return; }', '  if (R.pos >= R.list.length) { main.replaceChildren(runSummary()); window.scrollTo(0, 0); return; }')
sub("小结返回", '    h("button", { class: "btn", onclick: exitRun }, "回到今日")));', '    h("button", { class: "btn", onclick: exitRun }, current() === "today" ? "回到今日" : "返回")));')
sub("小结不拦回车", '  if (!S.run || !runState || /INPUT|SELECT|TEXTAREA/.test(e.target.tagName) || e.metaKey || e.ctrlKey || e.altKey) return;',
    '  if (!S.run || !runState || !$("#qcard") || /INPUT|SELECT|TEXTAREA/.test(e.target.tagName) || e.metaKey || e.ctrlKey || e.altKey) return;')
sub("作答算活动", '''function reveal(q) {
  if (runState.revealed) return;
  runState.revealed = true;''', '''function reveal(q) {
  if (runState.revealed) return;
  runState.revealed = true; lastAct = Date.now();''')
sub("下一题算活动", 'function nextQ() { if (S.run && S.run.pos <= S.run.list.length) { syncRun(); renderRun(); } }',
    'function nextQ() { lastAct = Date.now(); if (S.run && S.run.pos <= S.run.list.length) { syncRun(); renderRun(); } }')

# ---------- 七、说明文字 ----------
sub("小结-考试当天", '''  const box = h("section", { class: "panel today" }, h("h2", { text: `${R.label}：答对${right}/${R.list.length}` }),
    h("p", { class: "sub", text: wrong.length ? "下面是答错的题，明天会再出现；也可以现在再做一遍（政常题会换选项顺序，判断题换成改正后的说法）。当天重做不算过关，明天照样先出。" : (R.mode === "redo" ? "这一遍都对了。今天答错过的题明天还会先出一次，隔天答对才算过关。" : "全对。做对的题会隔几天再出，检验是不是真记住了。") }));''',
    '''  const exam = daysLeft() === 0;      // 考试当天：不提“明天”
  const box = h("section", { class: "panel today" }, h("h2", { text: `${R.label}：答对${right}/${R.list.length}` }),
    h("p", { class: "sub", text: wrong.length ? (exam ? "下面是答错的题，可以现在再做一遍（政常题会换选项顺序，判断题换成改正后的说法）。" : "下面是答错的题，明天会再出现；也可以现在再做一遍（政常题会换选项顺序，判断题换成改正后的说法）。当天重做不算过关，明天照样先出。")
      : exam ? (R.mode === "redo" ? "这一遍都对了。" : "全对。") : (R.mode === "redo" ? "这一遍都对了。今天答错过的题明天还会先出一次，隔天答对才算过关。" : "全对。做对的题会隔几天再出，检验是不是真记住了。") }));''')
sub("分科-做完", '`${t.ids.length}题，答对${right}题。错的题明天会再出现。` })),', '`${t.ids.length}题，答对${right}题。` + (daysLeft() === 0 ? "" : "错的题明天会再出现。") })),')
sub("分科-开关说明", '"这两个开关只管分科加练和自选练习；今日计划照精选名单出题。"', '"这两个开关只管分科加练和自选练习；今日计划的新题照精选名单出，不看这两个开关。"')
sub("题库说明", '`今日计划只用精选出来的${S.meta.plan.core + S.meta.plan.backup}道（核心${S.meta.plan.core}、备选${S.meta.plan.backup}），其余的题没有删，在“练习”里照样能选。`',
    '`今日计划的新题只从精选出来的${S.meta.plan.core + S.meta.plan.backup}道里出（核心${S.meta.plan.core}、备选${S.meta.plan.backup}）；其余的题没有删，在“练习”里照样能选，在那边答错的题第二天也会排进计划复习。`')

# ---------- 八、清除全部记录：清除时间只往后走 ----------
sub("清除", '  if (b.dataset.armed) { S.prog = { ...blankProg(), settings: S.prog.settings, epoch: new Date().toISOString() }; touch(); flushCloud(); route(); return; }',
    '''  if (b.dataset.armed) {
    // 清除时间只往后走：另一台设备的时钟偏快时，这一次清除也不会被当成更早的。设置和它的改动时间留着
    const pe = S.prog.epoch || "", ne = new Date().toISOString(), pt = new Date(pe).getTime();
    S.prog = { ...blankProg(), settings: S.prog.settings, ...(S.prog.st ? { st: S.prog.st } : {}), updated: S.prog.updated || "", epoch: ne > pe || isNaN(pt) ? ne : new Date(pt + 1).toISOString() };
    touch(); flushCloud(); route(); return;
  }''')

# ---------- 九、手机宽度下分栏条差2像素要横滑：窄屏时每个分栏左右各收2像素 ----------
sub("分栏条", 'nav.tabs .n { font-size: 11px; margin-left: 3px; color: var(--bad); font-variant-numeric: tabular-nums; }',
    'nav.tabs .n { font-size: 11px; margin-left: 3px; color: var(--bad); font-variant-numeric: tabular-nums; }\n@media (max-width: 430px) { nav.tabs a { padding-left: 6px; padding-right: 6px; } }')

open(p, "w", encoding="utf8").write(s)
print("ok", len(done), "处；", len(s), "字")
