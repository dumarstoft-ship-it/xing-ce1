"""Enumerate, for the matching-type items, which options survive when the solver
knows only a subset of the correct correspondences."""
import json
from itertools import combinations
items = {
 'Q05': {'slots': ['自由探索类', '目标导向类'],
         'key': ['原创性和学术贡献', '解决重大科学问题的效能'],
         'opts': {'A': ['短期转化收入', '论文数量'],
                  'B': ['解决重大科学问题的效能', '原创性和学术贡献'],
                  'C': ['原创性和学术贡献', '解决重大科学问题的效能'],
                  'D': ['形成专利的数量', '成果发表期刊的影响因子']}},
 'Q06': {'slots': ['①', '②', '③'], 'key': ['统一性', '包容性', '创新性'],
         'opts': {'A': ['统一性', '包容性', '创新性'], 'B': ['包容性', '统一性', '连续性'],
                  'C': ['统一性', '创新性', '包容性'], 'D': ['连续性', '包容性', '创新性']}},
 'Q12': {'slots': ['广州话', '梅县话', '潮州话', '雷州话'], 'key': ['粤', '客', '闽', '闽'],
         'opts': {'A': ['粤', '客', '粤', '闽'], 'B': ['粤', '客', '闽', '闽'],
                  'C': ['粤', '闽', '客', '闽'], 'D': ['粤', '客', '闽', '粤']}},
 'Q13': {'slots': ['思想建党政治建军', '统一战线策略方针', '全面抗战路线'], 'key': ['古田', '瓦窑堡', '洛川'],
         'opts': {'A': ['遵义', '洛川', '瓦窑堡'], 'B': ['古田', '洛川', '瓦窑堡'],
                  'C': ['遵义', '瓦窑堡', '洛川'], 'D': ['古田', '瓦窑堡', '洛川']}},
}
out = {}
for q, d in items.items():
    n = len(d['slots']); res = {}
    keyopts = [k for k, v in d['opts'].items() if v == d['key']]
    for r in range(1, n+1):
        for known in combinations(range(n), r):
            surv = [k for k, v in d['opts'].items() if all(v[i] == d['key'][i] for i in known)]
            res['+'.join(d['slots'][i] for i in known)] = surv
    out[q] = {'key_options': keyopts, 'survivors_by_known_slots': res}
    print(q, 'key', keyopts)
    for k, v in res.items():
        print('   know', k, '->', v, '(locked)' if len(v) == 1 else '')
json.dump(out, open('enum_matching.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
