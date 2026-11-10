import json, collections, re
H=json.load(open('hashes.json'))
def pid(t): return t.replace('_xc','')
items=[]
for r in H:
    for h in r['hs']: items.append((r['tag'],r['qno'],h['h'],h['ar']))
pairs=collections.defaultdict(lambda:99)
for i in range(len(items)):
    for j in range(i+1,len(items)):
        a,b=items[i],items[j]
        if pid(a[0])==pid(b[0]) : continue
        if abs(a[3]-b[3])>0.25*max(a[3],b[3]): continue
        d=bin(a[2]^b[2]).count('1')
        k=((a[0],a[1]),(b[0],b[1]))
        if d<pairs[k]: pairs[k]=d
close=[(k,d) for k,d in pairs.items() if d<=40]
# union find over question keys
parent={}
def f(x):
    parent.setdefault(x,x)
    while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
    return x
for (a,b),d in close: parent[f(a)]=f(b)
g=collections.defaultdict(set)
for x in list(parent): g[f(x)].add(x)
out=[]
for k,v in g.items():
    out.append(sorted(v))
json.dump(out,open('imgdups.json','w'))
# print groups with distinct pids (ignoring _xc twins)
n=0
for v in sorted(out):
    pids={pid(t) for t,q in v}
    if len(pids)>1:
        n+=1; print(' '.join(f'{t}-{q}' for t,q in v), ' d=', min(d for (a,b),d in close if a in v and b in v))
print('groups',n)
