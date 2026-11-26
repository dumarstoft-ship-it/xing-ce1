"""把出题人的新题去掉答案和解析，生成盲做输入：核对/blind_<编号>.json。

用法：python3 make_blind.py W1 W2 ...
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for w in sys.argv[1:]:
    qs = json.loads((HERE.parent / "新题" / f"{w}.json").read_text(encoding="utf-8"))
    out = [{"id": q["id"], "type": q["type"], "lead": q.get("lead") or "", "stem": q["stem"], "options": q.get("options") or {}} for q in qs]
    (HERE / f"blind_{w}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(w, len(out))
