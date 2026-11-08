"""leak_scan.py <结果.json> <文章目录>
1) 正确项、被删的句子，与做这题时题卡以外露出的文字（标题＋不在任何题范围内的段落；写了 hide_title 的题做完之前不算标题）的最长公共片段。
2) 同篇前面题的说明/选项，是否含后面题正确项的 4 字片段（且该片段在答前一题时露出的文字里没有）。"""
import json, sys, os, difflib

def lcs(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    m = sm.find_longest_match(0, len(a), 0, len(b))
    return a[m.a:m.a + m.size]

r = json.load(open(sys.argv[1], encoding='utf-8'))
for art in r['articles']:
    a = json.load(open(os.path.join(sys.argv[2], art['id'] + '.json'), encoding='utf-8'))
    P = a['paras']
    qs = art['questions']
    covered = set()
    for q in qs:
        covered |= set(range(q['from_p'], q['to_p'] + 1)) | set(q.get('hide_p') or [])
    body = '\n'.join(P[i - 1] for i in range(1, len(P) + 1) if i not in covered)
    # 写了 hide_title 的题没做完之前，标题不显示；按顺序做题，做第 i 题时，排在它后面（含它）只要有一题写了 hide_title，标题就还遮着
    tvis = [not any(q.get('hide_title') for q in qs[i:]) for i in range(len(qs))]
    static = (a['title'] if all(tvis) else '') + '\n' + body
    print('#', art['id'], a['title'])
    for i, q in enumerate(qs, 1):
        ans = q['options']['ABCD'.index(q['answer'])]
        seen = (a['title'] if tvis[i - 1] else '') + '\n' + body
        s = lcs(ans, seen)
        print(f'  第{i}题 正确项与露出文字最长公共片段：「{s}」({len(s)})')
        orig = '\n'.join(P[q['from_p'] - 1:q['to_p']])
        sm = difflib.SequenceMatcher(None, orig, q['passage'], autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ('delete', 'replace') and i2 - i1 >= 6:
                d = orig[i1:i2].strip('\n')
                s2 = lcs(d, seen)
                if len(s2) >= 6:
                    print(f'    被删句与露出文字重合：「{s2}」 ← 删去的「{d[:30]}」')
    # 跨题剧透
    for j, qj in enumerate(qs):
        ansj = qj['options']['ABCD'.index(qj['answer'])]
        grams = {ansj[k:k + 4] for k in range(len(ansj) - 3)}
        for i in range(j):
            qi = qs[i]
            shown = static + '\n' + '\n'.join(P[p - 1] for q in qs[:i + 1] for p in range(q['from_p'], q['to_p'] + 1))
            txt = qi['note'] + '|' + '|'.join(qi['options'])
            hit = sorted(g for g in grams if g in txt and g not in shown)
            if hit:
                print(f'  剧透？第{i+1}题说明/选项含第{j+1}题正确项片段 {hit[:6]}')
print('扫描完毕')
