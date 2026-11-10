import json, sys, re
P = json.load(open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pdb/pool.json'))
idx = {(o['pid'], o['qno']): o for o in P}
args = sys.argv[1:]
for a in args:
    pid, q = a.rsplit('-', 1); q = int(q)
    o = idx.get((pid, q))
    if not o: print('MISSING', a); continue
    t = re.sub(r'\n', '', o['text'])
    t = re.sub(r'([A-D][\.．、])', r'\n\1', t)
    print(f"=== {pid}-{q} [{o['typ']}] ans={o['ans']} rate={o['rate']} yc={o['yicuo']} dup={o['dup']}x{o['dupn']} img={o['nimg']}")
    print(t)
