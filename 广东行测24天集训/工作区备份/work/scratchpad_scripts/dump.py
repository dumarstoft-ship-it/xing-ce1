"""Read-only dump of judgment items (logic part) for given papers, with claim status and index answer.
Usage: python3 -I dump.py <paper-regex> [minqno] [maxqno] [maxchars]"""
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
prx = re.compile(sys.argv[1]); lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0; hi = int(sys.argv[3]) if len(sys.argv) > 3 else 999
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 260
DEF = re.compile(r'是指|指的是|根据上述定义|根据以上定义|下列属于|下列不属于|符合上述|不符合上述')
for f in sorted(glob.glob(W + '/index/*.json')):
    tag = os.path.basename(f)[:-5]; pid = tag.replace('_xc', '')
    if not prx.fullmatch(tag): continue
    for q in json.load(open(f)):
        if q.get('kind') != 'q' or not (lo <= q['qno'] <= hi): continue
        if q.get('section') not in ('判断', None): continue
        t = q['text'].replace('\n', ' ')
        if DEF.search(t[:300]): continue
        pass
        if len(t) < 60: continue
        key = f"{pid}-{q['qno']}"
        if os.environ.get('FREE') and status(key) != 'FREE' and not status(key).startswith('FREE'): continue
        a = ans.get(tag, {}).get(str(q['qno'])) or ans.get(pid, {}).get(str(q['qno']))
        print(f"### {key} [{status(key)}] ans={(a or {}).get('ans')} rate={(a or {}).get('rate')} p={q['segs'][0][0]+1}")
        print('   ' + t[:mx])
