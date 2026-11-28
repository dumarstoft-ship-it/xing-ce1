// ---------- 自编速练生成器（三项关系、数交点、灰格计数） ----------
// 每道题由 {k: 生成器名, s: 种子} 完全确定：同一个种子永远生成同一道题，错题本只存这两项。
const GEN_VER = 1;
function rng(seed) {            // mulberry32
  let a = seed >>> 0;
  const f = () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  f.int = (lo, hi) => lo + Math.floor(f() * (hi - lo + 1));
  f.pick = (arr) => arr[Math.floor(f() * arr.length)];
  f.shuffle = (arr) => { const a2 = arr.slice(); for (let i = a2.length - 1; i > 0; i--) { const j = Math.floor(f() * (i + 1)); [a2[i], a2[j]] = [a2[j], a2[i]]; } return a2; };
  return f;
}
const LET = ["A", "B", "C", "D"];
function optionsFrom(R, ans, cands) {     // 正确值＋候选干扰值 → 四个不同的选项
  const set = [ans];
  for (const v of cands) { if (set.length >= 4) break; if (Number.isFinite(v) && Number.isInteger(v) && !set.includes(v)) set.push(v); }
  let d = 1;
  while (set.length < 4) { for (const v of [ans + d, ans - d]) if (set.length < 4 && !set.includes(v)) set.push(v); d++; }
  const shown = set.slice().sort((x, y) => x - y);
  return { opts: shown.map(String), answer: LET[shown.indexOf(ans)] };
}

