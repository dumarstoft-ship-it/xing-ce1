from itertools import product
def imp(p, q): return (not p) or q

opts = {
 "A 谋杀": lambda D,L: D=="谋杀",
 "B 自杀": lambda D,L: D=="自杀",
 "C 意外": lambda D,L: D=="意外",
 "D 李某杀了张某": lambda D,L: D=="谋杀" and L,   # L false => Li not involved => certainly not killer
}
for jia_includes_divorce in (False, True):
    for j2 in ("exactly-one-wrong", "at-least-one-wrong"):
        sols = []
        for D, L, R in product(["谋杀","自杀","意外"], [True, False], [True, False]):
            if not jia_includes_divorce and R is False:
                continue  # R irrelevant; avoid duplicates
            jia = imp(D=="谋杀", L) and (R if jia_includes_divorce else True)
            yi  = D in ("自杀","谋杀")
            same = (jia == yi)
            wrong = [not jia, not yi].count(True)
            j1 = imp(same, D=="意外")
            cond2 = (wrong == 1) if j2 == "exactly-one-wrong" else (wrong >= 1)
            j2ok = imp(cond2, D != "意外")
            if j1 and j2ok:
                sols.append((D, L, R, jia, yi))
        print(f"--- Jia includes divorce fact={jia_includes_divorce}, judgment(2) read as {j2}")
        for s in sols: print("   solution D=%s L(李某有干系)=%s R(闹离婚)=%s jia=%s yi=%s" % s)
        for k, f in opts.items():
            vals = {f(s[0], s[1]) for s in sols}
            print(f"   {k}: {'必真' if vals=={True} else ('必假' if vals=={False} else '可真可假')}")
