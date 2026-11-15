# brute-force search: expressions over the three known cells (+ small constants) that fit circles 1-3
from itertools import permutations, product
from fractions import Fraction as F
circles = [(25,3,7,-4),(14,8,6,34),(51,9,4,-15)]
target = (22,8,7)
ops = ['+','-','*','/']
def ap(x,op,y):
    if op=='+': return x+y
    if op=='-': return x-y
    if op=='*': return x*y
    if op=='/': return None if y==0 else F(x)/F(y)
def evals(vals):
    # all binary trees over 3 values in given order, plus unary squares on leaves
    a,b,c = vals
    res = []
    for o1,o2 in product(ops,ops):
        # (a o1 b) o2 c
        t = ap(a,o1,b)
        if t is not None:
            r = ap(t,o2,c)
            if r is not None: res.append((f'(({{0}}{o1}{{1}}){o2}{{2}})', r))
        t = ap(b,o2,c)
        if t is not None:
            r = ap(a,o1,t)
            if r is not None: res.append((f'({{0}}{o1}({{1}}{o2}{{2}}))', r))
    return res
names = ['TL','TR','BL']
found = {}
for perm in permutations(range(3)):
    for sq in product([1,2],[1,2],[1,2]):
        def tf(v):
            return tuple(v[perm[i]]**sq[i] for i in range(3))
        exprs_per_circle = [dict() for _ in circles]
        for k,(a,b,c,d) in enumerate(circles):
            for e,r in evals(tf((a,b,c))):
                exprs_per_circle[k].setdefault(e,r)
        # check expression fits d (allow d = expr + const with const consistent)
        for e in exprs_per_circle[0]:
            rs = [exprs_per_circle[k].get(e) for k in range(3)]
            if any(r is None for r in rs): continue
            diffs = [circles[k][3]-rs[k] for k in range(3)]
            if diffs[0]==diffs[1]==diffs[2]:
                tv = [x for x in evals(tf(target)) if x[0]==e]
                if tv:
                    val = tv[0][1] + diffs[0]
                    label = e.format(*[names[perm[i]]+('^2' if sq[i]==2 else '') for i in range(3)]) + (f'+{diffs[0]}' if diffs[0] else '')
                    found[label]=val
for k,v in found.items(): print(k, '=>', v)
