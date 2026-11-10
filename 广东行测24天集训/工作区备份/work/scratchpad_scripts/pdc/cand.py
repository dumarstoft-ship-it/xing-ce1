"""List logic-judgement candidates (conditional / truth-value / analytical reasoning) from in-scope papers."""
import json, glob, os, re, sys, collections
IDX = '/home/user/work/index'
QI = [json.loads(l) for l in open('/home/user/work/qindex.jsonl')]
DUP = {(r['tag'], r['qno']): (r['dup_group'], r['dup_size'], r['answer']) for r in QI}

def in_scope(t):
    m = re.match(r'([A-Z]+?)(\d{4})', t); prov, yr = m.group(1), int(m.group(2))
    if prov == 'GDXD': return False
    if prov in ('GD', 'GK'): return 2017 <= yr <= 2026
    return 2020 <= yr <= 2026

TRANS = re.compile(r'如果|只有|除非|否则|那么|就会|才能|才会|必须|要么|或者|并且|若|则')
TRUTH = re.compile(r'真话|假话|为真|为假|一真|说对|猜对|说错|只有一[句个人项]|都不对|正确的只有|只对了')
ANAL = re.compile(r'分别|各不相同|每人|每个人|依次|排序|位置|名次|座位|相邻|左边|右边|值班|周[一二三四五六日]|星期|各有|恰好|各自|互不相同|编号|第[一二三四五六七八]|\d号|甲、乙、丙|[A-Z]、[A-Z]、[A-Z]')
ASK_NEC = re.compile(r'一定为真|一定为假|可以推出|能够推出|必然|一定是|可能为真|不可能|可以得出|能推出|一定正确|无法确定|不能确定')
ARG = re.compile(r'加强|削弱|支持|质疑|前提|假设|反驳|论证|解释|评价')

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    out = []
    for f in sorted(glob.glob(f'{IDX}/*.json')):
        t = os.path.basename(f)[:-5]
        if not in_scope(t): continue
        qs = json.load(open(f))
        for q in qs:
            if q['kind'] != 'q' or q['section'] not in ('判断', None): continue
            txt = q['text']
            s = re.sub(r'\s+', '', txt)
            if ARG.search(s.split('A')[0] if 'A' in s else s) and not TRUTH.search(s):
                continue
            tags = []
            if TRUTH.search(s): tags.append('真假')
            if ANAL.search(s): tags.append('分析')
            if len(TRANS.findall(s)) >= 2: tags.append('翻译')
            if not ASK_NEC.search(s) and '真假' not in tags and '分析' not in tags: continue
            if not tags: continue
            g = DUP.get((t, q['qno']), (None, 1, None))
            out.append(dict(tag=t, qno=q['qno'], tags=tags, dup=g[0], dsz=g[1], ans=g[2], nimg=len(q['images']), len=len(s), text=s[:400]))
    json.dump(out, open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pdc/cands.json', 'w'), ensure_ascii=False)
    c = collections.Counter();
    for o in out:
        for tg in o['tags']: c[tg] += 1
    print(len(out), c)
main()
