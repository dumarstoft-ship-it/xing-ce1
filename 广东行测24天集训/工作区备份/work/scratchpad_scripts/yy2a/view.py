import sys; sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yy2a')
from load_html import *
D = load(); ART = {a['id']: a for a in D}
def show(aid, notes=True):
    a = ART[aid]
    print('#####', aid, a['src'], a['col'], a['date'], a['title'], '| paras', len(a['paras']))
    marks = {}
    for q in a['q']:
        for i, b in enumerate(q['blanks']):
            marks.setdefault(q['p'], []).append((b['b'], b['e'], q['id']))
    for i, p in enumerate(a['paras'], 1):
        t = ptext(p)
        for b, e, qid in sorted(marks.get(i, []), key=lambda x: -x[0]):
            t = t[:b] + '【' + qid + ':' + t[b:e] + '】' + t[e:]
        lab = ''.join('<' + sg['label'] + '>' for sg in p if 'm' in sg and sg.get('label'))
        print(f'P{i}{lab}: {t}')
    for q in a['q']:
        print(f"--- {q['id']} {q['kind']} P{q['p']} blanks={[(b['b'],b['e']) for b in q['blanks']]} ans={'ABCD'[q['answer']]}")
        for k, o in zip('ABCD', q['options']): print(f'    {k}. {o}')
        if notes: print('    NOTE:', q['note'])
if __name__ == '__main__':
    for aid in sys.argv[1:]:
        show(aid)
        print()
