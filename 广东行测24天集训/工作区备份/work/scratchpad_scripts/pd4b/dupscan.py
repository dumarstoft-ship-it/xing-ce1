# find unlinked duplicates of selected keys across all index files by normalized stem substring
import json,os,re,sys
W='/home/user/work'
def norm(t):
    t=re.sub(r'^\s*\d+\s*[\.、．]?\s*','',t.strip())
    t=re.sub(r'（单选题）|\(单选题\)','',t)
    return re.sub(r'[^一-鿿]','',t)
allq=[]
for fn in sorted(os.listdir(f'{W}/index')):
    tag=fn[:-5]
    for q in json.load(open(f'{W}/index/{fn}')):
        if q.get('kind')=='q': allq.append((q['pid'].replace('_xc',''),q['qno'],norm(q['text'])))
keys=[l.strip() for f in sys.argv[1:] for l in open(f) if l.strip()]
for k in keys:
    pid,qn=k.rsplit('-',1); qn=int(qn)
    me=[x for x in allq if x[0]==pid and x[1]==qn]
    if not me: print(k,'NOT IN INDEX'); continue
    s=me[0][2]; frag=s[10:40]
    hits=sorted(set(f'{a}-{b}' for a,b,t in allq if frag and frag in t and not (a==pid and b==qn)))
    if hits: print(k,'~',hits)
