# 只读：导出 M05 selection.json 第16—30题的答案、解析、来源、编辑记录
import json, sys
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
sel = json.load(open(f"{M05}/selection.json", encoding="utf-8"))
for q in sel:
    if 16 <= q["number"] <= 30:
        out = {k: q.get(k) for k in ["number","source_id","source_bank","source_file","subtype","question_type","answer","source_answer","edits","selection_reason","verification"]}
        print(json.dumps(out, ensure_ascii=False, indent=1))
        print("STEM:", json.dumps(q.get("stem"), ensure_ascii=False))
        print("OPTIONS:", json.dumps(q.get("options"), ensure_ascii=False))
        print("ANALYSIS:", q.get("analysis"))
        other = {k: v for k, v in q.items() if k not in out and k not in ("stem","options","analysis")}
        print("OTHER:", json.dumps(other, ensure_ascii=False)[:3000])
        print("=" * 80)
