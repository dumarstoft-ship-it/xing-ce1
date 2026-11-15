#!/usr/bin/env python3
"""按现有 SVG 与 Claude 审核原型重绘 M03 第 35 题；不覆盖旧图。"""

import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image, ImageDraw, ImageFont


M03 = Path(__file__).resolve().parents[1]
OUT = M03 / "assets"
RECORD = Path(__file__).resolve().parent
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
SCALE = 3
WIDTH, HEIGHT = 720, 180
RADIUS = 70
STROKE = 1.8
PNG_LINE_WIDTH = 5  # 与既有 PNG、审核原型一致。
DX, DY, FONT_SIZE = 32, 22, 24
SIGNS = [(-1, -1), (1, -1), (-1, 1), (1, 1)]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(values, dx, dy, font_size):
    im = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), "white")
    d = ImageDraw.Draw(im)
    text_mask = Image.new("L", im.size, 0)
    td = ImageDraw.Draw(text_mask)
    font = ImageFont.truetype(str(FONT), font_size * SCALE)
    for j, vs in enumerate(values):
        cx, cy = 90 + j * 180, 90
        d.ellipse(((cx - RADIUS) * SCALE, (cy - RADIUS) * SCALE,
                   (cx + RADIUS) * SCALE, (cy + RADIUS) * SCALE),
                  outline="black", width=PNG_LINE_WIDTH)
        d.line(((cx - RADIUS) * SCALE, cy * SCALE,
                (cx + RADIUS) * SCALE, cy * SCALE), fill="black", width=PNG_LINE_WIDTH)
        d.line((cx * SCALE, (cy - RADIUS) * SCALE,
                cx * SCALE, (cy + RADIUS) * SCALE), fill="black", width=PNG_LINE_WIDTH)
        for v, (sx, sy) in zip(vs, SIGNS):
            pos = ((cx + sx * dx) * SCALE, (cy + sy * dy) * SCALE)
            d.text(pos, v, font=font, fill="black", anchor="mm")
            td.text(pos, v, font=font, fill=255, anchor="mm")
    return im, text_mask


def clearance(text_mask, values):
    """与审核原型相同的几何口径：字形深色像素到线中心，减 SVG 线宽的一半。

    另绘字形掩膜，避免把直径和圆周误认成字形；该值是几何估计，
    不声称消除了 SVG/Pillow 栅格化和打印机造成的亚像素差异。
    """
    a = np.asarray(text_mask) >= 128
    half_stroke = STROKE * SCALE / 2
    out = []
    for j, vs in enumerate(values):
        X, Y, R = (90 + j * 180) * SCALE, 90 * SCALE, RADIUS * SCALE
        for v, (sx, sy) in zip(vs, SIGNS):
            x0, x1 = (X, X + R) if sx > 0 else (X - R, X)
            y0, y1 = (Y, Y + R) if sy > 0 else (Y - R, Y)
            ys, xs = np.nonzero(a[y0:y1, x0:x1])
            ys, xs = ys + y0, xs + x0
            assert len(xs), (j + 1, v)
            to_line = min(np.min(abs(xs - X)), np.min(abs(ys - Y))) - half_stroke
            to_circle = np.min(R - np.hypot(xs - X, ys - Y)) - half_stroke
            out.append({"circle": j + 1, "quadrant": [sx, sy], "text": v,
                        "to_diameter_px": round(float(to_line), 1),
                        "to_circle_px": round(float(to_circle), 1)})
    return {"min_to_diameter_px": min(x["to_diameter_px"] for x in out),
            "min_to_circle_px": min(x["to_circle_px"] for x in out),
            "cells": out}


