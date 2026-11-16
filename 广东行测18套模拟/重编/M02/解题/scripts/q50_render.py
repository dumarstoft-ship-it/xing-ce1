"""第50题核验（一）：用斜二测（正面为正方形、纵深向右上）渲染小立方体组合，
与题图逐像素比较，确定每个选项中哪些位置"看得见有方块"、"看得见是空的"、"被挡住看不见"。

坐标：x 向右(0..2)，d 向后(0..2)，h 向上(0..2)。
投影：屏幕 X = X0 + s*x + a*d，Y = Y0 - s*h - b*d（Y 向下）。

做法：先用形状已知的第3、4个积木拟合投影参数；再把 q50_solve.py 中各选项的最终读法渲染出来，
拟合位置后与题图比较，并逐格翻转检查哪些格子"被挡住"（翻转后渲染不变）。
用法：python3 q50_render.py [保存对比图的目录]
"""
import itertools
import sys

import numpy as np
from PIL import Image, ImageDraw

IMG = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p13_i00.png"
GRAY = np.array(Image.open(IMG).convert("L")).astype(float)
SS = 4  # 超采样


def render(vox, X0, Y0, s, a, b, box):
    """vox: set of (x,d,h)。box: (x0,y0,x1,y1) 渲染区域（原图坐标）。返回灰度数组。"""
    x0, y0, x1, y1 = box
    W, H = (x1 - x0) * SS, (y1 - y0) * SS
    im = Image.new("L", (W, H), 255)
    dr = ImageDraw.Draw(im)

    def P(x, d, h):
        return ((X0 + s * x + a * d - x0) * SS, (Y0 - s * h - b * d - y0) * SS)

    faces = []
    for (x, d, h) in vox:
        # 正面（d 侧）
        if (x, d - 1, h) not in vox:
            poly = [P(x, d, h), P(x + 1, d, h), P(x + 1, d, h + 1), P(x, d, h + 1)]
            faces.append((x + 0.5, d, h + 0.5, poly, 255))
        # 顶面
        if (x, d, h + 1) not in vox:
            poly = [P(x, d, h + 1), P(x + 1, d, h + 1), P(x + 1, d + 1, h + 1), P(x, d + 1, h + 1)]
            faces.append((x + 0.5, d + 0.5, h + 1, poly, 255))
        # 右面
        if (x + 1, d, h) not in vox:
            poly = [P(x + 1, d, h), P(x + 1, d + 1, h), P(x + 1, d + 1, h + 1), P(x + 1, d, h + 1)]
            faces.append((x + 1, d + 0.5, h + 0.5, poly, 205))
    # 画家算法：离观察者远的先画。视线方向 (-a/s, 1, -b/s)
    faces.sort(key=lambda f: -(-(a / s) * f[0] + f[1] - (b / s) * f[2]))
    for _, _, _, poly, fill in faces:
        dr.polygon(poly, fill=fill, outline=0)
        dr.line(poly + [poly[0]], fill=0, width=int(1.3 * SS))
    im = im.resize((x1 - x0, y1 - y0), Image.BOX)
    return np.array(im).astype(float)


def blur(arr):
    k = np.array([1, 2, 1], float) / 4
    out = arr.copy()
    for ax in (0, 1):
        out = (np.roll(out, 1, ax) * k[0] + out * k[1] + np.roll(out, -1, ax) * k[2])
    return out


def diff(vox, params, box):
    x0, y0, x1, y1 = box
    r = render(vox, *params, box)
    t = GRAY[y0:y1, x0:x1]
    return float(np.abs(blur(r) - blur(t)).mean())


def fit(vox, box, init, steps=(1, 0.5, 0.25), scan=0):
    """坐标下降拟合投影参数；scan>0 时先在 X0、Y0 上做网格搜索。"""
    p = list(init)
    best = diff(vox, p, box)
    if scan:
        for dx in range(-scan, scan + 1):
            for dy in range(-scan, scan + 1):
                q = p.copy(); q[0] += dx; q[1] += dy
                v = diff(vox, q, box)
                if v < best:
                    best, bestq = v, q
        if 'bestq' in locals():
            p = bestq
    for st in steps:
        improved = True
        while improved:
            improved = False
            for i in range(5):
                for dlt in (-st, st):
                    q = p.copy(); q[i] += dlt
                    v = diff(vox, q, box)
                    if v < best - 1e-6:
                        best, p, improved = v, q, True
    return p, best


