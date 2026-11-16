# Q51 truth-table check: which options follow validly from the premises.
# Vars: J=均衡营养配比, G=规律喂食频率, K=科学饮食结构, S=免疫系统功能衰退
from itertools import product
def imp(a,b): return (not a) or b
premises = lambda J,G,K,S: imp(not K, S) and imp(not (J and G), not K)
opts = {
 'A 只要J且G则不衰退': lambda J,G,K,S: imp(J and G, not S),
 'B 如果J且G则K':      lambda J,G,K,S: imp(J and G, K),
 'C 如果衰退则非K':    lambda J,G,K,S: imp(S, not K),
 'D 除非G否则衰退(非G->S)': lambda J,G,K,S: imp(not G, S),
}
models = [m for m in product([False,True],repeat=4) if premises(*m)]
print("premise models:", len(models))
for name,f in opts.items():
    valid = all(f(*m) for m in models)
    cex = [m for m in models if not f(*m)]
    print(f"{name}: valid={valid}; counterexample(J,G,K,S)={cex[:1]}")
