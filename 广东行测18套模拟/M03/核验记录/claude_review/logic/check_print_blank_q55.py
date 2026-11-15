#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核验 M03 第55题“画横线位置”在打印链路中是否可见。

逻辑：
  1. 从 题目.jsonl 取第55题题干（考生可见、打印工具的输入）；
  2. 从 打印排版/build_print.py 源码中读出它识别填空线的正则（UNDERS = re.compile(r"_{3,}")），
     不 import 该模块（避免依赖 pypdf/playwright 等），只做静态读取；
  3. 检查 exam.css 中 white-space: pre/pre-wrap 是否作用于正文段落（若没有，连续空格在 HTML/PDF 中折叠为一个）；
  4. 对照同卷言语填空题的写法（____）。

用法：python3 check_print_blank_q55.py [仓库根目录]（默认 /home/user/xing-ce1）
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/user/xing-ce1")
M03 = ROOT / "广东行测18套模拟" / "M03"
TOOL = ROOT / "广东行测18套模拟" / "打印排版"

rows = [json.loads(l) for l in (M03 / "题目.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
q55 = next(r for r in rows if r["number"] == 55)
stem = "".join(p.get("text", "") for p in q55["stem"] if p.get("type") == "text")
print("Q55 题干：", stem.replace("\n", "⏎"))
runs = [(m.start(), len(m.group(0))) for m in re.finditer(r" {2,}", stem)]
print("连续空格段（起点, 长度）：", runs)

src = (TOOL / "build_print.py").read_text(encoding="utf-8")
m = re.search(r'UNDERS\s*=\s*re\.compile\(r"([^"]+)"\)', src)
unders = re.compile(m.group(1)) if m else None
print("打印工具填空线正则：", m.group(1) if m else "未找到")
print("Q55 题干中可被识别为填空线的片段数：", len(unders.findall(stem)) if unders else "n/a")

css = (TOOL / "exam.css").read_text(encoding="utf-8")
blocks = re.findall(r"([^{}]+)\{([^}]*)\}", css)
pre_selectors = [sel.strip() for sel, body in blocks if re.search(r"white-space\s*:\s*pre(-wrap|-line)?\s*;", body)]
print("exam.css 中设置 white-space: pre/pre-wrap/pre-line 的选择器：", pre_selectors)
print("  -> 若正文段落不在其中，HTML 会把连续空格折叠成一个空格，题面“画横线位置”在PDF中看不到横线。")

# 同卷言语填空题写法对照
verbal = [r for r in rows if r["section"].startswith("言语") and "横线" in "".join(
    p.get("text", "") for p in r["stem"] if p.get("type") == "text")]
for r in verbal[:3]:
    t = "".join(p.get("text", "") for p in r["stem"] if p.get("type") == "text")
    print(f"对照：第{r['number']}题含填空线 {re.findall(r'_{3,}', t)[:3]}")

ok = bool(unders and unders.search(stem))
print("\n结论：", "第55题填空线可被打印工具识别" if ok else
      "第55题横线位置只是8个半角空格，打印工具不会把它画成填空线，且空格会被折叠；建议在 stem_override 中改为“____”（与同卷言语题一致）。")
