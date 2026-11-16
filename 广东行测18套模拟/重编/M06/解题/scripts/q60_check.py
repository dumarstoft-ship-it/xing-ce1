"""第60题：逐项代入四个选项的排名，判断四人预测的真假，检验“至多两人说错”；并枚举全部排名组合作参考。"""
import itertools
P = ['赵', '钱', '孙', '李']

def judge(phy, che):
    """phy/che: 名次表（1为第一）。返回四人预测的真假。"""
    return {
        '赵': phy['赵'] < che['赵'],              # 我的物理排名比化学排名高
        '钱': phy['赵'] > phy['钱'],              # 物理中赵的排名比我低
        '孙': che['孙'] != 4,                     # 我的化学排名不是最低
        '李': phy['李'] != 1 and che['李'] != 1,  # 两科都不是第一
    }

def rank(order):
    return {p: i + 1 for i, p in enumerate(order)}

OPTS = {
    'A': ('孙李赵钱', '钱赵李孙'),
    'B': ('赵孙钱李', '李赵钱孙'),
    'C': ('李赵孙钱', '赵钱孙李'),
    'D': ('钱孙赵李', '赵李钱孙'),
}
for k, (p, c) in OPTS.items():
    j = judge(rank(p), rank(c))
    wrong = [n for n, v in j.items() if not v]
    print(k, '说错的人:', wrong, '→', '可能' if len(wrong) <= 2 else '不可能')

allc = 0
for p in itertools.permutations(P):
    for c in itertools.permutations(P):
        if sum(not v for v in judge(rank(p), rank(c)).values()) <= 2:
            allc += 1
print('（参考）全部 24×24 种排名中满足“至多两人说错”的有', allc, '种')
