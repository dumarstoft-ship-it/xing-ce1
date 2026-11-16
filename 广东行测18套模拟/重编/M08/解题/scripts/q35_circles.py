"""M08 第35题：四个圆，每圆分四格（左上, 右上, 左下, 右下），第4圆左上为？  选项 A9 B8 C7 D6
规律：左上×右下 = 右上 + 左下（两条对角线：一条作积，一条作和）。逐项检验选项唯一。"""
circles = [(2, 6, 10, 8), (5, 11, 4, 3), (7, 17, 11, 4)]
opts = {'A': 9, 'B': 8, 'C': 7, 'D': 6}
for ul, ur, ll, lr in circles:
    print((ul, ur, ll, lr), 'ul*lr =', ul*lr, ' ur+ll =', ur+ll)
    assert ul*lr == ur+ll
ur, ll, lr = 9, 18, 3
ans = [k for k, v in opts.items() if v*lr == ur+ll]
print('第4圆：?×3 = 9+18 =', ur+ll, '→ 满足的选项', ans)
assert ans == ['A']
# 排除其它常见组合（如 ul*lr-ur=ll 等价；ul+ur+ll+lr 恒定？）
print('各圆四数之和:', [sum(c) for c in circles], '(不恒定，排除“和相等”)')
