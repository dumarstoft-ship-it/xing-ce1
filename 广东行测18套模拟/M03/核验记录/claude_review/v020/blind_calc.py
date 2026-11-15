from math import comb
from itertools import product
# Q43
p1, p2, n = 0.8, 0.4, 4
total = 0.0
detail = {}
for X in range(n+1):
    pX = comb(n, X) * p1**X * (1-p1)**(n-X)
    if X < n/2:  # retake cancelled
        pr = 1.0 if X == 3 else 0.0
    else:
        need = 3 - X
        f = n - X
        pr = comb(f, need) * p2**need * (1-p2)**(f-need) if 0 <= need <= f else 0.0
    detail[X] = (pX, pr, pX*pr)
    total += pX*pr
print('Q43 detail', detail)
print('Q43 total', total)
# brute force check
tot2 = 0.0
for first in product([0,1], repeat=4):
    pf = 1
    for f in first: pf *= p1 if f else (1-p1)
    X = sum(first)
    if X < 2:
        if X == 3: tot2 += pf
        continue
    fails = [i for i,f in enumerate(first) if not f]
    for re in product([0,1], repeat=len(fails)):
        pr = 1
        for r in re: pr *= p2 if r else (1-p2)
        if X + sum(re) == 3: tot2 += pf*pr
print('Q43 brute', tot2)
# distractor guesses
print('only X=3 case', detail[3][2])
print('X=2 w/o x2', 0.1536*0.4*0.6 + detail[3][2])
# Q35
circles = [(25,3,7,-4),(14,8,6,34),(51,9,4,-15),(22,8,7,None)]
for a,b,c,d in circles:
    print('Q35', a,b,c,d, 'b*c-a=', b*c-a)
# Q69
edges = [('茶树','茶毛虫'),('茶树','茶尺蠖'),('草','茶毛虫'),('草','茶尺蠖'),
         ('茶毛虫','蜘蛛'),('茶毛虫','蛙'),('茶尺蠖','蜘蛛'),('茶尺蠖','鸟'),
         ('蜘蛛','蛙'),('蛙','蛇'),('鸟','蛇')]
from collections import defaultdict
g = defaultdict(list)
nodes=set()
for a,b in edges: g[a].append(b); nodes|={a,b}
indeg = {x:0 for x in nodes}
for a,b in edges: indeg[b]+=1
prods=[x for x in nodes if indeg[x]==0]
chains=[]
def dfs(path):
    x=path[-1]
    if not g[x]: chains.append(path); return
    for y in g[x]: dfs(path+[y])
for p in prods: dfs([p])
for c in chains: print(len(c), '->'.join(c))
print('num chains', len(chains))
levels=defaultdict(set)
for c in chains:
    for i,x in enumerate(c): levels[x].add(i+1)
print(dict(levels))
