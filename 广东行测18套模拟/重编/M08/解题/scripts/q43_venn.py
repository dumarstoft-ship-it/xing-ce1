"""M08 第43题：全班40多人。舞蹈∩乐器 比 舞蹈∩非乐器 多70%；乐器∩舞蹈 比 乐器∩非舞蹈 多3人；两者都没学的6人。求总人数。枚举。"""
from fractions import Fraction as F
sols = []
for x in range(0, 50):            # 只学舞蹈
    both = F(17, 10)*x
    if both.denominator != 1 or both == 0: continue
    both = int(both); y = both - 3   # 只学乐器
    if y < 0: continue
    tot = x + both + y + 6
    if 40 <= tot <= 49: sols.append((x, both, y, tot))
print('(只舞蹈, 两者都学, 只乐器, 总人数):', sols)
assert len(sols) == 1 and sols[0][3] == 47
print('一般式: 总人数 = 44k + 3, k=1 时 47')
print('漏掉6人:', sols[0][3]-6)
