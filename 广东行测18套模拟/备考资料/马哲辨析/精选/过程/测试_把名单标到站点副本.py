"""测试用：把 精选.json 的核心、备选标到一份站点副本上（不经过 build_data.py）。
用法：python3 apply_pick.py <仓库 site 目录> <精选.json> <输出站点目录> <index.html>"""
import json
import shutil
import sys
from pathlib import Path

src, pick_f, out, index = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
out.mkdir(parents=True, exist_ok=True)
for f in ("cards.json", "blocks.json"):
    shutil.copyfile(src / f, out / f)
shutil.copyfile(index, out / "index.html")
qs = json.loads((src / "questions.json").read_text(encoding="utf-8"))
pk = json.loads(pick_f.read_text(encoding="utf-8"))
by = {q["id"]: q for q in qs}
for q in qs:
    q.pop("t", None); q.pop("o", None)
for i, qid in enumerate(pk["order"]):
    by[qid]["o"] = i
    by[qid]["t"] = 1 if i < pk["core"] else 2
(out / "questions.json").write_text(json.dumps(qs, ensure_ascii=False), encoding="utf-8")
meta = json.loads((src / "meta.json").read_text(encoding="utf-8"))
meta["plan"] = {"core": pk["core"], "backup": len(pk["order"]) - pk["core"], "generated": pk.get("generated", ""), "basis": pk.get("basis") or ["（草稿）"],
                "modules": pk.get("modules") or [], "note": pk.get("note") or ""}
(out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
print("site ready:", out, "core", pk["core"], "backup", len(pk["order"]) - pk["core"])
