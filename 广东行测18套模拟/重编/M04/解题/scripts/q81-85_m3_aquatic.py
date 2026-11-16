#!/usr/bin/env python3
"""M04 资料分析第3组（第81—85题）：2022年6月—2023年5月全国水产品进出口。

用法：python3 q81-85_m3_aquatic.py
统计表从 ../../输入/data.json 读取；第85题四个选项图从模考资源目录读取，
用 Pillow 腐蚀掉细线、留下圆点标记，量出三个节点的像素坐标，与实际环比增速序列比对。
"""
import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter
import numpy as np

HERE = Path(__file__).resolve()
DATA = HERE.parents[2] / '输入' / 'data.json'
ASSETS = HERE.parents[5] / '模考' / '2026下半年广东卷_16-33季_AI可读'
MID = 'gd-mock-2026h2-s19-m3'

d = json.loads(DATA.read_text(encoding='utf-8'))
m = next(m for m in d['materials'] if m['id'] == MID)
tb = m['blocks'][0]
assert tb['type'] == 'table' and '统计表' in tb['title']


def num(s):
    return float(s.replace('−', '-'))


rows = {r[0]: [num(x) for x in r[1:]] for r in tb['rows']}
MONTHS = list(rows)
def col(i):
    return {k: v[i] for k, v in rows.items()}


# 进口数量、进口数量增速、进口金额、进口金额增速、出口数量、出口数量增速、出口金额、出口金额增速
IQ, IQG, IV, IVG, EQ, EQG, EV, EVG = (col(i) for i in range(8))


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据检查：12个月互不重叠，同比基期（2021年6月—2022年5月）不在表内，无分项合计可对；')
print('  反推的2022年1—5月进口金额均为正且量级与表内各月相当，未见矛盾。')
print('  表格标题为“统计表”（未标“图”），按表格排印。')

print('=' * 70)
print('第81题  2022年下半年（7—12月）贸易差额 = 出口金额 − 进口金额')
H2 = ['2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2022-12']
ex, im = sum(EV[k] for k in H2), sum(IV[k] for k in H2)
print(f'  出口 {" + ".join(f"{EV[k]:.0f}" for k in H2)} = {ex:.0f}')
print(f'  进口 {" + ".join(f"{IV[k]:.0f}" for k in H2)} = {im:.0f}')
bal = ex - im
print(f'  差额 {bal:+.0f} 亿元 ⇒ ' + ('顺差' if bal > 0 else '逆差') + f' {abs(bal):.0f} 亿元')
a81 = ('A' if abs(bal) >= 10 else 'C') if bal > 0 else ('B' if abs(bal) >= 10 else 'D')
print(f'  → {a81}')
bal6 = bal + EV['2022-06'] - IV['2022-06']
print(f'  干扰：误把6月算进下半年得 {bal6:+.0f}（顺差26亿元，A）')

print('=' * 70)
print('第82题  2023年1—5月平均进口单价 = 进口金额÷进口数量（亿元/万吨 = 万元/吨）')
c82 = 0
for k in ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05']:
    p = IV[k] / IQ[k]
    lo, hi = (IV[k] - .5) / (IQ[k] + .5), (IV[k] + .5) / (IQ[k] - .5)
    c82 += p > 3
    print(f'  {k}: {IV[k]:.0f}/{IQ[k]:.0f} = {p:.4f} 万元/吨  {">3" if p > 3 else "≤3"}'
          f'   （按表中数据舍入±0.5的区间 {lo:.3f}～{hi:.3f}，结论不变：{(lo > 3) == (hi > 3)}）')
a82, _ = pick(c82, {'A': 1, 'B': 2, 'C': 4, 'D': 5})
print(f'  个数 {c82} → {a82}')

print('=' * 70)
print('第83题  2022年1—5月进口金额 = 2023年同月 ÷ (1 + 同比增速)，逐月累计')
cum, a83 = 0.0, None
for i, k in enumerate(['2023-01', '2023-02', '2023-03', '2023-04', '2023-05'], start=1):
    base = IV[k] / (1 + IVG[k] / 100)
    cum += base
    print(f'  2022年{i}月: {IV[k]:.0f}/{1+IVG[k]/100:.3f} = {base:.3f}，累计 {cum:.3f}')
    if a83 is None and cum > 300:
        a83 = {3: 'A', 4: 'B', 5: 'C', 6: 'D'}[i]
        print(f'    ← 首次超过300亿元：{i}月')
print(f'  → {a83}')

