"""通用：从题图中提取方格黑白矩阵（用于第46题等黑白格类图推题）。

做法：在给定的面板 x、y 范围内，按列/按行统计暗像素，暗像素数接近满高/满宽的
列（行）视为格线；相邻格线之间为一个格子，取格子内部（去掉边缘2像素）的平均灰度，
<128 记为黑格(1)，否则白格(0)。
"""
import sys
import numpy as np
from PIL import Image


def find_lines(profile, full, tol=0.9):
    """返回格线中心位置列表：profile >= tol*full 的连续段取中心。"""
    idx = np.where(profile >= tol * full)[0]
    lines = []
    if len(idx) == 0:
        return lines
    start = idx[0]
    prev = idx[0]
    for i in idx[1:]:
        if i == prev + 1:
            prev = i
            continue
        lines.append(((start + prev) / 2.0, start, prev))
        start = prev = i
    lines.append(((start + prev) / 2.0, start, prev))
    return lines


def extract(img_path, x0, x1, y0, y1, n=None, thr=128, verbose=False):
    g = np.array(Image.open(img_path).convert('L')).astype(float)
    dark = g < thr
    sub = dark[y0:y1, x0:x1]
    h, w = sub.shape
    vlines = find_lines(sub.sum(axis=0), h)
    hlines = find_lines(sub.sum(axis=1), w)
    if verbose:
        print('vlines', [(round(a + x0, 1), b + x0, c + x0) for a, b, c in vlines])
        print('hlines', [(round(a + y0, 1), b + y0, c + y0) for a, b, c in hlines])
    # 去掉过近的重复线（双线外框）
    def dedup(lines):
        out = []
        for ln in lines:
            if out and ln[1] - out[-1][2] <= 2:
                # 合并
                out[-1] = ((out[-1][1] + ln[2]) / 2.0, out[-1][1], ln[2])
            else:
                out.append(ln)
        return out
    vlines = dedup(vlines)
    hlines = dedup(hlines)
    grid = []
    for r in range(len(hlines) - 1):
        row = []
        ya = hlines[r][2] + 1 + y0
        yb = hlines[r + 1][1] - 1 + y0
        for c in range(len(vlines) - 1):
            xa = vlines[c][2] + 1 + x0
            xb = vlines[c + 1][1] - 1 + x0
            cell = g[ya + 1:yb, xa + 1:xb]
            m = cell.mean() if cell.size else 255
            row.append(1 if m < thr else 0)
        grid.append(row)
    return grid, vlines, hlines


def show(grid):
    return '\n'.join(''.join('#' if v else '.' for v in row) for row in grid)


if __name__ == '__main__':
    p = sys.argv[1]
    x0, x1, y0, y1 = map(int, sys.argv[2:6])
    grid, v, h = extract(p, x0, x1, y0, y1, verbose=True)
    print(show(grid))
