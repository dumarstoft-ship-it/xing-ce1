# 只读：打印第20、25题原卷文字层原始行（含空格，repr），并逐字符列出选项行的字符与x坐标
import pdfplumber
XC = "/home/user/dumarstoft-ship-it/xingce"
f = f"{XC}/2022年江苏公务员考试《行测》真题（A类）....pdf"
with pdfplumber.open(f) as pdf:
    for label, pg, bbox in [("Q20 p7", 7, (36.0, 642.5, 557.5, 784.5)), ("Q20 p8", 8, (60.0, 35.6, 223.3, 53.1)), ("Q25 p3", 3, (36.0, 595.9, 553.1, 753.4))]:
        page = pdf.pages[pg - 1]
        crop = page.crop(bbox)
        print("=====", label)
        for ln in (crop.extract_text(keep_blank_chars=True) or "").split("\n"):
            print("  ", repr(ln))
        # 选项行逐字符
        words = crop.extract_words(keep_blank_chars=True, use_text_flow=False, x_tolerance=1.5)
        for w in words:
            if w["text"][:1] in "ABCD" or "如雷贯耳" in w["text"] or "耳熟能详" in w["text"]:
                print("   word:", repr(w["text"]), round(w["x0"], 1), round(w["top"], 1))
        chars = [c for c in crop.chars]
        opt_tops = sorted({round(c["top"]) for c in chars if c["text"] in "ABCD" and c.get("size", 0) > 5})
        for t in opt_tops:
            row = sorted([c for c in chars if abs(c["top"] - t) < 2], key=lambda c: c["x0"])
            seq = []
            prev = None
            for c in row:
                gap = (c["x0"] - prev["x1"]) if prev else 0
                seq.append(f"{c['text']}[{gap:.1f}]")
                prev = c
            print("   row@", t, " ".join(seq))