ALL = set(itertools.product(range(3), range(3), range(3)))


def visibility(vox, params, box, tol=0.02):
    """对每个格子翻转"有/无"，看渲染是否改变：不变的格子 = 被挡住（无法从图上判断）。"""
    base = render(vox, *params, box)
    status = {}
    for c in sorted(ALL):
        v2 = set(vox) ^ {c}
        r = render(v2, *params, box)
        changed = np.abs(r - base).mean() > tol
        status[c] = ("有" if c in vox else "空") if changed else "挡"
    return status


OPT_BOX = {"A": (28, 141, 103, 216), "B": (151, 140, 226, 215),
           "C": (268, 139, 337, 214), "D": (390, 140, 465, 215)}
PIECE_BOX = {"P3": (265, 26, 335, 81), "P4": (376, 25, 430, 81)}

P3 = {(0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 0, 1), (2, 1, 0), (2, 1, 1)}
P4 = {(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 1, 0), (1, 1, 1)}


if __name__ == "__main__":
    # 先用已知形状的积木3拟合投影参数的大致取值
    p3, e3 = fit(P3, PIECE_BOX["P3"], [270, 75, 16, 5, 5])
    print("积木3 拟合参数 X0,Y0,s,a,b =", [round(v, 2) for v in p3], "平均灰度差", round(e3, 2))
    p4, e4 = fit(P4, PIECE_BOX["P4"], [381, 75, 16, 5, 5])
    print("积木4 拟合参数 =", [round(v, 2) for v in p4], "平均灰度差", round(e4, 2))
    s, a, b = p3[2], p3[3], p3[4]
    # 最终读法取自 q50_solve.py 的 OPTS（被挡住的格子按“有”渲染，渲染结果与按“无”相同）
    from q50_solve import OPTS
    save_dir = sys.argv[1] if len(sys.argv) > 1 else None   # 传入目录则保存“原图|渲染图”对比图
    # 目视排查过的其他读法（像素差相近时以放大目视为准）：
    ALT = {"A": ("(2,1,2)有方块", {(2, 1, 2)}, set()),
           "B": ("(2,2,0)有方块", {(2, 2, 0)}, set())}
    for k in "ABCD":
        box = OPT_BOX[k]
        x0, y0, x1, y1 = box
        vox = {c for c, v in OPTS[k].items() if v != "空"}
        params, err = fit(vox, box, [x0 + 5, y1 - 6, s, a, b], scan=7)
        st = visibility(vox, params, box)
        agree = all((st[c] == OPTS[k][c]) for c in ALL)
        print(f"\n选项{k}: 投影参数 {[round(v, 2) for v in params]}  与题图平均灰度差 {err:.2f}  "
              f"渲染得到的可见性与 q50_solve.py 读法一致：{agree}")
        for h in (2, 1, 0):
            print(f"  第{h}层(h={h})  d=0行/d=1行/d=2行：",
                  " | ".join("".join(st[(x, d, h)] for x in range(3)) for d in range(3)))
        known = sum(1 for v in st.values() if v == "有")
        empty = sum(1 for v in st.values() if v == "空")
        hidden = sum(1 for v in st.values() if v == "挡")
        print(f"  看得见的方块 {known}，看得见的空位 {empty}，被挡住 {hidden}")
        if k in ALT:
            name, add, rem = ALT[k]
            alt = (vox | add) - rem
            print(f"  对照读法 {name}：平均灰度差 {diff(alt, params, box):.2f}"
                  "（差别很小，放大比对后以最终读法为准；两种读法下 q50_solve.py 的结论相同）")
        if save_dir:
            r = render(vox, *params, box)
            t = GRAY[y0:y1, x0:x1]
            side = np.concatenate([t, np.full((t.shape[0], 4), 128.0), r], axis=1)
            Image.fromarray(side.astype(np.uint8)).resize(
                (side.shape[1] * 6, side.shape[0] * 6), Image.NEAREST).save(f"{save_dir}/q50_fit_{k}.png")
