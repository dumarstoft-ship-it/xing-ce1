# -*- coding: utf-8 -*-
"""Q48 平面拼合：两块给定图形 + 一个选项 能否拼成扇形。

步骤：
1. 读出每块图形的轮廓，放大4倍，取“轮廓中线以内”的区域（内部再向外扩半个线宽）；
2. 给定的长条块P2：底边为直边、左边为直边、右边为弧。以P2左下角为圆心O、底边长为半径R作四分之一圆，
   检验P2右边弧和小块P1上边弧都在这个圆上（P1左边直边贴在竖直半径最上端）；
3. 扇形减去P1、P2后剩下的“空缺”，与每个选项（允许旋转0/90/180/270°，另外也试翻转）做全平移搜索，
   取最大重合度IoU，并统计多出/缺少的面积。拼得上的选项IoU应接近1。
"""
import numpy as np
from PIL import Image, ImageFilter

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i02.png'
S = 4  # 放大倍数
gray = Image.open(IMG).convert('L')

crops = {
    'P1': (177, 1, 225, 44), 'P2': (269, 7, 348, 38),
    'A': (39, 97, 90, 172), 'B': (164, 97, 213, 174), 'C': (283, 97, 334, 172), 'D': (405, 98, 458, 173),
}


def flood_outside(stroke):
    """从画面四边出发，沿非笔画像素做 4-连通填充，得到图形外部。"""
    from collections import deque
    h, w = stroke.shape
    out = np.zeros_like(stroke)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not stroke[y, x] and not out[y, x]:
                out[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not stroke[y, x] and not out[y, x]:
                out[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and not stroke[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                dq.append((ny, nx))
    return out


def region(box):
    im = gray.crop(box)
    im = im.resize((im.size[0] * S, im.size[1] * S), Image.BILINEAR)
    a = np.array(im)
    stroke = a < 128
    interior = ~stroke & ~flood_outside(stroke)
    # 线宽估计：每行的笔画像素段长度的中位数
    runs = []
    for row in stroke:
        r = 0
        for v in row:
            if v:
                r += 1
            elif r:
                runs.append(r)
                r = 0
    w = int(np.median(runs))
    half = max(1, w // 2)
    reg = Image.fromarray((interior * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * half + 1))
    return np.array(reg) > 0, w


def sector_mask(shape, O, R):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    dx = xx - O[0]
    dy = O[1] - yy
    return (dx >= 0) & (dy >= 0) & (dx * dx + dy * dy <= R * R)


def best_fit(hole, piece):
    """FFT 互相关，求 piece 在所有平移下与 hole 的最大 IoU。"""
    H, W = hole.shape
    ph, pw = piece.shape
    P = np.zeros((H + ph, W + pw))
    Hh = np.zeros_like(P)
    Hh[:H, :W] = hole
    P[:ph, :pw] = piece
    corr = np.real(np.fft.ifft2(np.fft.fft2(Hh) * np.conj(np.fft.fft2(P))))
    k = np.unravel_index(np.argmax(corr), corr.shape)
    ov = corr[k]
    a, b = hole.sum(), piece.sum()
    placed = np.roll(P, k, axis=(0, 1))[:H, :W] > 0.5
    return ov / (a + b - ov), k, ov, a, b, placed


def thick(mask, r=3):
    """去掉宽度不超过约 2r 像素的细条（线宽差造成的描边误差），返回剩下的“实质性”面积。"""
    im = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(2 * r + 1))
    return (np.array(im) > 0).sum()


if __name__ == '__main__':
    R_ = {k: region(b) for k, b in crops.items()}
    print('线宽(放大后像素):', {k: v[1] for k, v in R_.items()})
    P1, P2 = R_['P1'][0], R_['P2'][0]
    # P2 的左下角和底边长
    ys, xs = np.nonzero(P2)
    O2 = (xs.min(), ys.max())
    R = xs.max() - xs.min()
    # 用 P2 右边弧检验：右侧边界点到 O 的距离
    right_pts = [(np.nonzero(P2[y])[0].max(), y) for y in range(ys.min() + 4, ys.max() - 4)]
    dist = [np.hypot(x - O2[0], O2[1] - y) for x, y in right_pts]
    print('R =', R / S, '原图像素；P2右边弧到O的距离 %.1f~%.1f（/4后）' % (min(dist) / S, max(dist) / S))
    # P1：左上角 TL，放在竖直半径最上端
    ys1, xs1 = np.nonzero(P1)
    TL = (xs1.min(), ys1.min())
    top_pts = [(x, np.nonzero(P1[:, x])[0].min()) for x in range(xs1.min() + 4, xs1.max() - 4)]
    O1 = (TL[0], TL[1] + R)
    dist1 = [np.hypot(x - O1[0], O1[1] - y) for x, y in top_pts]
    print('P1上边弧到圆心距离 %.1f~%.1f（/4后）' % (min(dist1) / S, max(dist1) / S))
    # 拼装画布：圆心放在 (pad, pad+R)
    pad = 40
    Hc = R + 2 * pad
    canvas_shape = (Hc, Hc)
    O = (pad, pad + R)
    sec = sector_mask(canvas_shape, O, R)
    used = np.zeros(canvas_shape, bool)
    # 放 P2：左下角对齐 O
    y0 = O[1] - O2[1]
    x0 = O[0] - O2[0]
    used[y0:y0 + P2.shape[0], x0:x0 + P2.shape[1]] |= P2
    # 放 P1：左上角对齐 (O.x, O.y-R)
    y1 = (O[1] - R) - TL[1]
    x1 = O[0] - TL[0]
    used[y1:y1 + P1.shape[0], x1:x1 + P1.shape[1]] |= P1
    print('P1与P2放好后在扇形外的面积(原图像素²) %.1f' % ((used & ~sec).sum() / S / S))
    hole = sec & ~used
    print('空缺面积 %.1f 原图像素²' % (hole.sum() / S / S))
    for o in 'ABCD':
        piece = R_[o][0]
        res = []
        for flip in (False, True):
            base = piece[:, ::-1] if flip else piece
            for k in range(4):
                p = np.rot90(base, -k)  # 顺时针转 90k 度
                iou, pos, ov, a, b, placed = best_fit(hole, p)
                gap = thick(hole & ~placed) / S / S
                over = thick(placed & ~hole) / S / S
                res.append((iou, ('翻转+' if flip else '') + '顺时针%d°' % (90 * k), (a - ov) / S / S, (b - ov) / S / S,
                            gap, over))
        res.sort(key=lambda t: -t[0])
        r0 = res[0]
        print('选项%s 最佳: IoU=%.3f 方式=%s 空缺未填=%.1f 多出=%.1f；扣除1.5像素以内描边误差后：未填=%.1f 多出=%.1f'
              ' | 次佳: IoU=%.3f %s' % (o, r0[0], r0[1], r0[2], r0[3], r0[4], r0[5], res[1][0], res[1][1]))
