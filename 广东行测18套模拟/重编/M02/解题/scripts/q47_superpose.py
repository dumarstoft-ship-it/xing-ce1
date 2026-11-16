"""第47题核验：每行 图3 = (图1 与 图2 去同存异) 再逆时针旋转90°。

做法：把每幅图的线段换成格点坐标，拆成最小单位线段（"原子段"），
去同存异 = 两图原子段集合的对称差；旋转在像素坐标里做，再吸附到格点比较。
线段像素坐标见 q47_features.py（题图每格放大8倍后量取）。

第1行：4×4 正方形格点（3×3格），x/y 坐标约 115/310/495/700。
第2行：5×5 正方形格点，x/y 坐标约 120/262/405/545/695（含斜线）。
第3行和选项：三角形（等距）格点，竖边或横边长 ≈328px。
"""
import math
from fractions import Fraction as Fr

from q47_features import FIGS

# ---------- 通用：线段拆成原子段 ----------

def atoms(segs, step=Fr(1, 4)):
    """segs: [((x1,y1),(x2,y2)), ...]（格点坐标，可为分数）。
    在 x 或 y 为 step 整数倍处切分，返回原子段集合（端点无序）。"""
    out = set()
    for (x1, y1), (x2, y2) in segs:
        x1, y1, x2, y2 = map(Fr, (x1, y1, x2, y2))
        ts = {Fr(0), Fr(1)}
        dx, dy = x2 - x1, y2 - y1
        for v0, dv in ((x1, dx), (y1, dy)):
            if dv == 0:
                continue
            lo, hi = sorted((v0, v0 + dv))
            k = math.ceil(lo / step)
            while k * step <= hi:
                ts.add((k * step - v0) / dv)
                k += 1
        ts = sorted(t for t in ts if 0 <= t <= 1)
        pts = [(x1 + t * dx, y1 + t * dy) for t in ts]
        for p, q in zip(pts, pts[1:]):
            if p != q:
                out.add(frozenset((p, q)))
    return out


def snap(segs_px, xs, ys):
    """把像素坐标吸附到最近的格点坐标（xs/ys 为各格点的像素位置）。"""
    def s(v, grid):
        return min(range(len(grid)), key=lambda i: abs(grid[i] - v))
    return [((s(a[0], xs), s(a[1], ys)), (s(b[0], xs), s(b[1], ys))) for a, b in segs_px]


def rot_ccw_grid(S, n):
    """正方形格点上逆时针转90°（屏幕坐标，y向下）：(x,y)->(y, n-x)。"""
    return {frozenset((p[1], n - p[0]) for p in e) for e in S}


# ---------- 第1行 ----------
X1 = [117, 310, 497, 703]
R1 = {k: atoms(snap(FIGS[k], X1, X1)) for k in "123"}
row1_ok = R1["3"] == rot_ccw_grid(R1["1"] ^ R1["2"], 3)

# ---------- 第2行 ----------
# 格点 0..4；斜线端点也落在格点上（2个单位竖、1个单位横等）
X2 = [120, 262, 405, 545, 695]
Y2 = [110, 255, 398, 535, 688]
R2 = {k: atoms(snap(FIGS[k], X2, Y2)) for k in "456"}
row2_ok = R2["6"] == rot_ccw_grid(R2["4"] ^ R2["5"], 4)

# ---------- 第3行（等距格点） ----------
# 竖边格点：列 c∈{0,1,2} 对应 x≈120/405/688；行 r 为半格，y≈75+164r（r=0..4）。
CX = [120, 405, 688]
RY = [75, 237, 400, 565, 730]


def to_iso(segs_px):
    return snap(segs_px, CX, RY)


def iso_atoms(segs):
    # 等距格点里，竖边 (c,r)-(c,r+2) 拆成两段半边，斜边 (c,r)-(c±1,r±1) 本身为原子
    return atoms(segs, step=Fr(1))


R3 = {k: iso_atoms(to_iso(FIGS[k])) for k in "78"}
xor78 = R3["7"] ^ R3["8"]

# 选项：A 与第3行同一方向的格子；B、C、D 是横边格子，先顺时针转90°还原到竖边格子再比较。
CENTER = (400, 400)


def rot_cw_px(segs_px):
    # 屏幕坐标顺时针90°：(dx,dy)->(-dy,dx)
    cx, cy = CENTER
    f = lambda p: (cx - (p[1] - cy), cy + (p[0] - cx))
    return [(f(a), f(b)) for a, b in segs_px]


def rot_ccw_px(segs_px):
    cx, cy = CENTER
    f = lambda p: (cx + (p[1] - cy), cy - (p[0] - cx))
    return [(f(a), f(b)) for a, b in segs_px]


def iso_of_option(k, undo):
    segs = FIGS[k]
    if undo == "cw":       # 选项 = 逆时针转后的图 → 顺时针转回
        segs = rot_cw_px(segs)
    elif undo == "ccw":    # 选项 = 顺时针转后的图 → 逆时针转回
        segs = rot_ccw_px(segs)
    # 吸附前检查与格点的偏差
    snapped = to_iso(segs)
    err = 0
    for (a, b), (sa, sb) in zip(segs, snapped):
        for p, (c, r) in ((a, sa), (b, sb)):
            err = max(err, abs(p[0] - CX[c]), abs(p[1] - RY[r]))
    return iso_atoms(snapped), err


if __name__ == "__main__":
    print("第1行：图3 == 逆时针90°(图1 XOR 图2) ->", row1_ok)
    print("第2行：图6 == 逆时针90°(图4 XOR 图5) ->", row2_ok)
    # 顺时针的对照（应为 False）
    print("  对照：第1行若顺时针 ->", R1["3"] == rot_ccw_grid(rot_ccw_grid(rot_ccw_grid(R1["1"] ^ R1["2"], 3), 3), 3))
    print("第3行：图7 XOR 图8 共", len(xor78), "个原子段")
    for k in "ABCD":
        same, e0 = iso_of_option(k, None)
        ccw, e1 = iso_of_option(k, "cw")    # 选项若为 XOR 逆时针转90°的结果，顺时针转回应等于 XOR
        cw, e2 = iso_of_option(k, "ccw")
        print(f"选项{k}: 等于XOR(不转)={same == xor78 and e0 < 40}  "
              f"等于逆时针90°(XOR)={ccw == xor78 and e1 < 40}  "
              f"等于顺时针90°(XOR)={cw == xor78 and e2 < 40}  "
              f"[吸附偏差px: {e0:.0f}/{e1:.0f}/{e2:.0f}]")
