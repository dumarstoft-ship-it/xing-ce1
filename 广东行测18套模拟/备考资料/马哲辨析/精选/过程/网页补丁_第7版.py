"""把“每日计划”两轮审查后的改动打进 index.html（先在副本上试，确认后再对仓库文件运行同一个脚本）。

用法：python3 patch_v7.py <index.html 路径>
每处替换都要求原文恰好出现一次，否则报错、不写文件。
"""
import sys
from pathlib import Path

path = Path(sys.argv[1])
s = path.read_text(encoding="utf-8")


def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)


def block(start, end, new):
    """把 start 标记（含）到 end 标记（不含）之间的内容换成 new。"""
    global s
    assert s.count(start) == 1, (s.count(start), start)
    assert s.count(end) == 1, (s.count(end), end)
    i, j = s.index(start), s.index(end)
    assert i < j
    s = s[:i] + new + s[j:]


# ---- 样式：真题来源标签太长时换行 ----
sub('.qmeta { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }',
    '.qmeta { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }\n.qmeta .pill { white-space: normal; }')

# ---- 状态 ----
sub('ref: null, saving: false, again: false, cloud: "connecting", cloudNote: "" };',
    'ref: null, saving: false, again: false, cloud: "connecting", cloudNote: "", synced: false, setSeen: "" };')

