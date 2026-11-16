"""Q56: 从A-F六种商品中选4种; (1)选A则不选B; (2)C、E被选情况相同. 枚举全部选法."""
from itertools import combinations
ok=[]
for s in combinations('ABCDEF',4):
    s=set(s)
    if 'A' in s and 'B' in s: continue
    if ('C' in s)!=('E' in s): continue
    ok.append(''.join(sorted(s)))
print(len(ok), ok)
