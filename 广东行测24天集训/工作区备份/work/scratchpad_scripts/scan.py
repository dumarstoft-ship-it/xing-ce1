"""Read-only scan: list formal-logic candidates (判断 section) with claim status.
Usage: python3 -I scan.py [cond|combo|all] [paper-regex]"""
import json, glob, os, re, sys
W = '/home/user/work'
claims = [json.loads(l) for l in open(W + '/out/claims.jsonl') if l.strip()]
taken = {}
for c in claims:
    for k in [c['key']] + c.get('dups', []):
        taken.setdefault(k, c['owner'])
qi = [json.loads(l) for l in open(W + '/qindex.jsonl')]
grp = {}
by_group = {}
for r in qi:
    k = f"{r['pid']}-{r['qno']}"
    g = r.get('dup_group')
    grp[k] = g
    if g: by_group.setdefault(g, set()).add(k)
ans = {}
for f in glob.glob(W + '/answers/*.json'):
    tag = os.path.basename(f)[:-5]
    try:
        a = json.load(open(f))
        ans[tag] = a.get('answers', {})
    except Exception:
        pass

def status(key):
    ks = {key} | by_group.get(grp.get(key), set())
    for k in ks:
        if k in taken: return 'TAKEN:' + taken[k] + '(' + k + ')'
    return 'FREE'

mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
prx = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
ARG = re.compile(r'削弱|加强|支持|质疑|前提|假设|解释|评价|反驳|说明.*?问题|论证方式|推理结构|逻辑结构|相似|类似|不能(?:支持|削弱)|反对|证明')
COND = re.compile(r'如果|只有|除非|否则|那么|只要|则|必须|才能|才会|才')
ASK = re.compile(r'推出|得出|必然|一定|可能|推知|可知|为真|为假|正确的是|不正确|不能确定|是哪|以下哪|下列哪|由此')
COMBO = re.compile(r'分别|各不相同|每人|每个|座位|相邻|左边|右边|左手|右手|对面|顺时针|逆时针|排成|一排|排在|名次|值班|安排|分组|组成|编号|第[一二三四五六七八1-9]位|房间|楼层|号楼|依次')
seen_hash = set()
out = []
for f in sorted(glob.glob(W + '/index/*.json')):
    tag = os.path.basename(f)[:-5]
    pid = tag.replace('_xc', '')
    if re.match(r'GD202[456]', pid): continue
    if prx and not prx.search(pid): continue
    for q in json.load(open(f)):
        if q.get('kind') != 'q' or q.get('section') not in ('判断', None): continue
        t = q['text'].replace('\n', '')
        if ARG.search(t[:400]) and mode != 'all': continue
        if len(q.get('images') or []) and mode != 'all': continue
        iscombo = bool(COMBO.search(t))
        iscond = bool(COND.search(t)) and bool(ASK.search(t))
        if mode == 'cond' and not iscond: continue
        if mode == 'combo' and not iscombo: continue
        key = f"{pid}-{q['qno']}"
        if key in seen_hash: continue
        seen_hash.add(key)
        a = ans.get(tag, {}).get(str(q['qno'])) or ans.get(pid, {}).get(str(q['qno'])) or ans.get(pid + '_xc', {}).get(str(q['qno']))
        out.append((key, tag, status(key), (a or {}).get('ans'), (a or {}).get('rate'), t[:150]))
for o in out:
    print(' | '.join(str(x) for x in o))
print(len(out), 'rows', file=sys.stderr)
