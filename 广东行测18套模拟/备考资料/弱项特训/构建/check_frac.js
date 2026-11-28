// 独立复核分数速练：对给出的每一项枚举反约分倍数（1—6倍，全部组合），看分子列、分母列能否各自是常见数列，
// 或分子分母之间有常见关系；凡能解释的都算出下一项，和生成器给的答案比较。
const G = require("./gen.js");
const gcd = (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b) { const t = a % b; a = b; b = t; } return a; };
const eq = (x, y) => x[0] * y[1] === x[1] * y[0];
const parse = (t) => { if (t.includes("/")) { const [a, b] = t.split("/").map(Number); return [a, b]; } return [Number(t), 1]; };
function nextOf(arr) {          // 常见整数数列的下一项（等差、二级等差(≥5项)、等比2/3倍、平方/立方连续），可能多个
  const n = arr.length, out = [];
  const d = arr.map((v, i) => (i ? v - arr[i - 1] : null)).slice(1);
  if (d.every((x) => x === d[0])) out.push(arr[n - 1] + d[0]);
  if (n >= 5) { const d2 = d.map((v, i) => (i ? v - d[i - 1] : null)).slice(1); if (d2.every((x) => x === d2[0]) && d2[0] !== 0) out.push(arr[n - 1] + d[d.length - 1] + d2[0]); }
  for (const r of [2, 3]) if (arr.every((v, i) => !i || v === arr[i - 1] * r)) out.push(arr[n - 1] * r);
  for (const m of [2, 3]) for (let s = 0; s <= 8; s++) for (const c of [-1, 0, 1]) if (arr.every((v, i) => v === (s + i) ** m + c)) out.push((s + n) ** m + c);
  return [...new Set(out)];
}
function preds(sh) {
  const n = sh.length, res = [];
  const ks = []; const rec = (i, cur) => { if (i === n) { ks.push(cur.slice()); return; } for (let k = 1; k <= 6; k++) { cur.push(k); rec(i + 1, cur); cur.pop(); } }; rec(0, []);
  for (const k of ks) {
    const N = sh.map((x, i) => x[0] * k[i]), D = sh.map((x, i) => x[1] * k[i]);
    for (const a of nextOf(N)) for (const b of nextOf(D)) if (a > 0 && b > 0) res.push([a, b]);
    // 分子分母之间的关系
    if (N.every((v, i) => !i || v === D[i - 1])) { const g = D.map((v, i) => v - N[i]); for (const gn of nextOf(g)) res.push([D[n - 1], D[n - 1] + gn]); }
    if (N.every((v, i) => !i || (v === D[i - 1] && D[i] === N[i - 1] + D[i - 1]))) res.push([D[n - 1], N[n - 1] + D[n - 1]]);
    if (N.every((v, i) => !i || (v === N[i - 1] + D[i - 1] && D[i] === v + D[i - 1]))) { const a = N[n - 1] + D[n - 1]; res.push([a, a + D[n - 1]]); }
    const c = D[0] - N[0] * N[0]; if (D.every((v, i) => v === N[i] * N[i] + c)) for (const a of nextOf(N)) res.push([a, a * a + c]);
    const c2 = D[0] - N[0]; if (D.every((v, i) => v - N[i] === c2)) for (const a of nextOf(N)) res.push([a, a + c2]);
  }
  // 数值层面：作商成等差、作差成等差
  const v = sh;
  const r = v.slice(1).map((x, i) => [x[0] * v[i][1], x[1] * v[i][0]]);
  const sub = (x, y) => [x[0] * y[1] - y[0] * x[1], x[1] * y[1]];
  const dr = r.slice(1).map((x, i) => sub(x, r[i]));
  if (n >= 5 && dr.every((x) => eq(x, dr[0])) && dr[0][0] !== 0) { const nr = [r[r.length - 1][0] * dr[0][1] + dr[0][0] * r[r.length - 1][1], r[r.length - 1][1] * dr[0][1]]; if (nr[0] > 0) res.push([v[n - 1][0] * nr[0], v[n - 1][1] * nr[1]]); }
  return res;
}
let bad = 0, total = 0;
const N0 = Number(process.argv[2] || 1), N1 = Number(process.argv[3] || 600);
for (let s = N0; s <= N1; s++) {
  const q = G.GENS.frac(s); if (!q) continue; total++;
  const sh = q.stem.replace("，（　　）", "").split("，").map(parse);
  const ans = parse(q.opts[q.answer.charCodeAt(0) - 65]);
  const ps = preds(sh);
  const other = ps.filter((p) => !eq(p, ans));
  const optHit = other.filter((p) => q.opts.some((o) => eq(parse(o), p)));
  if (!ps.some((p) => eq(p, ans)) || optHit.length) { bad++; if (bad <= 8) console.log("seed", s, q.tag, q.stem, q.opts.join(" "), "ans", q.answer, "| 自己的规律复现:", ps.some((p) => eq(p, ans)), "| 指向别的选项:", JSON.stringify(optHit.slice(0, 3))); }
}
console.log(`共${total}题，复核不过${bad}题`);
