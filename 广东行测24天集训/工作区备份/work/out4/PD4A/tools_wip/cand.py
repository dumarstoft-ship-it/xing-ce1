"""candidate list with claim status + image twins. usage: cand.py REGEX [all]"""
import json, sys, re, numpy as np, collections
sys.path.insert(0,'/home/user/work/out3/PD3A/tools'); sys.path.insert(0,'.')
import pool, mypool
z=np.load('imgsig.npz'); K=[str(k) for k in z['keys']]; S=z['sigs']
byk=collections.defaultdict(list)
for i,k in enumerate(K): byk[k].append(i)
def twins(tag,qno,thr=0.82):
    out={}
    for i in byk.get(f'{tag}|{qno}',[]):
        c=S@S[i]
        for j in np.where(c>=thr)[0]:
            t2,q2=K[j].split('|'); k2=f"{t2.replace('_xc','')}-{q2}"
            if k2==f"{tag.replace('_xc','')}-{qno}": continue
            out[k2]=max(out.get(k2,0),round(float(c[j]),2))
    return out
if __name__=='__main__':
    P=pool.pool(); flt=sys.argv[1]; showall=len(sys.argv)>2
    for p in P:
        if not re.search(flt,p['tag']): continue
        key=f"{p['pid']}-{p['qno']}"
        st,who=mypool.status(key)
        tw=twins(p['tag'],p['qno'])
        tws=[]
        for k2,c in sorted(tw.items()):
            s2,w2=mypool.status(k2)
            tws.append(f"{k2}({c},{s2}{':'+w2.split('<')[0] if s2!='FREE' else ''})")
        if st=='USED' and not showall: continue
        print(f"{p['tag']:11s}{p['qno']:4d} {'S' if p['space'] else 'P'} {str(p['ans'] or '-'):3s} {str(p['rate'] or '-'):4s} {st:4s} {who[:20]:20s} | {' '.join(tws)[:150]}")
