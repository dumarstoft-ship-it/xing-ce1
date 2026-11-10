import json,collections,re,os,sys
W='/home/user/work'
qi=[json.loads(l) for l in open(f'{W}/qindex.jsonl')]
claims=[json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
taken={}
for c in claims:
    for k in [c['key']]+c.get('dups',[]):
        taken.setdefault(k,c['owner'])
# dup groups
grp=collections.defaultdict(list)
for r in qi:
    if r.get('dup_group'): grp[r['dup_group']].append(f"{r['pid']}-{r['qno']}")
def is_taken(pid,qno):
    k=f'{pid}-{qno}'
    if k in taken: return taken[k]
    for r in qi:
        pass
    return None
key2grp={f"{r['pid']}-{r['qno']}":r.get('dup_group') for r in qi}
def taken_any(k):
    g=key2grp.get(k)
    ks=set(grp[g]) if g else {k}
    ks.add(k)
    for x in ks:
        if x in taken: return taken[x]+'('+x+')'
    return None
# scope
def in_scope(pid):
    m=re.match(r'([A-Z]+)(20\d\d)(.*)',pid)
    if not m: return False
    p,y,v=m.group(1),int(m.group(2)),m.group(3)
    if p=='GD': return y<=2023
    if p=='GDXD': return True
    if p=='GK': return 2013<=y<=2025
    if p in('JS','ZJ','ZJXD','SD','SC','HB','SZ'): return y>=2015
    return False
# load index texts
texts={}
for fn in os.listdir(f'{W}/index'):
    tag=fn[:-5]
    for q in json.load(open(f'{W}/index/{fn}')):
        if q.get('kind')=='q':
            texts.setdefault((q['pid'].replace('_xc',''),q['qno']),[]).append((tag,q['text']))
out=[]
for r in qi:
    if r['section']!='判断': continue
    if not in_scope(r['pid']): continue
    t=texts.get((r['pid'],r['qno']),[(None,'')])[0][1]
    tt=re.sub(r'\s','',t)
    typ=None
    if re.search(r'结构.{0,6}(相似|类似|一致|相同)|(相似|类似|一致|相同).{0,8}(推理|论证|结构|逻辑错误|谬误|错误)|与.{0,6}(题干|上述).{0,10}(最为|最|相)?(相似|类似)|推理形式|论证方式|论证方法',tt): typ='结构'
    elif re.search(r'削弱|质疑|反驳|反对|否定上述|不能支持|无法支持|动摇',tt): typ='削弱'
    elif re.search(r'加强|支持|证明|佐证',tt): typ='加强'
    elif re.search(r'前提|假设|假定|必须补充|补充.{0,4}(前提|条件)|成立.{0,6}需要',tt): typ='前提'
    elif re.search(r'解释|调和|说明.{0,6}(现象|矛盾)',tt): typ='解释'
    elif re.search(r'缺陷|漏洞|错误|谬误|不当',tt): typ='缺陷'
    elif re.search(r'推出|得出|结论|推断|可知',tt): typ='推出'
    else: typ='其他'
    k=f"{r['pid']}-{r['qno']}"
    out.append(dict(key=k,pid=r['pid'],qno=r['qno'],typ=typ,ans=r.get('answer'),rate=r.get('rate'),yicuo=r.get('yicuo'),taken=taken_any(k),dupsize=r.get('dup_size'),head=tt[:60],n=len(tt)))
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False)
cnt=collections.Counter((o['typ'],o['taken'] is None) for o in out)
print(cnt)
