import json, collections
H=json.load(open('hashes32.json'))
def pid(t): return t.replace('_xc','')
items=[]
for r in H:
    for h in r['hs']: items.append((r['tag'],r['qno'],h['h'],h['ar']))
best={}
for i in range(len(items)):
    for j in range(i+1,len(items)):
        a,b=items[i],items[j]
        if pid(a[0])==pid(b[0]): continue
        if abs(a[3]-b[3])>0.2*max(a[3],b[3]): continue
        d=bin(a[2]^b[2]).count('1')
        k=tuple(sorted([(pid(a[0]),a[1]),(pid(b[0]),b[1])]))
        if d<best.get(k,9999): best[k]=d
pairs=sorted([(d,k) for k,d in best.items() if d<=260])
json.dump([[d,[list(x) for x in k]] for d,k in pairs],open('pairs32.json','w'))
import sys
for d,k in pairs: print(d, f'{k[0][0]}-{k[0][1]}', f'{k[1][0]}-{k[1][1]}')