# ---- 云端同步：拿到云端确认过的记录之前不写；两边的记录按题合并，不整份覆盖；写之前先读；清除记录带时间戳 ----
block('function touch() {', 'function renderCloudNote()', """function stamp() {   // 记录的更新时间：保证比上一次的大（另一台设备的时钟偏快时，这边的改动也不会被当成旧的）
  const now = new Date().toISOString(), prev = S.prog.updated || "";
  if (now > prev) return now;
  const t = new Date(prev).getTime();
  return isNaN(t) ? now : new Date(t + 1).toISOString();
}
function touch() {
  S.prog.updated = stamp();
  const sj = canon(S.prog.settings);
  if (sj !== S.setSeen) { S.setSeen = sj; S.prog.st = S.prog.updated; }      // 设置改动的时间单独记：合并时设置跟最后改它的那台设备走
  saveLocal(); scheduleCloud();
}
let cloudTimer = 0, retryTimer = 0, retryWait = 0;
function scheduleCloud() { clearTimeout(cloudTimer); cloudTimer = setTimeout(() => { cloudTimer = 0; pushCloud(); }, 900); }
function flushCloud() { if (cloudTimer) { clearTimeout(cloudTimer); cloudTimer = 0; pushCloud(); } }   // 页面转到后台或关掉之前，把还没推的记录马上推出去
// 比较两份内容不看键的先后：云端返回的文档，键是按字母排过的，和本机写出去时的顺序不同
const canon = (v) => JSON.stringify(v, (k, x) => (x && typeof x === "object" && !Array.isArray(x) ? Object.fromEntries(Object.keys(x).sort().map((key) => [key, x[key]])) : x));
const sameRec = (a, b) => { const ka = Object.keys(a), kb = Object.keys(b); return ka.length === kb.length && ka.every((k) => a[k] === b[k]); };
async function pushCloud() {
  if (!S.ref || S.cloud === "local" || !S.synced) return;     // 没拿到云端确认过的记录之前不写，免得用这台设备的旧记录盖掉云端
  if (S.saving) { S.again = true; return; }
  S.saving = true; clearTimeout(retryTimer);
  try {
    const cur = await S.ref.get();                             // 写之前先读云端现在的记录并进来：整份写入才不会盖掉别的设备刚写的
    if (cur.metadata && cur.metadata.fromCache) throw { code: "unavailable" };
    const r = cur.exists ? cur.data() : null;
    if (r && r.v === 1 && mergeProg(JSON.parse(JSON.stringify(r))).took) { normalize(S.prog); saveLocal(); cloudSettled(true); }
    const body = JSON.parse(JSON.stringify(S.prog));
    if (!r || canon(body) !== canon(r)) await S.ref.set(body); // 内容一样就不写
    S.cloud = "ok"; retryWait = 0;
  }
  catch (e) {
    const code = e && e.code;
    if (code === "quota_exceeded") { S.cloud = "local"; S.cloudNote = "云端存储已满，记录先存在这台设备上。"; }
    else if (["invalid_argument", "not_granted", "revoked", "capability_disabled", "capability_removed", "transform_error"].includes(code)) { S.cloud = "local"; S.cloudNote = "只有页面的所有者能把记录存到云端；你的记录存在这台设备的浏览器里。"; }
    else { retryWait = Math.min(60000, (retryWait || 1000) * 2); retryTimer = setTimeout(pushCloud, retryWait + Math.random() * 1000); }   // 一时连不上：过一会儿再试，只留一条重试，间隔逐次加长
    renderCloudNote();
  } finally {
    S.saving = false;
    if (S.again) { S.again = false; pushCloud(); }
  }
}
// 把另一份记录并进本机。返回 took（采用了对方几处）和 ahead（本机有几处比对方新，需要推回云端）。
// 规则：谁“清除全部记录”的时间更晚，就整份跟谁；否则同一道题留最近练过的那份（同一天取作答次数多的），每天的作答数取多的，
// 当天定好的题组留今天的那份，设置和其余拿不准的地方跟较新的整份记录。
function mergeProg(inc) {
  const ie = inc.epoch || "", me = S.prog.epoch || "";
  if (ie > me) { S.prog = normalize(inc); S.setSeen = canon(S.prog.settings); return { took: 1, ahead: 0 }; }     // 对方是清除之后的记录：整份采用，本机清除前的记录不再并回去
  if (me > ie) return { took: 0, ahead: 1 };                                   // 本机清除过、对方还是清除前的：整份推上去
  const mine = S.prog, iq = inc.q || {}, idays = inc.days || {};
  const iu = inc.updated || "", mu = mine.updated || "";
  const incWins = (a, b) => iu > mu || (iu === mu && canon(b) > canon(a));     // 一样新时按内容定一个固定的先后，两台设备不会各执一词来回写
  let took = 0, ahead = 0;
  const newer = (a, b) => (a.d || "") > (b.d || "") || ((a.d || "") === (b.d || "") && (a.n || 0) > (b.n || 0));
  for (const [id, p] of Object.entries(iq)) {
    const m = mine.q[id];
    if (!m || newer(p, m)) { mine.q[id] = p; took++; }
    else if (newer(m, p)) ahead++;
    else if (!sameRec(p, m)) {       // 同一天、同样的作答次数但内容不同：一边答错一边答对的，以答错的为准（明天再出）；否则冲突的跟较新的一份。只有一边有的字段（如“能讲清”的自评）留着
      const u = ((p.l === 0) !== (m.l === 0) ? p.l === 0 : incWins(m, p)) ? { ...m, ...p } : { ...p, ...m };
      if (!sameRec(u, m)) { mine.q[id] = u; took++; }
      if (!sameRec(u, p)) ahead++;
    }
  }
  for (const id in mine.q) if (!iq[id]) ahead++;
  for (const [d, v] of Object.entries(idays)) {
    const m = mine.days[d];
    if (!m || (v.n || 0) > (m.n || 0)) { mine.days[d] = v; took++; } else if ((m.n || 0) > (v.n || 0)) ahead++;
  }
  for (const d in mine.days) if (!idays[d]) ahead++;
  const day = dayStr(), isToday = (g) => !!g && g.day === day;
  for (const k of ["today", "today2", "plan"]) {       // 只有一边是今天的题组：留今天的；否则跟较新的整份记录
    const a = mine[k] || null, b = inc[k] || null;
    if (canon(a) === canon(b)) continue;
    if (isToday(a) !== isToday(b) ? isToday(b) : incWins(a, b)) { mine[k] = b; took++; } else ahead++;
  }
  const iset = { ...DEFAULT_SETTINGS, ...(inc.settings || {}) }, ist = inc.st || "", mst = mine.st || "";
  if (canon(mine.settings) !== canon(iset)) {          // 设置跟最后改它的一边；都没记改动时间的老记录，跟较新的整份记录
    if (ist !== mst ? ist > mst : incWins(mine.settings, iset)) { mine.settings = iset; mine.st = ist; S.setSeen = canon(iset); took++; } else ahead++;
  } else if (ist > mst) mine.st = ist;
  if (iu > mu) mine.updated = iu; else if (mu > iu) ahead++;
  return { took, ahead };
}
const syncing = () => S.cloud === "connecting" && !S.synced;   // 还在等云端的记录：这时先不让开始，免得照着空白记录排计划
function cloudSettled(changed) {   // 同步状态变了：今日页要重画（按钮可用了、记录变了）；做题中只在眼前这道题已经在别处做过时才换题
  renderCloudNote();
  if (S.run) { if (changed && runState && !runState.revealed) { const at = S.run.pos; syncRun(); if (S.run.pos !== at) renderRun(); } updateTabs(); return; }
  if (changed || current() === "today") route(true); else updateTabs();
}
async function connectCloud() {
  const timer = setTimeout(() => { if (S.cloud === "connecting") { S.cloud = "slow"; S.cloudNote = "云端记录暂时连不上，先存在这台设备上，连上后会自动合并。"; cloudSettled(false); } }, 10000);
  let db = null;
  try { db = window.claude && window.claude.use ? await window.claude.use("db") : null; } catch (e) { db = null; }
  if (!db) { clearTimeout(timer); S.cloud = "local"; S.cloudNote = "在这里打开时，记录只存在这台设备的浏览器里；可以在“记录”页导出备份。"; cloudSettled(false); return; }
  try { S.ref = db.doc("progress/main"); } catch (e) { clearTimeout(timer); S.cloud = "local"; cloudSettled(false); return; }
  S.ref.onSnapshot((snap) => {
    const fresh = !snap.metadata.fromCache;            // 云端确认过的记录；否则只是这台设备上次留下的副本
    if (!fresh && !snap.exists) return;
    if (snap.metadata.hasPendingWrites) return;
    const first = fresh && !S.synced;
    if (fresh) { clearTimeout(timer); S.synced = true; if (S.cloud === "connecting" || S.cloud === "slow") { S.cloud = "ok"; S.cloudNote = ""; } }
    const remote = snap.exists ? snap.data() : null;
    let took = 0, ahead = S.prog.updated ? 1 : 0;
    if (remote && remote.v === 1) ({ took, ahead } = mergeProg(JSON.parse(JSON.stringify(remote))));
    if (took) { normalize(S.prog); saveLocal(); }
    if (fresh && ahead) scheduleCloud();              // 本机有云端没有的内容：推回去（推之前会再读一次，内容一样就不写）
    if (took || first) cloudSettled(took > 0); else renderCloudNote();
  }, () => { clearTimeout(timer); S.cloud = "local"; S.cloudNote = "云端记录连不上，记录先存在这台设备上。"; cloudSettled(false); });
}
""")

