"""第三批额外逻辑复核：仅编码明确的条件，不读取Claude核验程序。"""
from itertools import permutations, product
from collections import Counter
from pathlib import Path
import json
names='赵王张李'
strict=[]; loose=[]
for perm in permutations(names):
    p={a:perm.index(a) for a in names}
    for killer in names:
        k=p[killer]
        # Each visitor enters/exits once, without overlapping visits.
        # Dead at departure iff killer has visited by then; dead at arrival iff earlier.
        sayings=[(False,p['赵']<k),(p['王']==1,k<p['王']),(p['张']==2,p['张']<k),(k<=p['李'],k<p['李'])]
        if all(not a and not b for a,b in sayings):strict.append({'order':''.join(perm),'killer':killer})
        if all(not(a and b) for a,b in sayings):loose.append({'order':''.join(perm),'killer':killer})
assert strict==[{'order':'王李赵张','killer':'赵'}],strict
assert set(x['killer'] for x in loose)==set(names)
# Quarter assignments; a partial-order DAG can always be topologically ordered within
# a quarter if all its directed edges are non-decreasing in quarter number.
names2='甲乙丙丁戊己庚辛'; solutions=[]
for qs in product(range(1,5),repeat=8):
    d=dict(zip(names2,qs));c=Counter(qs)
    if max(c.values())>3 or d['丁']!=2 or d['辛']!=2 or d['甲']!=d['戊']:continue
    if not(d['乙']<=d['丁']<=d['丙']<=d['甲'] and d['己']<=d['丙']):continue
    solutions.append(d)
assert len(solutions)==42,len(solutions)
results={}
def evaluate(q, sols, predicates, mode, expected):
    totals=[sum(bool(fn(s)) for s in sols) for fn in predicates]
    ok=[n>0 if mode=='possible' else n==len(sols) if mode=='necessary' else n==0 for n in totals]
    assert sum(ok)==1,(q,totals,ok)
    key='ABCD'[ok.index(True)];assert key==expected
    results[q]={'answer':key,'models':len(sols),'option_true_counts':totals,'mode':mode}
def pair(a,b,k):return lambda d:d[a]==d[b]==k
evaluate('D09-PD-104',solutions,[pair('甲','戊',1),pair('丙','丁',1),pair('丁','己',1),pair('己','庚',1)],'possible','D')
s=[d for d in solutions if list(d.values()).count(2)==2]
preds=[(lambda d,a=a:d[a]==1) for a in '甲乙庚丙'];evaluate('D09-PD-105',s,preds,'necessary','B')
s=[d for d in solutions if d['丙']==d['戊']==4]
evaluate('D09-PD-106',s,[pair('甲','庚',3),pair('乙','丁',3),pair('乙','己',3),pair('己','庚',3)],'possible','D')
s=[d for d in solutions if set(d.values())=={1,2,3,4} and list(d.values()).count(4)==1]
evaluate('D09-PD-107',s,[pair('甲','戊',3),pair('乙','丙',3),pair('丙','己',3),pair('己','庚',3)],'necessary','A')
s=[d for d in solutions if d['甲']==3 and 4 not in d.values()]
preds=[(lambda d,a=a:d['庚']==d[a]) for a in '乙丙己辛'];evaluate('D09-PD-108',s,preds,'impossible','B')
results['D09-PD-089']={'answer':'A','clause_false_models':strict,'whole_statement_false_possible_killers':sorted(set(x['killer'] for x in loose)),'interpretation':'各个分句均假才唯一；整段至少一分句假不唯一'}
Path(__file__).with_name('reasoning_extra_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
