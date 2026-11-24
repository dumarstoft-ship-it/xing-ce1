#!/usr/bin/env python3
"""从《广东数字推理 · 条件反射训练》提取每道题：所在页、版面框、出处、答案、解析。

python3 extract_sx.py <原书PDF> <records.json>
"""
import json, re, sys, unicodedata, logging
import pdfplumber
logging.getLogger("pdfminer").setLevel(logging.ERROR)

EXTRA = {"⻚": "页", "⻓": "长", "⻛": "风", "⻔": "门", "⻜": "飞", "⻢": "马", "⻅": "见", "⻆": "角",
         "⻋": "车", "⻝": "食", "⻘": "青", "⻩": "黄", "⻨": "麦", "⻬": "齐", "⻰": "龙", "⻳": "龟",
         "⻉": "贝", "⻈": "钅", "⻓": "长", "⻖": "阝", "⻊": "足", "⻑": "长"}
def norm(s):
    s = unicodedata.normalize("NFKC", s)
    return "".join(EXTRA.get(c, c) for c in s)

def lines_of(page):
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False, extra_attrs=["size", "fontname"])
    for w in words:
        w["text"] = norm(w["text"])
    return words

def group_lines(words, tol=3.2):
    rows = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        for r in rows:
            if abs(r["top"] - w["top"]) <= tol:
                r["words"].append(w); break
        else:
            rows.append({"top": w["top"], "words": [w]})
    for r in rows:
        r["words"].sort(key=lambda w: w["x0"])
        r["text"] = " ".join(w["text"] for w in r["words"])
        r["bottom"] = max(w["bottom"] for w in r["words"])
        r["size"] = max(w["size"] for w in r["words"])
    return rows

def is_label(w):
    return re.fullmatch(r"\d{2}", w["text"]) and w["x0"] < 52 and 9.3 < w["size"] < 10.2 and "Arial" in w["fontname"]

def page_kind(rows):
    head = next((r["text"] for r in rows if 60 < r["top"] < 75), "")
    title = next((r["text"] for r in rows if 76 < r["top"] < 100 and r["size"] > 18), "")
    return head, title

def main():
    pdf_path, out = sys.argv[1], sys.argv[2]
    recs = []
    with pdfplumber.open(pdf_path) as pdf:
        H = pdf.pages[0].height
        pages = []
        for pi, page in enumerate(pdf.pages):
            words = lines_of(page)
            rows = group_lines(words)
            head, title = page_kind(rows)
            pages.append((pi + 1, page, words, rows, head, title))
        for pno, page, words, rows, head, title in pages:
            if not head.endswith("习题"): continue
            m = re.match(r"(M\d{2})\s+(\S+)\s*/\s*习题", head)
            if m:
                section, family, model = m.group(1), m.group(2), title
            else:
                section, family, model = title, "跨模型", ""
            labels = sorted([w for w in words if is_label(w)], key=lambda w: w["top"])
            if not labels: continue
            # 解析页：同一节的下一页起，找同编号
            sol = None
            for q in pages[pno:pno + 3]:
                if q[4].endswith("解析") and (q[4].startswith(section) or q[5] == title):
                    sol = q; break
            # 区块边界：下一个编号、或者“第二轮”等节标题、或者页脚统计
            stops = sorted([r["top"] for r in rows if re.match(r"^(第一轮|第二轮)", r["text"]) or re.match(r"^首式\s*≤", r["text"])
                            or r["text"].startswith("返回训练索引")] + [l["top"] for l in labels])
            for k, lab in enumerate(labels):
                top = lab["top"] - 9
                nxt = min([s for s in stops if s > lab["top"] + 5] or [H - 60])
                body = [r for r in rows if lab["top"] - 4 <= r["top"] < nxt - 2]
                bottom = min(max(r["bottom"] for r in body) + 9, nxt - 1)
                sw = sorted([w for w in words if abs(w["top"] - lab["top"]) <= 6 and w["x0"] > 150], key=lambda w: w["x0"])
                src = " ".join(w["text"] for w in sw)
                txt = " / ".join(r["text"] for r in body)
                rnd = ""
                for r in rows:
                    if r["top"] < lab["top"] and re.match(r"^(第一轮|第二轮)", r["text"]): rnd = r["text"].split()[0]
                qid = f"{section}-{lab['text']}"
                rec = dict(id=qid, section=section, family=family, model=model, round=rnd, num=lab["text"],
                           page=pno, bbox=[0, round(top, 1), round(page.width, 1), round(bottom, 1)],
                           source=src.strip(), selfmade=("自拟" in src), text=txt)
                # 解析
                if sol:
                    spno, spage, swords, srows = sol[0], sol[1], sol[2], sol[3]
                    slabels = sorted([w for w in swords if is_label(w)], key=lambda w: w["top"])
                    sl = next((w for w in slabels if w["text"] == lab["text"]), None)
                    if sl:
                        sstops = sorted([r["top"] for r in srows if re.match(r"^(第一轮|第二轮|换法或验算|返回训练索引)", r["text"])]
                                        + [r["top"] for r in srows if r["text"].startswith("三题连做")]
                                        + [w["top"] - 5 for w in slabels])
                        snxt = min([s for s in sstops if s > sl["top"] + 5] or [H - 60])
                        sbody = [r for r in srows if sl["top"] - 6 <= r["top"] < snxt - 1]
                        sbottom = min(max(r["bottom"] for r in sbody) + 9, snxt - 1)
                        stop_top = min([sl["top"]] + [r["top"] for r in sbody])
                        back = [r for r in sbody if r["text"].startswith("回练")]
                        back_top = back[0]["top"] if back else None
                        stext = " / ".join(r["text"] for r in sbody)
                        aw = sorted([w for w in swords if abs(w["top"] - sl["top"]) <= 6 and 58 < w["x0"] < 200 and w["size"] > 10.5],
                                    key=lambda w: w["x0"])
                        am = re.match(r"([A-D])\s+(.+)", " ".join(w["text"] for w in aw)) if aw else None
                        rec.update(spage=spno, sbbox=[0, round(stop_top - 9, 1), round(spage.width, 1), round(sbottom, 1)],
                                   sback_top=round(back_top, 1) if back_top else None,
                                   answer=am.group(1) if am else "", answer_value=am.group(2) if am else "", solution=stext)
                        bm = re.search(r"回练\s*(M\d{2}|基础)", stext)
                        rec["back_ref"] = bm.group(1) if bm else ""
                recs.append(rec)
        models = {}
        for pno, page, words, rows, head, title in pages:
            m = re.match(r"(M\d{2})\s+(\S+)\s*/\s*(习题|解析)", head)
            if not m: continue
            d = models.setdefault(m.group(1), {"id": m.group(1), "family": m.group(2), "title": title, "pages": []})
            d["pages"].append(pno)
            for r in rows:
                if m.group(3) == "习题" and 100 < r["top"] < 130 and "desc" not in d: d["desc"] = r["text"]
                if m.group(3) == "习题" and r["text"].startswith("首式 ") and r["top"] < 170: d["hint"] = r["text"][3:].strip()
                if m.group(3) == "解析" and r["text"].startswith(("换法或验算", "换法依据")): d.setdefault("check", r["text"].split(" ", 1)[-1])
        json.dump(list(models.values()), open(out.replace(".json", "_models.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(recs, open(out, "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(recs), "题；", Counter(r["family"] for r in recs))
    print("自拟", sum(r["selfmade"] for r in recs), "；缺解析", [r["id"] for r in recs if "answer" not in r or not r["answer"]])

if __name__ == "__main__":
    main()
