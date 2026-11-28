// 数推候选题的程序复核：用一批常见的“三项”运算去拟合给出的项，看能不能独立得到同一个答案。
// 用法：node check_ss.js ../drill/ss_candidates.json
const fs = require('fs');
const items = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const num = (s) => { s = String(s).trim().replace(/（|）|\(|\)/g, ''); if (/^-?\d+(\.\d+)?$/.test(s)) return Number(s); const m = /^(-?\d+)\/(\d+)$/.exec(s); if (m) return Number(m[1]) / Number(m[2]); return NaN; };
const K = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5];
const REC = [
  ['a+b+k', (a, b, k) => a + b + k], ['a+b+i', (a, b, k, i) => a + b + i + k], ['a+b-i', (a, b, k, i) => a + b - i + k], ['2a+b+k', (a, b, k) => 2 * a + b + k], ['a+2b+k', (a, b, k) => a + 2 * b + k],
  ['b-a+k', (a, b, k) => b - a + k], ['a-b+k', (a, b, k) => a - b + k], ['ab+k', (a, b, k) => a * b + k], ['ab+a', (a, b) => a * b + a], ['ab-a', (a, b) => a * b - a], ['ab+b', (a, b) => a * b + b], ['ab-b', (a, b) => a * b - b],
  ['(a+b)a', (a, b) => (a + b) * a], ['(a+b)b', (a, b) => (a + b) * b], ['a2+b+k', (a, b, k) => a * a + b + k], ['a+b2+k', (a, b, k) => a + b * b + k], ['b2-a+k', (a, b, k) => b * b - a + k], ['a2-b', (a, b) => a * a - b],
  ['(a+b)*k', (a, b, k) => (a + b) * k], ['b*k+a', (a, b, k) => b * k + a], ['b*k-a', (a, b, k) => b * k - a], ['a*k+b', (a, b, k) => a * k + b], ['ab/2', (a, b) => a * b / 2], ['(a+b)/2', (a, b) => (a + b) / 2],
  ['b2-a2', (a, b) => b * b - a * a], ['a2+b2', (a, b) => a * a + b * b], ['b/a*?', (a, b, k) => (b / a) * k], ['b*b/a', (a, b) => b * b / a], ['ab-k', (a, b, k) => a * b - k],
];
function fitsRec(t) {
  const res = [];
  // 通用线性递推 c = p·a + q·b + r
  const PQ = [-4, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 3, 4];
  for (const p of PQ) for (const q of PQ) for (let r = -12; r <= 12; r++) {
    if (p === 0 && q === 0) continue;
    let ok = true; for (let i = 2; i < t.length && ok; i++) if (Math.abs(p * t[i - 2] + q * t[i - 1] + r - t[i]) > 1e-9) ok = false;
    if (ok) res.push([`${p}a+${q}b+${r}`, p * t[t.length - 2] + q * t[t.length - 1] + r]);
  }
  // 交替修正：a+b±k 交替
  for (const k of [1, 2, 3, 4, 5]) for (const sg of [1, -1]) { let ok = true; for (let i = 2; i < t.length && ok; i++) if (t[i - 2] + t[i - 1] + sg * k * (i % 2 ? 1 : -1) !== t[i]) ok = false; if (ok) { const i = t.length; res.push([`a+b±${k}交替`, t[i - 2] + t[i - 1] + sg * k * (i % 2 ? 1 : -1)]); } }
  // 几何平均：b² = a·c → c = b²/a
  { let ok = true; for (let i = 2; i < t.length && ok; i++) if (Math.abs(t[i - 1] * t[i - 1] - t[i - 2] * t[i]) > 1e-9) ok = false; if (ok) res.push(['b²=ac', t[t.length - 1] ** 2 / t[t.length - 2]]); }
  // (b−a)×k
  for (const k of [2, 3, 4, 5]) { let ok = true; for (let i = 2; i < t.length && ok; i++) if ((t[i - 1] - t[i - 2]) * k !== t[i]) ok = false; if (ok) res.push([`(b−a)×${k}`, (t[t.length - 1] - t[t.length - 2]) * k]); }
  for (const [name, f] of REC) for (const k of K) {
    let ok = true; for (let i = 2; i < t.length && ok; i++) if (Math.abs(f(t[i - 2], t[i - 1], k, i - 1) - t[i]) > 1e-9) ok = false;
    if (ok) res.push([name + (k ? '(k=' + k + ')' : ''), f(t[t.length - 2], t[t.length - 1], k, t.length - 1)]);
  }
  // 前三项之和、（首+尾）×k=中
  { let ok = t.length >= 4; for (let i = 3; i < t.length && ok; i++) if (t[i] !== t[i - 1] + t[i - 2] + t[i - 3]) ok = false; if (ok) res.push(['a+b+c', t[t.length - 1] + t[t.length - 2] + t[t.length - 3]]); }
  for (const k of [1, 2, 3, 0.5]) { let ok = true; for (let i = 2; i < t.length && ok; i++) if (Math.abs(t[i - 1] - k * (t[i - 2] + t[i])) > 1e-9) ok = false; if (ok) res.push(['(首+尾)*' + k + '=中', t[t.length - 1] / k - t[t.length - 2]]); }
  return res;
}
const TAB = [['a+b+k', (a, b, k) => a + b + k], ['ab+k', (a, b, k) => a * b + k], ['ab-a', (a, b) => a * b - a], ['ab+a', (a, b) => a * b + a], ['ab+b', (a, b) => a * b + b], ['ab-b', (a, b) => a * b - b], ['a2+b+k', (a, b, k) => a * a + b + k], ['a+b2+k', (a, b, k) => a + b * b + k], ['a2-b+k', (a, b, k) => a * a - b + k], ['b2-a+k', (a, b, k) => b * b - a + k], ['(a+b)2', (a, b) => (a + b) ** 2], ['(a-b)2', (a, b) => (a - b) ** 2], ['(a+b)k', (a, b, k) => (a + b) * k], ['(b-a)k', (a, b, k) => (b - a) * k], ['2a+b+k', (a, b, k) => 2 * a + b + k], ['a+2b+k', (a, b, k) => a + 2 * b + k], ['a2+b2', (a, b) => a * a + b * b], ['a*b/k', (a, b, k) => k ? a * b / k : NaN], ['(a+b)/k', (a, b, k) => k ? (a + b) / k : NaN]];
function fitsTab(rows) {
  const given = rows.slice(0, -1), last = rows[rows.length - 1], res = [];
  // 通用：c = p·a + q·b + r·a·b + s
  for (const p of [-2, -1, 0, 1, 2, 3]) for (const q of [-2, -1, 0, 1, 2, 3]) for (const r of [0, 1, -1, 2]) for (let s0 = -6; s0 <= 6; s0++) {
    if (given.every((x) => p * x[0] + q * x[1] + r * x[0] * x[1] + s0 === x[2])) res.push([`${p}a+${q}b+${r}ab+${s0}`, p * last[0] + q * last[1] + r * last[0] * last[1] + s0]);
  }
  for (const [name, f] of TAB) for (const k of K) if (given.every((r) => Math.abs(f(r[0], r[1], k) - r[2]) < 1e-9)) res.push([name + (k ? '(k=' + k + ')' : ''), f(last[0], last[1], k)]);
  const s = given.map((r) => r[0] + r[1] + r[2]); if (s.length >= 3 && s[2] - s[1] === s[1] - s[0]) res.push(['行和等差', s[2] + (s[1] - s[0]) - last[0] - last[1]]);
  if (s.every((v) => v === s[0])) res.push(['行和相等', s[0] - last[0] - last[1]]);
  return res;
}
let agree = 0, none = 0, clash = 0;
for (const it of items) {
  if (!it.three_term) continue;
  const opts = Object.fromEntries(Object.entries(it.options || {}).map(([L, v]) => [L, num(v)]));
  const ansL = it.official_answer || it.my_answer;
  let fits = [];
  const st = String(it.stem || '');
  if (st.includes('/')) {   // 数表
    const rows = st.replace(/（.*$/, '').split('/').map((r) => r.trim().split(/\s+/).map((x) => (x === '?' || x === '？' ? null : num(x))));
    if (rows.every((r) => r.length === 3) && rows.slice(0, -1).every((r) => r.every((x) => Number.isFinite(x)))) fits = fitsTab(rows);
  } else {
    const t = st.replace(/（\s*）|\(\s*\)|，\s*$/g, '').split(/[，,、\s]+/).map(num).filter((x) => Number.isFinite(x));
    if (t.length >= 4) fits = fitsRec(t);
  }
  const hit = [...new Set(fits.map(([, v]) => Object.keys(opts).find((L) => Math.abs(opts[L] - v) < 1e-9)).filter(Boolean))];
  const tag = !fits.length ? '无模板拟合' : hit.length === 1 && hit[0] === ansL ? '一致' : hit.includes(ansL) && hit.length > 1 ? '多解' : '不一致';
  if (tag === '一致') agree++; else if (tag === '无模板拟合') none++; else clash++;
  console.log(`${it.id}\t答案${ansL}\t${tag}\t${fits.slice(0, 3).map((x) => x[0] + '→' + x[1]).join('；')}\t| ${it.type}`);
}
console.log({ agree, none, clash });
