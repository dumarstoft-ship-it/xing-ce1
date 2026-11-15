#!/usr/bin/env python3
"""M03 第71-90题：舍入敏感性 + 能源表来源一致性探查。

Part 1  对依赖“显示舍入数据”的题，枚举输入的舍入区间（整数±0.5、一位小数±0.05），
        检查最接近选项/判断结论是否会翻转。
Part 2  能源双表：检查每行各分项是否等于“总量×0.1%精度的构成比”（统计年鉴常见做法），
        以判断转写是否自洽、2022年行是否存在特殊处理。只读 题目.jsonl。

用法: python3 sensitivity_and_provenance.py [repo_root]
"""
import json, sys, itertools

repo = sys.argv[1] if len(sys.argv) > 1 else '/home/user/xing-ce1'
Q = {}
for line in open(repo + '/广东行测18套模拟/M03/题目.jsonl', encoding='utf-8'):
    d = json.loads(line)
    Q[d['number']] = d


def lohi(v, half):
    return (v - half, v + half)


def closest(v, opts):
    return min(opts, key=lambda k: abs(v - opts[k]))


print('Part 1  舍入敏感性')
# 74
vals = [((1 + a / 100) / (1 + b / 100) - 1) * 100 for a in lohi(4.4, .05) for b in lohi(9.4, .05)]
print('  74: 2025Q1同比区间 %.3f%% ~ %.3f%%（选项边界-5%%）→ 始终“下降不到5%%”' % (min(vals), max(vals)))
# 75 B, D
print('  75B: 电视用户 %.1f ~ %.1f 万户（>3000）' % (2905 / 0.895, 2905 / 0.885))
vals = [10803 * g / (1 + g) for g in (2.45, 2.55)]
print('  75D: 增长额 %.1f ~ %.1f 亿元（>7500，D恒错）' % tuple(vals))
# 80 item 2
vals = [5107.65 * g / (1 + g) for g in (0.2555, 0.2565)] + [5107.75 * g / (1 + g) for g in (0.2555, 0.2565)]
print('  80②: 2013利润增量 %.1f ~ %.1f 亿元（>1000）' % (min(vals), max(vals)))
# 81
opts81 = {'A': 10189, 'B': 11236, 'C': 12058, 'D': 13131}
vals = [d - c / (1 + g / 100) for d in lohi(22247, .5) for c in lohi(14060, .5) for g in lohi(16.6, .05)]
print('  81: 2022H2 %.1f ~ %.1f 万台；最接近项集合 %s' % (min(vals), max(vals), sorted({closest(v, opts81) for v in vals})))
# 82
vals = [(c - b) / (b - a) * 100 - 100 for a in lohi(15722, .5) for b in lohi(17492, .5) for c in lohi(18960, .5)]
print('  82: 10月环比 %.2f%% ~ %.2f%%' % (min(vals), max(vals)))
# 83
opts83 = {'A': 16.6, 'B': 20.8, 'C': 23.2, 'D': 28.3}
vals = []
for x6, x5, g6, g5 in itertools.product(lohi(14060, .5), lohi(11425, .5), lohi(16.6, .05), lohi(14.2, .05)):
    vals.append(((x6 - x5) / (x6 / (1 + g6 / 100) - x5 / (1 + g5 / 100)) - 1) * 100)
print('  83: 6月当月同比 %.2f%% ~ %.2f%%；最接近项集合 %s（编辑记录27.69%%~28.90%%）' % (
    min(vals), max(vals), sorted({closest(v, opts83) for v in vals})))
# 84
opts84 = {'A': -13.9, 'B': -16.5, 'C': 13.9, 'D': 16.5}
vals = [((1 - a / 100) / (1 + b / 100) - 1) * 100 for a in lohi(15.4, .05) for b in lohi(1.3, .05)]
print('  84: 单价增速 %.3f%% ~ %.3f%%；最接近项集合 %s' % (min(vals), max(vals), sorted({closest(v, opts84) for v in vals})))
print('  86/87/89/90/76/79: 输入均为表内整数或一位小数直接相除，无舍入翻转风险（最近边界：89题均值24053.4距24000；90A 2022年|差|10042距10000）')

print('\nPart 2  能源表：分项 = 总量 × 构成比(0.1%) ?')
tabs = [b for m in Q[86]['materials'] for b in m['blocks'] if b['type'] == 'table']
for t in tabs:
    print('  ' + t['title'])
    for r in t['rows']:
        y = r[0]; tot, *parts = [int(x) for x in r[1:]]
        shares = [p / tot * 100 for p in parts]
        round_ok = [abs(round(s, 1) * tot / 100 - p) <= 1 for s, p in zip(shares, parts)]
        print('    %s 总量 %d 构成 %s  分项=总量×一位小数构成? %s' % (
            y, tot, ' / '.join('%.3f' % s for s in shares), round_ok))
# Probe the 2022 rows against the totals that make coal/oil/gas round.
for name, tot_try, sh in (('生产', 466000, (67.4, 6.3, 5.9, 20.4)), ('消费', 541000, (56.2, 17.9, 8.4, 17.5))):
    t = tabs[0] if name == '生产' else tabs[1]
    r = [x for x in t['rows'] if x[0] == '2022'][0]
    tot, *parts = [int(x) for x in r[1:]]
    implied = [round(tot_try * s / 100) for s in sh]
    print('  2022%s: 表中 %s 总量 %d；若总量=%d、构成=%s → %s 总量差 %d' % (
        name, parts, tot, tot_try, sh, implied, tot_try - tot))
print('  （探查用，仅说明2022行“其他能源/总量”与前三项的取数口径可能不同；表内行和自洽，不影响作答。'
      '466000/541000及构成比为审稿人记忆中的统计年鉴值，未在仓库内核实。）')
