"""主旨题作答卷：python3 -I make_zz_sheet.py <结果.json> <输出.md>
像考场上一样只给题干材料、问句和选项，不给原文和答案；答案另存 <输出>.key.json。"""
import json, sys
r = json.load(open(sys.argv[1], encoding='utf-8'))
out = sys.argv[2]
lines, key = ['# 片段阅读作答卷', '', '每题只有一段材料和四个选项，像考场上一样作答。', ''], {}
for art in r['articles']:
    for i, q in enumerate(art['questions'], 1):
        k = f"{art['id']}#{i}"
        key[k] = q['answer']
        lines += [f'## {k}', '']
        lines += [p.strip() for p in q['passage'].strip().split('\n') if p.strip()]
        lines += ['', q['stem'].strip(), '']
        lines += [f"{'ABCD'[j]}. {o}" for j, o in enumerate(q['options'])]
        lines += ['']
open(out, 'w', encoding='utf-8').write('\n'.join(lines))
json.dump(key, open(out + '.key.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(key), '题')
