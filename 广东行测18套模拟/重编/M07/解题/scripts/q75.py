"""第75题：2022年10-12月空调产量环比增量的走势，与四个折线图选项逐点对照。
环比增量 = 当月产量 - 上月产量；当月产量 = 相邻累计相减。"""
from q71_75_group1_data import cum
import numpy as np
from PIL import Image, ImageFilter

m = {}
ks = ['2022-08', '2022-09', '2022-10', '2022-11', '2022-12']
for a, b in zip(ks, ks[1:]):
    m[b] = cum[b][0] - cum[a][0]
inc = {k: m[k] - m[p] for p, k in zip(['2022-09', '2022-10', '2022-11'], ['2022-10', '2022-11', '2022-12'])}
print('当月产量:', m)
print('环比增量（10、11、12月）:', inc)
seq = list(inc.values())
print('相邻两段变化:', [seq[1]-seq[0], seq[2]-seq[1]], '-> 两段都上升，前段略陡')

# 读取选项图中方形标记的中心（像素y向下，取负即数值方向）
BASE = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/'
files = {'A': 's22_p19_i01', 'B': 's22_p19_i02', 'C': 's22_p20_i00', 'D': 's22_p20_i01'}

def markers(path):
    a = np.array(Image.open(path).convert('L')) < 128
    er = np.array(Image.fromarray((a*255).astype('uint8')).filter(ImageFilter.MinFilter(7))) > 0
    H, W = er.shape
    lab = np.zeros((H, W), int); n = 0
    for y in range(H):
        for x in range(W):
            if er[y, x] and not lab[y, x]:
                n += 1; st = [(y, x)]; lab[y, x] = n
                while st:
                    cy, cx = st.pop()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = cy+dy, cx+dx
                            if 0 <= yy < H and 0 <= xx < W and er[yy, xx] and not lab[yy, xx]:
                                lab[yy, xx] = n; st.append((yy, xx))
    pts = []
    for i in range(1, n+1):
        ys, xs = np.nonzero(lab == i)
        pts.append((xs.mean(), ys.mean()))
    return sorted(pts)

for k, f in files.items():
    pts = markers(BASE + f + '.png')
    ys = [p[1] for p in pts]
    d1, d2 = ys[0]-ys[1], ys[1]-ys[2]   # 正=上升
    shape = {(True, True): '升-升', (False, False): '降-降', (False, True): '降-升(V)', (True, False): '升-降(倒V)'}[(d1 > 0, d2 > 0)]
    line = f'{k}: 标记中心 ' + ', '.join(f'({x:.1f},{y:.1f})' for x, y in pts) + f'  两段像素升幅 {d1:.1f}, {d2:.1f}  形状 {shape}'
    if k == 'A':
        # 用首末两点定比例尺，预测中间点位置
        scale = (seq[2]-seq[0]) / (ys[0]-ys[2])
        y_mid = ys[0] - (seq[1]-seq[0]) / scale
        line += f'\n    按首末点定标尺（每像素{scale:.2f}万台），11月应在 y={y_mid:.1f}，实测 y={ys[1]:.1f}'
        # 对照：若画的是当月产量本身
        mm = [m['2022-10'], m['2022-11'], m['2022-12']]
        y_mid2 = ys[0] - (mm[1]-mm[0]) / ((mm[2]-mm[0])/(ys[0]-ys[2]))
        line += f'\n    若画的是当月产量(1468,1489,1798)，11月应在 y={y_mid2:.1f}，与实测不符'
    print(line)

# 易错：不算增量，直接拿表中10-12月的累计同比增速作图
g = [cum[k][1] for k in ['2022-10', '2022-11', '2022-12']]
print('拿累计同比增速作图：', g, '-> 逐月下降，对应C')
# 对照：环比增长率、当月产量的走势也都是上升，不会改变答案
rr = [round(100*(m[k]/m[p]-1), 2) for p, k in zip(['2022-09', '2022-10', '2022-11'], ['2022-10', '2022-11', '2022-12'])]
print('环比增长率(%)：', rr, '（同为上升）')
