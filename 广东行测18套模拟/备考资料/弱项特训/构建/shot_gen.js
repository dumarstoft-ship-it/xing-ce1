const { GENS } = require('./gen.js'); const { svgPts, svgGrid } = require('./svg.js');
const { chromium } = require('playwright');
(async () => {
  let html = '<html><body style="font:13px sans-serif;display:flex;flex-wrap:wrap;gap:10px;background:#fff">';
  for (let s = 1; s <= 8; s++) { const q = GENS.pts(s * 31337); html += `<div style="width:230px"><div>pts ${s}: 答案${q.opts[q.answer.charCodeAt(0)-65]} ${q.exp.推导.slice(0,24)}</div><div style="width:220px">${svgPts(q.fig,false)}</div><div style="width:220px">${svgPts(q.fig,true)}</div></div>`; }
  for (let s = 1; s <= 4; s++) { const q = GENS.ptscl(s * 31337); html += `<div style="width:230px"><div>cl ${s}: 答案${q.opts[q.answer.charCodeAt(0)-65]}</div><div style="width:220px">${svgPts(q.fig,false)}</div><div style="width:220px">${svgPts(q.fig,true)}</div></div>`; }
  for (let s = 1; s <= 2; s++) { const q = GENS.grid(s * 999); html += `<div style="width:100%">grid ${s}: ${q.tag} 答案${q.answer}<br>` + q.fig.stem.map(g => svgGrid(g, 22)).join(' ') + ' || ' + q.fig.opts.map(g => svgGrid(g, 22)).join(' ') + '</div>'; }
  html += '</body></html>';
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1000, height: 1400 } });
  await pg.setContent(html); await pg.screenshot({ path: 'gen_sheet.png', fullPage: true }); await b.close();
})();
