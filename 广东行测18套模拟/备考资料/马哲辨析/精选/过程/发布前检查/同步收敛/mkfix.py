# 审查用：在 v7b 的副本上试改（只为验证建议的改法能不能过同一套测试；不动 v7b 本身）
import re, shutil, sys, os
here = os.path.dirname(os.path.abspath(__file__))
src, dst = os.path.join(here, "site"), os.path.join(here, "site_fix")
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(src, dst)
p = os.path.join(dst, "index.html")
s = open(p, encoding="utf8").read()
only = set(sys.argv[1:])          # 可以只打其中几处：run epoch wrong days mid st late

def rep(tag, old, new, regex=False):
    global s
    if only and tag not in only: return
    if regex:
        s2, n = re.subn(old, lambda m: new, s, count=1, flags=re.S)
    else:
        n = s.count(old); s2 = s.replace(old, new)
    assert n == 1, (tag, n, old[:60])
    s = s2

# 1 做题页只往“自己那一组”里写，而且只在自己更靠前时才写
rep("run", 'pos: t.pos, res: t.res, label: "今日计划"', 'pos: t.pos, res: { ...t.res }, label: "今日计划"')
rep("run", 'pos: t.pos, res: t.res, label: bank === "fm"', 'pos: t.pos, res: { ...t.res }, label: bank === "fm"')
rep("run", 'tkey: "plan", mode: "" };', 'tkey: "plan", mode: "", day: t.day };')
rep("run", 'tkey: todayKey(bank), mode: "" };', 'tkey: todayKey(bank), mode: "", day: t.day };')
rep("run", 'tkey: hot.run.tkey || "", mode: hot.run.mode || "" };', 'tkey: hot.run.tkey || "", mode: hot.run.mode || "", day: hot.run.day || dayStr() };')
rep("run", 'tkey: S.run.tkey, mode: S.run.mode } : null }));', 'tkey: S.run.tkey, mode: S.run.mode, day: S.run.day } : null }));')
rep("run", '''function syncRun() {
  const R = S.run; if (!R || !R.tkey) return;
  const today = dayStr(), P = S.prog.q;''', '''function ownGroup(R) {      // 做题页手里这一组，还是不是记录里当天的那一组（隔了一天、或别的设备另排了一组，就不是了）
  const t = R && R.tkey ? S.prog[R.tkey] : null;
  if (!t || t.day !== dayStr() || t.day !== R.day || t.ids.length !== R.list.length || !R.list.every((q) => t.ids.includes(q.id))) return null;
  return t;
}
function saveRun() {         // 把做题页的进度写回题组：只在比记录里的靠前（多做了题）时才写
  const R = S.run; if (!R || !R.tkey) return;
  const t = ownGroup(R); if (!t) { R.tkey = ""; return; }
  if (R.pos > t.pos || Object.keys(R.res).some((id) => !(id in t.res))) { t.ids = R.list.map((q) => q.id); t.pos = R.pos; t.res = { ...t.res, ...R.res }; touch(); }
}
function syncRun() {
  const R = S.run; if (!R || !R.tkey) return;
  if (!ownGroup(R)) { R.tkey = ""; return; }
  const today = dayStr(), P = S.prog.q;''')
rep("run", '''  const t = S.prog[R.tkey];
  if (t && t.day === today && (t.pos !== R.pos || t.res !== R.res)) { t.ids = R.list.map((q) => q.id); t.pos = R.pos; t.res = R.res; touch(); }
''', '''  saveRun();
''')
rep("run", '  if (R.tkey && S.prog[R.tkey]) { S.prog[R.tkey].pos = R.pos; S.prog[R.tkey].res = R.res; touch(); }', '  saveRun();')

# 2 清除时间不倒退
rep("epoch", 'S.prog = { ...blankProg(), settings: S.prog.settings, epoch: new Date().toISOString() };',
    '{ const pe = S.prog.epoch || "", ne = new Date().toISOString(); S.prog = { ...blankProg(), settings: S.prog.settings, epoch: ne > pe ? ne : new Date(new Date(pe).getTime() + 1).toISOString() }; }')