// ===== 1. 三项关系 =====
// 递推：c 由前两项 a、b 算出（少数用前三项）；数表：每行 a、b、c，c 由 a、b 算出，或 b、c 都由 a 算出。
const fmt = (x) => (x < 0 ? "（" + x + "）" : String(x));
const REC = [      // id, 名称, f(a,b,k,i) , 说明（给解析用）, 题眼提示, 难度
  { id: "sum", name: "前两项之和", f: (a, b) => a + b, say: () => "前两项之和", eye: "数列平稳增长，作差后差列和原数列“长得像”，先试前两项相加。", lv: 1 },
  { id: "sumk", name: "前两项之和加常数", f: (a, b, k) => a + b + k, say: (k) => "前两项之和" + (k > 0 ? "再加" + k : "再减" + -k), eye: "前两项相加后和下一项总差同一个数，先算“和”，再看差。", lv: 1, ks: [-3, -2, -1, 1, 2, 3] },
  { id: "sumi", name: "前两项之和加递增数", f: (a, b, k, i) => a + b + i, say: () => "前两项之和再依次加1、2、3……", eye: "前两项之和与下一项的差越来越大，差本身成等差。", lv: 2 },
  { id: "dbl", name: "前项×2＋后项", f: (a, b) => 2 * a + b, say: () => "前一项（隔一项的那个）×2再加后一项", eye: "相邻两项相加差一点，再试“某一项×2”。", lv: 2 },
  { id: "dbl2", name: "前项＋后项×2", f: (a, b) => a + 2 * b, say: () => "前一项加后一项的2倍", eye: "下一项约为前一项的两倍多，试“后项×2＋前项”。", lv: 2 },
  { id: "diff", name: "后项减前项", f: (a, b) => b - a, say: () => "后一项减前一项", eye: "数列忽大忽小、有正有负，试相邻两项相减。", lv: 2 },
  { id: "prod", name: "前两项之积", f: (a, b) => a * b, say: () => "前两项之积", eye: "前几项很小、后面陡增，试前两项相乘。", lv: 1 },
  { id: "prodk", name: "前两项之积加常数", f: (a, b, k) => a * b + k, say: (k) => "前两项之积" + (k > 0 ? "再加" + k : "再减" + -k), eye: "相乘后与下一项总差同一个数，先算“积”，再看差。", lv: 2, ks: [-3, -2, -1, 1, 2, 3] },
  { id: "proda", name: "前两项之积加前项", f: (a, b) => a * b + a, say: () => "前两项之积再加前一项（即前项×(后项＋1)）", eye: "积与下一项的差恰好是前面的某一项，把差和前两项比一比。", lv: 3 },
  { id: "prodb", name: "前两项之积减前项", f: (a, b) => a * b - a, say: () => "前两项之积再减前一项（即前项×(后项－1)）", eye: "积比下一项多一点，多出的恰好是前面的某一项。", lv: 3 },
  { id: "suma", name: "前两项之和×前项", f: (a, b) => (a + b) * a, say: () => "前两项之和×前一项（＝前两项之积＋前项的平方）", eye: "下一项比前两项之积多出的部分是平方数，把“积＋平方”合并成“和×前项”。", lv: 3 },
  { id: "sqa", name: "前项平方＋后项", f: (a, b) => a * a + b, say: () => "前一项的平方加后一项", eye: "增长很快但不像乘积那么整齐，试把前面某一项平方。", lv: 3 },
  { id: "sqb", name: "前项＋后项平方", f: (a, b) => a + b * b, say: () => "后一项的平方加前一项", eye: "下一项接近后一项的平方，差的是前一项。", lv: 3 },
  { id: "sqd", name: "后项平方减前项", f: (a, b) => b * b - a, say: () => "后一项的平方减前一项", eye: "下一项比后一项的平方小一点，小的恰好是前一项。", lv: 3 },
  { id: "tri", name: "前三项之和", f: null, say: () => "前三项之和", eye: "数列平稳增长，前两项相加不够、差的恰好是再往前一项，试前三项相加。", lv: 2 },
  { id: "mid", name: "相邻三项：（首＋尾）×2＝中", f: null, say: () => "每相邻三项中，第一项与第三项之和的2倍等于中间项", eye: "数列有正有负、忽大忽小，作差作商都乱，试相邻三项“首尾和”与中间项的关系。", lv: 3 },
];
const TAB = [      // 数表每行 a、b → c
  { id: "t_sumk", name: "c＝a＋b±k", f: (a, b, k) => a + b + k, say: (k) => "第三个数＝前两个数之和" + (k ? (k > 0 ? "再加" + k : "再减" + -k) : ""), eye: "每行第三个数比前两数之和多（少）同一个数。", lv: 1, ks: [-3, -2, -1, 0, 1, 2, 3] },
  { id: "t_prod", name: "c＝a×b±k", f: (a, b, k) => a * b + k, say: (k) => "第三个数＝前两个数之积" + (k ? (k > 0 ? "再加" + k : "再减" + -k) : ""), eye: "第三个数和前两数之积接近，先乘再看差。", lv: 1, ks: [-3, -2, -1, 0, 1, 2, 3] },
  { id: "t_proda", name: "c＝a×b－a", f: (a, b) => a * b - a, say: () => "第三个数＝前两个数之积减第一个数（即a×(b－1)）", eye: "第三个数比前两数之积小，小的恰好是第一个数。", lv: 2 },
  { id: "t_prodb", name: "c＝a×b＋b", f: (a, b) => a * b + b, say: () => "第三个数＝前两个数之积加第二个数（即(a＋1)×b）", eye: "第三个数比前两数之积大，大的恰好是第二个数。", lv: 2 },
  { id: "t_sqa", name: "c＝a²＋b", f: (a, b) => a * a + b, say: () => "第三个数＝第一个数的平方加第二个数", eye: "第三个数比第一个数的平方大一点，大的是第二个数。", lv: 2 },
  { id: "t_sqb", name: "c＝a＋b²", f: (a, b) => a + b * b, say: () => "第三个数＝第二个数的平方加第一个数", eye: "第三个数接近第二个数的平方。", lv: 2 },
  { id: "t_sqd", name: "c＝a²－b", f: (a, b) => a * a - b, say: () => "第三个数＝第一个数的平方减第二个数", eye: "第三个数比第一个数的平方小，小的是第二个数。", lv: 2 },
  { id: "t_sum2", name: "c＝(a＋b)²", f: (a, b) => (a + b) * (a + b), say: () => "第三个数＝前两个数之和的平方", eye: "第三个数都是平方数，开方看和前两个数的关系。", lv: 2 },
  { id: "t_dif2", name: "c＝(a－b)²", f: (a, b) => (a - b) * (a - b), say: () => "第三个数＝前两个数之差的平方", eye: "第三个数都是平方数，开方后等于两数之差。", lv: 2 },
  { id: "t_sumx", name: "c＝(a＋b)×k", f: (a, b, k) => (a + b) * k, say: (k) => "第三个数＝前两个数之和的" + k + "倍", eye: "第三个数都是前两数之和的整数倍。", lv: 1, ks: [2, 3, 4] },
  { id: "t_2ab", name: "c＝2a＋b", f: (a, b) => 2 * a + b, say: () => "第三个数＝第一个数×2再加第二个数", eye: "和不够、积太大，试“某个数×2再相加”。", lv: 2 },
  { id: "t_rowsum", name: "每行三数之和成等差", f: null, say: () => "每行三个数之和依次成等差", eye: "单看行内运算凑不出，试每行三数相加，看和的规律。", lv: 3 },
  { id: "t_pow", name: "b＝a²＋m，c＝a³＋n", f: null, say: () => "第二个数＝第一个数的平方加常数，第三个数＝第一个数的立方加常数", eye: "第二列比第一列的平方多同一个数，第三列增长更快，试立方。", lv: 3 },
];
function recFits(kind, t, kTry) {   // 递推模板能否解释给出的各项（返回 k 或 null）
  const T = REC.find((x) => x.id === kind);
  if (kind === "tri") { for (let i = 3; i < t.length; i++) if (t[i] !== t[i - 1] + t[i - 2] + t[i - 3]) return null; return 0; }
  if (kind === "mid") { for (let i = 2; i < t.length; i++) if (t[i - 1] !== 2 * (t[i - 2] + t[i])) return null; return 0; }
  for (const k of (T.ks || [0])) {
    let ok = true;
    for (let i = 2; i < t.length && ok; i++) if (T.f(t[i - 2], t[i - 1], k, i - 1) !== t[i]) ok = false;
    if (ok) return k;
  }
  return null;
}
function recNext(kind, t, k) {
  const n = t.length, T = REC.find((x) => x.id === kind);
  if (kind === "tri") return t[n - 1] + t[n - 2] + t[n - 3];
  if (kind === "mid") return t[n - 1] / 2 - t[n - 2];
  return T.f(t[n - 2], t[n - 1], k, n - 1);
}
function genRec(seed) {
  const R = rng(seed);
  for (let tries = 0; tries < 400; tries++) {
    const T = R.pick(REC);
    const k = T.ks ? R.pick(T.ks) : 0;
    let t;
    if (T.id === "tri") t = [R.int(0, 3), R.int(1, 4), R.int(1, 5)];
    else if (T.id === "mid") { const a = R.int(-6, 9), c = R.int(-12, 12); t = [a, 2 * (a + c), c]; }
    else if (["prod", "prodk", "proda", "prodb", "suma"].includes(T.id)) t = [R.int(1, 3), R.int(1, 4)];
    else if (["sqa", "sqb", "sqd"].includes(T.id)) t = [R.int(0, 3), R.int(1, 3)];
    else if (T.id === "diff") t = [R.int(2, 15), R.int(2, 25)];
    else t = [R.int(1, 9), R.int(1, 12)];
    const total = T.id === "mid" ? 7 : (["prod", "prodk", "proda", "prodb", "suma", "sqa", "sqb", "sqd"].includes(T.id) ? 6 : R.pick([6, 7]));
    let bad = false;
    while (t.length < total) {
      let v;
      if (T.id === "mid") { if (t[t.length - 1] % 2) { bad = true; break; } v = t[t.length - 1] / 2 - t[t.length - 2]; }
      else v = recNext(T.id, t, k);
      if (!Number.isInteger(v) || Math.abs(v) > 3000) { bad = true; break; }
      t.push(v);
    }
    if (bad) continue;
    const shown = t.slice(0, -1), ans = t[t.length - 1];
    if (new Set(shown).size < shown.length - 1) continue;       // 太多重复项，像常数列，不要
    if (shown.every((x, i) => i === 0 || x > shown[i - 1]) && T.id === "sum" && shown[1] - shown[0] === shown[2] - shown[1]) continue;
    // 唯一性：别的模板也能解释给出的项、却指向另一个答案 → 换一道
    const fits = REC.map((X) => [X, recFits(X.id, shown)]).filter(([, kk]) => kk !== null);
    const preds = new Set(fits.map(([X, kk]) => recNext(X.id, shown, kk)));
    if (preds.size !== 1 || !preds.has(ans)) continue;
    // 干扰项：漏掉修正项、错用相近模板、±1/±2
    const near = [];
    const a = shown[shown.length - 2], b = shown[shown.length - 1];
    for (const X of REC) if (X.f && X.id !== T.id) near.push(X.f(a, b, k || 1, shown.length - 1));
    near.push(a + b, a * b, ans + k, ans - k);
    const cands = R.shuffle(near.filter((v) => v !== ans && Math.abs(v - ans) <= Math.max(12, Math.abs(ans) * 0.5)));
    const { opts, answer } = optionsFrom(R, ans, cands.concat([ans + 1, ans - 1, ans + 2, ans - 2]));
    // 解析
    const say = T.say(k);
    const lines = [];
    if (T.id === "tri") for (let i = 3; i < shown.length; i++) lines.push(`${fmt(shown[i - 3])}＋${fmt(shown[i - 2])}＋${fmt(shown[i - 1])}＝${shown[i]}`);
    else if (T.id === "mid") for (let i = 2; i < shown.length; i++) lines.push(`(${fmt(shown[i - 2])}＋${fmt(shown[i])})×2＝${shown[i - 1]}`);
    else for (let i = 2; i < shown.length; i++) lines.push(recFormula(T.id, shown[i - 2], shown[i - 1], k, i - 1) + "＝" + shown[i]);
    const last = T.id === "tri" ? `${fmt(shown[shown.length - 3])}＋${fmt(a)}＋${fmt(b)}＝${ans}`
      : T.id === "mid" ? `(${fmt(a)}＋？)×2＝${b}，？＝${b}÷2－${fmt(a)}＝${ans}` : recFormula(T.id, a, b, k, shown.length - 1) + "＝" + ans;
    const wrongV = T.id === "prodk" || T.id === "proda" || T.id === "prodb" || T.id === "suma" ? a * b : (T.id === "sumk" || T.id === "sumi" ? a + b : null);
    const trap = wrongV !== null && opts.includes(String(wrongV)) ? `只做“${T.id.startsWith("sum") ? "前两项相加" : "前两项相乘"}”得${wrongV}，会误选${LET[opts.indexOf(String(wrongV))]}；规律要用前面每一组都验证一遍。`
      : "找到一组关系后，至少再验证两组；只凑上一组就选，很容易掉进相近的干扰项。";
    return { k: "rec", s: seed, v: GEN_VER, type: "数推", sub: "递推", tag: T.name, lv: T.lv,
      stem: shown.map(fmt).join("，") + "，（　　）", opts, answer,
      exp: { 题眼: T.eye, 推导: `从第${T.id === "tri" ? 4 : 3}项起，每一项＝${say}：\n${lines.join("；\n")}。\n所求项：${last}。`, 易错: trap } };
  }
  return null;
}
function recFormula(id, a, b, k, i) {
  const A = fmt(a), B = fmt(b);
  switch (id) {
    case "sum": return `${A}＋${B}`;
    case "sumk": return `${A}＋${B}${k > 0 ? "＋" + k : "－" + -k}`;
    case "sumi": return `${A}＋${B}＋${i}`;
    case "dbl": return `${A}×2＋${B}`;
    case "dbl2": return `${A}＋${B}×2`;
    case "diff": return `${B}－${A}`;
    case "prod": return `${A}×${B}`;
    case "prodk": return `${A}×${B}${k > 0 ? "＋" + k : "－" + -k}`;
    case "proda": return `${A}×${B}＋${A}`;
    case "prodb": return `${A}×${B}－${A}`;
    case "suma": return `(${A}＋${B})×${A}`;
    case "sqa": return `${A}²＋${B}`;
    case "sqb": return `${A}＋${B}²`;
    case "sqd": return `${B}²－${A}`;
  }
  return "";
}
function tabFits(id, rows) {        // 数表模板能否解释给出的完整行（返回参数或 null）
  const T = TAB.find((x) => x.id === id);
  if (id === "t_rowsum") { const s = rows.map((r) => r[0] + r[1] + r[2]); const d = s[1] - s[0]; if (d === 0) return null; for (let i = 2; i < s.length; i++) if (s[i] - s[i - 1] !== d) return null; return d; }
  if (id === "t_pow") { const m = rows[0][1] - rows[0][0] ** 2, n = rows[0][2] - rows[0][0] ** 3; for (const r of rows) if (r[1] !== r[0] ** 2 + m || r[2] !== r[0] ** 3 + n) return null; return [m, n]; }
  for (const k of (T.ks || [0])) if (rows.every((r) => T.f(r[0], r[1], k) === r[2])) return k;
  return null;
}
function tabNext(id, rows, last, k) {
  if (id === "t_rowsum") { const s = rows.map((r) => r[0] + r[1] + r[2]); return s[s.length - 1] + k - last[0] - last[1]; }
  if (id === "t_pow") return last[0] ** 3 + k[1];
  return TAB.find((x) => x.id === id).f(last[0], last[1], k);
}
function genTab(seed) {
  const R = rng(seed);
  for (let tries = 0; tries < 400; tries++) {
    const T = R.pick(TAB);
    const k = T.ks ? R.pick(T.ks) : 0;
    const rows = [];
    let ok = true;
    if (T.id === "t_pow") {
      const m = R.int(-2, 3), n = R.int(-3, 4), start = R.int(1, 2);
      for (let i = 0; i < 4; i++) { const a = start + i; rows.push([a, a * a + m, a ** 3 + n]); }
    } else if (T.id === "t_rowsum") {
      const s0 = R.int(10, 25), d = R.pick([4, 5, 6, 8, 10, 12, 16]);
      for (let i = 0; i < 4; i++) { const S = s0 + d * i; const a = R.int(1, Math.max(2, Math.floor(S / 3))), b = R.int(1, Math.max(2, Math.floor(S / 3))); if (S - a - b < 1) { ok = false; break; } rows.push([a, b, S - a - b]); }
    } else {
      const small = ["t_prod", "t_proda", "t_prodb", "t_sqa", "t_sqb", "t_sqd", "t_sum2"].includes(T.id);
      const used = new Set();
      for (let i = 0; i < 4; i++) {
        let a, b, g = 0;
        do { a = small ? R.int(1, 9) : R.int(1, 20); b = small ? R.int(1, 9) : R.int(1, 20); g++; } while ((used.has(a + "," + b) || a === b) && g < 30);
        used.add(a + "," + b);
        const c = T.f(a, b, k);
        if (!Number.isInteger(c) || c < 0 || c > 999) { ok = false; break; }
        rows.push([a, b, c]);
      }
    }
    if (!ok) continue;
    const given = rows.slice(0, 3), last = rows[3], ans = last[2];
    if (ans < 0 || ans > 999) continue;
    const fits = TAB.map((X) => [X, tabFits(X.id, given)]).filter(([, kk]) => kk !== null);
    const preds = new Set(fits.map(([X, kk]) => tabNext(X.id, given, last, kk)));
    if (preds.size !== 1 || !preds.has(ans)) continue;
    const near = [];
    for (const X of TAB) if (X.f && X.id !== T.id) near.push(X.f(last[0], last[1], k || 1));
    near.push(last[0] * last[1], last[0] + last[1]);
    const cands = R.shuffle(near.filter((v) => v !== ans && v > 0 && Math.abs(v - ans) <= Math.max(12, ans * 0.5)));
    const { opts, answer } = optionsFrom(R, ans, cands.concat([ans + 1, ans - 1, ans + 2, ans - 2]));
    const say = T.say(k);
    let lines;
    if (T.id === "t_rowsum") { const s = given.map((r) => r[0] + r[1] + r[2]); lines = given.map((r, i) => `第${i + 1}行：${r[0]}＋${r[1]}＋${r[2]}＝${s[i]}`).join("；\n") + `。\n三行之和${s.join("、")}，每次加${s[1] - s[0]}，第4行之和应为${s[2] + s[1] - s[0]}`; }
    else if (T.id === "t_pow") { const [pm, pn] = tabFits("t_pow", given); lines = given.map((r, i) => `第${i + 1}行：${r[0]}²${pm >= 0 ? "＋" + pm : "－" + -pm}＝${r[1]}，${r[0]}³${pn >= 0 ? "＋" + pn : "－" + -pn}＝${r[2]}`).join("；\n"); }
    else lines = given.map((r, i) => `第${i + 1}行：${tabFormula(T.id, r[0], r[1], k)}＝${r[2]}`).join("；\n");
    const lastLine = T.id === "t_rowsum" ? `${tabNext(T.id, given, last, tabFits(T.id, given)) + last[0] + last[1]}－${last[0]}－${last[1]}＝${ans}`
      : T.id === "t_pow" ? (() => { const pn = tabFits("t_pow", given)[1]; return `${last[0]}³${pn >= 0 ? "＋" + pn : "－" + -pn}＝${ans}`; })() : `${tabFormula(T.id, last[0], last[1], k)}＝${ans}`;
    const plain = last[0] * last[1], plus = last[0] + last[1];
    let trap = "一条规律要在每一行都成立；只凑通一行就选，最容易错。";
    if ((T.id === "t_prod" && k) && opts.includes(String(plain))) trap = `只算两数之积${plain}、忘了${k > 0 ? "加" : "减"}${Math.abs(k)}，会误选${LET[opts.indexOf(String(plain))]}。`;
    else if ((T.id === "t_sumk" && k) && opts.includes(String(plus))) trap = `只算两数之和${plus}、忘了${k > 0 ? "加" : "减"}${Math.abs(k)}，会误选${LET[opts.indexOf(String(plus))]}。`;
    else if (!["t_prod", "t_sumk"].includes(T.id) && opts.includes(String(plain)) && plain !== ans) trap = `只看第4行凑“两数相乘”得${plain}，会误选${LET[opts.indexOf(String(plain))]}；这条在前三行不成立。`;
    return { k: "tab", s: seed, v: GEN_VER, type: "数推", sub: "数表", tag: T.name, lv: T.lv,
      rows: rows.map((r, i) => (i === 3 ? [r[0], r[1], null] : r)), stem: "", opts, answer,
      exp: { 题眼: T.eye, 推导: `横着看，每行三个数：${say}。\n${lines}。\n第4行：${lastLine}。`, 易错: trap } };
  }
  return null;
}
function tabFormula(id, a, b, k) {
  switch (id) {
    case "t_sumk": return `${a}＋${b}${k ? (k > 0 ? "＋" + k : "－" + -k) : ""}`;
    case "t_prod": return `${a}×${b}${k ? (k > 0 ? "＋" + k : "－" + -k) : ""}`;
    case "t_proda": return `${a}×${b}－${a}`;
    case "t_prodb": return `${a}×${b}＋${b}`;
    case "t_sqa": return `${a}²＋${b}`;
    case "t_sqb": return `${a}＋${b}²`;
    case "t_sqd": return `${a}²－${b}`;
    case "t_sum2": return `(${a}＋${b})²`;
    case "t_dif2": return `(${a}－${b})²`;
    case "t_sumx": return `(${a}＋${b})×${k}`;
    case "t_2ab": return `${a}×2＋${b}`;
  }
  return "";
}

