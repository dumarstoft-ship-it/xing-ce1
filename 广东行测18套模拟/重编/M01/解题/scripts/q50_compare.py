# 第50题：把24种摆放的渲染图与四个选项逐一比较（双向平均倒角距离，单位px），并输出对照图
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from q50_fold import ROTS, render, face_in_view, S, K
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s16_p12_i01.png'
im = Image.open(IMG).convert('L')
a = np.array(im)
BOX = {'A': (165, 22), 'B': (277, 21), 'C': (390, 22), 'D': (501, 21)}
N = int(round(S + K)) + 2

def pts(mask):
    ys, xs = np.nonzero(mask)
    return np.stack([xs, ys], 1).astype(float)

def chamfer(P, Q):
    d = np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(-1))
    return d.min(1).mean(), d.min(0).mean()

out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
summary = {}
panels = []
for k, (x0, y0) in BOX.items():
    opt = a[y0:y0 + N, x0:x0 + N] < 110
    P = pts(opt)
    res = []
    for i, R in enumerate(ROTS):
        img, vis = render(R, size=(N, N))
        Q = pts(np.array(img) < 110)
        d1, d2 = chamfer(P, Q)
        res.append(((d1 + d2) / 2, d1, d2, i, face_in_view(R)))
    res.sort(key=lambda t: t[0])
    summary[k] = res
    print(f'选项{k}: 最好的三种摆放（平均倒角距离px, 选项→渲染, 渲染→选项, 前/上/右面）')
    for r in res[:3]:
        print(f'    {r[0]:.2f}  ({r[1]:.2f}, {r[2]:.2f})  {r[4]}')
    best = res[0]
    rimg, _ = render(ROTS[best[3]], size=(N, N), scale=4, width=5)
    oimg = im.crop((x0, y0, x0 + N, y0 + N)).resize((N * 4, N * 4), Image.LANCZOS)
    panel = Image.new('L', (N * 8 + 10, N * 4), 255)
    panel.paste(oimg, (0, 0)); panel.paste(rimg, (N * 4 + 10, 0))
    panels.append(panel)
canvas = Image.new('L', (panels[0].width, sum(p.height + 10 for p in panels)), 255)
y = 0
for p in panels:
    canvas.paste(p, (0, y)); y += p.height + 10
canvas.save(os.path.join(out_dir, 'q50_compare.png'))
print('对照图已保存')
