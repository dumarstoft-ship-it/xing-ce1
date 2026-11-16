"""第51题：5人各用4类工具之一（可重复），枚举全部 4^5 种分配，找满足(1)-(4)的情形，
检验每个选项是否在所有情形下都成立。"""
import itertools

TOOLS = ['写作', '数据分析', '绘图', '视频剪辑']
PEOPLE = ['陈', '杨', '黄', '吴', '郑']


def ok(a):
    c1 = (a['陈'] != '写作') or (a['吴'] == '绘图')                  # 陈写作 → 吴绘图
    c2 = (a['杨'] == '数据分析') or (a['黄'] != '视频剪辑')           # 除非杨数据分析，否则黄不视频剪辑
    c3 = (a['吴'] != '绘图') or (a['黄'] == '视频剪辑')               # 吴不绘图 或 黄视频剪辑
    c4 = (a['郑'] != '写作') or (a['杨'] != '数据分析')               # 只有杨不数据分析，郑才写作：郑写作 → 杨不数据分析
    return c1 and c2 and c3 and c4


OPTS = {
    'A': lambda a: a['陈'] == '写作' or a['郑'] == '写作',
    'B': lambda a: not (a['陈'] == '写作' and a['郑'] == '写作'),
    'C': lambda a: a['陈'] != '写作' or a['郑'] == '写作',
    'D': lambda a: a['陈'] == '写作' or a['郑'] != '写作',
}

models = []
for combo in itertools.product(TOOLS, repeat=5):
    a = dict(zip(PEOPLE, combo))
    if ok(a):
        models.append(a)
print('满足条件的分配数：', len(models))
for k, f in OPTS.items():
    bad = [m for m in models if not f(m)]
    print(f'选项{k}：必然成立={not bad}', '' if not bad else f'反例：{bad[0]}')

# 若要求四类工具都有人用（5人4类，满射）也检验一次
models2 = [m for m in models if set(m.values()) == set(TOOLS)]
print('\n附：要求四类工具都至少有1人使用时，满足条件的分配数：', len(models2))
for k, f in OPTS.items():
    bad = [m for m in models2 if not f(m)]
    print(f'选项{k}：必然成立={not bad}')