# ---- 作答记录：当天重做不改复习安排 ----
block('function record(q, correct) {', 'function setExplain(', '''function record(q, correct) {
  const today = dayStr();
  const old = S.prog.q[q.id];
  const p = old || { n: 0, c: 0, l: 0, b: 0, f: today, d: today, due: today, f1: correct ? 1 : 0 };
  const again = !!old && old.d === today;        // 今天已经答过这道题
  const b0 = Number.isFinite(p.b) ? p.b : 0;     // 很老的记录可能没有盒子编号
  p.n = (p.n || 0) + 1; p.c = (p.c || 0) + (correct ? 1 : 0); p.l = correct ? 1 : 0; p.d = today;
  if (!correct) { p.b = 0; p.due = addDays(today, 1); }
  else if (!again) { p.b = Math.min(b0 + 1, INTERVALS.length - 1); p.due = addDays(today, INTERVALS[p.b]); if (p.f < today) p.x = 1; }
  else { p.b = b0; if (!p.due) p.due = addDays(today, 1); }
  // 当天再答对不改复习安排：今天答错过的，明天照样先出（b 仍是 0）；今天已经答对过的，不连升两级
  S.prog.q[q.id] = p;
  const dd = S.prog.days[today] || { n: 0, c: 0 };
  dd.n += 1; dd.c += correct ? 1 : 0; S.prog.days[today] = dd;
  touch();
}
''')

