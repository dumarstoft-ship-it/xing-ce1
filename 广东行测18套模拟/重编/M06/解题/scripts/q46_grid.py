"""第46题：读出每幅9x9方格图的黑格位置，检验规律。
做法：按灰度找出每幅图的格线，取每个小格中心区域的平均灰度判黑白。"""
from PIL import Image
import numpy as np

PATH = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i00.png'
im = np.array(Image.open(PATH).convert('L')).astype(int)

def lines_1d(profile, thr):
    idx = [i for i, v in enumerate(profile) if v >= thr]
    groups = []
    for i in idx:
        if groups and i - groups[-1][-1] <= 1:
            groups[-1].append(i)
        else:
            groups.append([i])
    return [(g[0] + g[-1]) / 2 for g in groups]

def read_grid(x0, x1, y0, y1, n=9):
    sub = im[y0:y1, x0:x1]
    # 格线：整列/整行较多暗像素；但黑格也暗，所以改用等分：先找外框
    dark = sub < 128
    colp = dark.sum(axis=0)
    rowp = dark.sum(axis=1)
    cl = lines_1d(colp, 0.75 * colp.max())
    rl = lines_1d(rowp, 0.75 * rowp.max())
    left, right = cl[0], cl[-1]
    top, bot = rl[0], rl[-1]
    cw = (right - left) / n
    ch = (bot - top) / n
    g = []
    for r in range(n):
        row = []
        for c in range(n):
            cx = x0 + left + (c + 0.5) * cw
            cy = y0 + top + (r + 0.5) * ch
            patch = im[int(cy) - 2:int(cy) + 3, int(cx) - 2:int(cx) + 3]
            row.append(1 if patch.mean() < 128 else 0)
        g.append(row)
    return g, (left, right, top, bot)

def show(g):
    return '\n'.join(''.join('#' if v else '.' for v in row) for row in g)

# 题干5幅：每幅约97px宽，内格区域
panels_top = [(10, 102), (107, 200), (204, 297), (302, 394), (399, 492)]
# 选项4幅：先找竖向分隔
grids = {}
for k, (a, b) in enumerate(panels_top):
    g, box = read_grid(a, b, 10, 106)
    grids[f'图{k+1}'] = g
# 选项区域
dark = im[130:245, :] < 128
colp = dark.sum(axis=0)
print('option region strong cols:', [x for x, v in enumerate(colp) if v > 100])

panels_opt = [(108, 203), (206, 300), (303, 398), (401, 496)]
for k, (a, b) in enumerate(panels_opt):
    g, box = read_grid(a, b, 139, 237)
    grids['ABCD'[k]] = g

if __name__ == '__main__':
    for name, g in grids.items():
        print(name, '黑格数', sum(map(sum, g)))
        print(show(g))
        print()

# 规律检验：整体向左上平移1格（出界部分从对边补回）
def shift_ul(g):
    n = len(g)
    return [[g[(r + 1) % n][(c + 1) % n] for c in range(n)] for r in range(n)]

if __name__ == '__main__':
    seq = [grids[f'图{i}'] for i in range(1, 6)]
    for i in range(4):
        print(f'图{i+1}左上平移1格 == 图{i+2}:', shift_ul(seq[i]) == seq[i + 1])
    pred = shift_ul(seq[4])
    print('预测第6幅:')
    print(show(pred))
    for k in 'ABCD':
        diff = sum(pred[r][c] != grids[k][r][c] for r in range(9) for c in range(9))
        print(k, '与预测不同的格数:', diff)
