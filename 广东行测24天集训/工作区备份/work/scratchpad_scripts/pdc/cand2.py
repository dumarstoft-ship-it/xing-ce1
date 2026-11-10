import json, glob, os, re, sys, collections
IDX = '/home/user/work/index'
QI = [json.loads(l) for l in open('/home/user/work/qindex.jsonl')]
DUP = {(r['tag'], r['qno']): (r['dup_group'], r['dup_size'], r['answer']) for r in QI}
def in_scope(t):
    m = re.match(r'([A-Z]+?)(\d{4})', t); prov, yr = m.group(1), int(m.group(2))
    if prov == 'GDXD': return False
    if prov in ('GD', 'GK'): return 2017 <= yr <= 2026
    return 2020 <= yr <= 2026
ARGASK = re.compile(r'削弱|加强|支持|质疑|反驳|前提|假设|解释|评价|最能说明|有助于|最不能|驳斥|反对|论证|论据|漏洞|错误|相似|类似|结构|推理方式|方法|最为恰当|概括|主旨|意在|结论$')
NECASK = re.compile(r'一定为真|一定为假|可以推出|能够推出|必然|一定是|可能为真|不可能|可以得出|能推出|一定正确|无法确定|不能确定|可能是|可以确定|一定不|能够得出|必定|不能推出|推断|以下哪项为|下列哪项为|则以下|则下列|由此可知|由此可以|据此')
TRUTHW = re.compile(r'真话|假话|一真|说对|猜对|说错|只有一[句个人项条](?:话|预测|判断|说法|断定|陈述)?(?:为真|是真|正确|为假|是假)|只有[一二两三](?:句|个|人|项|条)(?:为真|是真|正确|为假|是假|说|猜)|都不对|正确的只有|只对了|预测|猜测|断定.*一真')
CONDW = re.compile(r'如果|只有|除非|否则|那么|才|必须|要么|或者|并且|若|则|只要|就|都|所有|有的|有些|不是')
def ask_of(s):
    m = re.search(r'A[、\.．:：]', s)
    pre = s[:m.start()] if m else s
    k = max(pre.rfind('。'), pre.rfind('：'), pre.rfind(':'), pre.rfind('？'), pre.rfind('?'), pre.rfind('”'), pre.rfind(')'))
    seg = pre[k-60 if k > 60 else 0:]
    # the ask is the final clause
    parts = re.split(r'[。]', pre)
    return (parts[-1] if parts[-1].strip() else (parts[-2] if len(parts) > 1 else pre))[-60:], pre
rows = []
for f in sorted(glob.glob(f'{IDX}/*.json')):
    t = os.path.basename(f)[:-5]
    if not in_scope(t): continue
    for q in json.load(open(f)):
        if q['kind'] != 'q' or q['section'] not in ('判断', None): continue
        s = re.sub(r'\s+', '', q['text'])
        if len(s) < 50: continue
        if re.search(r'定义|属于|符合', s[:400]) and not TRUTHW.search(s): continue
        if re.search(r'图形|六面体|立体|截面|视图|展开|折成|问号处|呈现一定的规律', s): continue
        ask, pre = ask_of(s)
        if ARGASK.search(ask) and not TRUTHW.search(pre): continue
        if not (NECASK.search(ask) or TRUTHW.search(pre)): continue
        g = DUP.get((t, q['qno']), (None, 1, None))
        kind = []
        if TRUTHW.search(pre): kind.append('T')
        nc = len(CONDW.findall(pre))
        if nc >= 3: kind.append('C%d' % nc)
        if re.search(r'分别|各不相同|互不相同|依次|排序|名次|座位|相邻|左边|右边|值班|周[一二三四五六日]|星期[一二三四五六日]|各有|恰好|各自|编号|[甲乙丙丁戊己]、[甲乙丙丁戊己]、[甲乙丙丁戊己]|[A-H]、[A-H]、[A-H]|\d号|每[人个位名]', pre): kind.append('A')
        rows.append(dict(tag=t, qno=q['qno'], k=kind, dup=g[0], dsz=g[1], ans=g[2], nimg=len(q['images']), ask=ask, head=s[:110]))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), 'cands3.json'), 'w'), ensure_ascii=False)
print(len(rows))
