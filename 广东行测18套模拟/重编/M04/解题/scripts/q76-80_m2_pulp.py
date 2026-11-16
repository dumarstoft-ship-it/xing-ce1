#!/usr/bin/env python3
"""M04 资料分析第2组（第76—80题）：2015—2022年全国纸浆消耗。

用法：python3 q76-80_m2_pulp.py
文字与两张表从 ../../输入/data.json 读取；第80题题图从模考资源目录读取，
用 Pillow 量出折线各节点的像素纵坐标，与各选项的同比增量序列比对。
"""
import json
from pathlib import Path

from PIL import Image
import numpy as np

HERE = Path(__file__).resolve()
DATA = HERE.parents[2] / '输入' / 'data.json'
ASSETS = HERE.parents[5] / '模考' / '2026下半年广东卷_16-33季_AI可读'
MID = 'gd-mock-2026h2-s19-m2'

d = json.loads(DATA.read_text(encoding='utf-8'))
m = next(m for m in d['materials'] if m['id'] == MID)
text = m['blocks'][0]['text']
t1, t2 = m['blocks'][1], m['blocks'][2]
assert t1['title'].startswith('图1') and t2['title'].startswith('图2')
for s in ['2022年全国纸浆消耗总量11295万吨', '国产纸浆消耗量8722万吨，占纸浆消耗总量的77.2%',
          '进口纸浆消耗量2573万吨，占纸浆消耗总量的22.8%']:
    assert s in text, s

YEARS = [int(r[0]) for r in t1['rows']]
DOM = {int(r[0]): int(r[1]) for r in t1['rows']}       # 国产纸浆
IMP = {int(r[0]): int(r[2]) for r in t1['rows']}       # 进口纸浆
WASTE = {int(r[0]): int(r[1]) for r in t2['rows']}     # 废纸浆
NONW = {int(r[0]): int(r[2]) for r in t2['rows']}      # 非木浆
WOOD = {int(r[0]): int(r[3]) for r in t2['rows']}      # 木浆
TOT = {y: DOM[y] + IMP[y] for y in YEARS}


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据自洽检查')
ok = True
for y in YEARS:
    s = WASTE[y] + NONW[y] + WOOD[y]
    flag = '' if s == DOM[y] else '  ← 不一致'
    ok &= s == DOM[y]
    print(f'  {y}: 废{WASTE[y]}+非木{NONW[y]}+木{WOOD[y]} = {s}  vs 国产 {DOM[y]}{flag}；总量 {TOT[y]}')
print(f'  图2三项之和与图1国产纸浆逐年相符：{ok}')
assert ok
assert TOT[2022] == 11295
print(f'  2022年：8722+2573 = {TOT[2022]}（文字11295）；国产占 {DOM[2022]/TOT[2022]*100:.3f}%（文字77.2%），'
      f'进口占 {IMP[2022]/TOT[2022]*100:.3f}%（文字22.8%）→ 一致')

print('=' * 70)
print('第76题  进口纸浆占比 2022 vs 2021')
s22 = IMP[2022] / TOT[2022] * 100
s21 = IMP[2021] / TOT[2021] * 100
a = IMP[2022] / IMP[2021] - 1
b = TOT[2022] / TOT[2021] - 1
fml = s22 * (a - b) / (1 + a)
print(f'  2022 {IMP[2022]}/{TOT[2022]} = {s22:.4f}%；2021 {IMP[2021]}/{TOT[2021]} = {s21:.4f}%；'
      f'差 {s22 - s21:+.4f} 个百分点')
print(f'  公式核对：a={a*100:.3f}%，b={b*100:.3f}%，现期比重×(a−b)/(1+a) = {fml:+.4f}')
a76, dd = pick(s22 - s21, {'A': -1.6, 'B': 1.6, 'C': -3.7, 'D': 3.7})
print(f'  → {a76}  偏差 {dd}')

print('=' * 70)
print('第77题  2016—2022年国产非木浆同比增速')
g_nonw = {y: NONW[y] / NONW[y - 1] - 1 for y in YEARS[1:]}
for y, g in g_nonw.items():
    print(f'  {y}: {NONW[y]}/{NONW[y-1]} − 1 = {g*100:+.3f}%   （同年废纸浆 {(WASTE[y]/WASTE[y-1]-1)*100:+.3f}%）')
ymax = max(g_nonw, key=g_nonw.get)
v77 = (WASTE[ymax] / WASTE[ymax - 1] - 1) * 100
print(f'  非木浆增速最快：{ymax}年；当年废纸浆 {WASTE[ymax]}/{WASTE[ymax-1]} − 1 = {v77:+.4f}%')
a77, dd = pick(v77, {'A': -13.6, 'B': -0.4, 'C': 11.2, 'D': 12.5})
print(f'  → {a77}  偏差 {dd}')
print(f'  干扰：A=2018年废纸浆 {(WASTE[2018]/WASTE[2017]-1)*100:+.2f}%（非木浆增速第二），'
      f'B=2017年废纸浆 {(WASTE[2017]/WASTE[2016]-1)*100:+.2f}%')

