#!/usr/bin/env python3
"""校验数字推理精选本：python3 verify_sx.py <精选PDF> <selection.json> <records.json> <layout.json>"""
import json, re, subprocess, sys, unicodedata
from pypdf import PdfReader

out_pdf, sel_p, rec_p, lay_p = sys.argv[1:5]
sel = json.load(open(sel_p)); recs = {r["id"]: r for r in json.load(open(rec_p))}; lay = json.load(open(lay_p))
r = PdfReader(out_pdf); N = len(r.pages); problems = []
def text(i):
    return subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), out_pdf, "-"], capture_output=True, text=True).stdout
norm = lambda s: re.sub(r"[\s,，、:：()（）]", "", unicodedata.normalize("NFKC", s))
order = [q["id"] for m in sel["modules"] for g in m["groups"] for q in g["questions"]]
if len(order) != len(set(order)): problems.append("选题有重复")
if N != lay["pages"]: problems.append("页数与排版记录不符")
for i, k in enumerate(lay["kinds"], 1):
    if k == "front" and i % 2 != 1: problems.append(f"第{i}页练习页落在偶数页")
pages_txt = {}
for i in range(1, N + 1):
    t = text(i); pages_txt[i] = t
    last = [l for l in t.rstrip().splitlines() if l.strip()][-1] if t.strip() else ""
    m = re.search(r"(\d+)\s*$", last)
    if not m or int(m.group(1)) != i: problems.append(f"第{i}页页脚页码异常：{last[-24:]!r}")
for n, qid in enumerate(order, 1):
    rec = recs[qid]; p = lay["pageno"][f"q:{qid}"]
    f, b = norm(pages_txt[p]), norm(pages_txt[p + 1])
    if f"精选{n:02d}原书{norm(qid)}" not in f: problems.append(f"{qid}：练习页缺少“精选 {n:02d}”标签")
    if norm(rec["source"]) not in f: problems.append(f"{qid}：练习页找不到出处“{rec['source']}”")
    if f"精选{n:02d}解析" not in b: problems.append(f"{qid}：背面缺少对应解析标签")
    if norm(f'{rec["answer"]}{rec["answer_value"]}') not in b: problems.append(f"{qid}：背面找不到答案 {rec['answer']} {rec['answer_value']}")
    rows = [x for x in rec["solution"].split(" / ") if len(re.findall(r"[\u4e00-\u9fff]", x)) >= 6
            and not x.startswith("回练") and not re.match(r"^(\d{2}\s+)?[A-D]\s", x)]
    cjk = lambda s: "".join(re.findall(r"[\u4e00-\u9fff]", unicodedata.normalize("NFKC", s)))
    first = cjk(rows[0])[:10] if rows else ""
    if first and first not in cjk(pages_txt[p + 1]): problems.append(f"{qid}：背面找不到解析首句")
ids = {p.indirect_reference.idnum: k for k, p in enumerate(r.pages)}
dest = uri = 0
for k, pg in enumerate(r.pages):
    for a in pg.get("/Annots") or []:
        o = a.get_object()
        if o.get("/Dest") is not None:
            d = o["/Dest"][0]; t = ids.get(d.idnum) if hasattr(d, "idnum") else int(d)
            if t is None or not 0 <= t < N: problems.append(f"第{k+1}页有失效内部链接")
            dest += 1
        elif o.get("/A") is not None and o["/A"].get_object().get("/S") == "/URI": uri += 1
alltext = subprocess.run(["pdftotext", out_pdf, "-"], capture_output=True, text=True).stdout
bad = sorted({c for c in alltext if 0x2E80 <= ord(c) < 0x2FE0})
if bad: problems.append(f"文字层残留部首码位：{''.join(bad)}")
fonts = subprocess.run(["pdffonts", out_pdf], capture_output=True, text=True).stdout
for line in fonts.splitlines()[2:]:
    parts = line.split()
    if len(parts) >= 5 and parts[-5] != "yes" and "Helvetica" not in line: problems.append(f"字体未嵌入：{line}")
print(f"共 {N} 页，{len(order)} 题；内部链接 {dest} 个，真题出处链接 {uri} 个")
print("\n".join(problems) if problems else "全部检查通过")
sys.exit(1 if problems else 0)
