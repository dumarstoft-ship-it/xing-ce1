# -*- coding: utf-8 -*-
"""为第76、81、86题的 chart_note 找依据：列出题库各季资料材料中“转写成表”的原图尺寸（pt），
按标题是否带“图”“表”分组，与第23季三张表对照。

原图尺寸取材料 source_spans 中面积最大的一块（即嵌入图片的框）。只读题库文件，不涉及答案。
"""
import json
import re
from pathlib import Path

BANK = Path("/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读")
rows_out = []
for season in range(16, 34):
    fn = next(BANK.glob(f"第{season}季/题目.json"))
    d = json.load(open(fn, encoding="utf-8"))
    for m in d["materials"]:
        tables = [b for b in m["blocks"] if b.get("type") == "table" and b.get("source_asset_id")]
        if not tables:
            continue
        # 高度超过40pt的框是嵌入图片；按页码、纵坐标排序后与材料中表的先后一一对应
        big = sorted([s for s in m["source_spans"] if (s["bbox_pt"][3] - s["bbox_pt"][1]) > 40],
                     key=lambda s: (s["pdf_page"], s["bbox_pt"][1]))
        for i, t in enumerate(tables):
            title = t.get("title", "")
            kind = "图" if re.match(r"^\s*图", title) else ("表" if re.match(r"^\s*表", title) else "无")
            box = big[i] if i < len(big) else None
            wh = [(round(box["bbox_pt"][2] - box["bbox_pt"][0]), round(box["bbox_pt"][3] - box["bbox_pt"][1]))] if box else []
            rows_out.append((season, m["number"], kind, title[:30], len(t["rows"]) + 1, len(t["headers"]), wh))

for kind in ("图", "表", "无"):
    print(f"\n=== 标题以“{kind}”开头 ===" if kind != "无" else "\n=== 标题无“图”“表”字样 ===")
    for r in rows_out:
        if r[2] == kind:
            s, mn, _, title, nrow, ncol, boxes = r
            note = ""
            if boxes:
                w, h = boxes[0]
                note = f"每行约{h / nrow:.1f}pt"
            print(f"第{s}季第{mn}组 行{nrow}×列{ncol} 原图(宽×高pt) {boxes} {note} | {title}")

# 汇总
for kind in ("图", "表"):
    hs = [r[6][0][1] for r in rows_out if r[2] == kind and r[6]]
    pr = [r[6][0][1] / r[4] for r in rows_out if r[2] == kind and r[6]]
    print(f"标题带“{kind}”：高度 {min(hs)}—{max(hs)}pt，每行 {min(pr):.1f}—{max(pr):.1f}pt，共{len(hs)}张")