// ===== 2. 数交点 =====
// 图由一个外框（矩形、三角形、梯形）和若干条内部线段组成；可选加一个圆（只数“曲直交点”时用）。
// 交点：两条（或几条）线相交、相接的位置，包括交叉、T形（一条线的端点落在另一条线上）和拐角；几条线交于一点只算一个。
const EPS = 1e-6;
function segInter(p, q) {     // 线段 p=[x1,y1,x2,y2]、q 的公共点（不平行时），返回 {x,y,tp,tq} 或 null
  const [x1, y1, x2, y2] = p, [x3, y3, x4, y4] = q;
  const d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3);
  if (Math.abs(d) < EPS) return null;
  const tp = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d;
  const tq = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d;
  if (tp < -1e-9 || tp > 1 + 1e-9 || tq < -1e-9 || tq > 1 + 1e-9) return null;
  return { x: x1 + tp * (x2 - x1), y: y1 + tp * (y2 - y1), tp, tq };
}
function distPtSeg(px, py, s) {
  const [x1, y1, x2, y2] = s, dx = x2 - x1, dy = y2 - y1, L = dx * dx + dy * dy;
  let t = L ? ((px - x1) * dx + (py - y1) * dy) / L : 0; t = Math.max(0, Math.min(1, t));
  const cx = x1 + t * dx, cy = y1 + t * dy;
  return Math.hypot(px - cx, py - cy);
}
function angleBetween(p, q) {
  const a1 = Math.atan2(p[3] - p[1], p[2] - p[0]), a2 = Math.atan2(q[3] - q[1], q[2] - q[0]);
  let d = Math.abs(a1 - a2) % Math.PI; if (d > Math.PI / 2) d = Math.PI - d;
  return d * 180 / Math.PI;
}
function circleSeg(c, s) {    // 圆 c={x,y,r} 与线段的交点
  const [x1, y1, x2, y2] = s, dx = x2 - x1, dy = y2 - y1;
  const A = dx * dx + dy * dy, B = 2 * (dx * (x1 - c.x) + dy * (y1 - c.y)), C = (x1 - c.x) ** 2 + (y1 - c.y) ** 2 - c.r * c.r;
  const disc = B * B - 4 * A * C;
  if (disc < 0) return { pts: [], disc };
  const out = [];
  for (const sg of [-1, 1]) { const t = (-B + sg * Math.sqrt(disc)) / (2 * A); if (t >= -1e-9 && t <= 1 + 1e-9) out.push({ x: x1 + t * dx, y: y1 + t * dy, t }); }
  return { pts: out, disc };
}
function analyze(segs, circle) {   // 返回 {ok, pts:[{x,y,kind}], cpts, why}
  const raw = [];
  for (let i = 0; i < segs.length; i++) for (let j = i + 1; j < segs.length; j++) {
    const p = segs[i], q = segs[j];
    // 共线重叠：不允许
    const cr = (p[2] - p[0]) * (q[3] - q[1]) - (p[3] - p[1]) * (q[2] - q[0]);
    if (Math.abs(cr) < 1e-6) { if (distPtSeg(q[0], q[1], p) < 1 || distPtSeg(q[2], q[3], p) < 1 || distPtSeg(p[0], p[1], q) < 1) return { ok: false, why: "共线" }; continue; }
    const r = segInter(p, q);
    if (r) {
      if (angleBetween(p, q) < 22) return { ok: false, why: "夹角太小" };
      const endP = r.tp < 1e-6 || r.tp > 1 - 1e-6, endQ = r.tq < 1e-6 || r.tq > 1 - 1e-6;
      raw.push({ x: r.x, y: r.y, kind: endP && endQ ? "拐角" : (endP || endQ ? "T形" : "交叉") });
    }
  }
  // 合并同一位置
  const pts = [];
  for (const r of raw) { const m = pts.find((p) => Math.hypot(p.x - r.x, p.y - r.y) < 0.6); if (m) { m.n = (m.n || 1) + 1; if (r.kind !== m.kind) m.kind = "多线"; } else pts.push({ ...r }); }
  for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) if (Math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y) < 7) return { ok: false, why: "两个交点太近" };
  // 悬空的端点不能“看起来碰到”别的线
  for (let i = 0; i < segs.length; i++) for (const [ex, ey] of [[segs[i][0], segs[i][1]], [segs[i][2], segs[i][3]]]) {
    const onPt = pts.some((p) => Math.hypot(p.x - ex, p.y - ey) < 0.6);
    if (onPt) continue;
    for (let j = 0; j < segs.length; j++) if (j !== i && distPtSeg(ex, ey, segs[j]) < 6) return { ok: false, why: "端点贴近别的线" };
  }
  let cpts = [];
  if (circle) {
    for (const s of segs) {
      const { pts: cp, disc } = circleSeg(circle, s);
      const L = Math.hypot(s[2] - s[0], s[3] - s[1]);
      const dmin = distPtSeg(circle.x, circle.y, s);
      if (Math.abs(dmin - circle.r) < 5) return { ok: false, why: "圆与线近乎相切" };
      for (const c of cp) {
        if (c.t < 0.02 || c.t > 0.98) return { ok: false, why: "圆刚好落在端点" };
        if (pts.some((p) => Math.hypot(p.x - c.x, p.y - c.y) < 7)) return { ok: false, why: "曲直交点贴近直线交点" };
        cpts.push({ x: c.x, y: c.y, kind: "曲直" });
      }
      for (const [ex, ey] of [[s[0], s[1]], [s[2], s[3]]]) if (Math.abs(Math.hypot(ex - circle.x, ey - circle.y) - circle.r) < 6) return { ok: false, why: "端点贴近圆" };
      if (L < 1) return { ok: false };
    }
    for (let i = 0; i < cpts.length; i++) for (let j = i + 1; j < cpts.length; j++) if (Math.hypot(cpts[i].x - cpts[j].x, cpts[i].y - cpts[j].y) < 7) return { ok: false, why: "曲直交点太近" };
    for (const p of pts) if (Math.abs(Math.hypot(p.x - circle.x, p.y - circle.y) - circle.r) < 6) return { ok: false, why: "直线交点贴近圆" };
  }
  return { ok: true, pts, cpts };
}
function genPts(seed, mode) {     // mode: "all" 数全部交点；"cl" 只数曲直交点
  const R = rng(seed);
  for (let tries = 0; tries < 2000; tries++) {
    const segs = [];
    const shape = R.pick(["rect", "rect", "tri", "trap", "none"]);
    const P = (x, y) => [Math.round(x), Math.round(y)];
    let poly = null;
    if (shape === "rect") { const x0 = R.int(10, 30), y0 = R.int(12, 30), x1 = R.int(70, 90), y1 = R.int(70, 88); poly = [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]; }
    else if (shape === "tri") { poly = [P(R.int(35, 65), R.int(8, 18)), P(R.int(78, 92), R.int(80, 90)), P(R.int(8, 22), R.int(80, 90))]; }
    else if (shape === "trap") { const t = R.int(25, 40); poly = [P(t, R.int(12, 22)), P(100 - t + R.int(-8, 8), R.int(12, 22)), P(R.int(82, 92), R.int(80, 90)), P(R.int(8, 18), R.int(80, 90))]; }
    if (poly) for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length]; segs.push([a[0], a[1], b[0], b[1]]); }
    const m = poly ? R.int(2, 4) : R.int(4, 6);
    for (let s = 0; s < m; s++) {
      const end = () => {          // 端点：落在已有线上（T形）、取已有顶点（拐角）、或自由
        const r = R();
        if (segs.length && r < 0.5) { const sg = R.pick(segs), t = 0.2 + R() * 0.6; return [sg[0] + t * (sg[2] - sg[0]), sg[1] + t * (sg[3] - sg[1])]; }
        if (segs.length && r < 0.62) { const sg = R.pick(segs); return R() < 0.5 ? [sg[0], sg[1]] : [sg[2], sg[3]]; }
        return [R.int(8, 92), R.int(8, 92)];
      };
      const a = end(), b = end();
      if (Math.hypot(a[0] - b[0], a[1] - b[1]) < 22) { s--; if (segs.length > 40) break; continue; }
      segs.push([a[0], a[1], b[0], b[1]]);
    }
    let circle = null;
    if (mode === "cl") circle = { x: R.int(30, 70), y: R.int(30, 70), r: R.int(16, 30) };
    const res = analyze(segs, circle);
    if (!res.ok) continue;
    const n = mode === "cl" ? res.cpts.length : res.pts.length;
    if (mode === "all" && (n < 4 || n > 12)) continue;
    if (mode === "cl" && (n < 2 || n > 8)) continue;
    let lo = n - R.int(0, 3); if (lo < 0) lo = 0;
    const opts = [lo, lo + 1, lo + 2, lo + 3].map(String), answer = LET[n - lo];
    const kinds = {}; for (const p of res.pts) kinds[p.kind] = (kinds[p.kind] || 0) + 1;
    const say = mode === "cl" ? `直线与圆相交的点共${n}个（直线与直线的交点不算）。` : `共${n}个：` + Object.entries(kinds).map(([k2, v]) => `${k2}${v}个`).join("、") + "。";
    return { k: mode === "cl" ? "ptscl" : "pts", s: seed, v: GEN_VER, type: "图推", sub: "数交点", tag: mode === "cl" ? "曲直交点" : "全部交点",
      fig: { segs: segs.map((x) => x.map((v) => Math.round(v * 10) / 10)), circle, pts: res.pts, cpts: res.cpts, mode },
      stem: mode === "cl" ? "图中直线与圆一共有几个交点（只数曲直交点）？" : "图中一共有几个交点？（交叉、T形相接、拐角都算；几条线交于一点只算一个）",
      opts, answer, exp: { 题眼: mode === "cl" ? "有直线又有曲线时，先单独数“曲直交点”，再看它和别的量（曲线数、直线数）的关系。" : "线条交叉、相接的地方多，线条数和面数又没有规律时，数交点。", 推导: say + "答完后图上红点就是全部交点，对着数一遍。", 易错: mode === "cl" ? "直线与直线的交点、直线端点落在圆内都不算曲直交点；一条直线穿过圆要数两个。" : "最容易漏的是T形点（线的端头接在另一条线上）和外框的拐角；几条线交在同一点只算一个。" } };
  }
  return null;
}

