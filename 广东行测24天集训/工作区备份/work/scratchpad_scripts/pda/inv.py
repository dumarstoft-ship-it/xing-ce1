import json,glob,os,re,collections
IDX='/home/user/work/index'
def cls(t):
    t=t.replace('\n','')
    if re.search(r'截面|切面|切割|截得|截取|剖面|横截|纵截', t): return '截面'
    if re.search(r'视图|俯视|主视|左视|正视|侧视|看到的图形|观察.*图形', t): return '视图'
    if re.search(r'折叠|纸盒|展开|外表面|折成|折起|围成', t):
        if re.search(r'裁剪|剪|对折.*展开|沿.*折叠.*展开', t): return '折纸剪纸'
        return '折叠展开'
    if re.search(r'拼合|拼接|拼成|组合成|组成|拼凑|拼出|嵌入|填补|放入', t):
        if re.search(r'立体|正方体|长方体|多面体|立方体|小正方体|方块', t): return '立体拼合'
        return '平面拼合'
    if re.search(r'旋转|翻转|角度', t) and not re.search(r'规律', t): return '空间旋转?'
    if re.search(r'分为两类|分成两类|分为两组', t): return '分类'
    if re.search(r'规律|填入问号|替代问号|问号处', t): return '规律'
    if re.search(r'立体|正方体|多面体|长方体', t): return '其他立体'
    return '?'
rows=[]
for f in sorted(glob.glob(f'{IDX}/*.json')):
    tag=os.path.basename(f)[:-5]
    qs=json.load(open(f))
    for q in qs:
        if q['kind']!='q': continue
        t=q['text']
        if q['section'] in ('判断',None) and (q['images'] or re.search(r'图形|立体|正方体|视图|截面|折叠', t[:120])):
            c=cls(t[:200])
            rows.append(dict(tag=tag,qno=q['qno'],sec=q['section'],nimg=len(q['images']),cls=c,file=q['file'],head=re.sub(r'\s+',' ',t[:90])))
json.dump(rows,open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pda/inv.json','w'),ensure_ascii=False)
c=collections.Counter(r['cls'] for r in rows); print(c)
