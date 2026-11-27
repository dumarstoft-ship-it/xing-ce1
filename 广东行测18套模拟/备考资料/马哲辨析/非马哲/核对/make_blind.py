"""政常新题去掉答案和解析，生成盲做输入：非马哲/核对/blind_<编号>.json。选项按出题人的原顺序编A、B、C、D。

网页在作答之后才显示“适用条件”（condition），所以盲做输入也不给它，核对人看到的就是用户作答时看到的。
（第一批 F1—F6 的盲做输入带了 condition；之后发现这个差别，另做了一遍“题干是否自足”的检查。）

用法：python3 make_blind.py F1 F2 ...
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for w in sys.argv[1:]:
    qs = json.loads((HERE.parent / "新题" / f"{w}.json").read_text(encoding="utf-8"))
    out = [{"id": q["id"], "type": q["type"], "lead": q.get("lead") or "", "stem": q["stem"],
            "options": {"ABCDEF"[i]: o["text"] for i, o in enumerate(q.get("options") or [])}} for q in qs]
    (HERE / f"blind_{w}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(w, len(out))
