from itertools import product

def imp(p, q): return (not p) or q

def check(name, varnames, premises, options, goal=None):
    """For each option: valid iff true in all models of premises (goal=None),
    or, if goal given, premises+option entail goal (and option consistent)."""
    models = []
    for vals in product([True, False], repeat=len(varnames)):
        m = dict(zip(varnames, vals))
        if all(p(m) for p in premises):
            models.append(m)
    print(f"== {name}: {len(models)} models satisfy premises")
    for k, f in options.items():
        if goal is None:
            ok = all(f(m) for m in models)
            print(f"  {k}: {'VALID' if ok else 'not valid'}")
        else:
            sub = [m for m in models if f(m)]
            ok = len(sub) > 0 and all(goal(m) for m in sub)
            print(f"  {k}: consistent={len(sub)>0}, entails goal={ok}, "
                  f"goal values in sub-models={sorted(set(goal(m) for m in sub))}")

# R01: C=long-term closed, S=decline, J=exchange/mutual learning, Q=learn strengths, V=vitality
check("R01", ["C","S","J","Q","V"],
      [lambda m: imp(m["C"], m["S"]),
       lambda m: imp(m["V"], m["J"] and m["Q"])],
      {"A ~J->~V": lambda m: imp(not m["J"], not m["V"]),
       "B ~C->~S": lambda m: imp(not m["C"], not m["S"]),
       "C (J&Q)->V": lambda m: imp(m["J"] and m["Q"], m["V"]),
       "D ~V->~Q": lambda m: imp(not m["V"], not m["Q"])})
# R01 alt reading: treat "jiaoliu hujian, quchang buduan" as one atom X
check("R01-alt(single atom X)", ["C","S","X","V"],
      [lambda m: imp(m["C"], m["S"]), lambda m: imp(m["V"], m["X"])],
      {"A ~X->~V": lambda m: imp(not m["X"], not m["V"]),
       "B ~C->~S": lambda m: imp(not m["C"], not m["S"]),
       "C X->V": lambda m: imp(m["X"], m["V"]),
       "D ~V->~X": lambda m: imp(not m["V"], not m["X"])})

# R02: premise (Jia or not Yi) -> Bing ; goal: Yi
prem = [lambda m: imp(m["J"] or not m["Y"], m["B"])]
check("R02", ["J","Y","B"], prem,
      {"A ~B": lambda m: not m["B"],
       "B ~J": lambda m: not m["J"],
       "C J&B": lambda m: m["J"] and m["B"],
       "D(at least one of J,B false)": lambda m: (not m["J"]) or (not m["B"]),
       "D(exactly one of J,B false)": lambda m: (not m["J"]) != (not m["B"])},
      goal=lambda m: m["Y"])

# R03: P = company raises price, O = consumers choose other companies; premise P->O
check("R03 (II, III)", ["P","O"], [lambda m: imp(m["P"], m["O"])],
      {"II ~P->~O": lambda m: imp(not m["P"], not m["O"]),
       "III ~O->~P": lambda m: imp(not m["O"], not m["P"])})
