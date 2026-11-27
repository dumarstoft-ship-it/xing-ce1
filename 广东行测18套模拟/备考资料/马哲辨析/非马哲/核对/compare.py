"""对照政常新题出题人答案与核对人盲做结果，列出不一致和有疑点的题。用法：python3 compare.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
key = {}
for f in sorted((HERE.parent / "新题").glob("F*.json")):
    for q in json.loads(f.read_text(encoding="utf-8")):
        ans = q["answer"] if q["type"] == "判断" else "".join("ABCDEF"[i] for i, o in enumerate(q["options"]) if o["correct"])
        key[q["id"]] = (f.stem, q["type"], ans, q.get("review") or "")
checks = {}
for f in sorted(HERE.glob("check_*_F*.json")):
    who = f.stem.split("_")[1]
    for r in json.loads(f.read_text(encoding="utf-8")):
        checks.setdefault(r["id"], []).append((who, r))
missing = [i for i in key if i not in checks]
print(f"新题{len(key)}道，已核对{len(checks)}道，未核对{len(missing)}道", missing[:12] if missing else "")
ok = 0
for i, (w, t, ans, rv) in key.items():
    rs = checks.get(i, [])
    bad = [(who, r) for who, r in rs if str(r.get("answer")).strip() != ans]
    doubt = [(who, r) for who, r in rs if (r.get("doubt") or "").strip()]
    if not bad and not doubt and not rv:
        ok += 1
        continue
    print(f"\n=== {i}（{w}，{t}）出题人答案 {ans}" + (f"；出题人标待审：{rv}" if rv else "") + "；核对：" + "；".join(f"{who}={r.get('answer')}（{r.get('confidence')}）" for who, r in rs))
    for who, r in bad:
        print(f"  [{who}不一致] {r.get('reason')}")
    for who, r in doubt:
        print(f"  [{who}疑点] {r.get('doubt')}")
print(f"\n一致且无疑点：{ok}道")
