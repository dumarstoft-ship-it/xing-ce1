from itertools import product, combinations
from collections import Counter
cats = ["民","经","行","商","国"]
need = Counter({"民":5,"经":3,"行":3,"商":2,"国":1})
days = ["一","二","三","四","五","六","日"]
forbidden = [{"民","行"}, {"经","商"}]

def run(label, thursday_fixed=True, allow_same_cat_other_days=False, ignore_rule3=False, ignore_rule4=False):
    pairs = []
    for a, b in combinations(cats, 2):
        pairs.append((a, b))
    if allow_same_cat_other_days:
        pairs += [(c, c) for c in cats]
    def ok_pair(p):
        s = set(p)
        if not ignore_rule3 and s == {"民","行"}: return False
        if not ignore_rule4 and s == {"经","商"}: return False
        return True
    pairs = [p for p in pairs if ok_pair(p)]
    schedules = []
    other = [d for d in days if d != "四"]
    for combo in product(pairs, repeat=len(other)):
        sched = dict(zip(other, combo))
        sched["四"] = ("民","民")
        cnt = Counter()
        for d in days: cnt.update(sched[d])
        if cnt != need: continue
        if "国" not in sched["日"]: continue          # rule (2)
        if any("国" in sched[d] for d in days if d != "日"): continue
        schedules.append(sched)
    print(f"== {label}: {len(schedules)} valid schedules")
    cooccur = Counter()
    for s in schedules:
        seen = set()
        for d in days:
            a, b = s[d]
            if a != b: seen.add(frozenset((a, b)))
        for x in seen: cooccur[x] += 1
    allpairs = [frozenset(p) for p in combinations(cats, 2)]
    print("   pair -> #schedules in which the two categories share a day")
    for p in allpairs:
        print("    ", "-".join(sorted(p, key=cats.index)), cooccur[p])
    opts = {"A 经-国": {"经","国"}, "B 行-经": {"行","经"}, "C 行-商": {"行","商"}, "D 民-经": {"民","经"}}
    for k, v in opts.items():
        print(f"   {k}: {'不可能同天' if cooccur[frozenset(v)]==0 else '可以同天'}")
    if schedules:
        ex = schedules[0]; print("   example:", {d: ex[d] for d in days})
    return schedules

run("R06 standard reading")
