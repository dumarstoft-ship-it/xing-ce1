import json, os, re, glob, collections, sys
IDX='/home/user/work/index'
claims=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
taken={}
for c in claims:
    for k in [c['key']]+c.get('dups',[]):
        taken.setdefault(k,c['owner'])
GRAPH = re.compile(r'问号处|规律性|分为两类|分成两类|纸盒|外表面|展开|折成|立体|截面|剖|视图|俯视|主视|左视|正视|后视|拼合|拼成|组成|正方体|六面体|多面体|旋转|圆柱|圆锥|小方块|小正方体|折叠|切割|切面|轴|穿|阴影部分|图形|下图|如图|左图|右图')
SPATIAL = re.compile(r'纸盒|外表面|展开|折成|立体|截面|剖|视图|俯视|主视|左视|正视|后视|正方体|六面体|多面体|旋转|圆柱|圆锥|小方块|小正方体|切割|切面|轴|三维|空间|零件|长方体|四面体|棱')
PLANAR_STEM = re.compile(r'问号处|规律性|分为两类|分成两类|分为三类')
rows=[]
for f in sorted(glob.glob(IDX+'/*.json')):
    tag=os.path.basename(f)[:-5]
    for q in json.load(open(f)):
        if q['kind']!='q': continue
        t=q['text'].replace('\n','')
        if q.get('section') not in ('判断',None): continue
        if not q['images'] and not re.search(r'问号处|规律性|纸盒|外表面|截面|视图',t): continue
        if not GRAPH.search(t): continue
        sp = bool(SPATIAL.search(t))
        pl = bool(PLANAR_STEM.search(t))
        typ = 'S' if sp and not pl else ('P' if pl and not sp else ('PS?' if sp and pl else 'other'))
        pid=q['pid']
        key=f"{pid}-{q['qno']}"
        rows.append(dict(tag=tag,pid=pid,qno=q['qno'],typ=typ,n_img=len(q['images']),taken=taken.get(key),text=t[:90]))
json.dump(rows,open('inv.json','w'),ensure_ascii=False)
c=collections.Counter((r['tag'],r['typ']) for r in rows)
bytag=collections.defaultdict(dict)
for (t,ty),n in c.items(): bytag[t][ty]=n
for t in sorted(bytag): print(t, bytag[t])
