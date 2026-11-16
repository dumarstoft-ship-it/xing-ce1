# 第50题：只比较三个可见面内部的线条（去掉正方体轮廓），指标为
#   d = 选项内部线条像素到渲染线条的平均距离 与 反向距离 的平均；
#   miss = 两个方向上距离 > 2.5px 的像素占比（越小越吻合）
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from q50_fold import ROTS, render, face_in_view, S, K, project
from PIL import Image, ImageDraw

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s16_p12_i01.png'
a = np.array(Image.open(IMG).convert('L'))
BOX = {'A': (165, 22), 'B': (277, 21), 'C': (390, 22), 'D': (501, 21)}
N = int(round(S + K)) + 2

# 轮廓掩码：正方体9条可见棱附近 3px 以内
edge = Image.new('L', (N, N), 0)
d = ImageDraw.Draw(edge)
cube = [((0,0,1),(1,0,1)),((1,0,1),(1,1,1)),((1,1,1),(0,1,1)),((0,1,1),(0,0,1)),
        ((0,1,1),(0,1,0)),((0,1,0),(1,1,0)),((1,1,0),(1,1,1)),((1,1,0),(1,0,0)),((1,0,0),(1,0,1))]
for p, q in cube:
    A = project(np.array(p, float)); B = project(np.array(q, float))
    d.line([A, B], fill=255, width=7)
EDGE = np.array(edge) > 0

def pts(mask):
    ys, xs = np.nonzero(mask & ~EDGE)
    return np.stack([xs, ys], 1).astype(float)

def dist(P, Q):
    D = np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(-1))
    return D.min(1), D.min(0)

def best_offset(opt_mask):
    # 选项外接框与渲染外接框对齐：取外接框左上角
    ys, xs = np.nonzero(opt_mask)
    return xs.min(), ys.min()

results = {}
for k, (x0, y0) in BOX.items():
    region = a[y0 - 2:y0 + N + 2, x0 - 2:x0 + N + 2] < 110
    ox, oy = best_offset(region)
    opt = region[oy:oy + N, ox:ox + N]
    if opt.shape != (N, N):
        pad = np.zeros((N, N), bool); pad[:opt.shape[0], :opt.shape[1]] = opt; opt = pad
    P = pts(opt)
    res = []
    for i, R in enumerate(ROTS):
        img, vis = render(R, size=(N, N))
        Q = pts(np.array(img) < 110)
        d1, d2 = dist(P, Q)
        miss = (np.sum(d1 > 2.5) + np.sum(d2 > 2.5)) / (len(d1) + len(d2))
        res.append((miss, (d1.mean() + d2.mean()) / 2, i, face_in_view(R)))
    res.sort(key=lambda t: (t[0], t[1]))
    results[k] = res
    print(f'选项{k}（内部线条像素 {len(P)} 个）：')
    for r in res[:3]:
        print(f'    不吻合像素占比={r[0]:.3f}  平均距离={r[1]:.2f}px  前/上/右={r[3]}')
