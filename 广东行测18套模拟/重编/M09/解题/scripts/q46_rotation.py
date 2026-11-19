# -*- coding: utf-8 -*-
"""M09 第46题（GD2020-XZ-Q047）：梯形与三角形各自的朝向。

顶点坐标由各小图4倍放大后读出（原图像素＝放大坐标/4＋小图偏移）。对每幅图算：
  梯形：一组平行边（两底）中短底在梯形中心的哪一侧；
  三角形：顶角（最小内角）相对于底边中点的方向；
  另附“三角形有一边与梯形两底平行且不重合”的检查（静态特征，用来说明B项为何会被误选）。
另用霍夫变换独立测各图7条直线的方向角，核对“正放/斜放”的判断。
"""
import math
import numpy as np
from PIL import Image

SRC = "/home/user/xing-ce1/广东/行测/2013-2021/assets/GD2020-XZ/GD2020-XZ-p07-i02.png"
OFF = {"图1": (5, 0), "图2": (205, 0), "图3": (405, 0), "A": (5, 235), "B": (205, 235), "C": (405, 235), "D": (605, 235)}
Z = {  # 4倍放大图上读出的顶点：梯形4点（顺时针）、三角形3点
    "图1": ([(210, 195), (615, 195), (668, 560), (140, 560)], [(403, 197), (617, 652), (193, 652)]),
    "图2": ([(148, 188), (515, 132), (515, 662), (148, 595)], [(176, 312), (645, 470), (176, 715)]),
    "图3": ([(133, 247), (690, 247), (630, 612), (205, 612)], [(87, 195), (512, 195), (300, 655)]),
    "A": ([(268, 175), (632, 228), (632, 632), (268, 702)], [(175, 430), (632, 228), (632, 632)]),
    "B": ([(213, 228), (578, 175), (578, 703), (213, 632)], [(155, 438), (635, 228), (635, 650)]),
    "C": ([(220, 215), (585, 160), (585, 690), (220, 620)], [(388, 255), (600, 715), (178, 715)]),
    "D": ([(165, 175), (530, 228), (530, 632), (165, 702)], [(165, 175), (600, 440), (250, 685)]),
}


def orig(k, pts):
    ox, oy = OFF[k]
    return [np.array([x / 4 + ox, y / 4 + oy]) for x, y in pts]


def ang(v):  # 方向角，图像坐标y向下，换成y向上
    return math.degrees(math.atan2(-v[1], v[0])) % 360


def side_name(a):
    names = {0: "右", 90: "上", 180: "左", 270: "下"}
    for k, n in names.items():
        if min(abs(a - k), 360 - abs(a - k)) <= 12:
            return n
    return f"斜向{a:.0f}°"


def analyse(k):
    T, R = [orig(k, Z[k][0]), orig(k, Z[k][1])]
    sides = [(T[i], T[(i + 1) % 4]) for i in range(4)]
    best = None
    for i in range(2):  # 对边 (0,2) 或 (1,3) 中更接近平行的一组是两底
        a, b = sides[i], sides[i + 2]
        da, db = ang(a[1] - a[0]) % 180, ang(b[1] - b[0]) % 180
        diff = min(abs(da - db), 180 - abs(da - db))
        if best is None or diff < best[0]:
            best = (diff, a, b, da)
    _, a, b, base_dir = best
    la, lb = np.linalg.norm(a[1] - a[0]), np.linalg.norm(b[1] - b[0])
    short = a if la < lb else b
    c = np.mean(T, axis=0)
    short_side = side_name(ang((short[0] + short[1]) / 2 - c))
    # 三角形顶角＝最小内角
    angs = []
    for i in range(3):
        p, q, r = R[i], R[(i + 1) % 3], R[(i + 2) % 3]
        v1, v2 = q - p, r - p
        angs.append(math.degrees(math.acos(np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2))))
    i = int(np.argmin(angs))
    apex, b1, b2 = R[i], R[(i + 1) % 3], R[(i + 2) % 3]
    apex_dir = side_name(ang(apex - (b1 + b2) / 2))
    # 三角形各边与梯形两底是否平行、是否重合
    par, coin = 0, 0
    for j in range(3):
        p, q = R[j], R[(j + 1) % 3]
        d = ang(q - p) % 180
        if min(abs(d - base_dir), 180 - abs(d - base_dir)) <= 3:
            # 与哪条底共线？
            n = np.array([-(short[1] - short[0])[1], (short[1] - short[0])[0]]); n /= np.linalg.norm(n)
            dist = min(abs(np.dot(p - s[0], n)) for s in (a, b))
            if dist < 2:
                coin += 1
            else:
                par += 1
    return short_side, apex_dir, round(min(angs)), par, coin


def hough_dirs(k):
    g = np.array(Image.open(SRC).convert("L")).astype(float)
    ox, oy = OFF[k]
    m = g[oy + 12: oy + 200, ox + 7: ox + 195] < 128
    ys, xs = np.nonzero(m)
    th = np.deg2rad(np.arange(0, 180, 0.5))
    diag = int(math.hypot(*m.shape)) + 2
    acc = np.zeros((2 * diag, len(th)), int)
    c, s = np.cos(th), np.sin(th)
    for x, y in zip(xs, ys):
        acc[np.round(x * c + y * s).astype(int) + diag, np.arange(len(th))] += 1
    out = []
    for _ in range(7):
        r, t = np.unravel_index(acc.argmax(), acc.shape)
        out.append(round((math.degrees(th[t]) - 90) % 180, 1))
        dt = np.abs(np.arange(len(th)) - t); dt = np.minimum(dt, len(th) - dt)
        acc[max(0, r - 10): r + 11, dt <= 12] = 0
        if t < 12 or t > len(th) - 12:
            r2 = 2 * diag - r
            acc[max(0, r2 - 10): r2 + 11, dt <= 12] = 0
    return sorted(out)


if __name__ == "__main__":
    print("图/选项  梯形短底在  三角形顶角朝  顶角度数  与两底平行的三角形边（不重合/重合）  霍夫直线方向角")
    for k in Z:
        s, a, deg, par, coin = analyse(k)
        print(f"{k:>4}    {s:<6}    {a:<8}    {deg:>3}°      {par}/{coin}        {hough_dirs(k)}")
    print("\n位置规律：梯形短底 上→左→下（每次逆时针90°）⇒ 问号处在右；三角形顶角 上→右→下（每次顺时针90°）⇒ 问号处朝左。")
    for k in "ABCD":
        s, a, *_ = analyse(k)
        print(f"  {k}：短底在{s}{'✓' if s == '右' else '✗'}，顶角朝{a}{'✓' if a == '左' else '✗'}")
