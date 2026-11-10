"""Build a candidate pool of figure-reasoning questions with claim status."""
import json, glob, re, collections, sys
W='/home/user/work'
claims=[json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
direct=collections.defaultdict(list); duplock=collections.defaultdict(list)
for c in claims:
    direct[c['key']].append(c['owner'])
    for d in c.get('dups',[]):
        if d!=c['key']: duplock[d].append((c['owner'],c['key']))
qi={}
for l in open(f'{W}/qindex.jsonl'):
    r=json.loads(l); qi[(r['tag'],r['qno'])]=r
FIG=re.compile(r'图形|问号|分为两类|纸盒|展开|折叠|立体|正方体|立方体|多面体|视图|截面|剖开|切面|拼合|拼接|组合而成|旋转|规律|折成|方块|小正方|长方体|四面体|圆柱|圆锥|纸片|俯视|正视|左视|轨迹')
SCI=re.compile(r'电路|小球|杠杆|溶解度|冰块|试管|蜡烛|斜面|电源|视力表|平面镜|蹦极|杯子|滑轮|弹簧|磁|浮力|光线|入射|透镜|电流|电压|气球|木块|重力|摩擦')
SPACE=re.compile(r'纸盒|展开|折叠|立体|正方体|立方体|多面体|视图|截面|剖开|切面|长方体|四面体|圆柱|圆锥|俯视|正视|左视|后视|仰视|切割|切开|旋转一周|绕.*旋转|纸片|纸条|三棱|棱柱|棱锥|球体|折成|粘接|堆叠|堆成|拼接构成')
def status(pid,qno):
    k=f'{pid}-{qno}'
    if direct.get(k): return 'USED:'+','.join(direct[k])
    if duplock.get(k): return 'LOCK:'+';'.join(f'{o}<{kk}' for o,kk in duplock[k][:3])
    return 'FREE'
def pool():
    out=[]
    for f in sorted(glob.glob(f'{W}/index/*.json')):
        tag=f.split('/')[-1][:-5]; pid=tag.replace('_xc','')
        for q in json.load(open(f)):
            if q['kind']!='q': continue
            t=q['text']
            if not q.get('images') and not re.search(r'图形|纸盒|展开图', t[:80]): continue
            if q.get('section') not in ('判断',None,'') and not FIG.search(t[:120]): continue
            if not FIG.search(t[:150]): continue
            if SCI.search(t[:150]): continue
            sp=bool(SPACE.search(t[:150]))
            r=qi.get((tag,q['qno']),{})
            out.append(dict(tag=tag,pid=pid,qno=q['qno'],sec=q.get('section'),space=sp,stem=re.sub(r'\s+',' ',t)[:70],
                            ans=r.get('answer'),rate=r.get('rate'),dup=r.get('dup_group'),dsz=r.get('dup_size'),st=status(pid,q['qno'])))
    return out
if __name__=='__main__':
    P=pool()
    flt=sys.argv[1] if len(sys.argv)>1 else ''
    for p in P:
        if flt and not re.search(flt, p['tag']): continue
        print(f"{p['tag']:12s} {p['qno']:3d} {'S' if p['space'] else 'P'} {str(p['ans']):4s} {p['st'][:40]:40s} {p['stem'][:60]}")
