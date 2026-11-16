"""第60题：逐个选项计算四人预测的真假，要求假话至多2句。
排名"高"按名次靠前（第1名最高）理解；附带检验反向理解，看是否会出现多解。"""

OPTS = {
    'A': ('孙>李>赵>钱', '钱>赵>李>孙'),
    'B': ('赵>孙>钱>李', '李>赵>钱>孙'),
    'C': ('李>赵>孙>钱', '赵>钱>孙>李'),
    'D': ('钱>孙>赵>李', '赵>李>钱>孙'),
}


def ranks(s):
    return {name: i + 1 for i, name in enumerate(s.split('>'))}   # 名次：1最好


def judge(phy, chem, better_is_smaller=True):
    def higher(a, b):  # a 的排名比 b 高
        return a < b if better_is_smaller else a > b
    zhao = higher(phy['赵'], chem['赵'])
    qian = higher(phy['钱'], phy['赵'])          # 赵的物理排名比钱低 ⇔ 钱比赵高
    lowest = 4 if better_is_smaller else 1
    sun = chem['孙'] != lowest
    first = 1 if better_is_smaller else 4
    li = phy['李'] != first and chem['李'] != first
    return {'赵': zhao, '钱': qian, '孙': sun, '李': li}


for mode in (True, False):
    print('理解：' + ('名次数字小=排名高（常规）' if mode else '名次数字大=排名高（反向，仅作对照）'))
    for k, (p, c) in OPTS.items():
        t = judge(ranks(p), ranks(c), mode)
        nf = sum(not v for v in t.values())
        print(f'  选项{k}：{t}  假话{nf}句  →', '可能' if nf <= 2 else '不可能')
