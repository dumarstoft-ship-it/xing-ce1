"""第51题：枚举5人各用4类工具之一的全部 4^5 种情形，筛出满足(1)~(4)的情形，检验各选项是否一定为真。"""
import itertools
TOOLS = ['写作', '数据分析', '绘图', '视频剪辑']
P = ['陈', '杨', '黄', '吴', '郑']

def ok(a):
    c1 = (a['陈'] != '写作') or (a['吴'] == '绘图')            # 陈写作 → 吴绘图
    c2 = (a['杨'] == '数据分析') or (a['黄'] != '视频剪辑')      # 除非杨数据分析，否则黄不视频剪辑
    c3 = (a['吴'] != '绘图') or (a['黄'] == '视频剪辑')          # 吴不绘图 或 黄视频剪辑
    c4 = (a['郑'] != '写作') or (a['杨'] != '数据分析')          # 郑写作 → 杨不数据分析（只有…才…）
    return c1 and c2 and c3 and c4

sols = [dict(zip(P, t)) for t in itertools.product(TOOLS, repeat=5) if ok(dict(zip(P, t)))]
opts = {
    'A': lambda a: a['陈'] == '写作' or a['郑'] == '写作',
    'B': lambda a: not (a['陈'] == '写作' and a['郑'] == '写作'),
    'C': lambda a: a['陈'] != '写作' or a['郑'] == '写作',
    'D': lambda a: a['陈'] == '写作' or a['郑'] != '写作',
}
print('满足条件的情形数:', len(sols))
for k, f in opts.items():
    bad = [s for s in sols if not f(s)]
    print(k, '一定为真' if not bad else f'不一定为真，反例: {bad[0]}')
# 若不要求每类工具都有人用，上面即全部；若要求4类工具都有人用，再检验一次
sols2 = [s for s in sols if set(s.values()) == set(TOOLS)]
print('（附）要求4类工具都有人用时的情形数:', len(sols2))
for k, f in opts.items():
    print(k, all(f(s) for s in sols2))
