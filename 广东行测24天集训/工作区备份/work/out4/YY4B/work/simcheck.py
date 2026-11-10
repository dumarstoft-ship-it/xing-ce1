"""For each key given, find questions in ANY index (any section) whose passage text overlaps strongly
(4-gram containment) -> same-passage duplicates that dup_group may miss. Also report claim status."""
import json, os, re, sys, unicodedata, collections
IDX='/home/user/work/index'
def norm(s):
    s=unicodedata.normalize('NFKC', s)
    s=re.sub(r'本试卷由粉笔用户\S*?生成', '', s)
    s=re.sub(r'(免费获取更多考公资料|认准淘宝店铺|第\s*\d+\s*页[，,]?\s*共\s*\d+\s*页)', '', s)
    s=re.sub(r'[^一-鿿0-9A-Za-z%]', '', s)
    return s
def body(t):
    m=re.search(r'\n\s*A\s*[\.、．]', t)
    return t[:m.start()] if m else t
def grams(s,n=4): return {s[i:i+n] for i in range(max(0,len(s)-n+1))}
_all=None
def all_q():
    global _all
    if _all is not None: return _all
    _all=[]
    for f in sorted(os.listdir(IDX)):
        if not f.endswith('.json'): continue
        tag=f[:-5]
        for q in json.load(open(f'{IDX}/{f}')):
            if q['kind']!='q': continue
            nb=norm(re.sub(r'^\s*\d{1,3}\s*[、\.．]', '', body(q['text'])))
            _all.append((tag, q['qno'], q.get('section'), nb, grams(nb)))
    return _all
claims=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
taken={}
for c in claims:
    for k in [c['key']]+c.get('dups',[]): taken.setdefault(k.replace('_xc',''), c['owner'])
def sims(tag,qno,thr=0.45):
    A=all_q()
    me=[x for x in A if x[0]==tag and x[1]==qno]
    if not me: return None
    g=me[0][4]
    out=[]
    for (t,q,sec,nb,gg) in A:
        if t==tag and q==qno: continue
        if not gg or not g: continue
        inter=len(g&gg)
        if inter<20: continue
        c=inter/min(len(g),len(gg))
        if c>=thr: out.append((round(c,2), t, q, sec, inter))
    return sorted(out, reverse=True)
if __name__=='__main__':
    for key in sys.argv[1:]:
        tag,q=key.rsplit('-',1); q=int(q)
        r=sims(tag,q)
        pid=tag.replace('_xc','')
        print(f'{key}: claim={taken.get(f"{pid}-{q}","FREE")}', end=' | ')
        if r is None: print('NOT IN INDEX'); continue
        print('; '.join(f'{t}-{qq}[{sec}] c={c} n={n} {"TAKEN:"+taken[t.replace("_xc","")+"-"+str(qq)] if taken.get(t.replace("_xc","")+"-"+str(qq)) else ""}' for c,t,qq,sec,n in r) or 'no similar')
