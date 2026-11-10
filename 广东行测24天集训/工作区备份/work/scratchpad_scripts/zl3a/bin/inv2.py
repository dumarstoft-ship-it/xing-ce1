"""Block inventory: group each paper's 资料 questions by material (or by blocks of 5 when segmentation merged them).
Prints blocks with >= MINFREE free questions, with growth-rate keyword markers.
usage: inv2.py MINFREE [tag-regex] [--all]"""
import json, re, sys, collections
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl3a'
inv = json.load(open(f'{SP}/inv/inv.json'))
MINFREE = int(sys.argv[1]); rx = re.compile(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
GR = re.compile(r'(增速|增长率|增幅|最快|最慢|快于|慢于|增长最|下降最|降幅|百分点|加快|放缓|回落|年均|倍)')
bytag = collections.defaultdict(list)
for o in inv: bytag[o['tag']].append(o)
blocks = []
for t, mats in bytag.items():
    if rx and not rx.search(t): continue
    rows = []
    for o in mats:
        for r in o['rows']: rows.append((o['mid'], o['idx'], r))
    rows.sort(key=lambda x: x[2][0])
    merged = any(o['n'] > 5 for o in mats)
    if merged:
        # blocks of 5 by qno
        b = collections.OrderedDict()
        q0 = rows[0][2][0]
        for mid, idx, r in rows:
            k = (r[0] - q0) // 5
            b.setdefault(k, []).append(r)
        for k, rr in b.items(): blocks.append((t, f'B{k+1}', rr, True))
    else:
        b = collections.OrderedDict()
        for mid, idx, r in rows: b.setdefault((idx, mid), []).append(r)
        for (idx, mid), rr in b.items(): blocks.append((t, f'#{idx}', rr, False))
json.dump([(t, lab, rr, m) for t, lab, rr, m in blocks], open(f'{SP}/inv/blocks.json', 'w'), ensure_ascii=False)
for t, lab, rr, m in blocks:
    free = [r for r in rr if r[1] is None]
    if len(free) < MINFREE: continue
    g = sum(1 for r in free if GR.search(r[2]))
    print(f"## {t} {lab}{'(blk)' if m else ''} q{rr[0][0]}-{rr[-1][0]} free={len(free)}/{len(rr)} grQ={g}")
    for (qno, st, txt, a, gg) in rr:
        mark = '*' if GR.search(txt) else ' '
        s = re.sub(r'^\d+\s*[\.、．]\s*', '', txt)
        print(f"  {mark}{qno:>3} {'F' if st is None else 'X'} {a or '-'} {s[:95]}")
