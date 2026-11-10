import json,collections,re,os,sys
W='/home/user/work'
qi=[json.loads(l) for l in open(f'{W}/qindex.jsonl')]
claims=[json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
taken={}
for c in claims:
    for k in [c['key']]+c.get('dups',[]):
        taken.setdefault(k,c['owner'])
grp=collections.defaultdict(list)
for r in qi:
    if r.get('dup_group'): grp[r['dup_group']].append(f"{r['pid']}-{r['qno']}")
key2grp={f"{r['pid']}-{r['qno']}":r.get('dup_group') for r in qi}
def taken_any(k):
    g=key2grp.get(k)
    ks=set(grp[g]) if g else {k}
    ks.add(k)
    for x in ks:
        if x in taken: return taken[x]+'('+x+')'
    return None
def in_scope(pid):
    m=re.match(r'([A-Z]+)(20\d\d)(.*)',pid)
    if not m: return False
    p,y,v=m.group(1),int(m.group(2)),m.group(3)
    if p=='GD': return y<=2023
    if p=='GDXD': return True
    if p=='GK': return 2013<=y<=2025
    if p in('JS','ZJ','ZJXD','SD','SC','HB','SZ'): return y>=2015
    return False
texts={}
for fn in sorted(os.listdir(f'{W}/index')):
    tag=fn[:-5]
    for q in json.load(open(f'{W}/index/{fn}')):
        if q.get('kind')=='q':
            texts.setdefault((q['pid'].replace('_xc',''),q['qno']),[]).append((tag,q['text']))
def prompt_of(t):
    tt=t.replace('\n','')
    m=re.search(r'A[\.．、]',tt)
    pre=tt[:m.start()] if m else tt
    # last sentence
    seg=re.split(r'[。！？]',pre)
    last=seg[-1] if seg[-1].strip() else (seg[-2] if len(seg)>1 else pre)
    return pre, last[-80:]
out=[]
for r in qi:
    if r['section']!='判断': continue
    if not in_scope(r['pid']): continue
    t=texts.get((r['pid'],r['qno']),[(None,'')])[0][1]
    pre,last=prompt_of(t)
    L=re.sub(r'\s','',last)
    typ='其他'
    if re.search(r'相似|类似|最为一致|相同|推理形式|论证方式|论证方法|论证手法|逻辑错误|谬误|论证结构',L): typ='结构'
    elif re.search(r'缺陷|漏洞|错误|不当|问题在于|论证.*?(存在|犯)',L): typ='缺陷'
    elif re.search(r'解释|调和|说明.{0,8}(现象|矛盾|差异|原因)',L): typ='解释'
    elif re.search(r'削弱|质疑|反驳|反对|否定|动摇|不能支持|无法支持|难以支持',L) and not re.search(r'除了|除外|除哪项',L): typ='削弱'
    elif re.search(r'削弱|质疑|反驳|反对|不能支持|无法支持|难以支持',L): typ='削弱/选非'
    elif re.search(r'加强|支持|证明|佐证|证实',L): typ='加强' if not re.search(r'除|不能|无法|没有',L) else '加强/选非'
    elif re.search(r'前提|假设|假定|必须补充|补充|成立.{0,6}需要|依赖',L): typ='前提'
    elif re.search(r'推出|得出|结论|推断|可知|一定为真|必然|可以确定|能够确定',L): typ='推出'
    k=f"{r['pid']}-{r['qno']}"
    out.append(dict(key=k,pid=r['pid'],qno=r['qno'],typ=typ,prompt=L,ans=r.get('answer'),rate=r.get('rate'),yicuo=r.get('yicuo'),taken=taken_any(k),dupsize=r.get('dup_size'),n=len(pre)))
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False)
cnt=collections.Counter((o['typ'],o['taken'] is None) for o in out)
for k in sorted(cnt): print(k,cnt[k])
