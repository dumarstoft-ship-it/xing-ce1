"""show.py <tag> <q0> <q1> [width]: print full question texts (stem+options) with claim status and answer."""
import json, sys, re, unicodedata, collections
W = '/home/user/work'
tag, q0, q1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
wid = int(sys.argv[4]) if len(sys.argv) > 4 else 400
qrows = [json.loads(l) for l in open(f'{W}/qindex.jsonl')]
grp = {}; members = collections.defaultdict(set); ans = {}
for r in qrows:
    k = f"{r['pid']}-{r['qno']}"
    if r.get('dup_group'): grp[k] = r['dup_group']; members[r['dup_group']].add(k)
    if r.get('answer') and r['tag'] == tag: ans[k] = (r['answer'], r.get('rate'), r.get('yicuo'))
claims = [json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
ck = {}
for c in claims:
    for kk in [c['key']] + c.get('dups', []): ck.setdefault(kk, c['owner'] + ':' + c['key'])
def status(key):
    ks = {key} | (members[grp[key]] if key in grp else set())
    for kk in sorted(ks):
        if kk in ck: return ck[kk]
    return 'FREE'
d = json.load(open(f'{W}/index/{tag}.json'))
paper = tag.replace('_xc', '')
for x in d:
    if x['kind'] == 'q' and q0 <= x['qno'] <= q1:
        key = f'{paper}-{x["qno"]}'
        t = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', x['text']))
        dg = grp.get(key)
        print(f'[{key}] {status(key)} ans={ans.get(key)} dup={dg}({len(members[dg]) if dg else 0}) p{x["segs"][0][0]+1} img={len(x["images"])} mat={x.get("material")}')
        print('   ' + t[:wid])
