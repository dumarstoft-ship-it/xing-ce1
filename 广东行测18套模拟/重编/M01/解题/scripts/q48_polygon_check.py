# 第48题：平面拼合（用顶点坐标精确比对）
# 顶点坐标由放大6倍、每10像素一格的网格图读出（单位：原图像素），见 q48_complement_check.py 的同一张图。
# 做法：左图在外接正方形中的补形 = 正方形去掉左图；把每个选项做 4种旋转 × 是否翻转，
# 归一化到外接框后与补形比较（栅格化求IoU，并给出锯齿边顶点的最大偏差）。
from PIL import Image, ImageDraw
import numpy as np

L = [(2.5,10.8),(56.7,24.2),(56.7,38),(16.2,58),(70.8,58),(30,70.8),(30,85),(84.2,91.3),(2.5,91.3)]
opts = {
 'A': [(15.5,98.3),(22.2,44.5),(35.8,44.5),(49.2,85.3),(49.2,30.8),(70,71.3),(83,71.3),(96.3,17.5),(96.3,98.3)],
 'B': [(18.3,19.7),(99.5,19.7),(45,40),(45,53.3),(86.2,66.7),(31.7,66.7),(72.5,73.3),(72.5,87),(18.3,100.5)],
 'C': [(19.2,20),(100,20),(86.2,73.3),(73,73.3),(66.3,33.8),(66.3,87.5),(53,46.7),(39.7,46.7),(19.2,100.8)],
 'D': [(96.3,23.3),(54.7,28.3),(54.7,48),(82.8,57),(29.2,57),(69.2,77.2),(69.2,90.8),(15.5,103.7),(96.3,103.7)],
}

def norm(poly):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, y0, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    return [((x - x0) / w, (y - y0) / h) for x, y in poly]

def transforms(poly):
    out = []
    for flip in (False, True):
        p = [(1 - x, y) for x, y in poly] if flip else poly
        for k in range(4):
            q = p
            for _ in range(k):          # 每次顺时针转90°（y轴向下的图像坐标）：(x,y)->(1-y,x)
                q = [(1 - y, x) for x, y in q]
            out.append((('翻转+' if flip else '') + f'顺时针{90*k}°', q))
    return out

N = 800
def raster(poly):
    img = Image.new('1', (N, N), 0)
    ImageDraw.Draw(img).polygon([(x * (N - 1), y * (N - 1)) for x, y in poly], fill=1)
    return np.array(img, dtype=bool)

Ln = norm(L)
square = np.ones((N, N), dtype=bool)
comp = square & ~raster(Ln)
# 补形的多边形（顺时针）：左上角 -> 右上角 -> 右下角 -> 沿锯齿边回到左上角
# 左图顶点：0左上,1..6锯齿,7右下,8左下；补形 = [左上, 右上, 右下, 锯齿6..1]
comp_poly = [Ln[0], (1.0, 0.0), Ln[7]] + Ln[6:0:-1]
print('补形面积比例(栅格) = %.3f, 多边形栅格 = %.3f' % (comp.mean(), raster(comp_poly).mean()))

def iou(a, b):
    return (a & b).sum() / (a | b).sum()

for k, poly in opts.items():
    res = []
    for name, q in transforms(norm(poly)):
        res.append((iou(raster(q), comp), name, q))
    res.sort(key=lambda t: -t[0])
    rot_only = [r for r in res if '翻转' not in r[1]]
    best = rot_only[0]
    # 顶点偏差：补形每个顶点到该选项（变换后）最近顶点的距离，换算成原图像素（边长约81px）
    dev = max(min(((cx - x) ** 2 + (cy - y) ** 2) ** 0.5 for x, y in best[2]) for cx, cy in comp_poly) * 81
    print(f'选项{k}: 仅旋转最佳 {best[1]} IoU={best[0]:.3f}, 补形顶点最大偏差≈{dev:.1f}px; '
          f'含翻转最佳 {res[0][1]} IoU={res[0][0]:.3f}')