// ===== 3. 灰格计数（按行、按列、按整体） =====
const GRULES = [
  { id: "rowd1", name: "上下两行灰格数相差1", rows: 2, test: (g) => Math.abs(cnt(g[0]) - cnt(g[1])) === 1 },
  { id: "roweq", name: "每行灰格数相同", test: (g) => g.every((r) => cnt(r) === cnt(g[0])) },
  { id: "coleq", name: "每列灰格数相同", test: (g) => cols(g).every((c) => cnt(c) === cnt(cols(g)[0])) },
  { id: "top", name: "上行灰格比下行多", rows: 2, test: (g) => cnt(g[0]) > cnt(g[1]) },
  { id: "bw", name: "灰格与白格一样多", even: true, test: (g) => tot(g) * 2 === g.length * g[0].length },
  { id: "lr", name: "最左列与最右列灰格数相同", test: (g) => { const c = cols(g); return cnt(c[0]) === cnt(c[c.length - 1]); } },
  { id: "tot", name: "灰格总数都相同", seq: "same", test: () => true },
];
const cnt = (arr) => arr.filter(Boolean).length;
const tot = (g) => g.reduce((s, r) => s + cnt(r), 0);
const cols = (g) => g[0].map((_, j) => g.map((r) => r[j]));
function genGrid(seed) {
  const R = rng(seed);
  for (let tries = 0; tries < 3000; tries++) {
    const rows = R.pick([2, 2, 3]), ncol = R.pick([3, 3, 4]);
    const usable = GRULES.filter((r) => (!r.rows || r.rows === rows) && (!r.even || (rows * ncol) % 2 === 0));
    const rule = R.pick(usable);
    const rand = () => Array.from({ length: rows }, () => Array.from({ length: ncol }, () => R() < 0.5));
    const sat = (g) => (rule.id === "tot" ? true : rule.test(g));
    let K = null;
    const mk = (want) => { for (let i = 0; i < 400; i++) { const g = rand(); if (tot(g) === 0 || tot(g) === rows * ncol) continue; if (rule.id === "tot") { if ((tot(g) === K) === want) return g; } else if (sat(g) === want) return g; } return null; };
    if (rule.id === "tot") K = R.int(2, rows * ncol - 2);
    const stem = []; for (let i = 0; i < 5; i++) { const g = mk(true); if (!g) break; stem.push(g); }
    if (stem.length < 5) continue;
    // 题干五幅不能都相同、不能有两幅一模一样
    const keyOf = (g) => g.map((r) => r.map((x) => (x ? 1 : 0)).join("")).join("/");
    if (new Set(stem.map(keyOf)).size < 5) continue;
    // 与题干相符的规律（可能不止目标规律一条，例如“每列相同”也意味着“左右两列相同”）
    const consistent = usable.filter((o) => (o.id === "tot" ? stem.every((g) => tot(g) === tot(stem[0])) : stem.every((g) => o.test(g))));
    // 总数依次加1之类的顺带规律不允许出现
    const T = stem.map(tot);
    if (T.every((v, i) => i === 0 || v === T[i - 1] + 1) || T.every((v, i) => i === 0 || v === T[i - 1] - 1)) continue;
    const okFor = (o, g) => (o.id === "tot" ? tot(g) === tot(stem[0]) : o.test(g));
    const right = mk(true); if (!right) continue;
    const wrong = []; for (let i = 0; i < 3; i++) { const g = mk(false); if (g) wrong.push(g); }
    if (wrong.length < 3) continue;
    const all = [right, ...wrong].map((g) => ({ g, key: keyOf(g) }));
    if (new Set(all.map((x) => x.key)).size < 4) continue;
    // 每一条与题干相符的规律都只能认出同一个选项（正确项）
    if (!consistent.every((o) => okFor(o, right) && wrong.every((g) => !okFor(o, g)))) continue;
    const order = R.shuffle([0, 1, 2, 3]);
    const opts = order.map((i) => all[i].g), answer = LET[order.indexOf(0)];
    const desc = (g) => {
      if (["rowd1", "roweq", "top"].includes(rule.id)) return g.map((r, i) => (rows === 2 ? (i ? "下" : "上") : "第" + (i + 1)) + "行" + cnt(r)).join("、");
      if (["coleq", "lr"].includes(rule.id)) return cols(g).map((c, i) => "第" + (i + 1) + "列" + cnt(c)).join("、");
      if (rule.id === "bw") return `灰${tot(g)}白${rows * ncol - tot(g)}`;
      return `共${tot(g)}格`;
    };
    const firstGroup = stem.slice(0, 3).map((g, i) => `图${i + 1}：${desc(g)}`).join("；"), second = stem.slice(3).map((g, i) => `图${i + 4}：${desc(g)}`).join("；");
    const optsDesc = opts.map((g, i) => `${LET[i]}项${desc(g)}`).join("；");
    const also = consistent.filter((o) => o.id !== rule.id).map((o) => o.name);
    return { k: "grid", s: seed, v: GEN_VER, type: "图推", sub: "灰格计数", tag: rule.name, also,
      fig: { rows, cols: ncol, stem, opts }, stem: "两组图，第一组三幅图有一个共同规律，第二组也有同样的规律。从四个选项中选出最合适的一个填入问号处：", opts: LET.slice(), answer,
      exp: { 题眼: "格子位置看不出平移、旋转、叠加时，数灰格：先数总数；总数没规律，就分行、分列、分上下左右数，或者比灰格和白格。", 推导: `规律：${rule.name}${also.length ? "（同时也满足：" + also.join("、") + "）" : ""}。\n第一组 ${firstGroup}。\n第二组 ${second}。\n${optsDesc}，只有${answer}项符合。`, 易错: "只数灰格总数会觉得“乱”；总数看不出规律时，要拆成行、列分别数，再比较各部分。" } };
  }
  return null;
}
const GENS = { rec: genRec, tab: genTab, pts: (s) => genPts(s, "all"), ptscl: (s) => genPts(s, "cl"), grid: genGrid };
if (typeof module !== "undefined") module.exports = { GENS, rng, analyze, REC, TAB, recFits, tabFits };
