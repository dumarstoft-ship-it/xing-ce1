#!/usr/bin/env python3
"""按原图坐标把印刷时会看不清的小尺寸题图重绘为矢量图，并与原图逐像素比对。

    python3 广东行测18套模拟/打印排版/redraw_figures.py

只在打印排版目录内生成 SVG 与核对记录，源题库图片不改动。build_print.py 仅在
源图 SHA-256 与记录一致时才用重绘图替换，源图变了就退回原图并在日志中报出。

目前收录：
  s21_p18_i12（M01第70题经纬网，271×220像素，原卷印宽5.3cm，纬度标注字高约1.2mm）
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "重绘"


def p(cx, cy, r, deg):
    t = math.radians(deg)
    return cx + r * math.cos(t), cy - r * math.sin(t)


def arc(cx, cy, r, a_from, a_to):
    """沿数学正向（逆时针）从 a_from 画到 a_to（度）。"""
    span = (a_to - a_from) % 360 or 360
    x0, y0 = p(cx, cy, r, a_from)
    x1, y1 = p(cx, cy, r, a_from + span)
    large = 1 if span > 180 else 0
    return f"M{x0:.2f},{y0:.2f} A{r:.2f},{r:.2f} 0 {large} 0 {x1:.2f},{y1:.2f}"


def s21_p18_i12() -> str:
    """南极俯视经纬网。几何量均从原图（271×220像素）实测，坐标系与原图像素一致。"""
    cx, cy = 130.37, 100.95                       # 极点：虚线经线的交点
    # 三条纬线半径：逐圈最小二乘拟合（内圈拟合圆心偏离极点约1像素，属原图绘制误差，
    # 重绘取以极点为心的同心圆）
    r70, r60, r50 = 42.0, 67.6, 96.1
    # 纬线缺口（度，数学正向，沿拟合圆每0.5°采样实测），纬度标注写在缺口中
    gaps = {r70: (277.5, 306.0), r60: (284.0, 303.0), r50: (293.0, 307.0)}
    labels = [("70°", r70, 294.5), ("60°", r60, 291.5), ("50°", r50, 300.0)]
    ink = "#000"
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 271 220" width="271" height="220">',
             '<rect width="271" height="220" fill="#fff"/>',
             f'<g fill="none" stroke="{ink}" stroke-width="1.7">']
    for r, (g0, g1) in gaps.items():
        parts.append(f'<path d="{arc(cx, cy, r, g1, g0)}"/>')
    parts.append("</g>")
    # 四条经线（虚线直径），端点在最外一圈
    parts.append(f'<g stroke="{ink}" stroke-width="1.25" stroke-dasharray="4.2 2.6">')
    for a in (0, 45, 90, 135):
        x0, y0 = p(cx, cy, r50, a)
        x1, y1 = p(cx, cy, r50, a + 180)
        parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}"/>')
    parts.append("</g>")
    # 地点：实心小方块
    pts = {"A": (r50, 270), "B": (r60, 225), "C": (r70, 135), "D": (r70, 45)}
    for _, (r, a) in pts.items():
        x, y = p(cx, cy, r, a)
        parts.append(f'<rect x="{x - 2.6:.2f}" y="{y - 2.6:.2f}" width="5.2" height="5.2" fill="{ink}"/>')
    # 自转方向箭头：外侧圆弧，顺时针指向左下
    ra = 120.0
    parts.append(f'<path d="{arc(cx, cy, ra, 325.5, 339.5)}" fill="none" stroke="{ink}" stroke-width="2.3"/>')
    tip = p(cx, cy, ra, 318.0)
    base = p(cx, cy, ra, 326.5)
    # 箭头底边垂直于切线
    nx, ny = (base[0] - cx) / ra, (base[1] - cy) / ra
    w = 3.6
    b1 = (base[0] + nx * w, base[1] + ny * w)
    b2 = (base[0] - nx * w, base[1] - ny * w)
    parts.append(f'<path d="M{tip[0]:.2f},{tip[1]:.2f} L{b1[0]:.2f},{b1[1]:.2f} L{b2[0]:.2f},{b2[1]:.2f} Z" fill="{ink}"/>')
    # 文字：原图为无衬线字体
    font = 'font-family="Liberation Sans, Arial, Helvetica, sans-serif"'
    big = [("0°", 17.6, 104.9), ("180°", 254.2, 104.9), ("A", 131.2, 213.6),
           ("B", 82.6, 164.6), ("C", 89.7, 77.7), ("D", 174.6, 77.7)]
    for t, x, y in big:
        parts.append(f'<text x="{x}" y="{y}" {font} font-size="11.6" text-anchor="middle" fill="{ink}">{t}</text>')
    for t, r, a in labels:
        x, y = p(cx, cy, r, a)
        parts.append(f'<text x="{x:.2f}" y="{y + 2.9:.2f}" {font} font-size="8.2" text-anchor="middle" fill="{ink}">{t}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


FIGURES = {
    "s21_p18_i12": {
        "source": "模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p18_i12.png",
        "draw": s21_p18_i12,
        "print_width_mm": 80.0,
        "note": "原图271×220像素，原卷印宽5.3cm，纬度标注字高约1.2mm且发虚；按原图像素坐标矢量重绘：三条纬线及缺口、四条虚线经线、A—D四点、自转箭头、全部标注位置不变，不增删任何信息。三条纬线取以极点为心的同心圆（原图内圈圆心偏约1像素，属绘制误差）。",
    },
}


def rasterize(svg: str, w: int, h: int, png: Path) -> None:
    js = """
