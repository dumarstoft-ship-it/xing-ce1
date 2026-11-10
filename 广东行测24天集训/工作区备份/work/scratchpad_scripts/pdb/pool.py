import json, re, glob, os, collections
IDX='/home/user/work/index'; ANS='/home/user/work/answers'
def inrange(pid):
    m=re.match(r'([A-Z]+?)(20\d\d)',pid)
    if not m: return False
    p,y=m.group(1),int(m.group(2))
    if p=='GD': return y>=2017
    if p=='GDXD': return True
    if p=='GK': return y>=2017
    return y>=2020
qi={}
for l in open('/home/user/work/qindex.jsonl'):
    r=json.loads(l); qi[(r['tag'],r['qno'])]=r
tags=sorted(os.path.basename(f)[:-5] for f in glob.glob(IDX+'/*.json'))
use={}
for t in tags:
    pid=t.replace('_xc','')
    if not inrange(pid): continue
    if pid in use and not use[pid].endswith('_xc'): continue
    use[pid]=t
STEM=[
 ('不能削弱', r'(不能|无法|不能够|最不能)\s*(削弱|质疑|反驳|弱化)|除.{0,6}外.{0,20}(削弱|质疑|反驳)'),
 ('削弱', r'削弱|质疑|反驳|弱化|否定上述|驳斥|动摇'),
 ('不能加强', r'(不能|无法|最不能)\s*(支持|加强|证明|强化)|除.{0,6}外.{0,20}(支持|加强)'),
 ('加强', r'支持|加强|证明|强化|佐证|论据'),
 ('前提', r'前提|假设|必须补充|需要补充|需补充|必需补充|暗含|隐含|补充'),
 ('不能解释', r'(不能|无法|最不能|不可能)\s*解释|除.{0,6}外.{0,20}解释'),
 ('解释', r'解释'),
 ('相似', r'(最为|最|)相似|类似|相同|一致'),
 ('评价', r'逻辑错误|漏洞|缺陷|错误在于|评价|最需要|最关心|论证方式|论证方法|论证手法|论证技巧|推理方式|谬误|问题在于|最重要的|论证结构'),
 ('推出', r'推出|得出|推断|结论|可知|必然|一定|正确的是|错误的是|不可能'),
]
def classify(text):
    # stem = text between first line after qno and first option 'A.'
    t=text.replace('\n','')
    m=re.search(r'A[\.．、]',t)
    body=t[:m.start()] if m else t
    # question sentence = last sentence fragment before options
    q=re.split(r'[。]',body)
    stem=q[-1] if q[-1].strip() else (q[-2] if len(q)>1 else body)
    stem=stem[-60:]
    for name,pat in STEM:
        if re.search(pat,stem): return name,stem
    return '?',stem
out=[]
for pid,t in sorted(use.items()):
    d=json.load(open(f'{IDX}/{t}.json'))
    for q in d:
        if q['kind']!='q': continue
        if q['section'] not in ('判断',None): continue
        txt=q['text']
        if len(txt)<60: continue
        typ,stem=classify(txt)
        r=qi.get((t,q['qno']),{})
        out.append(dict(pid=pid,tag=t,qno=q['qno'],typ=typ,stem=stem,nimg=len(q['images']),len=len(txt),
            ans=r.get('answer'),rate=r.get('rate'),yicuo=r.get('yicuo'),dup=r.get('dup_group'),dupn=r.get('dup_size'),text=txt,file=q['file'],segs=q['segs']))
json.dump(out,open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pdb/pool.json','w'),ensure_ascii=False)
c=collections.Counter(o['typ'] for o in out)
print(len(out),c)