print('=' * 70)
print('第78题  2016—2022年国产废纸浆累计')
v78 = sum(WASTE[y] for y in range(2016, 2023))
print(f'  {" + ".join(str(WASTE[y]) for y in range(2016, 2023))} = {v78} 万吨 = {v78/1e4:.4f} 亿吨')
a78, dd = pick(v78 / 1e4, {'A': 3.9, 'B': 4.1, 'C': 4.4, 'D': 4.7})
print(f'  → {a78}  偏差 {dd}')
print(f'  干扰：误含2015年得 {(v78 + WASTE[2015])/1e4:.4f} 亿吨（≈D）')

print('=' * 70)
print('第79题  国产纸浆占比（各年）')
shares = {y: DOM[y] / TOT[y] * 100 for y in YEARS}
for y in YEARS:
    print(f'  {y}: {DOM[y]}/{TOT[y]} = {shares[y]:.3f}%   进口/国产 = {IMP[y]/DOM[y]:.4f}')
ymin = min(shares, key=shares.get)
print(f'  全期最低：{ymin}年')
opts79 = {'A': 2020, 'B': 2019, 'C': 2016, 'D': 2015}
a79 = min(opts79, key=lambda k: shares[opts79[k]])
assert opts79[a79] == ymin
print(f'  → {a79}')

print('=' * 70)
print('第80题  2019—2022年各纸浆同比增量，与题图折线比对')
series = {
    'A 国产纸浆': DOM, 'B 进口纸浆': IMP, 'C 国产非木浆': NONW, 'D 国产木浆': WOOD,
}
inc = {k: [v[y] - v[y - 1] for y in range(2019, 2023)] for k, v in series.items()}
for k, v in inc.items():
    steps = [v[i + 1] - v[i] for i in range(3)]
    print(f'  {k}: 增量 {v}  相邻变化 {steps}  走势 {["升" if s > 0 else "降" for s in steps]}')

# 量题图：四个节点在横向等距的位置，节点处折线最粗（菱形标记）
q80 = next(q for q in d['questions'] if q['number'] == 80)
fig = next(s for s in q80['stem'] if s['type'] == 'figure')
img = np.array(Image.open(ASSETS / fig['path']).convert('L'))
dark = img < 128
cols = [x for x in range(img.shape[1]) if dark[:, x].any()]
cnt = {x: int(dark[:, x].sum()) for x in cols}
x0, x1 = cols[0], cols[-1]
nodes = []
for i in range(4):
    xc = x0 + 2 + i * (x1 - x0 - 4) / 3          # 等距节点的大致位置
    win = [x for x in cols if abs(x - xc) <= 6]
    xm = max(win, key=lambda x: (cnt[x], -abs(x - xc)))   # 窗口内最粗的列 = 标记中心
    ys = np.where(dark[:, xm])[0]
    nodes.append((xm, float(ys.mean())))
print(f'  题图 {fig["path"]}：节点 (x, y像素) = {[(x, round(y, 1)) for x, y in nodes]}')
h = [-y for _, y in nodes]                      # 像素y向下，取负得“高度”
dh = [h[i + 1] - h[i] for i in range(3)]
print(f'  题图相邻节点高度变化（像素）{[round(v, 2) for v in dh]}，走势 {["升" if s > 0 else "降" for s in dh]}')
best = None
for k, v in inc.items():
    steps = np.array([v[i + 1] - v[i] for i in range(3)], float)
    same_shape = all((s > 0) == (t > 0) for s, t in zip(steps, dh))
    # 最小二乘比例：像素 ≈ c × 数值，看残差
    c = float(np.dot(steps, dh) / np.dot(steps, steps))
    resid = float(np.sqrt(np.mean((np.array(dh) - c * steps) ** 2)))
    print(f'  {k}: 走势相同={same_shape}，比例 c={c:.4f} 像素/万吨，均方根残差 {resid:.2f} 像素')
    if same_shape and (best is None or resid < best[1]):
        best = (k, resid, c)
print(f'  → {best[0][0]}（唯一走势相同；按 c={best[2]:.4f} 换算后三段变化 '
      f'{[round(best[2]*s,1) for s in [inc[best[0]][i+1]-inc[best[0]][i] for i in range(3)]]} 像素，'
      f'实测 {[round(v,1) for v in dh]}）')

print('=' * 70)
print(f'答案：76{a76} 77{a77} 78{a78} 79{a79} 80{best[0][0]}')