const { chromium } = require('playwright');
(async () => {
  const [svgPath, pngPath, w, h] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await p.goto('file://' + svgPath);
  await p.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: +w, height: +h } });
  await b.close();
})();
"""
    with tempfile.TemporaryDirectory() as td:
        sp = Path(td) / "f.svg"
        sp.write_text(svg, encoding="utf-8")
        jp = Path(td) / "r.js"
        jp.write_text(js, encoding="utf-8")
        subprocess.run(["node", str(jp), str(sp), str(png), str(w), str(h)], check=True)


def compare(orig: Path, redraw_png: Path, overlay: Path) -> dict:
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(orig).convert("L"), dtype=float)
    b = np.asarray(Image.open(redraw_png).convert("L"), dtype=float)
    mad = float(np.abs(a - b).mean())
    da, db = a < 128, b < 128

    def dilate(m):
        out = m.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                out |= np.roll(np.roll(m, dy, 0), dx, 1)
        return out
    # 原图深色像素中有多少在重绘图1像素邻域内有对应，反之亦然
    recall = float((da & dilate(db)).sum() / max(1, da.sum()))
    precision = float((db & dilate(da)).sum() / max(1, db.sum()))
    rgb = np.stack([np.full_like(a, 255)] * 3, -1)
    rgb[da] = [220, 0, 0]
    rgb[db] = [0, 70, 220]
    rgb[da & db] = [0, 0, 0]
    Image.fromarray(rgb.astype("uint8")).resize((a.shape[1] * 3, a.shape[0] * 3), Image.NEAREST).save(overlay)
    return {"平均绝对灰度差": round(mad, 2), "原图深色像素被重绘覆盖率(±1px)": round(recall, 4),
            "重绘深色像素落在原图笔画上的比例(±1px)": round(precision, 4)}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    records = []
    for asset_id, spec in FIGURES.items():
        src = REPO / spec["source"]
        svg = spec["draw"]()
        (OUT / f"{asset_id}.svg").write_text(svg, encoding="utf-8")
        with tempfile.TemporaryDirectory() as td:
            png = Path(td) / "r.png"
            from PIL import Image
            w, h = Image.open(src).size
            rasterize(svg, w, h, png)
            metrics = compare(src, png, OUT / f"{asset_id}_叠图核对.png")
        records.append({
            "asset_id": asset_id,
            "source_path": spec["source"],
            "source_image_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "svg_path": f"重绘/{asset_id}.svg",
            "overlay_path": f"重绘/{asset_id}_叠图核对.png",
            "print_width_mm": spec["print_width_mm"],
            "method": spec["note"],
            "comparison": metrics,
            "overlay_legend": "叠图放大3倍：黑=两者重合，红=仅原图有，蓝=仅重绘有",
        })
        print(asset_id, metrics)
    (OUT / "重绘核对记录.json").write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
