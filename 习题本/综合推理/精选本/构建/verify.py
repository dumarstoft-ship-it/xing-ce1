#!/usr/bin/env python3
"""校验精选本：python3 verify.py <精选PDF> <selection.json> <records.json> <原书PDF>"""
import json, re, subprocess, sys
from pypdf import PdfReader

out_pdf, sel_path, rec_path, src_pdf = sys.argv[1:5]
sel = json.load(open(sel_path)); recs = {r["idx"]: r for r in json.load(open(rec_path))}
r = PdfReader(out_pdf); src = PdfReader(src_pdf)
N = len(r.pages)
problems = []
def text(i):
    return subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), out_pdf, "-"], capture_output=True, text=True).stdout
norm = lambda s: re.sub(r"\s+", "", s)
order = [q["idx"] for mod in sel["modules"] for m in mod["models"] for q in m["questions"]]
assert len(order) == len(set(order)), "选题有重复"
# 1. 页码连续 + 题页内容
pos = {}
for i in range(1, N + 1):
    t = text(i)
    lines = [l for l in t.rstrip().splitlines() if l.strip()]
    last = lines[-1] if lines else ""
    m = re.search(r"(\d+)\s*$", last)
    if not m or int(m.group(1)) != i: problems.append(f"第{i}页页脚页码异常：{last[-30:]!r}")
    m2 = re.search(r"\n\s*(\d{2,3})\s+二刷练习", t)
    if m2: pos[int(m2.group(1))] = i
n = 0
for idx in order:
    n += 1
    rec = recs[idx]
    if idx not in pos: problems.append(f"原{idx}题练习页没找到"); continue
    p = pos[idx]
    if p % 2 != 1: problems.append(f"原{idx}题练习页在偶数页{p}")
    t = norm(text(p)); stem = norm(rec["stem"])[:40]
    if stem not in t: problems.append(f"原{idx}题练习页题面不符")
    if f"精选{n:02d}/{len(order)}" not in t: problems.append(f"原{idx}题缺少“精选 {n:02d}”标签")
    ts = norm(text(p + 1))
    if not re.search(rf"{idx:02d}草稿解析答案", ts): problems.append(f"原{idx}题解析页不在练习页背面")
# 顺序
seq = sorted(pos, key=lambda k: pos[k])
if seq != order: problems.append("题目顺序与选题清单不一致")
# 2. 链接
ids = {p.indirect_reference.idnum: k for k, p in enumerate(r.pages)}
uri = dest = 0
for k, p in enumerate(r.pages):
    for a in p.get("/Annots") or []:
        o = a.get_object()
        if o.get("/Dest") is not None:
            d = o["/Dest"][0]
            tgt = ids.get(d.idnum) if hasattr(d, "idnum") else int(d)
            if tgt is None or not (0 <= tgt < N): problems.append(f"第{k+1}页有失效内部链接")
            dest += 1
        elif o.get("/A") is not None:
            act = o["/A"].get_object()
            if act.get("/S") == "/URI": uri += 1
            else: problems.append(f"第{k+1}页有非URI动作链接 {act.get('/S')}")
src_uri = 0
for idx in order:
    for sp in (recs[idx]["page"], recs[idx]["spage"]):
        for a in src.pages[sp - 1].get("/Annots") or []:
            act = a.get_object().get("/A")
            if act is not None and act.get_object().get("/S") == "/URI": src_uri += 1
if uri != src_uri: problems.append(f"外部链接数 {uri} 与原书对应页 {src_uri} 不一致")
# 3. 字体
fonts = subprocess.run(["pdffonts", out_pdf], capture_output=True, text=True).stdout
if "Type 3" in fonts: problems.append("出现 Type3 字体")
for line in fonts.splitlines()[2:]:
    parts = line.split()
    if "Helvetica" in line: continue
    if len(parts) >= 5 and parts[-5] != "yes": problems.append(f"字体未嵌入：{line}")
# 4. 部首码位
alltext = subprocess.run(["pdftotext", out_pdf, "-"], capture_output=True, text=True).stdout
bad = sorted({c for c in alltext if 0x2E80 <= ord(c) < 0x2FE0})
if bad: problems.append(f"文字层出现部首码位：{''.join(bad)}")
print(f"共 {N} 页，{len(order)} 题；内部链接 {dest} 个，外部链接 {uri} 个")
print("\n".join(problems) if problems else "全部检查通过")
sys.exit(1 if problems else 0)
