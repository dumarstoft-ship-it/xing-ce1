"""image-level duplicate detection across pool. writes imgdup.json: key 'PID-QNO' -> list of other keys with near-identical embedded image"""
import json, sys, collections, numpy as np
H=json.load(open('imghash.json'))
keys=[]; vecs=[]; meta=[]
for k,hs in H.items():
    for i,h in enumerate(hs):
        if h['w']*h['hh']<8000: continue   # tiny icons
        keys.append(k); vecs.append(np.array([c=='1' for c in h['h']],bool)); meta.append(h)
V=np.array(vecs)
dup=collections.defaultdict(set)
for i in range(len(keys)):
    d=(V^V[i]).sum(1)
    for j in np.where(d<=22)[0]:
        if keys[j]!=keys[i]:
            # aspect check
            a=meta[i]['w']/meta[i]['hh']; b=meta[j]['w']/meta[j]['hh']
            if abs(a-b)/max(a,b)<0.12:
                dup[keys[i]].add((keys[j],int(d[j])))
out={}
for k,v in dup.items():
    tag,q=k.split('|'); pid=tag.replace('_xc','')
    best={}
    for kk,d in v:
        t2,q2=kk.split('|'); key2=f"{t2.replace('_xc','')}-{q2}"
        if key2==f'{pid}-{q}': continue
        best[key2]=min(best.get(key2,99),d)
    if best: out.setdefault(f'{pid}-{q}',{}).update(best)
json.dump(out,open('imgdup.json','w'),ensure_ascii=False,indent=0)
print(len(out))
if len(sys.argv)>1:
    for k in sys.argv[1:]: print(k, out.get(k))