# ---- 每日计划 ----
block('// ---------- 每日计划：', 'function plannedMix(', '''// ---------- 每日计划：精选题（核心、备选）按价值顺序学，到期的先复习 ----------
// 平日一天的题按这个顺序填满，做不完的自动顺延：
//   ①答错后还没隔天答对的 ②保底的核心新题（每天题数的四成） ③核心里只答对过一次、今天到期的（第一次间隔复习）
//   ④其余核心新题 ⑤核心里答对两次以上、今天到期的 ⑥备选里到期的 ⑦备选新题 ⑧还有空位就补最久没见的
// 考前两天和考试当天：①之后先出错过的题和自评讲不清的题，再出其余到期的、新题（考试当天不上新题）、最久没见的核心题，最后才是备选。
// 间隔：答错次日再出；答对后依次隔2天、4天、7天。当天重做不算数（见 record）。
const TIER_NAME = { 1: "核心", 2: "备选", 3: "扩展" };
const tierOf = (q) => q.t || 3;
const inPlan = (q) => q.t === 1 || q.t === 2;
const hasPlan = () => S.qs.some((q) => q.t === 1);
const dailyOf = () => S.prog.settings.daily || 50;
const daysLeft = () => dayDiff(dayStr(), EXAM_DAY);
const finalDays = () => { const n = daysLeft(); return n >= 0 && n <= 2; };
const NEW_FLOOR = 0.4;      // 平日保底的核心新题占每天题数的比例
function planParts(size, skip) {
  const today = dayStr(), P = S.prog.q;
  const all = S.qs.filter((q) => !paused(q) && !(skip && skip.has(q.id)));
  const out = [], used = new Set(), cardsNew = new Set();
  const n = { wrong: 0, first: 0, look: 0, new1: 0, later: 0, new2: 0, extra: 0 };
  const ord = (q) => (q.o == null ? 1e9 : q.o);
  const byDue = (a, b) => (P[a.id].due < P[b.id].due ? -1 : P[a.id].due > P[b.id].due ? 1 : ord(a) - ord(b));
  const byLast = (a, b) => (P[a.id].d < P[b.id].d ? -1 : P[a.id].d > P[b.id].d ? 1 : ord(a) - ord(b));
  // 复习类打乱；新题保持价值顺序（只做一部分就停的话，学到的是排在前面的）
  const put = (pick, k, keep) => { for (const q of spread(keep ? pick : shuffle(pick))) { used.add(q.id); out.push(q); n[k]++; } };
  const addClass = (list, k, sorter) => { const room = size - out.length; if (room > 0) put(list.filter((q) => !used.has(q.id)).sort(sorter).slice(0, room), k); };
  for (const q of S.qs) { const p = P[q.id]; if (p && p.f === today) q.cards.forEach((c) => cardsNew.add(c)); }   // 今天已经学过新题的知识点（“再加20题”时用得上）
  const addNew = (tier, k, cap) => {
    const room = Math.min(size - out.length, cap == null ? size : cap), pick = [];
    if (room <= 0) return;
    const fresh = all.filter((x) => x.t === tier && !P[x.id] && !used.has(x.id)).sort((a, b) => ord(a) - ord(b));
    for (const q of fresh) {
      if (pick.length >= room) break;
      if (q.cards.some((c) => cardsNew.has(c))) continue;      // 同一个知识点一天只上一道新题
      q.cards.forEach((c) => cardsNew.add(c)); pick.push(q);
    }
    if (tier === 1) for (const q of fresh) { if (pick.length >= room) break; if (!pick.includes(q)) pick.push(q); }   // 核心凑不满时放宽这一条，不让备选插到核心前面
    put(pick.sort((a, b) => ord(a) - ord(b)), k, true);
  };
  const seen = all.filter((q) => P[q.id]);
  const isCore = (q) => q.t === 1, missed = (q) => P[q.id].c < P[q.id].n;
  const due = seen.filter((q) => P[q.id].due <= today && (inPlan(q) || !P[q.id].b));   // 计划外的题只追答错的
  const once1 = due.filter((q) => isCore(q) && P[q.id].b === 1);
  const fin = finalDays(), left = daysLeft(), cut = addDays(today, -1);
  addClass(due.filter((q) => !P[q.id].b), "wrong", byDue);
  if (fin) {
    addClass(once1.filter(missed), "first", byDue);
    addClass(seen.filter((q) => isCore(q) && P[q.id].d < cut && (missed(q) || P[q.id].e === 0)), "look", byLast);
    addClass(once1, "first", byDue);
  } else {
    addNew(1, "new1", Math.round(size * NEW_FLOOR));
    addClass(once1, "first", byDue);
  }
  if (left !== 0) addNew(1, "new1");
  addClass(due.filter((q) => isCore(q) && P[q.id].b >= 2), "later", byDue);
  if (fin) addClass(seen.filter((q) => isCore(q) && P[q.id].d < cut), "extra", byLast);
  addClass(due.filter((q) => q.t === 2 && P[q.id].b >= 1), "later", byDue);
  if (left !== 0) addNew(2, "new2");
  addClass(seen.filter((q) => inPlan(q) && P[q.id].d < today), "extra", (a, b) => (P[a.id].l - P[b.id].l) || byLast(a, b));
  return { list: out, n };
}
function planGroup(create) {
  const today = dayStr(), t = S.prog.plan;
  if (t && t.day === today) return t;
  if (!create) return null;
  const { list, n } = planParts(dailyOf());
  S.prog.plan = { day: today, ids: list.map((q) => q.id), pos: 0, res: {}, n };
  touch();
  return S.prog.plan;
}
// 当天定好的题组（今日计划、分科的今日一组）：清单里还没轮到、但今天已经在别处做过的题算作已做，不再出一遍；题库里已经没有的题去掉
function settle(t) {
  if (!t) return t;
  const today = dayStr(), P = S.prog.q;
  const head = t.ids.slice(0, t.pos).filter((id) => S.q[id]);
  const tail = t.ids.slice(t.pos).filter((id) => S.q[id]);
  const moved = tail.filter((id) => P[id] && P[id].d === today);
  if (!moved.length && head.length + tail.length === t.ids.length) return t;
  for (const id of moved) t.res[id] = P[id].l;
  t.ids = head.concat(moved, tail.filter((id) => !moved.includes(id)));
  t.pos = head.length + moved.length;
  touch();
  return t;
}
function resumePlan() {
  const t = settle(planGroup(false));
  if (!t) { route(); return; }      // 页面开着过了零点：重画成新一天的计划
  S.run = { list: t.ids.map((id) => S.q[id]), pos: t.pos, res: t.res, label: "今日计划", tkey: "plan", mode: "" };
  route();
}
// 当天定好的题组做到一半时并进了别处的记录：接下来的题如果今天已经在别处做过，算作已做、不再出一遍；题组的位置跟着眼前这一组走
function syncRun() {
  const R = S.run; if (!R || !R.tkey) return;
  const today = dayStr(), P = S.prog.q;
  while (R.pos < R.list.length) { const id = R.list[R.pos].id; if (!(id in R.res) && P[id] && P[id].d === today) { R.res[id] = P[id].l; R.pos++; } else break; }
  const t = S.prog[R.tkey];
  if (t && t.day === today && (t.pos !== R.pos || t.res !== R.res)) { t.ids = R.list.map((q) => q.id); t.pos = R.pos; t.res = R.res; touch(); }
}
// 粗算：照现在的量，到考前第3天为止（最后两天以复习为主）核心大约还差几道学不到；够学完时是0
function coreShort(size, newToday, done) {
  const left = daysLeft(), today = dayStr(), P = S.prog.q;
  const core = S.qs.filter((q) => q.t === 1 && !paused(q));
  const fresh = core.filter((q) => !P[q.id]).length;
  if (left <= 2) return fresh;
  const floor = Math.round(size * NEW_FLOOR), after = Math.max(0, left - 3);      // after：今天之后还能正常上新题的天数
  const firsts = Object.values(P).filter((p) => p.f1 === 0 || p.f1 === 1);
  const acc = firsts.length >= 20 ? Math.min(0.95, Math.max(0.5, firsts.filter((p) => p.f1).length / firsts.length)) : 0.75;
  let cap = done ? 0 : newToday;
  if (after >= 1) {       // 明天：今天答错的次日再出，加上明天到期的第一次复习，剩下的位置给新题（不少于保底）；再往后按保底算
    const tomorrow = addDays(today, 1);
    const firstDue = core.filter((q) => P[q.id] && P[q.id].b === 1 && P[q.id].due === tomorrow).length;
    cap += Math.min(size, Math.max(floor, size - firstDue - Math.round(size * (1 - acc)))) + floor * (after - 1);
  }
  return Math.max(0, fresh - cap);
}
function planCounts() {   // 核心、备选各学了多少
  const P = S.prog.q, c = {};
  for (const t of [1, 2]) {
    const qs = S.qs.filter((q) => q.t === t && !paused(q));
    c[t] = { total: qs.length, seen: qs.filter((q) => P[q.id]).length, twice: qs.filter((q) => P[q.id] && P[q.id].x).length, weak: qs.filter((q) => P[q.id] && !P[q.id].l).length };
  }
  return c;
}
function mixChips(n) {
  const rev = n.wrong + n.first + n.later + n.extra;
  return h("div", { class: "mix" },
    rev ? h("span", { class: "pill bad", text: `复习 ${rev}` + (n.wrong ? `（答错待过关 ${n.wrong}）` : "") }) : null,
    n.look ? h("span", { class: "pill warn", text: `考前回顾 ${n.look}` }) : null,
    n.new1 ? h("span", { class: "pill a", text: `核心新题 ${n.new1}` }) : null,
    n.new2 ? h("span", { class: "pill", text: `备选新题 ${n.new2}` }) : null);
}
function dailySelect() {
  const sel = h("select", { id: "dailySel", disabled: syncing(), onchange: (e) => { S.prog.settings.daily = Number(e.target.value); touch(); rerender("dailySel"); } });
  for (const k of [20, 30, 40, 50, 60, 80]) sel.append(h("option", { value: String(k), selected: k === dailyOf() }, `${k}题`));
  return sel;
}
function planPanel() {
  const t = settle(planGroup(false)), size = dailyOf(), c = planCounts();
  const box = h("section", { class: "panel today" });
  const left = daysLeft(), wait = syncing();
  const daily = (label) => [h("label", { class: "note", for: "dailySel" }, label), dailySelect()];
  const done = !!t && t.pos >= t.ids.length;
  let newToday = 0;         // 今天的计划里还没做的核心新题数
  if (done) {
    const right = Object.values(t.res).filter(Boolean).length;
    const more = left === 0 ? { list: [] } : planParts(20, new Set(t.ids));
    box.append(h("div", null, h("h2", { text: "今日计划：做完了" }), h("p", { class: "sub", text: `${t.ids.length}题，答对${right}题。答错的明天先出（当天重做不算过关），答对的隔2天、4天再出。` })),
      h("div", { class: "row" }, more.list.length ? h("button", { class: "btn primary", onclick: () => startRun(more.list, "计划加练") }, `再加${more.list.length}题`) : h("span", { class: "note", text: "计划里今天没有该做的题了。" }),
        ...daily("明天起每天题数")));
  } else if (t) {
    box.append(h("div", null, h("h2", { text: "今日计划" }), h("p", { class: "sub", text: `已做${t.pos}题，还剩${t.ids.length - t.pos}题。前面是该复习的和排在前面的新题，中途停下，没做的明天接着排。` })),
      h("div", { class: "row" }, h("button", { class: "btn primary", disabled: wait, onclick: resumePlan }, "继续"), ...daily("明天起每天题数")));
    if (wait) box.append(h("p", { class: "note", text: "正在同步云端的做题记录，同步好就能继续（最多等10秒）。" }));
    newToday = t.ids.slice(t.pos).filter((id) => S.q[id] && S.q[id].t === 1 && !S.prog.q[id]).length;
  } else {
    const prev = planParts(size);
    newToday = prev.n.new1;
    box.append(h("div", null, h("h2", { text: "今日计划" }), h("div", { class: "big", text: `${prev.list.length}题` })), mixChips(prev.n),
      h("div", { class: "row" }, h("button", { class: "btn primary", disabled: wait || !prev.list.length, onclick: () => { planGroup(true); resumePlan(); } }, "开始"), ...daily("每天题数")));
    if (wait) box.append(h("p", { class: "note", text: "正在同步云端的做题记录，同步好就能开始（最多等10秒）。" }));
    else if (left === 0) box.append(h("p", { class: "note", text: "今天考试：只出答错过的和该回顾的题，不上新题。" }));
    else if (finalDays()) box.append(h("p", { class: "note", text: "考前两天：先过答错过的和讲不清的题，再做到期的复习，新题排在后面。" }));
  }
  const freshCore = c[1].total - c[1].seen;
  box.append(h("div", { class: "stats3" },
    h("div", { class: "stat" }, h("div", { class: "v", text: `${c[1].seen}/${c[1].total}` }), h("div", { class: "k", text: "核心已学" })),
    h("div", { class: "stat" }, h("div", { class: "v", text: `${c[1].twice + c[2].twice}` }), h("div", { class: "k", text: "隔天又答对" })),
    h("div", { class: "stat" }, h("div", { class: "v", text: `${c[2].seen}/${c[2].total}` }), h("div", { class: "k", text: "备选已学" }))));
  if (left > 0 && freshCore > 0) {
    const short = coreShort(size, newToday, done), last = addDays(EXAM_DAY, -3).split("-");
    box.append(h("p", { class: "note", text: `核心还有${freshCore}道没学` + (!t && newToday ? `，今天的计划排了${newToday}道新题。` : "。")
      + (left <= 2 ? "考前两天以复习和回顾为主，新题排在后面，做不到也不要紧。"
        : short > 0 ? `照现在的量，到${Number(last[1])}月${Number(last[2])}日核心大约还差${short}道学不到；做完后点“再加20题”补上，或者把每天题数调高一档。` : "") }));
  }
  return box;
}
''')

