"""第48题核验：问号方块被遮住的内容，可由图形关于水平中线的对称位置取得
（中心圆、内接正方形、米字线都上下对称；左侧1/4圆的颜色上灰下黑，形状相同）。

做法：截取问号方块关于水平中线 y=138.5 的对称区域，上下翻转，得到问号处应有的线条；
把每个选项分别旋转0/90/180/270度（以及镜像后再旋转，作对照），与之逐像素比较。
只比较线条（深色像素）和灰色块两类像素，输出不一致像素的比例。
"""
import numpy as np
from PIL import Image

IMG = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p12_i01.png"
im = Image.open(IMG).convert("L")
A = np.array(im).astype(int)

BOX = (120, 153, 171, 204)          # 问号方块（含边框）x0,y0,x1,y1
MID_Y = 138.5                         # 水平中线
# 对称区域：y -> 2*MID_Y - y
sym_y0 = int(round(2 * MID_Y - BOX[3]))
sym_y1 = int(round(2 * MID_Y - BOX[1]))
target = A[sym_y0:sym_y1 + 1, BOX[0]:BOX[2] + 1][::-1, :]

OPTS = {"A": (27, 309, 80, 360), "B": (126, 309, 178, 361),
        "C": (222, 309, 276, 360), "D": (319, 309, 373, 361)}

N = 48  # 统一缩放到 N×N 后比较（去掉外框2px）


def classes(arr):
    """0=白, 1=线(黑), 2=灰/黑色块（被1/4圆填充的区域）。
    题图里左侧1/4圆在上方为黑色、问号处为灰色，所以颜色统一记为“填充”。"""
    out = np.zeros(arr.shape, dtype=int)
    out[arr < 140] = 1
    out[(arr >= 160) & (arr <= 215)] = 2
    return out


def prep(arr, fill_dark_region=False):
    img = Image.fromarray(arr.astype(np.uint8)).crop((2, 2, arr.shape[1] - 2, arr.shape[0] - 2))
    img = img.resize((N, N), Image.NEAREST)
    return np.array(img).astype(int)


t = prep(target)
# 对称区域里的1/4圆是黑色实心，问号处应为灰色：把与左上角相连的大块黑色视作“填充”
tc = classes(t)
# 黑色实心块：在左上角附近、连通的黑色大面积 → 记为填充(2)
from collections import deque
seen = np.zeros_like(tc, dtype=bool)
for sy, sx in ((0, 0), (1, 0), (0, 1)):
    if tc[sy, sx] == 1 and not seen[sy, sx]:
        q = deque([(sy, sx)]); comp = []
        while q:
            y, x = q.popleft()
            if 0 <= y < N and 0 <= x < N and not seen[y, x] and tc[y, x] == 1:
                seen[y, x] = True; comp.append((y, x))
                q.extend([(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)])
        if len(comp) > 30:
            for y, x in comp:
                tc[y, x] = 2


def score(opt_cls, tgt_cls):
    # 只统计任一方为非白的像素，计算不一致比例
    mask = (opt_cls != 0) | (tgt_cls != 0)
    # 线条允许1像素误差：把目标线条膨胀一下
    diff = (opt_cls != tgt_cls) & mask
    return diff.sum() / mask.sum()


def dilate(c, k=1):
    out = c.copy()
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            sh = np.roll(np.roll(c, dy, 0), dx, 1)
            out = np.where((out == 0) & (sh == 1), 1, out)
    return out


def chamfer(c1, c2):
    """线条像素的对称平均最近距离 + 填充区域的不重合比例。"""
    p1 = np.argwhere(c1 == 1); p2 = np.argwhere(c2 == 1)
    d12 = np.sqrt(((p1[:, None, :] - p2[None, :, :]) ** 2).sum(-1)).min(1).mean()
    d21 = np.sqrt(((p2[:, None, :] - p1[None, :, :]) ** 2).sum(-1)).min(1).mean()
    f1 = c1 == 2; f2 = c2 == 2
    iou = (f1 & f2).sum() / max(1, (f1 | f2).sum())
    return round(float(d12 + d21), 2), round(float(iou), 2)


if __name__ == "__main__":
    print("目标（问号处应有内容，由对称区域翻转得到）字符画：")
    for row in tc[::2, ::1]:
        print("".join(" #o"[v] for v in row))
    for k, (x0, y0, x1, y1) in OPTS.items():
        o = classes(prep(A[y0:y1 + 1, x0:x1 + 1]))
        res = []
        for mirror in (False, True):
            base = o[:, ::-1] if mirror else o
            for r in range(4):
                cand = np.rot90(base, r)  # np.rot90 正方向 = 逆时针
                d, iou = chamfer(cand, tc)
                res.append((d, iou, ("镜像+" if mirror else "") + f"逆时针{90 * r}°"))
        res.sort()
        print(k, "线条平均偏差(像素,越小越好)/灰块重合度 最佳:", res[0], " 次佳:", res[1])
