import sys, re; sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yy2a')
from load_html import *
D = load(); ART = {a['id']: a for a in D}
REF = re.compile(r'(上一段|下一段|前一段|后一段|上段|下段|第[一二三四五六七八九十0-9]+段|开头|结尾|全文|标题|小标题|前文|后文|上文|下文|这一节|上一节|下一节|首段|末段|通篇|篇末|文末|前面|后面几|前几段|第[一二三四五]部分)')
def show(aid, width=170):
    a = ART[aid]
    print('#####', aid, a['src'], a['col'], a['date'], a['title'], '| paras', len(a['paras']))
    qp = {q['p'] for q in a['q']}
    need = set()
    for p in qp: need |= {p - 1, p, p + 1}
    marks = {}
    for q in a['q']:
        for b in q['blanks']:
            marks.setdefault(q['p'], []).append((b['b'], b['e'], q['id']))
    for i, p in enumerate(a['paras'], 1):
        t = ptext(p)
        for b, e, qid in sorted(marks.get(i, []), key=lambda x: -x[0]):
            t = t[:b] + '【' + qid + ':' + t[b:e] + '】' + t[e:]
        lab = ''.join('<' + sg['label'] + '>' for sg in p if 'm' in sg and sg.get('label'))
        if i in need: print(f'P{i}{lab}: {t}')
        else: print(f'P{i}{lab}: {t[:40]}…')
    for q in a['q']:
        refs = sorted(set(REF.findall(q['note'])))
        print(f"--- {q['id']} {q['kind']} P{q['p']} ans={'ABCD'[q['answer']]} | " + ' / '.join(f'{k}.{o}' for k, o in zip('ABCD', q['options'])))
        print('    REFS:', refs, '| NOTE:', q['note'][:width])
if __name__ == '__main__':
    for aid in sys.argv[1:]:
        show(aid); print()
