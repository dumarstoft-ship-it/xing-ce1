// 合并规则的性质检查（Node 的 vm 里原样运行页面脚本，直接调 mergeProg）：
//   随机造两台设备的记录 A、B（故意让 updated、st、epoch 经常相同或只差一点，题组有昨天/今天/明天的），
//   模拟“读云端→并进来→不一样就写”来回交换，看几轮之内能不能三方一致；不能的打印出来。
// 用法：TZ=Asia/Shanghai SITE=site_v7c node u1_merge_prop.js [轮数=4000] [起始种子=1]
'use strict';
process.env.TZ = 'Asia/Shanghai';
const vm = require('vm'), fs = require('fs'), path = require('path');
const SITE = path.join(__dirname, process.env.SITE || 'site_v7c');
const html = fs.readFileSync(path.join(SITE, 'index.html'), 'utf8');
const script = (() => { const re = /<script>([\s\S]*?)<\/script>/g; let m, best = null; while ((m = re.exec(html))) if (m[1].includes('LS_KEY')) best = m[1]; return best; })();
const BH = new Proxy(function () {}, { get(t, k) { if (k === Symbol.iterator) return function* () {}; if (k === Symbol.toPrimitive) return () => ''; if (k === 'then') return undefined; if (k === 'length') return 0; if (k === 'nodeType') return 1; return BH; }, apply() { return BH; }, construct() { return BH; }, set() { return true; }, has() { return true; } });
function makeCtx(nowMs) {
  const sb = { console, __now: () => nowMs, setTimeout: () => 1, clearTimeout() {}, localStorage: { getItem: () => null, setItem() {}, removeItem() {} }, fetch: () => new Promise(() => {}),
    location: { hash: '' }, navigator: {}, scrollY: 0, scrollTo() {}, addEventListener() {}, removeEventListener() {},
    document: { hidden: false, body: BH, createElement: () => BH, createTextNode: () => BH, getElementById: (id) => (id === 'mz-data' ? null : BH), querySelector: () => BH, querySelectorAll: () => [], addEventListener() {}, removeEventListener() {} } };
  sb.window = sb; const ctx = vm.createContext(sb);
  vm.runInContext('(function(){ const R = Date; class D extends R { constructor(...a){ if (a.length) super(...a); else super(__now()); } static now(){ return __now(); } } globalThis.Date = D; })();', ctx);
  vm.runInContext(script, ctx);
  vm.runInContext('globalThis.__m = { merge(mine, inc) { S.prog = normalize(JSON.parse(mine)); S.setSeen = canon(S.prog.settings); const r = mergeProg(JSON.parse(inc)); normalize(S.prog); return JSON.stringify({ r, prog: S.prog }); }, canon, day: () => dayStr() };', ctx);
  return sb.__m;
}
const NOW = new Date('2026-11-28T10:00:00+08:00').getTime();
const M = makeCtx(NOW);
function rng(a) { return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const DAYS = ['2026-11-26', '2026-11-27', '2026-11-28'], GDAYS = ['2026-11-27', '2026-11-28', '2026-11-28', '2026-11-29'];
const TS = ['2026-11-28T01:00:00.000Z', '2026-11-28T01:00:00.001Z', '2026-11-28T01:30:00.000Z', '2026-11-28T02:00:00.000Z'];
const EP = ['', '', '', '2026-11-26T03:00:00.000Z', '2026-11-27T03:00:00.000Z', '2026-11-27T03:00:00.001Z'];
const IDS = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8'];
function addDays(day, n) { const [y, m, d] = day.split('-').map(Number); const x = new Date(y, m - 1, d + n); const p = (v) => String(v).padStart(2, '0'); return `${x.getFullYear()}-${p(x.getMonth() + 1)}-${p(x.getDate())}`; }
function gen(R) {
  const pick = (a) => a[Math.floor(R() * a.length)];
  const p = { v: 1, q: {}, days: {}, settings: { size: 15, size2: 15, daily: pick([50, 50, 40]), why: false, fmB: true, fmC: R() < 0.2 }, today: null, today2: null, plan: null, updated: pick(TS) };
  for (const id of IDS) if (R() < 0.7) { const d = pick(DAYS), l = R() < 0.7 ? 1 : 0, n = 1 + Math.floor(R() * 3), b = l ? pick([0, 1, 1, 2]) : 0; const rec = { n, c: Math.min(n, Math.floor(R() * (n + 1))), l, b, f: pick(DAYS.filter((x) => x <= d)), d, due: addDays(d, b ? 2 : 1), f1: R() < 0.7 ? 1 : 0 }; if (R() < 0.2) rec.e = R() < 0.5 ? 1 : 0; if (R() < 0.2) rec.x = 1; p.q[id] = rec; }
  for (const d of DAYS) if (R() < 0.6) { const n = 1 + Math.floor(R() * 4); p.days[d] = { n, c: Math.floor(R() * (n + 1)) }; }
  for (const k of ['plan', 'today']) if (R() < 0.6) { const ids = IDS.filter(() => R() < 0.5); const pos = Math.floor(R() * (ids.length + 1)); const res = {}; for (const id of ids.slice(0, pos)) res[id] = R() < 0.7 ? 1 : 0; p[k] = { day: pick(GDAYS), ids, pos, res }; if (k === 'plan') p[k].n = { wrong: 0, first: 0, look: 0, new1: ids.length, later: 0, new2: 0, extra: 0 }; }
  if (R() < 0.5) p.st = pick(TS);
  const e = pick(EP); if (e) p.epoch = e;
  return p;
}
const sortDeep = (v) => (Array.isArray(v) ? v.map(sortDeep) : v && typeof v === 'object' ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, sortDeep(v[k])])) : v);
const canon = (v) => JSON.stringify(sortDeep(v));
function exchange(A0, B0, maxRounds) {
  let A = JSON.stringify(A0), B = JSON.stringify(B0), cloud = canon(B0), writes = 0; const trace = [];
  for (let round = 0; round < maxRounds; round++) {
    let wrote = false;
    for (const who of ['A', 'B']) {
      const mine = who === 'A' ? A : B; const out = JSON.parse(M.merge(mine, cloud)); const np = JSON.stringify(out.prog);
      if (who === 'A') A = np; else B = np;
      // 页面只有在 ahead>0（本机有云端没有的内容）时才会去推；推的时候内容和云端一样就不写
      if (out.r.ahead && canon(out.prog) !== cloud) { cloud = canon(out.prog); writes++; wrote = true; trace.push(who + ' 写（took ' + out.r.took + ', ahead ' + out.r.ahead + '）'); }
      else if (out.r.ahead) trace.push(who + ' 内容与云端相同但 ahead=' + out.r.ahead);
    }
    if (!wrote) { const nz = (t) => { const o = JSON.parse(t); if (o.st === '') delete o.st; return canon(o); };      // st 为空串和没有 st 当作一样（单独计数）
      const strict = canon(JSON.parse(A)) === cloud && canon(JSON.parse(B)) === cloud;
      return { ok: nz(A) === nz(cloud) && nz(B) === nz(cloud), stOnly: !strict, rounds: round + 1, writes, A, B, cloud, trace }; }
  }
  return { ok: false, rounds: maxRounds, writes, A, B, cloud, trace, loop: true };
}
function diffTop(a, b) { const out = {}; for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) { if (canon(a[k]) === canon(b[k])) continue; if ((k === 'q' || k === 'days') && a[k] && b[k]) { const ids = [...new Set([...Object.keys(a[k]), ...Object.keys(b[k])])].filter((id) => canon(a[k][id]) !== canon(b[k][id])); out[k] = ids.slice(0, 3).map((id) => [id, a[k][id], b[k][id]]); } else out[k] = [a[k], b[k]]; } return out; }
const N = Number(process.argv[2] || 4000), S0 = Number(process.argv[3] || 1);
let bad = 0, maxWrites = 0, hist = {}, selfBad = 0, stOnly = 0;
for (let s = S0; s < S0 + N; s++) {
  const R = rng(s * 7919 + 13); const A = gen(R), B = gen(R);
  // 自己并自己（键的先后打乱）：应当 took=0、ahead=0
  const self = JSON.parse(M.merge(JSON.stringify(A), canon(A)));
  if (self.r.took || self.r.ahead) { selfBad++; if (selfBad <= 3) console.log('自己并自己却有改动 种子', s, self.r, JSON.stringify(diffTop(A, self.prog)).slice(0, 300)); }
  const r = exchange(A, B, 8);
  hist[r.writes] = (hist[r.writes] || 0) + 1; maxWrites = Math.max(maxWrites, r.writes);
  if (r.ok && r.stOnly) stOnly++;
  if (!r.ok) { bad++; if (bad <= 6) { console.log(`✗ 种子 ${s}：${r.loop ? '8轮还在互写' : '停下时三方不一致'}（写了${r.writes}次）`); console.log('   A与云端的差别', JSON.stringify(diffTop(JSON.parse(r.A), JSON.parse(r.cloud))).slice(0, 500)); console.log('   B与云端的差别', JSON.stringify(diffTop(JSON.parse(r.B), JSON.parse(r.cloud))).slice(0, 500)); console.log('   过程', r.trace.slice(0, 10).join('；')); } }
}
console.log(`${path.basename(SITE)}：${N} 对随机记录，起始种子 ${S0}。不能一致的 ${bad} 对；自己并自己有改动的 ${selfBad} 对；只差一个空的 st 的 ${stOnly} 对；写云端次数分布 ${JSON.stringify(hist)}`);
process.exit(bad || selfBad ? 1 : 0);
