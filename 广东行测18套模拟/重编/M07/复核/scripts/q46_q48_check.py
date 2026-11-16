# Q46 / Q48 rule checks on the grids extracted by q46_grid.py / q48_grid.py
# Q46: black cells as row-major indices 0..15; rule: whole pattern advances +1 (wrap 15->0)
def idx(g): return sorted(r*4+c for r in range(4) for c in range(4) if g[r][c]=='#')
P=[['#..#','...#','..#.','.#..'],['.#..','#...','#..#','..#.'],['..#.','.#..','.#..','#..#'],
   ['#..#','..#.','..#.','.#..'],['.#..','#..#','...#','..#.']]
O={'A':['..#.','##..','#...','...#'],'B':['...#','..#.','#...','#..#'],
   'C':['..#.','.#..','#...','#..#'],'D':['...#','#.#.','#...','.#..']}
seq=[idx(g) for g in P]
print('Q46 sequence',seq)
ok=all(sorted((i+1)%16 for i in seq[k])==seq[k+1] for k in range(4))
pred=sorted((i+1)%16 for i in seq[-1])
print('shift+1 holds for all steps:',ok,' predicted',pred)
for k,g in O.items(): print('  ',k,idx(g),'<- match' if idx(g)==pred else '')
