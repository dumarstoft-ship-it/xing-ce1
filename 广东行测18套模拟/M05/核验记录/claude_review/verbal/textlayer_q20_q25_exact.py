# 只读：第20、25题原卷文字层去掉相邻题文字后，与 M05 逐字（去空白）比对；第20题引号在文字层中被排到下一行，按字符多重集再核一次
import json, re, collections
import pdfplumber
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
XC = "/home/user/dumarstoft-ship-it/xingce"
tm = {json.loads(l)["number"]: json.loads(l) for l in open(f"{M05}/题目.jsonl", encoding="utf-8")}
def flat(bl): return "".join(b["text"] for b in bl if b["type"] == "text")
def ws(s): return re.sub(r"[\s_]", "", s)
f = f"{XC}/2022年江苏公务员考试《行测》真题（A类）....pdf"
with pdfplumber.open(f) as pdf:
    def region(pg, bbox):
        return pdf.pages[pg - 1].crop(bbox).extract_text(keep_blank_chars=True) or ""
    q20 = region(7, (36.0, 655.0, 557.5, 784.5)) + "\n" + region(8, (60.0, 35.6, 223.3, 53.1))
    q25 = region(3, (36.0, 608.0, 553.1, 753.4))
for n, raw in ((20, q20), (25, q25)):
    pdf_txt = ws(raw)
    pdf_txt = re.sub(r"^\d+", "", pdf_txt)                       # 题号
    m = tm[n]
    m05 = ws(flat(m["stem"])) + "".join("、" + ws(flat(m["options"][k])) + k for k in "ABCD")  # 文字层把“A”排在“、”行之后
    same_seq = pdf_txt == m05
    same_multiset = collections.Counter(pdf_txt) == collections.Counter(m05)
    print(f"第{n}题 文字层顺序一致={same_seq} 字符多重集一致={same_multiset}")
    if not same_multiset:
        print("  仅PDF有:", collections.Counter(pdf_txt) - collections.Counter(m05))
        print("  仅M05有:", collections.Counter(m05) - collections.Counter(pdf_txt))
    if not same_seq:
        import difflib
        for op in difflib.SequenceMatcher(None, pdf_txt, m05, autojunk=False).get_opcodes():
            if op[0] != "equal":
                print("  ", op[0], "PDF:", repr(pdf_txt[op[1]:op[2]]), "M05:", repr(m05[op[3]:op[4]]))
