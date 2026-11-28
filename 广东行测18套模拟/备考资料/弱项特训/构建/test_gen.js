const { GENS, REC, TAB, recFits, tabFits } = require('./gen.js');
const stat = {};
for (const k of Object.keys(GENS)) {
  let ok = 0, fail = 0, tags = {}, t0 = Date.now(), ansDist = {};
  for (let s = 1; s <= 400; s++) {
    const q = GENS[k](s * 7919 + 13);
    if (!q) { fail++; continue; }
    ok++; tags[q.tag] = (tags[q.tag] || 0) + 1; ansDist[q.answer] = (ansDist[q.answer] || 0) + 1;
    if (new Set(q.opts).size !== 4) throw new Error('dup opts ' + k + ' ' + s);
    if (!['A','B','C','D'].includes(q.answer)) throw new Error('bad answer');
    // 同一种子重放一致
    const q2 = GENS[k](s * 7919 + 13); if (JSON.stringify(q) !== JSON.stringify(q2)) throw new Error('not deterministic ' + k);
  }
  stat[k] = { ok, fail, ms: Date.now() - t0, ansDist, tags };
}
console.log(JSON.stringify(stat, null, 1));
for (const k of ['rec', 'tab']) for (let s = 1; s <= 4; s++) { const q = GENS[k](s * 104729); console.log('\n---', k, q.tag, '|', q.stem || q.rows.map(r => r.map(x => x === null ? '?' : x).join(' ')).join(' / '), '|', q.opts.join(' / '), '→', q.answer); console.log(q.exp.题眼); console.log(q.exp.推导); console.log(q.exp.易错); }
const p = GENS.pts(5); console.log('\npts', p.opts, p.answer, p.exp.推导, p.fig.segs.length);
const g = GENS.grid(9); console.log('\ngrid', g.tag, g.answer); console.log(g.exp.推导);
