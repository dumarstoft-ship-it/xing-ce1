#!/usr/bin/env python3
"""M01 资料分析第1组（第71—75题）：2023年末全国水上运输船舶构成。

用法：python3 q71-75_m1_ship.py
表格直接从 ../../输入/data.json 读取，逐题按材料数据精确计算，并做本组数据自洽检查。
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / '输入' / 'data.json'
MID = 'gd-mock-2026h2-s16-m1'


def num(s):
    s = s.replace('−', '-').replace('—', '').strip()
    return float(s) if s else None


def load():
    d = json.loads(DATA.read_text(encoding='utf-8'))
    m = next(m for m in d['materials'] if m['id'] == MID)
    tb = m['blocks'][0]
    T = {}
    for area, ind, unit, val, g in tb['rows']:
        v = num(val)
        if v is not None and unit == '万艘':
            v *= 1e4                     # 船舶数统一成“艘”
        T[(area, ind)] = (v, num(g) / 100)
    return T


T = load()
AREAS = ['内河', '沿海', '远洋']
IND = ['运输船舶数量', '净载重量', '载客量', '集装箱箱位']


def cur(a, i):
    return T[(a, i)][0]


def r(a, i):
    return T[(a, i)][1]


def base(a, i):
    return cur(a, i) / (1 + r(a, i))


def inc(a, i):
    return cur(a, i) - base(a, i)


def pick(value, opts):
    """opts: {letter: numeric}; 返回最接近的选项及各选项偏差。"""
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据自洽检查（分项和 vs 合计；分项基期和推出的合计增速 vs 表中合计增速）')
for i in IND:
    parts = [cur(a, i) for a in AREAS]
    s = sum(parts)
    tot = cur('合计', i)
    sb = sum(base(a, i) for a in AREAS)
    implied = s / sb - 1
    if tot is None:
        print(f'  {i}: 合计年末数缺（—）；分项和={s:.2f}；分项基期和={sb:.2f}；'
              f'推得合计增速={implied*100:.3f}%（表中{r("合计", i)*100:.1f}%）')
    else:
        totb = tot / (1 + r('合计', i))
        print(f'  {i}: 分项和={s:.2f} 合计={tot:.2f} 差={s-tot:+.2f}；'
              f'分项基期和={sb:.2f} 合计基期={totb:.2f}；'
              f'推得合计增速={implied*100:.3f}%（表中{r("合计", i)*100:.1f}%）')
print('  另：各航区2022年末船舶数（推算）：',
      {a: round(base(a, '运输船舶数量'), 1) for a in AREAS})

print('=' * 70)
print('第71题  内河载客量占全国比重的变化')
a_now, b_now = cur('内河', '载客量'), cur('合计', '载客量')
sh_now = a_now / b_now
sh_base = base('内河', '载客量') / base('合计', '载客量')
d71 = (sh_now - sh_base) * 100
formula = sh_now * (r('内河', '载客量') - r('合计', '载客量')) / (1 + r('内河', '载客量')) * 100
print(f'  现期比重={sh_now*100:.3f}%  基期比重={sh_base*100:.3f}%  变化={d71:+.3f}个百分点'
      f'（公式 a/b×(ra-rb)/(1+ra) = {formula:+.3f}）')
ans71, diffs = pick(d71, {'A': 2.2, 'B': -2.2, 'C': 1.1, 'D': -1.1})
print('  选项偏差', {k: round(v, 3) for k, v in diffs.items()}, '→', ans71)
assert ans71 == 'A'

print('=' * 70)
print('第72题  各航区集装箱箱位同比变化量（万标准箱）')
ch = {a: inc(a, '集装箱箱位') for a in AREAS}
for a in AREAS:
    print(f'  {a}: 现期{cur(a, "集装箱箱位")}，增速{r(a, "集装箱箱位")*100:+.1f}% → 变化量{ch[a]:+.3f}')
signed = sorted(AREAS, key=lambda a: -ch[a])
absval = sorted(AREAS, key=lambda a: -abs(ch[a]))
print('  按带符号增长量排序：', '>'.join(signed), '（对应B）')
print('  按变化量绝对值排序：', '>'.join(absval), '（对应D）')
opts72 = {'A': ['内河', '沿海', '远洋'], 'B': ['沿海', '内河', '远洋'],
          'C': ['远洋', '内河', '沿海'], 'D': ['远洋', '沿海', '内河']}
ans72 = next(k for k, v in opts72.items() if v == absval)
print('  “变化量”按绝对值比较 →', ans72)
assert ans72 == 'D' and next(k for k, v in opts72.items() if v == signed) == 'B'

print('=' * 70)
print('第73题  平均每艘内河船净载重量的增速')
g73 = (1 + r('内河', '净载重量')) / (1 + r('内河', '运输船舶数量')) - 1
avg_now = cur('内河', '净载重量') / cur('内河', '运输船舶数量') * 1e4
avg_base = base('内河', '净载重量') / base('内河', '运输船舶数量') * 1e4
print(f'  (1+1.2%)/(1-2.6%)-1 = {g73*100:.4f}%；平均每艘 {avg_base:.2f}→{avg_now:.2f} 吨')
# 增速四舍五入区间敏感性（仅作说明）
lo = (1 + 0.0115) / (1 - 0.0255) - 1
hi = (1 + 0.0125) / (1 - 0.0265) - 1
print(f'  （增速若在四舍五入区间内变动，结果范围约 {lo*100:.3f}%～{hi*100:.3f}%）')
ans73 = ('D' if g73 > 0.038 else 'C') if g73 > 0 else ('B' if -g73 > 0.038 else 'A')
print('  →', ans73)
assert ans73 == 'D'

print('=' * 70)
print('第74题  远洋与沿海平均每艘载客量之比')
avg_ocean = cur('远洋', '载客量') * 1e4 / cur('远洋', '运输船舶数量')
avg_coast = cur('沿海', '载客量') * 1e4 / cur('沿海', '运输船舶数量')
ratio = avg_ocean / avg_coast
print(f'  远洋={avg_ocean:.3f}客位/艘  沿海={avg_coast:.3f}客位/艘  比值={ratio:.4f}')
ans74, diffs = pick(ratio, {'A': 5 / 3, 'B': 3 / 5, 'C': 5 / 4, 'D': 4 / 5})
print('  选项偏差', {k: round(v, 4) for k, v in diffs.items()}, '→', ans74)
assert ans74 == 'B'

print('=' * 70)
print('第75题  综合判断')
pull = inc('沿海', '集装箱箱位') / base('合计', '集装箱箱位')
print(f'  A: 沿海箱位增量{inc("沿海", "集装箱箱位"):.3f} / 全国上年{base("合计", "集装箱箱位"):.3f}'
      f' = 拉动{pull*100:.3f}% → {"对" if pull > 0.05 else "错"}')
okB = True
for a in AREAS:
    g = (1 + r(a, '载客量')) / (1 + r(a, '运输船舶数量')) - 1
    okB = okB and g < 0
    print(f'  B: {a}平均每艘载客量增速=(1{r(a, "载客量")*100:+.1f}%)/(1{r(a, "运输船舶数量")*100:+.1f}%)-1'
          f' = {g*100:+.4f}%')
print('     → B', '对' if okB else '错（内河持平，并非“均下降”）')
tot_ships = sum(cur(a, '运输船舶数量') for a in AREAS)
trap = 10.66 + cur('沿海', '运输船舶数量') + cur('远洋', '运输船舶数量')
print(f'  C: 船舶总数={tot_ships:.0f}艘≈{tot_ships/1e4:.2f}万艘，不是11655艘'
      f'（把10.66万艘当10.66艘相加得{trap:.2f}）→ 错')
shD = cur('远洋', '净载重量') / cur('合计', '净载重量')
print(f'  D: 远洋净载重量比重={shD*100:.3f}% → {"对" if shD > 0.15 else "错"}')
assert pull < 0.05 and not okB and abs(tot_ships - 11655) > 1000 and shD > 0.15
ans75 = 'D'
print('  →', ans75)

print('=' * 70)
print('第1组答案：', {71: ans71, 72: ans72, 73: ans73, 74: ans74, 75: ans75})
