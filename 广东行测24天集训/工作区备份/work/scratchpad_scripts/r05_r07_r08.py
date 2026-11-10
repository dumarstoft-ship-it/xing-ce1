from itertools import permutations, product
def imp(p, q): return (not p) or q
def report(name, sols, opts):
    print(f"== {name}: {len(sols)} solutions")
    for s in sols: print("   ", s)
    for k, f in opts.items():
        vals = {f(s) for s in sols}
        print(f"   {k}: {'必真' if vals=={True} else ('必假' if vals=={False} else '可真可假')}")

# ---------- R05 ----------
people = ["甲","乙","丙","丁","戊"]; seats = ["A","B","C","D","F"]
sols = []
for p in permutations(seats):
    s = dict(zip(people, p))
    c1 = imp(s["甲"]=="C" or s["乙"]=="C", s["丙"]=="B")
    c2 = imp(s["戊"]=="C", s["丁"]=="F")
    if c1 and c2 and s["丁"]=="B":
        sols.append(s)
report("R05 (丁 in B)", sols, {
    "A 甲A": lambda s: s["甲"]=="A", "B 乙D": lambda s: s["乙"]=="D",
    "C 丙C": lambda s: s["丙"]=="C", "D 戊F": lambda s: s["戊"]=="F"})

# ---------- R07 ----------
fams = ["张","王","李","赵"]; ents = ["甲","乙","丙"]
def r07(min_per_ent):
    sols = []
    for choice in product(ents, repeat=4):
        f = dict(zip(fams, choice))
        cnt = {e: choice.count(e) for e in ents}
        # every family got the entrepreneur it chose => each entrepreneur keeps all who chose him, must be within limits
        if not all(min_per_ent <= cnt[e] <= 2 for e in ents): continue
        c1 = f["张"]=="甲" or f["王"]=="甲"
        c2 = [f["王"], f["李"], f["赵"]].count("乙") >= 2
        c3 = f["张"]=="丙" or f["李"]=="丙"
        if c1 and c2 and c3: sols.append(f)
    return sols
o7 = {"A 甲-张": lambda f: f["张"]=="甲", "B 乙-赵": lambda f: f["赵"]=="乙",
      "C 丙-李": lambda f: f["李"]=="丙", "D 甲-王": lambda f: f["王"]=="甲"}
report("R07 (each entrepreneur 1-2 families)", r07(1), o7)
report("R07 alt (entrepreneur may get 0, max 2)", r07(0), o7)

# ---------- R08 ----------
jobs = ["企业家","大学教师","歌手","会计师"]; P = ["甲","乙","丙","丁"]
def preds(a):
    return {"甲": a["乙"]!="歌手", "乙": a["丙"]=="会计师",
            "丙": a["丁"]!="企业家", "丁": a["乙"]!="大学教师"}
o8 = {"A": ("企业家","大学教师","歌手","会计师"), "B": ("大学教师","歌手","企业家","会计师"),
      "C": ("企业家","歌手","会计师","大学教师"), "D": ("会计师","大学教师","歌手","企业家")}
def r08(mode):
    sols = []
    for perm in permutations(jobs):
        a = dict(zip(P, perm)); pr = preds(a)
        acc = [x for x in P if a[x]=="会计师"][0]
        if mode == "strict":   # accountant's prediction true, all others false
            ok = pr[acc] and all(not pr[x] for x in P if x != acc)
        elif mode == "weak":   # only requires accountant's prediction true
            ok = pr[acc]
        elif mode == "about-accountant":  # only the prediction ABOUT the accountant (乙's) true
            ok = pr["乙"] and all(not pr[x] for x in P if x != "乙")
        if ok: sols.append(perm)
    return sols
for mode in ("strict", "weak", "about-accountant"):
    sols = r08(mode)
    print(f"== R08 mode={mode}: {len(sols)} solutions: {sols}")
    for k, v in o8.items():
        print(f"    option {k} {v}: {'matches a solution' if v in sols else '-'}")
