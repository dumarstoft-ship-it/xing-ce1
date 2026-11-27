"""政常新题去掉答案和解析，生成盲做输入：非马哲/核对/blind_<编号>.json。选项按出题人的原顺序编A、B、C、D。

用法：python3 make_blind.py F1 F2 ...
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for w in sys.argv[1:]:
    qs = json.loads((HERE.parent / "新题" / f"{w}.json").read_text(encoding="utf-8"))
    out = [{"id": q["id"], "type": q["type"], "lead": q.get("lead") or "", "stem": q["stem"],
            "condition": q.get("condition") or "",
            "options": {"ABCDEF"[i]: o["text"] for i, o in enumerate(q.get("options") or [])}} for q in qs]
    (HERE / f"blind_{w}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(w, len(out))
