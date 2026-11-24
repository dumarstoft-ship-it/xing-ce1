#!/usr/bin/env python3
"""提取两本图推书的逐题记录与裁切坐标。

python3 extract_tt.py <固定题型178题PDF> <平面图推200题PDF> <200题答案数据.json> <records.json>
"""
import json, re, sys, logging, unicodedata
import pdfplumber
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def rows_of(page, tol=3.0):
    rows = []
    for w in sorted(page.extract_words(extra_attrs=["size"]), key=lambda w: (w["top"], w["x0"])):
        w["text"] = unicodedata.normalize("NFKC", w["text"])
        for r in rows:
            if abs(r["top"] - w["top"]) <= tol: r["words"].append(w); break
        else: rows.append({"top": w["top"], "words": [w]})
    for r in rows:
        r["words"].sort(key=lambda w: w["x0"]); r["text"] = " ".join(w["text"] for w in r["words"])
        r["bottom"] = max(w["bottom"] for w in r["words"]); r["x0"] = min(w["x0"] for w in r["words"])
    return rows

CH = {"1": "折纸盒与六面体", "2": "视图", "3": "截面与切割", "4": "立体拼合与补形", "5": "平面拼合与分割", "6": "折纸与剪纸", "7": "立体识别"}

def spatial(pdf_path):
    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for pi, page in enumerate(pdf.pages):
            rows = rows_of(page); imgs = sorted(page.images, key=lambda i: i["top"])
            heads = [r for r in rows if re.fullmatch(r"第(\d)章 (\d+)", r["text"])]
            for k, h in enumerate(heads):
                ch, num = re.fullmatch(r"第(\d)章 (\d+)", h["text"]).groups()
                nxt = heads[k + 1]["top"] if k + 1 < len(heads) else page.height - 40
                src = next((r for r in rows if h["top"] < r["top"] < h["top"] + 30 and r["text"].startswith("真题")), None)
                img = [i for i in imgs if h["top"] < i["top"] < nxt]
                q_bottom = max(i["bottom"] for i in img) if img else (src["bottom"] if src else h["bottom"])
                ans_rows = [r for r in rows if q_bottom - 2 < r["top"] < nxt - 4 and r["top"] < page.height - 40]
                text = " ".join(r["text"] for r in ans_rows)
                m = re.search(r"答案\s*([A-D])\b", text) or re.search(r"\b([A-D])\b", text)
                expl = re.sub(r"^.*?答案\s*([A-D]\s*)?", "", text).strip()
                img_top = min(i["top"] for i in img) if img else (src["bottom"] if src else h["bottom"])
                out.append(dict(id=f"S{ch}-{int(num):02d}", book="固定题型178题", chapter=CH[ch], ch=int(ch), num=int(num), page=pi + 1,
                                q_top=round(img_top - 4, 1), q_bottom=round(q_bottom + 6, 1), head_top=round(h["top"] - 7, 1),
                                a_top=round(min(r["top"] for r in ans_rows) - 9, 1) if ans_rows else None,
                                a_bottom=round(max(r["bottom"] for r in ans_rows) + 9, 1) if ans_rows else None,
                                source=re.sub(r"^真题\s*", "", src["text"]).split("｜")[0].strip() if src else "",
                                answer=m.group(1) if m else "", explanation=expl))
    return out

def plane(pdf_path, data_path):
    data = {x["id"]: x for x in json.load(open(data_path))}
    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for pid, x in data.items():
            pno = int(pid[1:]) + 2
            page = pdf.pages[pno - 1]; rows = rows_of(page); imgs = sorted(page.images, key=lambda i: i["top"])
            head = next(r for r in rows if r["text"].startswith(pid))
            ans = next(r for r in rows if r["text"].startswith("答案"))
            ext = next((r for r in rows if r["text"].startswith("延伸阅读")), None)
            note = next((r for r in rows if r["text"].startswith("原答案")), None)
            qimgs = [i for i in imgs if i["top"] < ans["top"]]
            img_top, img_bottom = min(i["top"] for i in qimgs), max(i["bottom"] for i in qimgs)
            # 题号行（P001 2026年广东 · 原第47题）与本书标签重复，从它下面开始裁；题号行与图之间若有文字，从文字开始
            between = [r for r in rows if head["bottom"] + 1 < r["top"] < img_top]
            q_top = (min(r["top"] for r in between) - 6) if between else (img_top - 4)
            # 解析块止于正文：不含“延伸阅读”（指向原书的 M1—M8 模型）和“原答案／参考口径”
            stop = min([r["top"] for r in (ext, note) if r] + [page.height - 40])
            body = [r for r in rows if ans["top"] <= r["top"] < stop]
            out.append(dict(id=pid, book="平面图推200题", year=x["year"], region=x["region"], qno=x["qno"], page=pno,
                            q_top=round(q_top, 1), q_bottom=round(img_bottom + 8, 1),
                            a_top=round(ans["top"] - 10, 1),
                            a_bottom=round(min(max(r["bottom"] for r in body) + 6, stop - 3), 1),
                            head_between=bool(between),
                            source=x["source_label"], answer=x["answer"], models=x["models"],
                            explanation=x["explanation"], editor_note=x.get("editor_note") or "", explanation_source=x.get("explanation_source", "")))
    return out

if __name__ == "__main__":
    s = spatial(sys.argv[1]); p = plane(sys.argv[2], sys.argv[3])
    json.dump(s + p, open(sys.argv[4], "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print("空间", len(s), Counter(r["chapter"] for r in s)); print("平面", len(p))
    print("空间缺答案：", [r["id"] for r in s if not r["answer"]], "缺解析框：", [r["id"] for r in s if r["a_top"] is None])
