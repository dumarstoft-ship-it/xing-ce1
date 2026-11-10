from itertools import permutations, product

print("== V11 单排座位 (positions 1..6 left->right)")
names = ["教育","住建","交通","农业","人社","财政"]
sols = []
for p in permutations(range(1,7)):
    pos = dict(zip(names,p))
    if pos["财政"] != pos["人社"]+1: continue           # 财政在人社右边且相邻
    if not (pos["住建"] > pos["财政"]+1): continue        # 财政在住建左边且不相邻
    if abs(pos["教育"]-pos["交通"]) != 2: continue        # 教育与交通之间隔一个
    if abs(pos["农业"]-pos["财政"]) != 1: continue        # 附加条件 农业与财政相邻
    sols.append(pos)
for s in sols: print("  ", sorted(s, key=s.get))
opts = {"A 教育 从右第3(=左4)": lambda s: s["教育"]==4,
        "B 住建 从右第2(=左5)": lambda s: s["住建"]==5,
        "C 交通 从左第3":       lambda s: s["交通"]==3,
        "D 人社 从左第2":       lambda s: s["人社"]==2}
for k,f in opts.items(): print("  ", k, "必然" if all(f(s) for s in sols) else ("可能" if any(f(s) for s in sols) else "不可能"))

print("== V13 两维匹配")
roles = ["教硕","教学","哲硕","哲学"]
subj = {"教硕":"教","教学":"教","哲硕":"哲","哲学":"哲"}
for p in permutations(roles):
    a = dict(zip("甲乙丙丁",p))
    if a["甲"] in ("教硕","哲学"): continue
    if subj[a["甲"]] != subj[a["丙"]]: continue
    if a["乙"] not in ("教学","哲学"): continue
    if subj[a["丁"]] == "哲": continue
    print("  ", a)

print("== V14 真假推理")
for C,L,W in product([0,1],repeat=3):
    preds = [C and L, not (C and L), C and not L, (not C) and L, (not C) or W]
    if sum(bool(x) for x in preds)==1:
        print(f"  小陈={C} 小李={L} 小刘={W}  truth={[int(bool(x)) for x in preds]}")

print("== V15 排序 (销售在戊=1)")
deps = ["生产","销售","研发","人事","财务","法务"]
sols=[]
for p in permutations(range(1,7)):
    d = dict(zip(deps,p))
    if d["销售"]!=1: continue
    if not (d["销售"]<d["财务"] and d["销售"]<d["生产"]): continue
    if not (d["人事"]==d["研发"]+1 or d["人事"]==d["生产"]+1): continue
    after = [k for k,v in d.items() if v==d["法务"]+1]
    if not after or after[0] not in ("研发","销售"): continue
    sols.append(d)
print("  #solutions", len(sols))
bld = {1:"戊",2:"己",3:"庚",4:"辛",5:"壬",6:"癸"}
for k,(dep,b) in {"A 财务癸":("财务",6),"B 研发己":("研发",2),"C 法务辛":("法务",4),"D 人事庚":("人事",3)}.items():
    ex = [s for s in sols if s[dep]==b]
    print("  ", k, "可能" if ex else "不可能", (sorted(ex[0],key=ex[0].get) if ex else ""))

print("== V12 羽∧体→登")
def imp(a,b): return (not a) or b
checks = {
 "A 羽∧登→体": lambda y,t,d: imp(y and d, t),
 "B 体∧登→羽": lambda y,t,d: imp(t and d, y),
 "C ¬羽∧¬登→¬体": lambda y,t,d: imp((not y) and (not d), not t),
 "C' ¬(羽∧登)→¬体": lambda y,t,d: imp(not (y and d), not t),
 "D 羽∧¬登→¬体": lambda y,t,d: imp(y and not d, not t),
}
for k,f in checks.items():
    valid = all(f(y,t,d) for y,t,d in product([0,1],repeat=3) if imp(y and t, d))
    print("  ", k, "必然" if valid else "不必然")

print("== V16 捕鱼")
# vars: J=禁止, K=枯竭, Z=生涯终结, X=良性循环, S=收入保障
ok = lambda J,K,Z,X,S: imp(not J, K) and imp(K, Z) and imp(S, X)
checks = {
 "A ¬枯竭→保障": lambda J,K,Z,X,S: imp(not K, S),
 "B 禁止→保障":  lambda J,K,Z,X,S: imp(J, S),
 "C ¬终结→禁止": lambda J,K,Z,X,S: imp(not Z, J),
 "D ¬保障→¬良性": lambda J,K,Z,X,S: imp(not S, not X),
}
for k,f in checks.items():
    valid = all(f(*v) for v in product([0,1],repeat=5) if ok(*v))
    print("  ", k, "必然" if valid else "不必然")

print("== V07 结构核对 (A→B 前提)")
forms = {"题干 ¬B→¬A":(lambda a,b: imp(not b, not a)),
         "B ¬B→¬A":(lambda a,b: imp(not b, not a)),
         "C ¬A→¬B":(lambda a,b: imp(not a, not b)),
         "D B→A":(lambda a,b: imp(b, a))}
for k,f in forms.items():
    print("  ", k, "有效" if all(f(a,b) for a,b in product([0,1],repeat=2) if imp(a,b)) else "无效")
