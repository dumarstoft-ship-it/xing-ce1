import json, re, os, collections, unicodedata
IDX='/home/user/work/index'
allowed=[]
for f in sorted(os.listdir(IDX)):
    tag=f[:-5]; pid=tag.replace('_xc','')
    m=re.match(r'([A-Z]+)(\d{4})(.*)',pid)
    prov,yr,var=m.group(1),int(m.group(2)),m.group(3)
    ok=False
    if prov=='GD' and 2017<=yr<=2023: ok=True
    if prov=='GDXD': ok=True
    if prov=='GK' and 2017<=yr<=2025: ok=True
    if prov in ('HB','JS','SC','SD','SZ','ZJ') and 2020<=yr<=2026: ok=True
    if ok: allowed.append(tag)
claims=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
taken=set()
for c in claims:
    taken.add(c['key']); taken.update(c.get('dups',[]))
qi={}
for l in open('/home/user/work/qindex.jsonl'):
    r=json.loads(l); qi[(r['tag'],r['qno'])]=r
KW=re.compile(r'削弱|质疑|反驳|加强|支持|前提|假设|解释|相似|缺陷|漏洞|评价|论证方式|论证方法|不能推出|能够推出|可以推出|推出|结论|调和|矛盾')
out=[]
for tag in allowed:
    d=json.load(open(f'{IDX}/{tag}.json'))
    for q in d:
        if q['kind']!='q': continue
        t=unicodedata.normalize('NFKC',q['text'])
        if q.get('section') not in ('判断','科学',None,'常识','未知') and not re.search(r'削弱|加强|前提|解释|质疑',t): continue
        if not KW.search(t): continue
        pid=tag.replace('_xc','')
        key=f"{pid}-{q['qno']}"
        r=qi.get((tag,q['qno']),{})
        out.append(dict(tag=tag,key=key,qno=q['qno'],sec=q.get('section'),taken=key in taken,dup=r.get('dup_group'),dupsize=r.get('dup_size'),ans=r.get('answer'),rate=r.get('rate'),yicuo=r.get('yicuo'),text=t))
json.dump(out,open('cands.json','w'),ensure_ascii=False)
print(len(out), sum(1 for o in out if not o['taken']))
print(collections.Counter(o['tag'] for o in out))
