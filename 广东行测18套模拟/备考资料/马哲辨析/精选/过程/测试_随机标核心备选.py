"""测试副本里随机标出核心、备选（只在scratchpad里，用来测计划逻辑）。用法：python3 plan_samples.py <测试站点目录> [核心数] [备选数]"""
import json
import random
import sys

S = sys.argv[1].rstrip("/") + "/"
n1 = int(sys.argv[2]) if len(sys.argv) > 2 else 160
n2 = int(sys.argv[3]) if len(sys.argv) > 3 else 40
rnd = random.Random(7)
lines = [x for x in open(S + "questions.json", encoding="utf-8").read().splitlines()]
qs = [json.loads(x.strip().rstrip(",")) for x in lines if x.strip().startswith("{")]
ok = [q for q in qs if not q.get("hold") and not q.get("review")]
pick = rnd.sample(ok, n1 + n2)
for i, q in enumerate(pick):
    q["o"] = i
    q["t"] = 1 if i < n1 else 2
json.dump(qs, open(S + "questions.json", "w", encoding="utf-8"), ensure_ascii=False)
m = json.load(open(S + "meta.json", encoding="utf-8"))
m["plan"] = {"core": n1, "backup": n2, "generated": "测试", "basis": ["（测试数据）随机抽取，只用来检查计划逻辑。"],
             "modules": [{"name": "马哲", "share": "17%", "core": 40, "backup": 10, "total": 420}], "note": "测试"}
json.dump(m, open(S + "meta.json", "w", encoding="utf-8"), ensure_ascii=False)
print("plan samples:", n1, n2)
