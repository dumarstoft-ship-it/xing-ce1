"""show.py TAG:QNO [TAG:QNO ...] -> print full text, segs, images, ref answer, dup group"""
import json, sys, re
IDX = '/home/user/work/index'
QI = {}
for l in open('/home/user/work/qindex.jsonl'):
    r = json.loads(l); QI[(r['tag'], r['qno'])] = r
cache = {}
for arg in sys.argv[1:]:
    t, n = arg.split(':'); n = int(n)
    if t not in cache: cache[t] = {q['qno']: q for q in json.load(open(f'{IDX}/{t}.json')) if q['kind'] == 'q'}
    q = cache[t].get(n)
    r = QI.get((t, n), {})
    print(f'===== {t}-{n}  ans={r.get("answer")} rate={r.get("rate")} dup={r.get("dup_group")}x{r.get("dup_size")} imgs={len(q["images"]) if q else None} segs={q["segs"] if q else None}')
    if q: print(q['text'])