# ---- 重画：改设置后原地重画；页面开着过了零点自动换成新一天 ----
block('function route() {', 'window.addEventListener("hashchange"', '''const OPEN = {};          // 折叠面板的展开状态，重画时保持
let shownDay = "";
function route(keep) {    // keep === true：原地重画，不回到页顶
  shownDay = dayStr();
  renderCountdown();
  updateTabs();
  if (S.run) { renderRun(); return; }
  const y = window.scrollY;
  const view = { today: viewToday, practice: viewPractice, review: viewReview, cards: viewCards, pending: viewPending, appendix: viewAppendix, stats: viewStats }[current()];
  $("#main").replaceChildren(...[].concat(view()));
  window.scrollTo(0, keep === true ? y : 0);
}
function rerender(id) { route(true); const el = id && document.getElementById(id); if (el) el.focus({ preventScroll: true }); }   // 改了设置：原地重画，焦点放回原控件
function dayRolled() { if (S.prog && shownDay && shownDay !== dayStr() && !S.run) route(); }
document.addEventListener("visibilitychange", () => { if (document.hidden) flushCloud(); else dayRolled(); });
window.addEventListener("pagehide", flushCloud);
window.addEventListener("focus", dayRolled);
''')

# ---- 今日页的小改动 ----
sub('{ class: "btn primary", onclick: () => { todayGroup(bank, true); resumeToday(bank); } }',
    '{ class: "btn primary", disabled: syncing(), onclick: () => { todayGroup(bank, true); resumeToday(bank); } }')
