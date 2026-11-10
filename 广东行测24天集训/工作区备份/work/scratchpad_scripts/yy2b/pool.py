import json, re, sys, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import classify
IDX='/home/user/work/index'; ANS='/home/user/work/answers'
qi = {}
for l in open('/home/user/work/qindex.jsonl'):
    r = json.loads(l); qi[(r['tag'], r['qno'])] = r
claims = [json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
taken = {}
for c in claims:
    for k in [c['key']] + c.get('dups', []):
        taken.setdefault(k.replace('_xc',''), c['owner'])
def ans_of(tag, qno):
    p = f'{ANS}/{tag}.json'
    if not os.path.exists(p): return None
    a = json.load(open(p))['answers'].get(str(qno))
    return a
def pool(tags):
    out = []
    for tag in tags:
        if not os.path.exists(f'{IDX}/{tag}.json'): continue
        ix = json.load(open(f'{IDX}/{tag}.json'))
        mats = [m for m in ix if m['kind']=='material' and m.get('section')=='言语' and m.get('segs')]
        mstart = min(((m['segs'][0][0], m['segs'][0][1]) for m in mats), default=None)
        for q in ix:
            if q['kind']!='q' or q.get('section')!='言语': continue
            k, p = classify(q['text'])
            pos = (q['segs'][0][0], q['segs'][0][1])
            pz = bool(mstart and pos > mstart)
            pid = tag.replace('_xc','')
            r = qi.get((tag, q['qno']), {})
            a = ans_of(tag, q['qno']) or {}
            out.append(dict(tag=tag, pid=pid, qno=q['qno'], type=('PZ-'+k if pz else k), prompt=p, dup=r.get('dup_group'), dup_size=r.get('dup_size'),
                            ans=a.get('ans'), rate=a.get('rate'), yicuo=a.get('yicuo'), taken=taken.get(f'{pid}-{q["qno"]}'), text=q['text']))
    return out
if __name__=='__main__':
    tags = sys.argv[1:]
    for r in pool(tags):
        print(r['tag'], r['qno'], r['type'], r['dup'], r['dup_size'], r['ans'], r['rate'], r['taken'], '|', r['prompt'][:50])
