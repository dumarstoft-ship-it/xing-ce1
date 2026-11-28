// progress/main 的大小上限估算：625 题全做过、每题字段都齐、plan 80 题、today/today2 各 30 题、days 60 天
const L = require('./lib.js');
const SITE = process.argv[2];
(async () => {
  const b = await L.launch();
  const store = L.newStore(null);
  const A = await L.device(b, SITE, store, 'A', {});
  await A.wait(300);
  const r = await A.pg.evaluate(() => {
    const ids = S.qs.map((q) => q.id);
    const p = blankProg();
    for (const id of ids) p.q[id] = { n: 12, c: 10, l: 1, b: 5, f: '2026-11-27', d: '2026-12-05', due: '2026-12-19', f1: 1, x: 1, e: 1 };
    for (let i = 0; i < 60; i++) p.days[addDays('2026-10-08', i)] = { n: 120, c: 100 };
    const grp = (n) => ({ day: '2026-12-05', ids: ids.slice(0, n), pos: n, res: Object.fromEntries(ids.slice(0, n).map((id) => [id, 1])) });
    p.plan = { ...grp(80), n: { wrong: 10, first: 10, look: 10, new1: 20, later: 10, new2: 10, extra: 10 } };
    p.today = grp(30); p.today2 = grp(30); p.updated = new Date().toISOString();
    const s = JSON.stringify(p);
    return { nq: ids.length, bytes: new TextEncoder().encode(s).length, perQ: new TextEncoder().encode(JSON.stringify(p.q)).length / ids.length, idLen: ids[0].length, maxId: Math.max(...ids.map((x) => x.length)) };
  });
  console.log(JSON.stringify(r), '→', (r.bytes / 1024).toFixed(1), 'KiB，上限 256 KiB');
  await A.close(); await b.close();
})();
