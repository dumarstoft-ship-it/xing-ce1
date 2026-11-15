#!/usr/bin/env python3
"""Small enumerations: Q10 intensity-vs-total example; Q13 option orders vs dated events; Q15 mapping uniqueness."""
import json, itertools, datetime as dt
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'checks_q10_q13_q15.json')
res = {}
# Q10: total = intensity x GDP
intensity_change, gdp_change = -0.10, 0.20
total = (1 + intensity_change) * (1 + gdp_change) - 1
res['q10_example_total_change'] = round(total, 4)  # expect +0.08
# general: total falls iff (1+i)(1+g) < 1
res['q10_counterexample_exists'] = total > 0
# Q13: event dates (start dates; standard party-history chronology)
ev = {1: ('飞夺泸定桥', dt.date(1935, 5, 29)), 2: ('吴起镇会师/到达吴起镇', dt.date(1935, 10, 19)),
      3: ('四渡赤水(首渡起)', dt.date(1935, 1, 19)), 4: ('巧渡金沙江', dt.date(1935, 5, 3))}
true_order = [k for k, _ in sorted(ev.items(), key=lambda kv: kv[1][1])]
opts = {'A': [3, 1, 4, 2], 'B': [4, 3, 1, 2], 'C': [3, 4, 2, 1], 'D': [3, 4, 1, 2]}
res['q13_true_order'] = true_order
res['q13_matching_options'] = [k for k, v in opts.items() if v == true_order]
# Q13 robustness: even if 四渡赤水 dated by its last crossing (1935-03-21/22), order unchanged
ev_alt = dict(ev); ev_alt[3] = ('四渡赤水(四渡)', dt.date(1935, 3, 22))
res['q13_true_order_if_4th_crossing_date'] = [k for k, _ in sorted(ev_alt.items(), key=lambda kv: kv[1][1])]
# Q15: descriptor -> system ; check exactly one option matches
truth = {1: '两税法', 2: '一条鞭法', 3: '摊丁入亩'}
opt15 = {'A': ['租庸调制', '两税法', '摊丁入亩'], 'B': ['两税法', '摊丁入亩', '一条鞭法'],
         'C': ['两税法', '一条鞭法', '摊丁入亩'], 'D': ['一条鞭法', '租庸调制', '两税法']}
res['q15_matching_options'] = [k for k, v in opt15.items() if v == [truth[1], truth[2], truth[3]]]
# Q12: descriptor -> site
truth12 = ['红色砂砾岩侵蚀形成的赤壁丹崖', '石灰岩溶蚀形成的峰林溶洞', '火山喷发形成的火山口湖']
opt12 = {'A': ['红色砂砾岩侵蚀形成的赤壁丹崖', '石灰岩溶蚀形成的峰林溶洞', '火山喷发形成的火山口湖'],
         'B': ['红色砂砾岩侵蚀形成的赤壁丹崖', '火山喷发形成的孤立山峰', '冰川侵蚀形成的冰斗湖'],
         'C': ['石灰岩溶蚀形成的峰林', '红色砂砾岩侵蚀形成的赤壁', '火山喷发形成的火山口湖'],
         'D': ['火山喷发形成的赤壁', '石灰岩溶蚀形成的峰林溶洞', '河道改道形成的牛轭湖']}
res['q12_matching_options'] = [k for k, v in opt12.items() if v == truth12]
# Q12 cue analysis: options surviving if solver only knows '丹霞=红色砂砾岩' and '玛珥湖=火山口湖'
res['q12_survivors_using_only_name_cues'] = [k for k, v in opt12.items() if v[0].startswith('红色砂砾岩') and v[2].startswith('火山喷发')]

# Q12 proposed minimal fix: B third slot -> 火山口湖, so A vs B differ only in the 七星岩 slot
opt12_fix = dict(opt12); opt12_fix['B'] = ['红色砂砾岩侵蚀形成的赤壁丹崖', '火山喷发形成的孤立山峰', '火山喷发形成的火山口湖']
res['q12_fix_survivors_using_only_name_cues'] = [k for k, v in opt12_fix.items() if v[0].startswith('红色砂砾岩') and v[2].startswith('火山喷发')]
res['q12_fix_matching_options'] = [k for k, v in opt12_fix.items() if v == truth12]
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2, default=str)
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