sub('touch(); route(); } }), " 含B档")', 'touch(); rerender("fmB"); } }), " 含B档")')
sub('touch(); route(); } }), " 含C档（默认关）")));',
    'touch(); rerender("fmC"); } }), " 含C档（默认关）")),\n      ...(hasPlan() ? [h("p", { class: "note", text: "这两个开关只管分科加练和自选练习；今日计划照精选名单出题。" })] : []));')
sub('const sel = h("select", { id: "size-" + bank, onchange: (e) => { S.prog.settings[key] = Number(e.target.value); touch(); route(); } });',
    'const sel = h("select", { id: "size-" + bank, disabled: syncing(), onchange: (e) => { S.prog.settings[key] = Number(e.target.value); touch(); rerender("size-" + bank); } });')
sub('h("div", { class: "row" }, h("button", { class: "btn primary", onclick: () => resumeToday(bank) }, "继续")));',
    'h("div", { class: "row" }, h("button", { class: "btn primary", disabled: syncing(), onclick: () => resumeToday(bank) }, "继续")));')
sub('''  if (bank === "fm") {
    const nf = newFocusPool(), core = corePool();''',
    '''  if (!hasPlan() && syncing()) box.append(h("p", { class: "note", text: "正在同步云端的做题记录，同步好就能开始（最多等10秒）。" }));
  if (bank === "fm") {
    const nf = newFocusPool(), core = corePool();''')
