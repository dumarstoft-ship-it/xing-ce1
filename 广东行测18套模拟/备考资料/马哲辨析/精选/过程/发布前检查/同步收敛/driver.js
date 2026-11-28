// 在页面脚本的同一个环境里运行：只调用页面自己的函数（和页面按钮的 onclick 写法一致）
globalThis.__drv = {
  info() {
    return { ready: !!(S.prog && S.qs.length),
      run: S.run ? { tkey: S.run.tkey, pos: S.run.pos, len: S.run.list.length, revealed: !!(runState && runState.revealed), mode: S.run.mode } : null,
      synced: !!S.synced, cloud: S.cloud, epoch: (S.prog && S.prog.epoch) || "", day: dayStr(), updated: (S.prog && S.prog.updated) || "",
      wait: typeof syncing === "function" ? syncing() : false, nq: S.prog ? Object.keys(S.prog.q).length : 0 };
  },
  snap() { return JSON.stringify(S.prog); },
  group(k) { const t = S.prog && S.prog[k]; return t ? { day: t.day, ids: t.ids.slice(), pos: t.pos, nres: Object.keys(t.res || {}).length } : null; },
  panel() {   // 今日页“今日计划”那一栏现在显示什么
    const t = planGroup(false); if (!t) return "未开始";
    return t.pos >= t.ids.length ? "做完了(" + t.ids.length + "题)" : "已做" + t.pos + "题，还剩" + (t.ids.length - t.pos) + "题";
  },
  startPlan() {
    if (S.run) return { r: "inrun" };
    if (typeof syncing === "function" && syncing()) return { r: "wait" };
    if (!hasPlan()) return { r: "noplan" };
    let t = planGroup(false);
    if (t && typeof settle === "function") t = settle(t);     // 新版今日页画出来时就会 settle
    if (t && t.pos >= t.ids.length) {
      if (typeof daysLeft !== "function") return { r: "none" };
      const more = daysLeft() === 0 ? { list: [] } : planParts(20, new Set(t.ids));
      if (!more.list.length) return { r: "none" };
      startRun(more.list, "计划加练"); return { r: "more" };
    }
    let created = false;
    if (!t) { const prev = planParts(dailyOf()); if (!prev.list.length) return { r: "none" }; planGroup(true); created = true; }
    resumePlan();
    const g = S.prog.plan;
    return { r: created ? "created" : "resumed", day: g && g.day, ids: g ? g.ids.slice() : [] };
  },
  startBank(bank) {
    if (S.run) return { r: "inrun" };
    if (typeof syncing === "function" && syncing()) return { r: "wait" };
    const key = bank === "fm" ? "today2" : "today";
    const t = todayGroup(bank, false);
    if (t && t.pos >= t.ids.length) return { r: "done" };
    let created = false;
    if (!t) { todayGroup(bank, true); created = true; }
    resumeToday(bank);
    const g = S.prog[key];
    return { r: created ? "created" : "resumed", day: g && g.day, ids: g ? g.ids.slice() : [] };
  },
  practice(ids, mode) {
    if (S.run) return false;
    const list = ids.map((id) => S.q[id]).filter(Boolean);
    if (!list.length) return false;
    startRun(list, mode === "redo" ? "本组错题再做一遍" : "练习", mode || "");
    return true;
  },
  answer(ok) {
    const R = S.run; if (!R || R.pos >= R.list.length || !runState || runState.revealed) return null;
    const q = R.list[R.pos]; const pres = runState.pres; const ans = pres ? pres.answer : q.answer;
    if (q.type === "判断") runState.picked = new Set([ok ? ans : (ans === "正确" ? "错误" : "正确")]);
    else { const letters = pres && pres.letters ? pres.letters : Object.keys(q.options || {}).sort(); runState.picked = new Set(ok ? ans.split("") : [letters.find((x) => !ans.includes(x)) || ans[0]]); }
    reveal(q);
    const p = S.prog.q[q.id];
    return { id: q.id, day: dayStr(), epoch: S.prog.epoch || "", correct: p.l === 1, n: p.n, b: p.b, due: p.due };
  },
  next() { if (S.run && runState && runState.revealed) { nextQ(); return true; } return false; },
  rate(v) { const R = S.run; if (!R || !runState || !runState.revealed || R.pos < 1) return null; const q = R.list[R.pos - 1]; setExplain(q, v); return q.id; },
  exit() { if (S.run) { exitRun(); return true; } return false; },
  setting(k, v) {
    if (S.run) exitRun();
    if ((k === "daily" || k === "size" || k === "size2") && typeof syncing === "function" && syncing()) return false;
    if (S.prog.settings[k] === v) return false;
    S.prog.settings[k] = v; touch(); route(true); return true;
  },
  reset() { if (S.run) exitRun(); confirmReset({ currentTarget: { dataset: { armed: "1" } } }); return S.prog.epoch || ""; },
  todayIds() { const t = dayStr(); return Object.keys(S.prog.q).filter((id) => S.prog.q[id].d === t); },
  pool(n) { return S.qs.filter((q) => q.t === 1).sort((a, b) => a.o - b.o).slice(0, n).map((q) => q.id); },
  rec(id) { const p = S.prog.q[id]; return p ? JSON.parse(JSON.stringify(p)) : null; },
  days() { return JSON.parse(JSON.stringify(S.prog.days)); },
};
