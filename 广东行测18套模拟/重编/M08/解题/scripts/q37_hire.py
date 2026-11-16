"""M08 第37题：今年录取=去年的3/4；今年男比去年男少30，比去年女多12，比今年女多5。求两年共录取女员工。
枚举今年男员工人数 M，唯一满足比例条件。"""
from fractions import Fraction as F
opts = {'A': 32, 'B': 57, 'C': 69, 'D': 92}
sols = []
for M in range(13, 1000):
    last_m, last_f, this_f = M + 30, M - 12, M - 5
    if this_f < 0 or last_f < 0: continue
    if F(M + this_f) == F(3, 4) * (last_m + last_f):
        sols.append((M, this_f, last_m, last_f))
print('解(今年男, 今年女, 去年男, 去年女):', sols)
assert len(sols) == 1
M, tf, lm, lf = sols[0]
print('今年总', M+tf, '去年总', lm+lf, '两年女员工共', tf+lf)
assert [k for k, v in opts.items() if v == tf+lf] == ['B']
print('选项A=今年女', tf, '; C=今年总', M+tf, '; D=去年总', lm+lf)
# 另一读法：“比去年少30人”理解为比去年总人数少30
alt = []
for M in range(13, 1000):
    last_tot, last_f, this_f = M + 30, M - 12, M - 5
    if F(M + this_f) == F(3, 4)*last_tot: alt.append((M, this_f, last_f, this_f+last_f))
print('若理解为比去年总人数少30:', alt, '(两年女员工数不在选项中)')
