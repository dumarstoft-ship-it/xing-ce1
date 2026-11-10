"""Cluster GD2013-2016 verbal questions across papers; list free passage-reading clusters."""
import json, re, sys, os, collections, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import classify
from pool2 import norm, split_body, grams, cluster
IDX='/home/user/work/index'
def taken_map():
    claims=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
    taken={}
    for c in claims:
        for k in [c['key']]+c.get('dups',[]): taken.setdefault(k.replace('_xc',''), c['owner'])
    return taken
RANGES={'GD20131':(16,45),'GD20133':(16,45),'GD2014X':(11,40),'GD2014Z':(21,55),'GD2015X':(1,20),'GD2015Z':(1,20),'GD2016X':(16,35),'GD2016Z':(1,15)}
def rows():
    taken=taken_map(); out=[]
    for tag,(a,b) in RANGES.items():
        for q in json.load(open(f'{IDX}/{tag}.json')):
            if q['kind']!='q' or not (a<=q['qno']<=b): continue
            k,p=classify(q['text']); body,opts=split_body(q['text'])
            nb=norm(body.replace(p,'')) if p else norm(body)
            out.append(dict(tag=tag,pid=tag,qno=q['qno'],key=f"{tag}-{q['qno']}",type=k,prompt=p,nb=nb,g=grams(nb),taken=taken.get(f"{tag}-{q['qno']}"),text=q['text'],file=q['file'],segs=q['segs'],pz=False,ans=None))
    return out
if __name__=='__main__':
    R=rows(); cl=cluster(R,0.5)
    out=[]
    for c in cl:
        c=sorted(c,key=lambda r:r['key'])
        out.append(dict(members=[r['key'] for r in c], types=[r['type'] for r in c], taken=sorted({r['taken'] for r in c if r['taken']}), text=c[0]['text'], nb=c[0]['nb'], prompts=[r['prompt'] for r in c]))
    json.dump(out, open('gd_old_clusters.json','w'), ensure_ascii=False, indent=0)
    XC={'XC','TK'}
    n=0
    for o in out:
        t=re.sub(r'\s+','',o['text'])
        isxc = ('____' in t or re.search(r'[（(]\s*[)）]',t[:len(t)//1]) ) and re.search(r'填入', t)
        if o['taken']: continue
        if isxc: continue
        n+=1
        m=re.search(r'A[、\.．]',t); body=t[:m.start()] if m else t; opts=t[m.start():] if m else ''
        print(f"## {','.join(o['members'])} {o['types']}")
        print('   ', body[:130],'…',body[-30:],'||',opts[:150])
    print(n)
