"""换入题 第32、35题（数字推理）与第37题（行程）的验证。"""
from fractions import Fraction as F
import itertools

# ---------- 第32题 ----------
a = [3, 7, 16, 36, 80]
opts32 = {'A': 176, 'B': 148, 'C': 166, 'D': 188}
print('第32题')
# 规律1：a(n+1) = 2a(n) + 2^(n-1)
r1 = all(a[i + 1] == 2 * a[i] + 2 ** i for i in range(4))
print('  a(n+1)=2a(n)+2^(n-1) 对已知项成立：', r1, ' 下一项', 2 * a[-1] + 2 ** 4)
# 规律2：通项 (n+5)·2^(n-2)
r2 = all(F(n + 5) * F(2) ** (n - 2) == a[n - 1] for n in range(1, 6))
print('  通项 (n+5)·2^(n-2) 成立：', r2, ' 第6项', (6 + 5) * 2 ** 4)
# 穷举小整数系数的二阶线性递推 a(n+1)=p·a(n)+q·a(n-1)+r，看能否推出别的选项
preds = {}
for p, q, r in itertools.product(range(-6, 7), range(-6, 7), range(-30, 31)):
    if all(a[i + 1] == p * a[i] + q * a[i - 1] + r for i in range(1, 4)):
        nxt = p * a[-1] + q * a[-2] + r
        preds.setdefault(nxt, []).append((p, q, r))
print('  二阶线性递推（|p|,|q|≤6,|r|≤30）可得的下一项：', {k: v[:3] for k, v in preds.items()})
print('  命中的选项：', [k for k, v in opts32.items() if v in preds])

# ---------- 第35题 ----------
seq = [F(32, 7), F(4), F(128, 25), F(128, 17), F(512, 43)]
nums = [32, 64, 128, 256, 512]
dens = [7, 16, 25, 34, 43]
print('\n第35题')
print('  改写为 2^k/分母：', all(F(n, d) == s for n, d, s in zip(nums, dens, seq)),
      ' 分母差', [dens[i + 1] - dens[i] for i in range(4)])
nxt = F(1024, 52)
opts35 = {'A': F(6), 'B': F(256, 13), 'C': F(512, 19), 'D': F(512, 53)}
print('  下一项 1024/52 =', nxt, ' 对应选项', [k for k, v in opts35.items() if v == nxt])
print('  数列数值：', [round(float(x), 3) for x in seq + [nxt]])

# ---------- 第37题 ----------
# 甲用时120分钟，乙用时100分钟；120v甲 - 100v乙 = 2800，v甲 = v乙 + 10
print('\n第37题')
for v in range(1, 300):
    if 120 * v - 100 * (v - 10) == 2800:
        print(f'  甲 {v} 米/分 = {v * 60 / 1000} 千米/小时；乙 {v - 10} 米/分；'
              f'甲走 {120 * v} 米，乙走 {100 * (v - 10)} 米，差 {120 * v - 100 * (v - 10)}')
