# 只读：紧凑导出 M05 selection.json 第16—30题关键字段
import json
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
sel = json.load(open(f"{M05}/selection.json", encoding="utf-8"))
q16 = [q for q in sel if q["number"] == 16][0]
print("KEYS:", list(q16.keys()))
print("source_question KEYS:", list(q16["source_question"].keys()))
for q in sel:
    if 16 <= q["number"] <= 30:
        sq = q["source_question"]
        print(f"### {q['number']} {q['source_id']} answer={q['answer']} source_answer={q['source_answer']} edits={q['edits']}")
        print("  file:", sq["source"]["file"], "pages:", sq["source"]["pdf_pages"])
        print("  regions:", sq["source"]["regions"])
        print("  quality_flags:", sq.get("quality_flags"), "notes:", sq.get("notes"), "instruction:", sq.get("instruction"))
        print("  source_notice:", q.get("source_notice"))
        sar = q.get("source_answer_reference")
        if sar:
            s = sar.get("source", {})
            print("  answer_ref:", s.get("file"), s.get("pdf_pages"), {k: v for k, v in sar.items() if k not in ("source", "file")})
        print("  selection_reason:", q.get("selection_reason"))
        print("  ANALYSIS:", q.get("analysis"))
        for k in q:
            if k not in ("number","source_id","source_bank","source_file","section","subtype","question_type","answer","source_answer","edits","selection_reason","verification","stem","options","analysis","source_question","source_locators","source_notice","source_answer_reference"):
                print("  EXTRA", k, ":", json.dumps(q[k], ensure_ascii=False)[:800])
