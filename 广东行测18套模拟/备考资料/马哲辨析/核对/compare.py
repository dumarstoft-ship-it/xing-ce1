"""对照出题人答案与核对人盲做结果：列出不一致的题和核对人标了疑点的题。

用法：python3 compare.py
"""
import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
key = {}
for f in sorted((HERE.parent / "新题").glob("W*.json")):
    for q in json.loads(f.read_text(encoding="utf-8")):
        key[q["id"]] = (f.stem, q["type"], q["answer"])
checks = {}
for f in sorted(HERE.glob("check_C*_W*.json")):
    who = f.stem.split("_")[1]
    for r in json.loads(f.read_text(encoding="utf-8")):
        checks.setdefault(r["id"], []).append((who, r))
missing = [i for i in key if i not in checks]
print(f"新题{len(key)}道，已核对{len(checks)}道，未核对{len(missing)}道", missing[:10] if missing else "")
n_ok = 0
for i, (w, t, ans) in key.items():
    rs = checks.get(i, [])
    bad = [(who, r) for who, r in rs if str(r.get("answer")).strip() != ans]
    doubt = [(who, r) for who, r in rs if (r.get("doubt") or "").strip()]
    if not bad and not doubt:
        n_ok += 1
        continue
    print(f"\n=== {i}（{w}，{t}）出题人答案 {ans}；核对：" + "；".join(f"{who}={r.get('answer')}（{r.get('confidence')}）" for who, r in rs))
    for who, r in bad:
        print(f"  [{who}不一致] {r.get('reason')}")
    for who, r in doubt:
        print(f"  [{who}疑点] {r.get('doubt')}")
print(f"\n一致且无疑点：{n_ok}道")
