"""换入题 第61题（gd-mock-2026h2-s24-q58）论证结构比较：把题干与各选项写成命题形式，
比较"前提形式 ⊢ 结论形式"是否与题干相同，并用真值表判断有效性。

题干：观察到 Q（续航提升）；P（掺杂纳米硅）→ Q；所以 P。
A：观察到 ¬Q（繁殖加快＝未被抑制）；P（紫外照射）→ Q（抑制繁殖）；所以 ¬P。
B：观察到 Q（沉降减小）；P（合理回灌）→ Q；所以 P。
C：P（碳纤维）→ Q（载重提升）；该无人机 P；所以 Q。
D：观察到 Q（数据异常）；P（进入辐射带）→ Q；所以 R（地面启动应急程序，新概念）。
"""
import itertools

imp = lambda a, b: (not a) or b
ARGS = {
    '题干': (('Q', 'P→Q'), 'P'),
    'A': (('¬Q', 'P→Q'), '¬P'),
    'B': (('Q', 'P→Q'), 'P'),
    'C': (('P→Q', 'P'), 'Q'),
    'D': (('Q', 'P→Q'), 'R'),
}


def ev(f, P, Q, R):
    return {'P': P, 'Q': Q, 'R': R, '¬P': not P, '¬Q': not Q, 'P→Q': imp(P, Q)}[f]


def valid(prem, concl):
    return all(ev(concl, *v) for v in itertools.product([True, False], repeat=3)
               if all(ev(p, *v) for p in prem))


stem = ARGS['题干']
for k, (prem, concl) in ARGS.items():
    same = (sorted(prem), concl) == (sorted(stem[0]), stem[1])
    print(f'{k}：前提{prem} ⊢ {concl}  有效={valid(prem, concl)}  与题干形式相同={same}')
