# -*- coding: utf-8 -*-
"""Q60 枚举：甲乙丙丁戊己庚 7 人周一到周日各值班一天。

条件：(1) 乙、丙值班日期间隔大于2天；(2) 丙在甲前，且二人间隔大于2天；
(3) 丁、戊不相邻；(4) 甲、庚相邻且甲在庚前。

“间隔大于2天”有两种读法，分别枚举：
  读法一：两人中间隔着的天数 > 2，即日期差 >= 4（如周一与周五，中间隔周二、三、四共3天）；
  读法二：日期差 > 2，即日期差 >= 3。
"""
import itertools

people = ['甲', '乙', '丙', '丁', '戊', '己', '庚']
days = '一二三四五六日'


def count(min_diff):
    sols = []
    for perm in itertools.permutations(range(1, 8)):
        d = dict(zip(people, perm))
        if abs(d['乙'] - d['丙']) < min_diff:
            continue
        if not (d['甲'] - d['丙'] >= min_diff):
            continue
        if abs(d['丁'] - d['戊']) == 1:
            continue
        if d['庚'] - d['甲'] != 1:
            continue
        sols.append(d)
    return sols


for name, md in (('读法一（中间隔着的天数>2，日期差>=4）', 4), ('读法二（日期差>2，即>=3）', 3)):
    sols = count(md)
    print(name, '共', len(sols), '种')
    if len(sols) <= 10:
        for s in sols:
            order = sorted(s, key=lambda p: s[p])
            print('   ', ' '.join('周%s%s' % (days[s[p] - 1], p) for p in order))
