"""第49题：正方体展开图折叠模拟。

1. 从题图中截取展开图六个面的贴图（按网格线定位）；
2. 按展开图连接关系折成正方体，记录每个面局部坐标 -> 三维坐标的映射；
3. 对正方体的24种朝向，渲染出"正面、顶面、右侧面"三个可见面的贴图；
4. 把每个选项立体图的三个可见面（斜二测投影的平行四边形）反变换成正方形；
5. 逐像素比较（黑色填充为主），给出每个选项与24种朝向的最佳吻合度。

展开图（列, 行）：
    .   .   T2  T3
    M0  M1  M2  .
    .   B1  .   .
"""
import itertools
import numpy as np
from PIL import Image

P = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p12_i00.png"
G = np.array(Image.open(P).convert('L')).astype(float)

N = 40  # 每个面重采样的分辨率


def bilinear(img, x, y):
    x0 = np.clip(np.floor(x).astype(int), 0, img.shape[1] - 2)
    y0 = np.clip(np.floor(y).astype(int), 0, img.shape[0] - 2)
    fx = x - x0; fy = y - y0
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


# ---- 展开图各面（像素边界取格线中心） ----
XL = [19.5, 47.5, 75.5, 104.5, 132.5]
YL = [20.5, 48.5, 76.5, 105.5]
NET = {'T2': (2, 0), 'T3': (3, 0), 'M0': (0, 1), 'M1': (1, 1), 'M2': (2, 1), 'B1': (1, 2)}
INSET = 0.06  # 去掉边框线附近


def face_tex(name):
    c, r = NET[name]
    xa, xb = XL[c], XL[c + 1]; ya, yb = YL[r], YL[r + 1]
    t = (np.arange(N) + 0.5) / N
    t = INSET + t * (1 - 2 * INSET)
    U, V = np.meshgrid(t, t)
    return bilinear(G, xa + U * (xb - xa), ya + V * (yb - ya))


TEX = {k: face_tex(k) for k in NET}

# ---- 折叠：局部(x,y) -> 三维 (X,Y,Z)，Z=1 为正面，Y=1 为顶面，X=1 为右面 ----
TO3D = {
    'M1': lambda x, y: (x, 1 - y, 1),
    'M2': lambda x, y: (1, 1 - y, 1 - x),
    'T2': lambda x, y: (y, 1, 1 - x),
    'T3': lambda x, y: (y, 1 - x, 0),
    'M0': lambda x, y: (0, 1 - y, x),
    'B1': lambda x, y: (x, 0, 1 - y),
}


def from3d(p):
    X, Y, Z = p
    eps = 1e-6
    if abs(Z - 1) < eps: return 'M1', X, 1 - Y
    if abs(X - 1) < eps: return 'M2', 1 - Z, 1 - Y
    if abs(Y - 1) < eps: return 'T2', 1 - Z, X
    if abs(Z) < eps: return 'T3', 1 - Y, X
    if abs(X) < eps: return 'M0', Z, 1 - Y
    if abs(Y) < eps: return 'B1', X, 1 - Z
    raise ValueError(p)


# 自检：折叠映射与反映射一致，且相邻面公共棱吻合
for k, f in TO3D.items():
    for x, y in [(0.2, 0.7), (0.9, 0.1)]:
        kk, xx, yy = from3d(f(x, y))
        assert kk == k and abs(xx - x) < 1e-9 and abs(yy - y) < 1e-9, (k, kk)


def rotations():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3))
            for i in range(3):
                M[i, perm[i]] = signs[i]
            if round(np.linalg.det(M)) == 1:
                mats.append(M)
    return mats


ROTS = rotations()
assert len(ROTS) == 24


def render(R, view):
    """R: 旋转矩阵（作用于以中心为原点的坐标）。view: 'front'/'top'/'right'。
    返回 N×N 灰度图 和 该视面上原来的面名。"""
    t = (np.arange(N) + 0.5) / N
    t = INSET + t * (1 - 2 * INSET)
    out = np.zeros((N, N)); names = set()
    Rinv = R.T
    for j, v in enumerate(t):
        for i, u in enumerate(t):
            if view == 'front':
                p = (u, 1 - v, 1)          # u: 左->右, v: 上->下
            elif view == 'top':
                p = (u, 1, v)              # u: 左->右, v: 后->前
            else:
                p = (1, 1 - v, 1 - u)      # u: 前->后, v: 上->下
            q = Rinv @ (np.array(p) - 0.5) + 0.5
            q = np.round(q, 9)
            k, x, y = from3d(q)
            names.add(k)
            out[j, i] = TEX[k][min(int(y * N), N - 1), min(int(x * N), N - 1)]
    assert len(names) == 1
    return out, names.pop()


# ---- 选项的三个可见面反变换 ----
OPT = {  # fx0, fx1, fy0, fy1, dx, dy
    'A': (178.5, 232.5, 47.5, 101.0, 17.0, 17.5),
    'B': (285.5, 339.5, 47.5, 101.0, 17.0, 17.5),
    'C': (396.5, 450.5, 46.5, 99.5, 18.0, 18.0),
    'D': (497.5, 550.5, 47.5, 101.0, 18.0, 17.5),
}


def opt_faces(k):
    fx0, fx1, fy0, fy1, dx, dy = OPT[k]
    W = fx1 - fx0; H = fy1 - fy0
    t = (np.arange(N) + 0.5) / N
    t = INSET + t * (1 - 2 * INSET)
    U, V = np.meshgrid(t, t)
    front = bilinear(G, fx0 + U * W, fy0 + V * H)
    top = bilinear(G, fx0 + U * W + (1 - V) * dx, fy0 - (1 - V) * dy)
    right = bilinear(G, fx1 + U * dx, fy0 + V * H - U * dy)
    return {'front': front, 'top': top, 'right': right}


def binar(a):
    return (a < 110).astype(float)


def score(a, b):
    """黑色像素的 IoU。"""
    A = binar(a); B = binar(b)
    inter = (A * B).sum(); uni = ((A + B) > 0).sum()
    return inter / uni if uni else 1.0


def ascii(a):
    return '\n'.join(''.join('#' if v < 110 else '.' for v in row[::2]) for row in a[::2])


if __name__ == '__main__':
    results = {}
    for k in 'ABCD':
        of = opt_faces(k)
        best = []
        for idx, R in enumerate(ROTS):
            s = []; nm = []
            for view in ('front', 'top', 'right'):
                img, name = render(R, view)
                s.append(score(img, of[view])); nm.append(name)
            best.append((min(s), s, nm, idx))
        best.sort(key=lambda z: -z[0])
        results[k] = best
        print(f'选项{k} 前三名朝向（三面黑块IoU最小值，[正,顶,右]IoU，[正,顶,右]对应展开图面）：')
        for b in best[:3]:
            print('   ', round(b[0], 3), [round(x, 3) for x in b[1]], b[2], 'rot#', b[3])
    # 输出最佳朝向下的对比图
    for k in 'ABCD':
        of = opt_faces(k)
        b = results[k][0]
        R = ROTS[b[3]]
        print(f'\n==== 选项{k} 最佳朝向 {b[2]} ====')
        for view in ('front', 'top', 'right'):
            img, name = render(R, view)
            la = ascii(of[view]).split('\n'); lb = ascii(img).split('\n')
            print(f'-- {view}: 选项图（左）  vs  折叠出的 {name}（右）')
            for x, y in zip(la, lb):
                print(x + '   |   ' + y)
