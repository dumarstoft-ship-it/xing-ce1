"""Pool of GD2013-2016 言语 questions (section labels unreliable -> take ranges by hand after viewing)."""
import json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import classify
IDX='/home/user/work/index'
claims=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
taken={}
for c in claims:
    for k in [c['key']]+c.get('dups',[]): taken.setdefault(k.replace('_xc',''), c['owner'])
RANGES={'GD20131':(16,45),'GD20133':(16,45),'GD2014X':(11,40),'GD2014Z':(21,55),'GD2015X':(1,20),'GD2015Z':(1,20),'GD2016X':(16,35),'GD2016Z':(1,15)}
if __name__=='__main__':
    for tag,(a,b) in RANGES.items():
        ix=json.load(open(f'{IDX}/{tag}.json'))
        print('=====',tag)
        for q in ix:
            if q['kind']!='q' or not (a<=q['qno']<=b): continue
            k,p=classify(q['text'])
            key=f"{tag}-{q['qno']}"
            print(q['qno'], q.get('section'), k, taken.get(key,'free'), 'p%d'%(q['segs'][0][0]+1), '|', p[:40], '|', re.sub(r'\s+',' ',q['text'])[:50])
