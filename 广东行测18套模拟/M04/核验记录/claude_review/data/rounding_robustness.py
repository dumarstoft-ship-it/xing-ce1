#!/usr/bin/env python3
"""第71—90题舍入稳健性：把每个显示值视为“末位±半个单位”的区间，
枚举各输入的上下端点（角点），看计算结果的范围是否仍落在同一最接近选项。
这是对“按显示值作答”之外的额外检查，用来区分“答案对舍入稳健”与“只能按显示值作答”。
运行：python3 -I rounding_robustness.py
"""
from decimal import Decimal
from itertools import product


def half_unit(s):
    """显示值字符串 → 半个末位单位。"""
    d = Decimal(s)
    exp = d.as_tuple().exponent
    return float(Decimal(1).scaleb(exp)) / 2


def corners(vals):
    """vals: list of display strings → 每个输入的(低,高)角点组合。"""
    rng = [(float(v) - half_unit(v), float(v) + half_unit(v)) for v in vals]
    return product(*rng)


def nearest(x, opts):
    return min(opts, key=lambda k: abs(x - opts[k]))


def report(name, f, vals, opts, exact_inputs=False):
    shown = f(*[float(v) for v in vals])
    if exact_inputs:
        lo = hi = shown
    else:
        outs = [f(*c) for c in corners(vals)]
        lo, hi = min(outs), max(outs)
    keys = {nearest(lo, opts), nearest(hi, opts), nearest(shown, opts)}
    # 区间内是否跨越选项分界：检查区间端点及分界点
    srt = sorted(opts.items(), key=lambda kv: kv[1])
    bounds = [(a[1] + b[1]) / 2 for a, b in zip(srt, srt[1:])]
    crosses = [b for b in bounds if lo < b < hi]
    verdict = "稳健（区间内最接近项不变）" if not crosses else f"不稳健：区间跨过选项分界 {crosses}，只能按显示值作答"
    print(f"{name}: 显示值计算={shown:.4f}，舍入区间=[{lo:.4f}, {hi:.4f}]，最接近项={nearest(shown, opts)}；{verdict}")


report("Q73 修复占比%", lambda a, b: b / (a + b) * 100, ["4931", "2682"],
       {"A": 35.2, "B": 40.1, "C": 45.8, "D": 51.3}, exact_inputs=True)
report("Q74 年均万场", lambda x: x / 5, ["7.39"], {"A": 1.28, "B": 1.48, "C": 1.65, "D": 1.92})
report("Q76 占比变化pp",
       lambda r, t, gr, gt: (r / t - (r / (1 + gr / 100)) / (t / (1 + gt / 100))) * 100,
       ["823.05", "1168.53", "-0.6", "0.8"], {"A": -1.0, "B": -1.4, "C": 1.0, "D": 1.4})
report("Q77 2022非住宅施工面积",
       lambda t, gt, r, gr: t / (1 + gt / 100) - r / (1 + gr / 100),
       ["15375.68", "-4.4", "10467.79", "-4.3"], {"A": 4691.4, "B": 4907.8, "C": 5145.2, "D": 10938.1})
report("Q79 非住宅销售额增量",
       lambda t, gt, r, gr: (t - r) - (t / (1 + gt / 100) - r / (1 + gr / 100)),
       ["1167.46", "32.1", "989.70", "29.4"], {"A": 59, "B": -60, "C": 30, "D": 225})
report("Q81 上半年月均",
       lambda a, b, c, d, e, f: (a + b + c + d + e + f) / 6,
       ["201.6", "193.0", "269.6", "409.4", "447.6", "553.3"], {"A": 345.8, "B": 362.4, "C": 386.1, "D": 406.5})
report("Q82 单价同比%", lambda ga, gq: ((1 + ga / 100) / (1 + gq / 100) - 1) * 100,
       ["295", "586.9"], {"A": 73.9, "B": 42.5, "C": -73.9, "D": -42.5})
report("Q83 金额环比%",
       lambda a1, a2, a3, a4, a5, a6: ((a4 + a5 + a6) / (a1 + a2 + a3) - 1) * 100,
       ["3.5", "3.2", "3.8", "6.1", "5.6", "7.6"], {"A": 80.1, "B": 83.8, "C": 85.5, "D": 88.2})
report("Q84 4月单价(阈值150)", lambda a, q: a / q * 1e4, ["6.1", "409.4"],
       {"≤150侧": 149.0, ">150侧": 151.0})
report("Q86 月均差", lambda o, g: (o - g) / 12, ["13050", "6847"],
       {"A": 253, "B": 412, "C": 517, "D": 661}, exact_inputs=True)
report("Q88 2022国铁周转量占比%",
       lambda n, gn, t, d: (n / (1 + gn / 100)) / (t - d) * 100,
       ["32638.50", "-0.1", "36460.39", "514.70"], {"A": 77, "B": 89, "C": 91, "D": 95})
report("Q89 年均增加亿吨", lambda a, b: (a - b) / 3 / 1e4, ["503535", "455236"],
       {"A": 2.2, "B": 2.0, "C": 1.8, "D": 1.6}, exact_inputs=True)

# Q78 施工面积一对（唯一接近边界的一对）
outs = []
for gt, gr in corners(["-4.4", "-4.3"]):
    t0 = 15375.68 / (1 + gt / 100); r0 = 10467.79 / (1 + gr / 100)
    gn = (15375.68 - 10467.79) / (t0 - r0) - 1
    outs.append(gr - gn * 100)
print(f"Q78 施工面积 住宅增速−非住宅增速（百分点）区间=[{min(outs):.4f}, {max(outs):.4f}]；"
      "仅在总增速与住宅增速同取−4.35%的退化角点相等，其余均为住宅更快")

# Q87 两个平均运距方向
for name, gT, gV in (("国家铁路", "-0.1", "0.2"), ("其他铁路", "16.6", "3.9")):
    vals = [((1 + a / 100) / (1 + b / 100) - 1) * 100 for a, b in corners([gT, gV])]
    print(f"Q87 {name}平均运距变化% 区间=[{min(vals):.4f}, {max(vals):.4f}] → 符号{'恒负' if max(vals) < 0 else '恒正' if min(vals) > 0 else '不定'}")

# Q85 各项
a = [5.6 / (1 + x / 100) + 7.6 / (1 + y / 100) for x, y in corners(["34.1", "121.0"])]
print(f"Q85A 2023年5—6月金额和区间=[{min(a):.3f}, {max(a):.3f}]（远低于10）")
b = [(193.0 / (1 + y / 100)) - (201.6 / (1 + x / 100)) for x, y in corners(["6.7", "-10.4"])]
print(f"Q85B 2023年2月减1月数量区间=[{min(b):.3f}, {max(b):.3f}]（恒正→2月高于1月）")
c = [(596.7 / (1 + x / 100)) / (65.2 / (1 + y / 100)) for x, y in corners(["910.9", "163.6"])]
print(f"Q85C 2023年10月越南/香港倍数区间=[{min(c):.3f}, {max(c):.3f}]（远非9倍）")
