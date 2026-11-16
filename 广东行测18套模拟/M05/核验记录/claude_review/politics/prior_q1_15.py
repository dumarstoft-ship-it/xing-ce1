# 只读：列出M01—M04第1—15题题干（截断）与答案，用于对照题位主题是否模板化
import json
base = '/home/user/xing-ce1/广东行测18套模拟/'
def flat(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return ''.join(flat(i) for i in x)
    if isinstance(x, dict): return x.get('text', '') if 'text' in x else ''
    return '' if x is None else str(x)
for d in ['M01', 'M02', 'M03', 'M04']:
    qs = json.load(open(base + d + '/selection.json', encoding='utf-8'))
    print('#' * 10, d)
    for q in qs:
        if q['number'] <= 15:
            print(f"{q['number']:>2} {q.get('subtype') or q.get('question_type')} [{q.get('answer')}] {flat(q.get('stem'))[:70]}")
