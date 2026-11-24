#!/usr/bin/env python3
"""校验图形推理精选本：python3 verify_tt.py <精选PDF> <selection.json> <records.json> <layout.json>"""
import json, re, subprocess, sys, unicodedata
from pypdf import PdfReader

out_pdf, sel_p, rec_p, lay_p = sys.argv[1:5]
sel = json.load(open(sel_p)); recs = {r["id"]: r for r in json.load(open(rec_p))}; lay = json.load(open(lay_p))
r = PdfReader(out_pdf); N = len(r.pages); problems = []
txt = {i: subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), out_pdf, "-"], capture_output=True, text=True).stdout for i in range(1, N + 1)}
norm = lambda s: re.sub(r"[\s,，、:：()（）·]", "", unicodedata.normalize("NFKC", s))
cjk = lambda s: "".join(re.findall(r"[一-鿿]", unicodedata.normalize("NFKC", s)))
order = [q["id"] for m in sel["modules"] for g in m["groups"] for q in g["questions"]]
timed = {q["id"] for m in sel["modules"] if m.get("kind") == "timed" for g in m["groups"] for q in g["questions"]}
if len(order) != len(set(order)): problems.append("选题有重复")
if N != lay["pages"]: problems.append("页数与排版记录不符")
for i in range(1, N + 1):
    lines = [l for l in txt[i].rstrip().splitlines() if l.strip()]
    m = re.search(r"(\d+)\s*$", lines[-1] if lines else "")
    if not m or int(m.group(1)) != i: problems.append(f"第{i}页页脚页码异常")
allcjk = {i: cjk(txt[i]) for i in txt}
for n, qid in enumerate(order, 1):
    rec = recs[qid]; p = lay["pageno"][f"q:{qid}"]
    if not re.search(rf"\b{n:03d}\b", txt[p]): problems.append(f"{qid}：第{p}页缺少编号 {n:03d}")
    first = cjk(rec["explanation"])[:10]
    if qid in timed:
        # 题页不露原题号；答案页在本组题页之后，带原题号和解析
        if qid in txt[p]: problems.append(f"{qid}：限时题页露出了原题号")
        hit = [k for k in range(p + 1, min(N, p + 7) + 1) if first in allcjk[k]]
        if not hit: problems.append(f"{qid}：限时组后找不到解析")
        elif qid not in txt[hit[0]]: problems.append(f"{qid}：答案页（第{hit[0]}页）缺原题号")
    elif qid not in txt[p]: problems.append(f"{qid}：第{p}页找不到原题号")
    if qid not in timed and first not in allcjk[p] and first not in allcjk.get(p + 1, ""):
        problems.append(f"{qid}：题后找不到解析首句")
ids = {pg.indirect_reference.idnum: k for k, pg in enumerate(r.pages)}
dest = 0
for k, pg in enumerate(r.pages):
    for a in pg.get("/Annots") or []:
        o = a.get_object()
        if o.get("/Dest") is not None:
            d = o["/Dest"][0]; t = ids.get(d.idnum) if hasattr(d, "idnum") else int(d)
            if t is None or not 0 <= t < N: problems.append(f"第{k+1}页有失效内部链接")
            dest += 1
alltext = subprocess.run(["pdftotext", out_pdf, "-"], capture_output=True, text=True).stdout
bad = sorted({c for c in alltext if 0x2E80 <= ord(c) < 0x2FE0})
if bad: problems.append(f"文字层残留部首码位：{''.join(bad)}")
fonts = subprocess.run(["pdffonts", out_pdf], capture_output=True, text=True).stdout
for line in fonts.splitlines()[2:]:
    parts = line.split()
    if len(parts) >= 5 and parts[-5] != "yes" and "Helvetica" not in line: problems.append(f"字体未嵌入：{line}")
print(f"共 {N} 页，{len(order)} 题（限时 {len(timed)} 题）；内部链接 {dest} 个")
print("\n".join(problems[:40]) if problems else "全部检查通过")
sys.exit(1 if problems else 0)
