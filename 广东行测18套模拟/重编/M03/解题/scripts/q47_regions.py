# 第47题：统计九宫格各图及选项的封闭区域数（白色连通域数-1）、连通部分数
from collections import deque
import numpy as np
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p11_i01.png'
im = Image.open(IMG).convert('L')
cells = {'(1,1)': (54, 11, 149, 100), '(1,2)': (153, 11, 248, 100), '(1,3)': (252, 11, 347, 100),
         '(2,1)': (54, 105, 149, 199), '(2,2)': (153, 105, 248, 199), '(2,3)': (252, 105, 347, 199),
         '(3,1)': (54, 205, 149, 299), '(3,2)': (153, 205, 248, 299),
         'A': (10, 333, 102, 428), 'B': (106, 333, 198, 428), 'C': (203, 333, 295, 428), 'D': (299, 333, 392, 428)}


def label(bw, eight):
    h, w = bw.shape
    lab = np.zeros((h, w), int); n = 0; sizes = []
    nb = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)] if eight else \
        [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for y in range(h):
        for x in range(w):
            if bw[y, x] and not lab[y, x]:
                n += 1; q = deque([(y, x)]); lab[y, x] = n; s = 0
                while q:
                    cy, cx = q.popleft(); s += 1
                    for dy, dx in nb:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and bw[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; q.append((ny, nx))
                sizes.append(s)
    return n, sizes


res = {}
for k, box in cells.items():
    a = np.array(im.crop(box)) < 140
    parts, _ = label(a, True)
    nw, ws = label(~a, False)
    regions = sorted(ws, reverse=True)[1:]          # 去掉最大的背景
    res[k] = len(regions)
    print(f'{k}: 部分数={parts}  封闭区域数={len(regions)}  区域像素={regions}')
print('每行封闭区域数之和：第一行', res['(1,1)'] + res['(1,2)'] + res['(1,3)'],
      '第二行', res['(2,1)'] + res['(2,2)'] + res['(2,3)'],
      '第三行前两图', res['(3,1)'] + res['(3,2)'])
print('注：B项约27像素的小区域是椭圆右侧与三角形右下角之间的小块，属正常区域，B共7个区域；'
      '选项中只有A为5个区域，满足每行之和14')