def main():
    OUT.mkdir(exist_ok=True)
    rows = json.loads((M03 / "selection.json").read_text())
    q = next(q for q in rows if q["number"] == 35)
    source_table = q["source_question"]["stem"][0]
    assert source_table["type"] == "table"
    assert source_table["headers"] == ["圆（自左向右）", "左上", "右上", "左下", "右下"]
    source_values = [r[1:] for r in source_table["rows"]]
    values = [[v.replace("？", "?") for v in row] for row in source_values]
    assert values == [["25", "3", "7", "−4"], ["14", "8", "6", "34"],
                      ["51", "9", "4", "−15"], ["22", "8", "7", "?"]]

    old_paths = [M03 / "编辑底稿/quant_data_number_grid.svg",
                 M03 / "编辑底稿/quant_data_number_grid.png"]
    old_hashes = {str(p.relative_to(M03)): sha256(p) for p in old_paths}
    old_im, old_mask = render(values, 29, 28, 28)
    with Image.open(old_paths[1]) as existing:
        assert np.array_equal(np.asarray(old_im), np.asarray(existing.convert("RGB")))

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="2160" height="540" '
           f'viewBox="0 0 {WIDTH} {HEIGHT}">',
           f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>']
    for j, vs in enumerate(values):
        cx, cy = 90 + j * 180, 90
        svg.append(f'<g fill="none" stroke="black" stroke-width="{STROKE}">'
                   f'<circle cx="{cx}" cy="{cy}" r="{RADIUS}"/>'
                   f'<path d="M {cx-RADIUS} {cy} H {cx+RADIUS} '
                   f'M {cx} {cy-RADIUS} V {cy+RADIUS}"/></g>')
        for v, (sx, sy) in zip(vs, SIGNS):
            svg.append(f'<text x="{cx+sx*DX}" y="{cy+sy*DY}" text-anchor="middle" '
                       f'dominant-baseline="central" font-family="DejaVu Serif,serif" '
                       f'font-size="{FONT_SIZE}">{escape(v)}</text>')
    svg.append('</svg>')
    svg_path = OUT / "q35_number_grid_v020.svg"
    png_path = OUT / "q35_number_grid_v020.png"
    svg_path.write_text("\n".join(svg) + "\n", encoding="utf-8")
    im, mask = render(values, DX, DY, FONT_SIZE)
    im.save(png_path)
    print_width = round(120 / 25.4 * 300)
    preview = RECORD / "v020_q35_print120mm.png"
    im.resize((print_width, round(print_width * im.height / im.width)),
              Image.Resampling.LANCZOS).save(preview, dpi=(300, 300))
    before, after = clearance(old_mask, values), clearance(mask, values)
    assert after["min_to_diameter_px"] >= 25.0
    assert after["min_to_circle_px"] >= 23.0
    assert old_hashes == {str(p.relative_to(M03)): sha256(p) for p in old_paths}
    report = {
        "scope": "第35题重建数阵图；保留旧图；未与缺失的原PDF逐像素比较。",
        "source_id": q["source_id"], "source_values_TL_TR_BL_BR": source_values,
        "display_values_TL_TR_BL_BR": values,
        "fullwidth_question_mark_normalization": "源表的？与既有图的?指同一待求数，本版沿用既有图?。",
        "canvas_px": [2160, 540], "svg_viewbox": [0, 0, 720, 180],
        "previous_parameters": {"font_size": 28, "dx": 29, "dy": 28, "radius": 70},
        "new_parameters": {"font_size": FONT_SIZE, "dx": DX, "dy": DY, "radius": RADIUS},
        "svg_stroke_width": STROKE, "png_line_width_px": PNG_LINE_WIDTH,
        "font_file": str(FONT), "font_sha256": sha256(FONT),
        "clearance_method": "深色字形像素到直径/圆周的几何距离，减SVG线宽的一半；与审核原型同口径。",
        "before": before, "after": after,
        "at_120mm_width": {
            "min_to_diameter_mm": round(after["min_to_diameter_px"] / 2160 * 120, 3),
            "min_to_circle_mm": round(after["min_to_circle_px"] / 2160 * 120, 3),
            "preview_png": str(preview.relative_to(M03)), "dpi": 300,
            "note": "仅为规定物理宽度的缩放预览，不代表整卷PDF排版已完成。"},
        "old_files_preserved_sha256": old_hashes,
        "new_files_sha256": {str(p.relative_to(M03)): sha256(p) for p in [svg_path, png_path, preview]},
        "status": "PASS"
    }
    (RECORD / "v020_q35_layout_check.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "new_canvas": im.size,
                      "old_min_clearance_px": [before["min_to_diameter_px"], before["min_to_circle_px"]],
                      "new_min_clearance_px": [after["min_to_diameter_px"], after["min_to_circle_px"]]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