sub('const extra = h("details", { class: "panel more" }, h("summary", null, h("b", { text: "分科加练（计划之外）" })',
    'const extra = h("details", { class: "panel more", open: !!OPEN.extra, ontoggle: (e) => { OPEN.extra = e.currentTarget.open; } }, h("summary", null, h("b", { text: "分科加练（计划之外）" })')
sub('return h("details", { class: "panel more" }, h("summary", null, h("b", { text: `精选依据：',
    'return h("details", { class: "panel more", open: !!OPEN.why, ontoggle: (e) => { OPEN.why = e.currentTarget.open; } }, h("summary", null, h("b", { text: `精选依据：')
sub('''function resumeToday(bank) {
  const t = todayGroup(bank, false);
  if (!t) return;''',
    '''function resumeToday(bank) {
  const t = settle(todayGroup(bank, false));
  if (!t) { route(); return; }''')
sub('''function todayPanel(bank) {
  const t = todayGroup(bank, false);''',
    '''function todayPanel(bank) {
  const t = settle(todayGroup(bank, false));''')

# ---- 小结页：当天重做不算过关 ----
sub('下面是答错的题，明天会再出现；也可以现在再做一遍（政常题会换选项顺序，判断题换成改正后的说法）。',
    '下面是答错的题，明天会再出现；也可以现在再做一遍（政常题会换选项顺序，判断题换成改正后的说法）。当天重做不算过关，明天照样先出。')
