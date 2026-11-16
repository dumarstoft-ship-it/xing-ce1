"""M08第48题（换入JS2021-A类-080）：从原图读出各4×4方格的黑格，按连接方式核对答案。

读法：每个小框内找出方格网的外框，按4×4取每格中心附近的平均灰度，<100记为黑格。
"""
import sys
from itertools import combinations
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]
img = Image.open(ROOT / "江浙行测_AI题库/images/original/649.png").convert("L")
W, H = img.size
px = img.load()


def dark(x, y):
    return px[x, y] < 128


def grid_box(x0, x1, y0, y1):
    """在区域内找方格网外框：取暗像素最多的行、列中最外侧的那些。"""
    cols = [sum(dark(x, y) for y in range(y0, y1)) for x in range(x0, x1)]
    rows = [sum(dark(x, y) for x in range(x0, x1)) for y in range(y0, y1)]
    # 框线：贯穿方格网的竖线/横线，暗像素数接近网格高度
    cmax, rmax = max(cols), max(rows)
    cx = [x0 + i for i, c in enumerate(cols) if c > 0.6 * cmax]
    ry = [y0 + i for i, r in enumerate(rows) if r > 0.6 * rmax]
    return min(cx), max(cx), min(ry), max(ry)


def read_grid(x0, x1, y0, y1):
    gx0, gx1, gy0, gy1 = grid_box(x0, x1, y0, y1)
    cw, ch = (gx1 - gx0) / 4, (gy1 - gy0) / 4
    cells = set()
    for r in range(4):
        for c in range(4):
            cx, cy = gx0 + (c + 0.5) * cw, gy0 + (r + 0.5) * ch
            vals = [px[int(cx + dx), int(cy + dy)] for dx in range(-4, 5) for dy in range(-4, 5)]
            if sum(vals) / len(vals) < 100:
                cells.add((r, c))
    return cells


# 小框位置：上排6框等宽，下排4框（选项）与上排第2—5框对齐
def frames_top():
    w = W / 6
    return [(int(i * w) + 8, int((i + 1) * w) - 8, 8, 122) for i in range(5)]


def frames_opt():
    w = W / 6
    return [(int((i + 1) * w) + 8, int((i + 2) * w) - 8, 165, 280) for i in range(4)]


def link(cells):
    """返回（边相连的对数，角相连的对数，按“边或角”是否连成一片）。"""
    edge = sum(1 for a, b in combinations(cells, 2) if abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1)
    corner = sum(1 for a, b in combinations(cells, 2) if abs(a[0] - b[0]) == 1 and abs(a[1] - b[1]) == 1)
    seen, todo = set(), [next(iter(cells))]
    while todo:
        a = todo.pop()
        if a in seen:
            continue
        seen.add(a)
        todo += [b for b in cells if b not in seen and max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1]
    return edge, corner, len(seen) == len(cells)


def show(cells):
    return "/".join("".join("■" if (r, c) in cells else "□" for c in range(4)) for r in range(4))


ok = True
print("题干：")
for i, f in enumerate(frames_top(), 1):
    g = read_grid(*f)
    e, k, conn = link(g)
    print(f"  图{i} {show(g)} 黑格{len(g)} 边相连{e} 角相连{k} 连成一片{conn}")
    ok &= (len(g) == 5 and e == 0 and conn)
print("选项：")
fits = []
for L, f in zip("ABCD", frames_opt()):
    g = read_grid(*f)
    e, k, conn = link(g)
    fit = len(g) == 5 and e == 0 and conn
    print(f"  {L} {show(g)} 黑格{len(g)} 边相连{e} 角相连{k} 连成一片{conn} {'符合' if fit else ''}")
    if fit:
        fits.append(L)
print("题干5幅都是5个黑格、只靠角相连、连成一片：", ok)
print("符合的选项：", fits)
assert ok and fits == ["C"]
