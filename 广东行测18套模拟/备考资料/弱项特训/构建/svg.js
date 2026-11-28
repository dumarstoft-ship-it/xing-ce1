// 自编图形的 SVG（页面里同一份代码）
function svgPts(fig, showPts) {
  const sw = 1.6;
  let out = `<svg viewBox="0 0 100 100" class="genfig" role="img" aria-label="线条图">`;
  for (const s of fig.segs) out += `<line x1="${s[0]}" y1="${s[1]}" x2="${s[2]}" y2="${s[3]}" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round"/>`;
  if (fig.circle) out += `<circle cx="${fig.circle.x}" cy="${fig.circle.y}" r="${fig.circle.r}" fill="none" stroke="currentColor" stroke-width="${sw}"/>`;
  if (showPts) { const list = fig.mode === "cl" ? fig.cpts : fig.pts; for (const p of list) out += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="2.4" fill="#d23c2a"/>`; }
  return out + `</svg>`;
}
function svgGrid(g, cell) {
  const R = g.length, C = g[0].length, W = C * cell + 2, H = R * cell + 2;
  let out = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" class="gridfig" role="img" aria-label="方格">`;
  for (let i = 0; i < R; i++) for (let j = 0; j < C; j++) out += `<rect x="${1 + j * cell}" y="${1 + i * cell}" width="${cell}" height="${cell}" fill="${g[i][j] ? "#9a9a9a" : "#fff"}" stroke="#222" stroke-width="1.5"/>`;
  return out + `</svg>`;
}
function svgCircles(list) {        // 四格圆：每个圆按 左上、右上、左下、右下 四个数
  const pos = [[29, 40], [71, 40], [29, 75], [71, 75]];
  return list.map((c) => {
    let s = `<svg viewBox="0 0 100 100" class="circ" role="img" aria-label="四格圆"><circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" stroke-width="2"/>`;
    s += `<line x1="5" y1="50" x2="95" y2="50" stroke="currentColor" stroke-width="1.5"/><line x1="50" y1="5" x2="50" y2="95" stroke="currentColor" stroke-width="1.5"/>`;
    c.forEach((v, i) => { s += `<text x="${pos[i][0]}" y="${pos[i][1]}" text-anchor="middle" font-size="18" font-family="'Noto Serif SC', serif" fill="currentColor">${String(v).replace(/[<>&]/g, "")}</text>`; });
    return s + `</svg>`;
  }).join("");
}
if (typeof module !== "undefined") module.exports = { svgPts, svgGrid, svgCircles };
