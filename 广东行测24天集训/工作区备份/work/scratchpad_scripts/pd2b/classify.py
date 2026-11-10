import json, re, collections
C=json.load(open('cands.json'))
def qline(t):
    # find the prompt sentence: the last sentence before option A
    s=t.split('A.')[0] if 'A.' in t else t
    return s[-120:]
def cat(t):
    p=qline(t)
    if re.search(r'相似|类似|一致|相同',p) and re.search(r'结构|推理|论证|逻辑|错误|方式|形式',p): return '结构'
    if re.search(r'缺陷|漏洞|错误|评价|论证方式|论证方法|论证手法|反驳方式|方法',p): return '缺陷/方法'
    if re.search(r'削弱|质疑|反驳|动摇|反对|驳斥|不成立',p): return '削弱'
    if re.search(r'解释|调和|矛盾|原因',p): return '解释'
    if re.search(r'前提|假设|必须|隐含|基于|预设',p): return '前提'
    if re.search(r'加强|支持|佐证|证明|论据|印证',p): return '加强'
    if re.search(r'推出|得出|结论|推断|说明|论断|可知',p): return '推出'
    return '其他'
seen={}
for c in C:
    c['cat']=cat(c['text'])
    c['prompt']=qline(c['text'])
# dedupe by dup group, prefer non-_xc
best={}
for c in C:
    g=c['dup'] or c['key']
    if g not in best or (best[g]['tag'].endswith('_xc') and not c['tag'].endswith('_xc')):
        best[g]=c
U=list(best.values())
json.dump(U,open('uniq.json','w'),ensure_ascii=False)
print(len(U))
cnt=collections.Counter((c['cat']) for c in U if not c['taken'])
print(cnt)
def grp(tag):
    p=tag.replace('_xc','')
    if p.startswith('GDXD'): return 'GDXD'
    if p.startswith('GD'): return 'GD'
    if p.startswith('GK'): return 'GK'
    return 'WS'
cnt2=collections.Counter((grp(c['tag']),c['cat']) for c in U if not c['taken'])
for k in sorted(cnt2): print(k,cnt2[k])
