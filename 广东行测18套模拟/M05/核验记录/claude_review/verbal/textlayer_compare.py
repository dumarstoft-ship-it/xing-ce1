# 只读：用 pdfplumber 取原卷文字层（按 regions 裁剪），与 M05 题目.jsonl 去空白后逐字比对；同时列出原卷文字层的空格
import json, re, difflib, unicodedata
import pdfplumber
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
XC = "/home/user/dumarstoft-ship-it/xingce"
sel = {q["number"]: q for q in json.load(open(f"{M05}/selection.json", encoding="utf-8"))}
tm = {json.loads(l)["number"]: json.loads(l) for l in open(f"{M05}/题目.jsonl", encoding="utf-8")}
def flat(bl): return "".join(b["text"] for b in bl if b["type"] == "text")
def norm(s):
    s = re.sub(r"<u>|</u>", "", s)
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s_]", "", s)
pdfs = {}
for n in range(16, 31):
    src = sel[n]["source_question"]["source"]
    f = src["file"]
    if f not in pdfs: pdfs[f] = pdfplumber.open(f"{XC}/{f}")
    pdf = pdfs[f]
    raw_lines = []
    for r in src["regions"]:
        page = pdf.pages[r["page"] - 1]
        x0, y0, x1, y1 = r["bbox"]
        crop = page.crop((max(0, x0 - 2), max(0, y0 - 2), min(page.width, x1 + 2), min(page.height, y1 + 2)))
        txt = crop.extract_text(keep_blank_chars=True) or ""
        raw_lines.extend(txt.split("\n"))
    raw = "\n".join(raw_lines)
    m = tm[n]
    mtext = flat(m["stem"]) + "".join(k + flat(m["options"][k]) for k in "ABCD")
    a, b = norm(raw), norm(mtext)
    # 去掉题号与选项标记差异：原卷 "21." 等题号、"A." "A、"
    a2 = re.sub(r"^\d+[.、．]", "", a)
    a2 = re.sub(r"([ABCD])[.、．]", r"\1", a2)
    print(f"### {n}  textlayer_chars={len(a2)}  m05_chars={len(b)}  identical_ignoring_ws={a2 == b}")
    if a2 != b:
        for op in difflib.SequenceMatcher(None, a2, b, autojunk=False).get_opcodes():
            if op[0] != "equal":
                print("   ", op[0], "PDF:", repr(a2[op[1]:op[2]]), "M05:", repr(b[op[3]:op[4]]), "ctx:", repr(a2[max(0, op[1]-8):op[2]+8]))
    # 原卷文字层中选项行的空格情况
    for ln in raw_lines:
        if re.match(r"^\s*[ABCD][.、．]", ln) or "  " in ln:
            print("    line:", repr(ln))
