# 第66题：读题图中两条平抛轨迹的落点，比较下落高度和水平位移。
# 平抛：t = sqrt(2h/g) 只由下落高度 h 决定；v = x / t。
# 同时检查 PDF 内嵌原图（216x170）和按原图坐标重绘的 PNG（放大6倍）。
from PIL import Image
import numpy as np

ORIG = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/原图核对/s21_p17_i04.png"
REDRAW = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p17_i04.png"


def box_count(mask, k):
    """每个像素 k×k 邻域内的黑点数（积分图）。"""
    p = np.pad(mask.astype(int), ((k, k), (k, k)))
    c = p.cumsum(0).cumsum(1)
    h, w = mask.shape
    r = k // 2
    y0, x0 = np.arange(h) + k - r - 1, np.arange(w) + k - r - 1
    y1, x1 = y0 + k, x0 + k
    return c[np.ix_(y1, x1)] - c[np.ix_(y0, x1)] - c[np.ix_(y1, x0)] + c[np.ix_(y0, x0)]


def analyse(path, s):
    im = np.array(Image.open(path).convert("L"))
    dark = im < 100
    H, W = im.shape
    # 横梁上沿：第一条黑像素占左半幅大部分的行
    bar_top = int(np.argmax(dark[:, : W // 2].mean(axis=1) > 0.8))
    # 竖墙右沿：横梁以下远处各行最右边的黑像素列（取众数）
    rows = range(bar_top + 25 * s, min(H, bar_top + 60 * s))
    wall_right = int(np.median([np.nonzero(dark[y])[0].max() for y in rows if dark[y].any()]))
    # O 点：横梁以上区域里最“实心”的黑块（圆点）
    cnt = box_count(dark[: bar_top // 2], 3 * s + 1)
    oy, ox = np.unravel_index(np.argmax(cnt), cnt.shape)
    # A 落点：横梁上沿紧上方、竖墙左侧的轨迹像素
    band = dark[bar_top - 3 * s: bar_top, : wall_right - 3 * s]
    ax = float(np.nonzero(band)[1].mean()); ay = bar_top
    # B 落点：竖墙右沿外侧（隔开抗锯齿边）仍有轨迹像素的最低行
    strip = dark[bar_top:, wall_right + 2: wall_right + 2 + 6 * s]
    by = bar_top + int(np.nonzero(strip.any(axis=1))[0].max()); bx = wall_right
    return dict(O=(int(ox), int(oy)), bar_top=bar_top, wall_right=wall_right, A=(round(ax, 1), ay), B=(bx, by))


for path, s in [(ORIG, 1), (REDRAW, 6)]:
    r = analyse(path, s)
    ox, oy = r["O"]
    hA, hB = r["A"][1] - oy, r["B"][1] - oy
    xA, xB = ox - r["A"][0], ox - r["B"][0]
    print(path.split("/")[-2], r)
    print("  下落高度 hA=%.0f hB=%.0f（像素）；水平位移 xA=%.0f xB=%.0f" % (hA, hB, xA, xB))
    # 结论只取决于两落点的相对位置：B 落点低于横梁上沿（在竖墙侧面），A 落点在横梁顶面且更靠左
    assert r["B"][1] > r["bar_top"] and r["A"][0] < r["wall_right"]
    assert hB > hA and xA > xB
    print("  => tA < tB（②）；且 xA > xB、tA < tB，故 vA > vB（③）")
print("答案: B（②③）")