print('=' * 70)
print('第84题  平均出口单价同比 = (1+金额增速)/(1+数量增速) − 1，低于上年同期 ⇔ 金额增速 < 数量增速')
c84 = []
for k in MONTHS:
    g = (1 + EVG[k] / 100) / (1 + EQG[k] / 100) - 1
    if g < 0:
        c84.append(k)
    print(f'  {k}: 金额 {EVG[k]:+.1f}%  数量 {EQG[k]:+.1f}%  单价同比 {g*100:+.3f}%' + ('  ← 低于上年' if g < 0 else ''))
a84, _ = pick(len(c84), {'A': 2, 'B': 4, 'C': 8, 'D': 10})
print(f'  个数 {len(c84)}（{c84}）→ {a84}')

print('=' * 70)
print('第85题  2023年1—3月出口金额环比增速')
seq = ['2022-12', '2023-01', '2023-02', '2023-03']
mom = [(EV[seq[i + 1]] / EV[seq[i]] - 1) * 100 for i in range(3)]
for i in range(3):
    print(f'  {seq[i+1]}: {EV[seq[i+1]]:.0f}/{EV[seq[i]]:.0f} − 1 = {mom[i]:+.3f}%')
steps = [mom[1] - mom[0], mom[2] - mom[1]]
print(f'  相邻变化 {[round(s, 3) for s in steps]}（先小降，后大升；降幅/升幅 = {abs(steps[0])/abs(steps[1]):.4f}）')

# 用作辨析的其他序列
yoy = [EVG[k] for k in seq[1:]]
imom = [(IV[seq[i + 1]] / IV[seq[i]] - 1) * 100 for i in range(3)]
print(f'  对照：出口金额同比 {yoy}；进口金额环比 {[round(v, 2) for v in imom]}')


def comps(mask):
    H, W = mask.shape
    seen = np.zeros_like(mask, bool)
    out = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not seen[y, x]:
                q = deque([(y, x)])
                seen[y, x] = True
                pts = []
                while q:
                    cy, cx = q.popleft()
                    pts.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                q.append((ny, nx))
                out.append((sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts)))
    return sorted(out)


q85 = next(q for q in d['questions'] if q['number'] == 85)


def fit(vals, dh):
    st = np.array([vals[1] - vals[0], vals[2] - vals[1]], float)
    same = all((s > 0) == (t > 0) for s, t in zip(st, dh))
    c = float(np.dot(st, dh) / np.dot(st, st))
    resid = float(np.sqrt(np.mean((np.array(dh) - c * st) ** 2)))
    return same, c, resid


a85, fits = None, {}
for k in 'ABCD':
    fig = q85['options'][k][0]
    im_ = Image.open(ASSETS / fig['path']).convert('L')
    er = np.array(im_.filter(ImageFilter.MaxFilter(5)))      # 腐蚀掉约3像素宽的线，只留圆点
    pts = comps(er < 128)
    assert len(pts) == 3, (k, pts)
    h = [-y for _, y in pts]
    dh = [h[1] - h[0], h[2] - h[1]]
    same, c, resid = fit(mom, dh)
    same_y, _, resid_y = fit(yoy, dh)
    same_i, _, resid_i = fit(imom, dh)
    print(f'  选项{k} {fig["path"]}: 节点 {[(round(x,1), round(y,1)) for x, y in pts]}，高度变化 {[round(v,1) for v in dh]}'
          f'；与出口金额环比走势相同={same}（残差 {resid:.1f}）'
          f'；与出口金额同比相同={same_y}（残差 {resid_y:.1f}）；与进口金额环比相同={same_i}（残差 {resid_i:.1f}）')
    if same:
        fits[k] = resid
        ratio = abs(dh[0]) / abs(dh[1])
        print(f'    升降方向一致；该图第一段/第二段幅度之比 = {ratio:.4f}，实际 {abs(steps[0])/abs(steps[1]):.4f}')
a85 = min(fits, key=fits.get)
print(f'  升降方向一致的选项 {list(fits)}，残差 { {k: round(v, 1) for k, v in fits.items()} }；'
      f'D是“先大降后小升”，与“先小降后大升”幅度相反')
assert sorted(fits.values())[1] > 20 * fits[a85]
print(f'  → {a85}（B恰是出口金额同比增速的走势，A恰是进口金额环比增速的走势）')

print('=' * 70)
print(f'答案：81{a81} 82{a82} 83{a83} 84{a84} 85{a85}')
