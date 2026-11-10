from itertools import permutations, product, combinations
RESULTS = {}
def imp(a, b): return (not a) or b
def judge(qid, models, opts, mode, expect, note=''):
    assert models, qid + ': no model satisfies the stem'
    stat = {}
    for k, f in opts.items():
        v = [bool(f(m)) for m in models]
        stat[k] = 'ALL' if all(v) else ('SOME' if any(v) else 'NONE')
    sel = {'must': lambda s: s == 'ALL', 'can': lambda s: s != 'NONE', 'cannot': lambda s: s == 'NONE', 'notmust': lambda s: s != 'ALL'}[mode]
    ans = ''.join(k for k, s in stat.items() if sel(s))
    RESULTS[qid] = ans
    print(f"{'OK ' if ans == expect else 'XX '}{qid:24s} models={len(models):6d} ask={mode:7s} -> {ans:4s} (expect {expect})  {stat} {note}")
    assert ans == expect, qid
def record(qid, ans, expect, msg):
    RESULTS[qid] = ans
    print(('OK ' if ans == expect else 'XX ') + f'{qid:24s} {msg} -> {ans} (expect {expect})')
    assert ans == expect, qid
B = (0, 1)
exec(open('funcs.py').read())
for f in [gk2020f_107, zjxd2020_30, gdxd2019sw_12, js2017a_97, gk2020f_111, gk2019f_115, js2019a_93, js2021a_94]: f()
