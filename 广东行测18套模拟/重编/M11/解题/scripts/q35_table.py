"""M11 第35题：数表（原卷2016年县级卷第40题题图，已看图）
  9   47  17
 15  （ ） 6.5
  4  −36  26        选项 A55 B103 C199 D212
规律：每行 第2个数 = 第1个数² − 2×第3个数。"""
from fractions import Fraction as Fr
rows = [(9, 47, 17), (4, -36, 26)]
opts = {'A': 55, 'B': 103, 'C': 199, 'D': 212}
for a, b, c in rows:
    assert b == a * a - 2 * c
ans = 15 * 15 - 2 * Fr(13, 2)
print('第2行：15²−2×6.5 =', ans)
assert ans == 212
# 形如 b = p·a² + q·c 的规律由两行唯一确定：p=1，q=−2
det = 81 * 26 - 16 * 17
p = Fr(47 * 26 - (-36) * 17, det); q = Fr(81 * (-36) - 16 * 47, det)
print('b=p·a²+q·c 的解：p =', p, 'q =', q)
assert (p, q) == (1, -2)
# 形如 b = p·a + q·c 的线性规律解不出整数系数
det2 = 9 * 26 - 4 * 17
print('b=p·a+q·c 的解：p =', Fr(47 * 26 - (-36) * 17, det2), 'q =', Fr(9 * (-36) - 4 * 47, det2))
print('答案：', [k for k, v in opts.items() if v == ans])
