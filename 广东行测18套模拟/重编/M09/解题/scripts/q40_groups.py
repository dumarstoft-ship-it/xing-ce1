"""M09 第40题：检验人员+其他人员=55；检验人员平均分成n组、每组k人；新增20人：检验人员增加2组(2k人)，
其他人员增加30%。求原有检验人员组数n。 选项 A4 B5 C6 D7
核验：枚举其他人员m（0…55）、每组人数k、组数n，全部正整数解。"""
sols = []
for m in range(1, 56):              # 其他工作人员至少1人
    if (3 * m) % 10:                # 增加30%须为整数
        continue
    add_other = 3 * m // 10
    two_k = 20 - add_other
    if two_k <= 0 or two_k % 2:
        continue
    k = two_k // 2
    insp = 55 - m
    if insp % k:
        continue
    n = insp // k
    sols.append((m, k, n))
print('全部解(其他人员m, 每组k人, 组数n):', sols)
assert sols == [(20, 7, 5)]
opts = {'A': 4, 'B': 5, 'C': 6, 'D': 7}
print('答案：', [kk for kk, v in opts.items() if v == sols[0][2]])
# 代入法：已知n时，nk+m=55，2k+0.3m=20 → k=(20−16.5)/(2−0.3n)
from fractions import Fraction as F
for kk, n in opts.items():
    k = (F(20) - F(3, 10) * 55) / (2 - F(3, 10) * n)
    m = 55 - n * k
    print(f'{kk}: n={n} → k={k}, m={m}', '整数解' if k.denominator == 1 and k > 0 and m > 0 and m.denominator == 1 else '')
# 易错核算：问“原有”组数，若答成补充后的组数 n+2
after = sols[0][2] + 2
print('补充后组数', after, '→', [kk for kk, v in opts.items() if v == after])
assert after == 7
