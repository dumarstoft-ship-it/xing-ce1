"""第90题：量出折线图四个数据点的像素位置，与各选项时间段的互联网保险保费同比增量逐一拟合。

数据点是实心黑圆点：对暗像素取5×5邻域计数，计数高的像素聚成4团，取质心。
每个选项的4个增量值与点的纵坐标做线性拟合（值＝a×高度＋b），比较残差和形状（升降方向）。
"""
import numpy as np
from PIL import Image

IMG = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s20_p24_i00.png"

PREMIUM = {2016: 2299, 2017: 1877, 2018: 1889, 2019: 2696, 2020: 2909,
           2021: 3779, 2022: 4783, 2023: 4949}
INC = {y: PREMIUM[y] - PREMIUM[y - 1] for y in range(2017, 2024)}
OPTIONS = {"A": range(2017, 2021), "B": range(2018, 2022),
           "C": range(2019, 2023), "D": range(2020, 2024)}


def find_dots():
    img = np.asarray(Image.open(IMG).convert("L"), dtype=float)
    dark = (img < 100).astype(int)
    h, w = dark.shape
    pad = np.pad(dark, 2)
    dens = np.zeros_like(dark)
    for dy in range(5):
        for dx in range(5):
            dens += pad[dy:dy + h, dx:dx + w]
    core = (dens >= 20) & (dark == 1)
    # 连通分量
    seen = np.zeros_like(core, dtype=bool)
    comps = []
    for y in range(h):
        for x in range(w):
            if core[y, x] and not seen[y, x]:
                stack = [(y, x)]
                seen[y, x] = True
                pts = []
                while stack:
                    cy, cx = stack.pop()
                    pts.append((cy, cx))
                    for ny in (cy - 1, cy, cy + 1):
                        for nx in (cx - 1, cx, cx + 1):
                            if 0 <= ny < h and 0 <= nx < w and core[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                stack.append((ny, nx))
                comps.append(pts)
    dots = []
    for pts in comps:
        if len(pts) >= 5:
            ys = [p[0] for p in pts]
            xs = [p[1] for p in pts]
            dots.append((sum(xs) / len(xs), sum(ys) / len(ys), len(pts)))
    dots.sort()
    return dots, h


def main():
    print("互联网保险保费同比增量（亿元）：", INC)
    dots, h = find_dots()
    print("数据点（x, y, 核心像素数）：", [(round(x, 1), round(y, 1), n) for x, y, n in dots])
    heights = np.array([h - y for _, y, _ in dots])  # 越大越高
    xs = [x for x, _, _ in dots]
    print("横向间距：", [round(xs[i + 1] - xs[i], 1) for i in range(len(xs) - 1)])
    print("点的相对高度（像素，向上为正）：", [round(v, 1) for v in heights - heights.min()])
    shape_chart = ["升" if heights[i + 1] > heights[i] else "降" for i in range(3)]
    print("图形升降：", shape_chart)
    print()
    for opt, yrs in OPTIONS.items():
        vals = np.array([INC[y] for y in yrs], dtype=float)
        shape = ["升" if vals[i + 1] > vals[i] else "降" for i in range(3)]
        A = np.vstack([heights, np.ones_like(heights)]).T
        coef, res, *_ = np.linalg.lstsq(A, vals, rcond=None)
        pred = A @ coef
        rmse = float(np.sqrt(np.mean((pred - vals) ** 2)))
        rng = vals.max() - vals.min()
        print(f"选项{opt} {yrs.start}-{yrs.stop - 1}: 增量{vals.astype(int).tolist()} 升降{shape}"
              f" 斜率{coef[0]:.2f}亿元/像素 残差RMSE={rmse:.1f}（占值域{rmse / rng * 100:.1f}%）"
              f" 形状{'吻合' if shape == shape_chart else '不符'}")


if __name__ == "__main__":
    main()