# 3 同一天有一边答错过：合并后照答错处理
rep("wrong", r"    if \(!m \|\| newer\(p, m\)\) \{ mine\.q\[id\] = p; took\+\+; \}\n.*?      if \(!sameRec\(u, p\)\) ahead\+\+;\n    \}\n", '''    let u;
    if (!m || newer(p, m)) u = p;
    else if (newer(m, p)) u = m;
    else if (sameRec(p, m)) continue;
    else u = ((p.l === 0) !== (m.l === 0) ? p.l === 0 : incWins(m, p)) ? { ...m, ...p } : { ...p, ...m };
    if (m && u.d && (m.d || "") === (p.d || "") && (m.b === 0 || p.b === 0) && u.b !== 0) u = { ...u, b: 0, due: addDays(u.d, 1) };
    if (!m || !sameRec(u, m)) { mine.q[id] = u; took++; }
    if (!sameRec(u, p)) ahead++;
''', regex=True)

# 4 每天作答数：题数一样时按答对数定
rep("days", '    if (!m || (v.n || 0) > (m.n || 0)) { mine.days[d] = v; took++; } else if ((m.n || 0) > (v.n || 0)) ahead++;',
    '''    const big = (x, y) => (x.n || 0) > (y.n || 0) || ((x.n || 0) === (y.n || 0) && (x.c || 0) > (y.c || 0));
    if (!m || big(v, m)) { mine.days[d] = v; took++; } else if (big(m, v)) ahead++;''')

# 5 零点前后两台设备日期不一致：不为“对方日期比我晚”的题组推回去
rep("mid", '    if (isToday(a) !== isToday(b) ? isToday(b) : incWins(a, b)) { mine[k] = b; took++; } else ahead++;',
    '''    if (isToday(a) !== isToday(b)) { if (isToday(b)) { mine[k] = b; took++; } else if (!(b && b.day > day)) ahead++; }
    else if (incWins(a, b)) { mine[k] = b; took++; } else ahead++;''')

rep("mid", 'function dayRolled() { if (S.prog && shownDay && shownDay !== dayStr() && !S.run) route(); }',
    'function dayRolled() { if (S.prog && shownDay && shownDay !== dayStr()) { scheduleCloud(); if (!S.run) route(); } }')

# 6 st 不一样也算一处不同
rep("st", '  } else if (ist > mst) mine.st = ist;', '  } else if (ist > mst) { mine.st = ist; took++; } else if (mst > ist) ahead++;')

# 7 清除迟到：只作废清除当天及之前的记录，之后的日子里做的留下；并让旧版页面把新版推上去的当成较新的
rep("late", r"  if \(ie > me\) \{ S\.prog = normalize\(inc\);.*?\n  if \(me > ie\) return \{ took: 0, ahead: 1 \};[^\n]*\n", '''  let took = 0, ahead = 0;
  if (ie !== me) {
    const hi = ie > me ? ie : me, cut = dayStr(new Date(hi)), old = ie > me ? S.prog : inc;
    old.q = Object.fromEntries(Object.entries(old.q || {}).filter(([, p]) => (p.d || "") > cut));
    old.days = Object.fromEntries(Object.entries(old.days || {}).filter(([d]) => d > cut));
    for (const k of ["today", "today2", "plan"]) if (old[k] && !(old[k].day > cut)) old[k] = null;
    old.epoch = hi;
    if (ie > me) took++; else ahead++;
  }
''', regex=True)
rep("late", '  let took = 0, ahead = 0;\n  const newer = (a, b) =>', '  const newer = (a, b) =>')
rep("late", '  if (iu > mu) mine.updated = iu; else if (mu > iu) ahead++;\n  return { took, ahead };',
    '''  if (iu > mu) mine.updated = iu; else if (mu > iu) ahead++;
  if (me > ie && iu >= mu) mine.updated = new Date(new Date(iu).getTime() + 1).toISOString();
  return { took, ahead };''')

open(p, "w", encoding="utf8").write(s)
print("ok", sorted(only) if only else "all", len(s))
