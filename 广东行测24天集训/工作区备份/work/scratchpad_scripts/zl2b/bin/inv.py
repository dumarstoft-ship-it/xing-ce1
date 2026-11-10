import json, os, re, glob, collections, sys
IDX='/home/user/work/index'
def claims():
    taken={}
    for l in open('/home/user/work/out/claims.jsonl'):
        if not l.strip(): continue
        c=json.loads(l)
        for k in [c['key']]+c.get('dups',[]):
            taken.setdefault(k,c['owner'])
    return taken
def inscope(tag):
    t=tag.replace('_xc','')
    m=re.match(r'([A-Z]+?)(20\d\d)(.*)',t)
    if not m: return False
    p,y,v=m.group(1),int(m.group(2)),m.group(3)
    if p=='GK': return 2017<=y<=2025
    if p=='GD': return 2017<=y<=2023
    if p=='GDXD': return True
    return 2020<=y<=2026
if __name__=='__main__':
    tk=claims()
    out=[]
    for f in sorted(glob.glob(IDX+'/*.json')):
        tag=os.path.basename(f)[:-5]
        if not inscope(tag) and '--all' not in sys.argv: continue
        d=json.load(open(f))
        mats=[x for x in d if x['kind']=='material']
        qs=[x for x in d if x['kind']=='q']
        for m in mats:
            mq=[q for q in qs if q.get('material')==m['mid']]
            pid=tag.replace('_xc','') if not tag.startswith('GK2022F_xc') else tag
            n=re.search(r'-M(\d+)$',m['mid']).group(1)
            mid=f"ZLM-{pid}-{n}"
            txt=re.sub(r'\s+','',m['text'])
            qinfo=[]
            for q in mq:
                key=f"{pid}-{q['qno']}"
                qinfo.append((q['qno'], tk.get(key,'-'), re.sub(r'\s+','',q['text'])[:40]))
            out.append(dict(tag=tag,mid=mid,len=len(txt),img=len(m['images']),mat_owner=tk.get('MAT:'+mid,'-'),qs=qinfo))
    json.dump(out,open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2b/inv.json','w'),ensure_ascii=False)
    for o in out:
        free=sum(1 for q in o['qs'] if q[1]=='-')
        print(f"{o['tag']:12s} {o['mid']:22s} len={o['len']:5d} img={o['img']:2d} mat={o['mat_owner']:6s} free={free}/{len(o['qs'])}")