sub(': "全对。做对的题会隔几天再出，检验是不是真记住了。"',
    ': (R.mode === "redo" ? "这一遍都对了。今天答错过的题明天还会先出一次，隔天答对才算过关。" : "全对。做对的题会隔几天再出，检验是不是真记住了。")')

# ---- 自选练习：选了精选档位时不再套B档、C档开关 ----
sub(': (q.bank !== "fm" || allowPrio(q)))', ': (q.bank !== "fm" || F.tier.size > 0 || allowPrio(q)))')

# ---- 记录页设置里也能改每天题数 ----
sub('h("label", { for: "size-fm", text: "政常每组题数" }), sizeSelect("fm")),',
    'h("label", { for: "size-fm", text: "政常每组题数" }), sizeSelect("fm")),\n    hasPlan() ? h("div", { class: "setting", style: "margin-top:8px" }, h("label", { for: "dailySel", text: "今日计划每天题数" }), dailySelect()) : null,')

# ---- 精选依据的表头、题库说明 ----
sub('h("th", { text: "近三年真题" })', 'h("th", { text: "近三年真题（45题）" })')
sub('"。所有新题都是自编训练题，不是官方真题；判断题照答题卡习惯，正确涂A、错误涂B。" }));',
    '"。所有新题都是自编训练题，不是官方真题；判断题照答题卡习惯，正确涂A、错误涂B。" +\n      (hasPlan() && S.meta.plan ? `今日计划只用精选出来的${S.meta.plan.core + S.meta.plan.backup}道（核心${S.meta.plan.core}、备选${S.meta.plan.backup}），其余的题没有删，在“练习”里照样能选。` : "") }));')

# ---- 做题当中并进了别处的记录：下一题之前先对一下 ----
sub('function nextQ() { if (S.run && S.run.pos <= S.run.list.length) renderRun(); }',
    'function nextQ() { if (S.run && S.run.pos <= S.run.list.length) { syncRun(); renderRun(); } }')

# ---- 清除全部记录：带上清除时间（合并时先比它，清掉的记录不会被别的设备并回来），并马上推到云端 ----
sub('if (b.dataset.armed) { S.prog = { ...blankProg(), settings: S.prog.settings }; touch(); route(); return; }',
    'if (b.dataset.armed) { S.prog = { ...blankProg(), settings: S.prog.settings, epoch: new Date().toISOString() }; touch(); flushCloud(); route(); return; }')

# ---- 启动：记下载入时的设置，之后设置有改动才更新“设置改动时间” ----
sub('  S.prog = loadLocal() || blankProg();',
    '  S.prog = loadLocal() || blankProg();\n  S.setSeen = canon(S.prog.settings);')

path.write_text(s, encoding="utf-8")
print("patched:", path)
