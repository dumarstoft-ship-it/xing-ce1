"""第二人盲解与第一遍答案对照。python3 compare_second.py M05"""
import json, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
p = sys.argv[1]
first = {}
for f in ("fig_logic.json", "quant_sci.json", "swaps.json"):
    fp = R / p / "解题" / f
    if fp.exists():
        for q in json.load(open(fp, encoding="utf-8")):
            first[q["id"]] = q["answer"]
for q in json.load(open(R / p / "原创.json", encoding="utf-8")) if (R / p / "原创.json").exists() else []:
    first[q["id"]] = q["answer"]
sec = json.load(open(R / p / "复核" / "second.json", encoding="utf-8"))
diff = [(q.get("number"), q.get("id"), q["answer"], first.get(q.get("id"))) for q in sec if first.get(q.get("id")) != q["answer"]]
print(p, "第二人", len(sec), "题，不一致", len(diff), diff)
