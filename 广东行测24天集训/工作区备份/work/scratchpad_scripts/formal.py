"""Read-only: list FREE formal-logic items (deduction asks, not argument asks) for papers matching regex.
Usage: FREE=1 python3 -I formal.py <tag-regex> [maxchars]"""
import json, glob, os, re, sys
W = '/home/user/work'
claims = [json.loads(l) for l in open(W + '/out/claims.jsonl') if l.strip()]
taken = {}
for c in claims:
    for k in [c['key']] + c.get('dups', []):
        taken.setdefault(k, c['owner'])
qi = [json.loads(l) for l in open(W + '/qindex.jsonl')]
grp = {}; by_group = {}
for r in qi:
    k = f"{r['pid']}-{r['qno']}"; g = r.get('dup_group'); grp[k] = g
    if g: by_group.setdefault(g, set()).add(k)
def status(key):
    ks = {key} | by_group.get(grp.get(key), set())
    hits = [k + ':' + taken[k] for k in sorted(ks) if k in taken]
    return ('TAKEN ' + ';'.join(hits)) if hits else 'FREE' + (' dups=' + ','.join(sorted(ks - {key})) if len(ks) > 1 else '')
ans = {}
for f in glob.glob(W + '/answers/*.json'):
    tag = os.path.basename(f)[:-5]
    try: ans[tag] = json.load(open(f)).get('answers', {})
    except Exception: pass
prx = re.compile(sys.argv[1]); mx = int(sys.argv[2]) if len(sys.argv) > 2 else 300
ARGASK = re.compile(r'削弱|加强|支持|质疑|前提|假设|解释|反驳|评价|推理方式|相似|结构|论证方法|论证方式|漏洞|谬误|焦点|争论|反对|不能(?:支持|削弱|解释)')
DEDASK = re.compile(r'推出|得出|一定为真|一定是真|必然|可能为真|可能是真|不可能|由此可知|推知|可以确定|可知|以下哪项一定|下列哪项一定|一定正确|一定不|是真的|为真的是|为假|正确的是|分别是|哪个|是谁|哪一位|哪位|第几')
DEF = re.compile(r'是指|指的是|根据上述定义|根据以上定义|属于.*?的是|不属于')
seen = set()
for f in sorted(glob.glob(W + '/index/*.json')):
    tag = os.path.basename(f)[:-5]; pid = tag.replace('_xc', '')
    if not prx.fullmatch(tag) or re.match(r'GD202[456]', pid): continue
    rows = json.load(open(f))
    mats = {q.get('mid'): q['text'] for q in rows if q.get('kind') == 'material'}
    for q in rows:
        if q.get('kind') != 'q' or q.get('section') not in ('判断', None): continue
        t = q['text'].replace('\n', ' ')
        if DEF.search(t[:200]): continue
        # ask = last sentence-ish before options
        m = re.search(r'A[、.．]', t)
        head = t[:m.start()] if m else t
        ask = head[-60:]
        if ARGASK.search(ask): continue
        if not DEDASK.search(head) and not q.get('material'): continue
        key = f"{pid}-{q['qno']}"
        if key in seen: continue
        seen.add(key)
        st = status(key)
        if os.environ.get('FREE') and not st.startswith('FREE'): continue
        a = ans.get(tag, {}).get(str(q['qno'])) or ans.get(pid, {}).get(str(q['qno']))
        print(f"### {key} [{st}] ans={(a or {}).get('ans')} rate={(a or {}).get('rate')} p={q['segs'][0][0]+1} img={len(q.get('images') or [])} mat={q.get('material')}")
        print('   ' + t[:mx])
