from itertools import permutations
deps = ["生产","销售","研发","人事","财务","法务"]
for strict in (True, False):
    sols=[]
    for p in permutations(range(1,7)):
        d = dict(zip(deps,p))
        if d["销售"]!=1: continue
        if not (d["销售"]<d["财务"] and d["销售"]<d["生产"]): continue
        if not (d["人事"]==d["研发"]+1 or d["人事"]==d["生产"]+1): continue
        after = [k for k,v in d.items() if v==d["法务"]+1]
        if after:
            if after[0] not in ("研发","销售"): continue
        elif strict: continue
        sols.append(d)
    print("strict" if strict else "vacuous(法务可在末位)", "#sol", len(sols))
    for k,(dep,b) in {"A 财务癸":("财务",6),"B 研发己":("研发",2),"C 法务辛":("法务",4),"D 人事庚":("人事",3)}.items():
        ex = [s for s in sols if s[dep]==b]
        print("   ", k, "可能" if ex else "不可能", (sorted(ex[0],key=ex[0].get) if ex else ""))
