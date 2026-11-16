"""Q52 and Q63 (翻译推理): enumerate all truth assignments of the premises and test
which options are entailed (true in every model of the premises)."""
from itertools import product

imp = lambda a, b: (not a) or b


def check(name, vars_, premises, options):
    models = [dict(zip(vars_, v)) for v in product([False, True], repeat=len(vars_))]
    models = [m for m in models if all(p(m) for p in premises)]
    print(f'{name}: {len(models)} models satisfy the premises')
    for k, f in options.items():
        ok = all(f(m) for m in models)
        print(f'  option {k}: {"entailed" if ok else "NOT entailed"}')


# Q52  Q=建设现代化强国  Z=科技自立自强  R=强化科技创新和产业创新深度融合  J=抓住发展机遇
#      Y=发挥好自身优势  K=把科技创新这篇文章做好
# 关键在于: Q -> Z ;  "不断强化…融合，才能抓住机遇": J -> R ; the rest is exhortation, no conditional
check('Q52', ['Q', 'Z', 'R', 'J', 'Y', 'K'],
      [lambda m: imp(m['Q'], m['Z']), lambda m: imp(m['J'], m['R'])],
      {'A (R -> Y)': lambda m: imp(m['R'], m['Y']),
       'B (Y -> K)': lambda m: imp(m['Y'], m['K']),
       'C (not Z -> not Q)': lambda m: imp(not m['Z'], not m['Q']),
       'D (not J -> not R)': lambda m: imp(not m['J'], not m['R'])})

# Q63  W=稳住企业  E=就业有支撑  M=民生有依托  P=稳企业政策落地显效  Y=小微企业有余力规划  S=市场经济更好运行
# "稳住了企业，就业才有支撑，民生才有依托": E -> W, M -> W
# "只有P，才Y": Y -> P ;  "除非Y，否则不S": S -> Y
check('Q63', ['W', 'E', 'M', 'P', 'Y', 'S'],
      [lambda m: imp(m['E'], m['W']), lambda m: imp(m['M'], m['W']),
       lambda m: imp(m['Y'], m['P']), lambda m: imp(m['S'], m['Y'])],
      {'A (S -> P, P是S的前提)': lambda m: imp(m['S'], m['P']),
       'B (W -> E or M)': lambda m: imp(m['W'], m['E'] or m['M']),
       'C (P -> Y)': lambda m: imp(m['P'], m['Y']),
       'D (not M -> not E)': lambda m: imp(not m['M'], not m['E'])})
