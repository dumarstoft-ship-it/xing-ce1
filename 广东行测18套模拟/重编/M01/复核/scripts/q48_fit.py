"""第48题：检验哪个选项能与左侧图形拼成正方形。
做法：
1. 每个图形都是封闭折线。把轮廓外部从边界泛洪填充，剩下的(轮廓+内部)即实心图形。
2. 左图：取其包围盒作为正方形，补集 = 包围盒 - 实心左图（轮廓线像素算两边共有）。
3. 每个选项：取实心图形，旋转 0/90/180/270 度（另附镜像仅作参考），缩放到与补集相同大小，
   计算与补集的 IoU（轮廓线带宽容差：比较前各自做 1 像素腐蚀/膨胀不影响结论）。
用法: python3 q48_fit.py <png>
"""
import sys
from collections import deque
from PIL import Image
import numpy as np

im = np.array(Image.open(sys.argv[1]).convert("L"))
H, W = im.shape
dark = im < 160


def solid(mask):
    """mask: 线条为 True。返回 实心(线+内部) 布尔数组。"""
    h, w = mask.shape
    ext = np.zeros_like(mask)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not mask[y, x] and not ext[y, x]:
                ext[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not mask[y, x] and not ext[y, x]:
                ext[y, x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx] and not ext[ny, nx]:
                ext[ny, nx] = True; dq.append((ny, nx))
    return ~ext


def crop_bbox(a):
    ys, xs = np.nonzero(a)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def resize(a, shape):
    img = Image.fromarray((a * 255).astype(np.uint8))
    img = img.resize((shape[1], shape[0]), Image.BILINEAR)
    return np.array(img) > 127


# 左图区域：x 0..115（选项框从约 x=120 开始）
left_mask = dark[:, 0:115].copy()
left_solid = crop_bbox(solid(left_mask))
N = 200  # 统一到 N x N
L = resize(left_solid, (N, N))
comp = ~L
# 左图实心的轮廓线也属于补集边界，补集稍作膨胀以容纳线宽
print("left bbox size(px, h x w):", left_solid.shape)

# 选项面板：检测面板竖线
colfrac = dark[10:130].mean(axis=0)
lines = [x for x in range(W) if colfrac[x] > 0.8]
groups = []
for x in lines:
    if groups and x - groups[-1][-1] <= 1:
        groups[-1].append(x)
    else:
        groups.append([x])
xs = [int(np.mean(g)) for g in groups]
print("panel vertical lines:", xs)
rowfrac = dark[:, xs[0]:xs[-1]].mean(axis=1)
hl = [y for y in range(H) if rowfrac[y] > 0.8]
print("panel horizontal lines:", hl)
y_top, y_bot = hl[0], hl[-1]

names = "ABCD"
for i, nm in enumerate(names):
    x0, x1 = xs[i] + 4, xs[i + 1] - 4
    sub = dark[y_top + 4:y_bot - 4, x0:x1]
    s = crop_bbox(solid(sub))
    res = []
    for flip in (False, True):
        base = np.fliplr(s) if flip else s
        for k in range(4):
            r = np.rot90(base, k)  # k*90 度逆时针
            R = resize(r, (N, N))
            inter = (R & comp).sum()
            union = (R | comp).sum()
            res.append(((inter / union), ("镜像+" if flip else "") + f"逆时针{90 * k}度"))
    res.sort(reverse=True)
    print(nm, "bbox(h x w)=", s.shape, " best:", [(round(a, 3), b) for a, b in res[:3]])


# ---- 第二种度量：只比较“锯齿边”（共享边界）的像素位置，倒角距离（像素）----
def lines_in_bbox(mask_region):
    s = solid(mask_region)
    ys, xs_ = np.nonzero(s)
    return mask_region[ys.min():ys.max() + 1, xs_.min():xs_.max() + 1]


def chamfer(a, b):
    pa = np.argwhere(a).astype(float)
    pb = np.argwhere(b).astype(float)
    d = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1))
    return d.min(1).mean(), d.min(0).mean(), d.min(1).max(), d.min(0).max()


Lline = lines_in_bbox(dark[:, 0:115])
h, w = Lline.shape
zz_left = Lline.copy()
zz_left[:, :4] = False      # 去掉正方形左边
zz_left[h - 4:, :] = False  # 去掉正方形底边
print("\n锯齿边倒角距离（左图锯齿 vs 选项旋转后锯齿；正方形上边、右边应由选项提供）")
for i, nm in enumerate(names):
    x0, x1 = xs[i] + 4, xs[i + 1] - 4
    sub = dark[y_top + 4:y_bot - 4, x0:x1]
    O = lines_in_bbox(sub)
    out = []
    for flip in (False, True):
        base = np.fliplr(O) if flip else O
        for k in range(4):
            r = np.rot90(base, k)
            r = np.array(Image.fromarray((r * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)) > 127
            # 选项旋转后应占正方形上边与右边，这两条边要真的存在
            top_ok = r[:3, :].mean(axis=0).max() > 0 and r[:3, :].any(axis=0).mean() > 0.9
            right_ok = r[:, w - 3:].any(axis=1).mean() > 0.9
            zz = r.copy()
            zz[:4, :] = False
            zz[:, w - 4:] = False
            m1, m2, x1_, x2_ = chamfer(zz_left, zz)
            out.append((round((m1 + m2) / 2, 2), round(max(x1_, x2_), 1), top_ok and right_ok,
                        ("镜像+" if flip else "") + f"逆时针{90 * k}度"))
    out.sort()
    print(nm, [o for o in out if o[2]][:2], "| 含不合边框的最优:", out[0])
