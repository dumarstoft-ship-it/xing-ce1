# 第50题：折纸盒。把展开图按面折成正方体，渲染24种摆放的“前、上、右”三面斜视图，
# 与四个选项逐一比较（线条图的双向倒角距离），并输出对照图。
# 面内坐标 (u,v)：u 向右、v 向下，取值 0~1；线段端点由放大网格图和像素值读出。
import itertools, numpy as np
from PIL import Image, ImageDraw

FACES = {  # 展开图中的位置 (列, 行)
    'F1': (0, 0), 'F2': (1, 0), 'F3': (1, 1), 'F4': (2, 1), 'F5': (3, 1), 'F6': (2, 2)}
LINES = {
    'F1': [((0.47, 0), (0, 1)), ((0.47, 0), (1, 1)), ((0, 0.49), (1, 0.49))],                # “A”形
    'F2': [((0.34, 0), (0.34, 0.44)), ((0.34, 0.44), (1, 0)), ((0.34, 0.44), (0, 1)),
           ((0.32, 0.49), (1, 0.49)), ((0.15, 0.72), (1, 0.75))],
    'F3': [((0, 1), (1, 0)), ((0, 0.45), (1, 0.45))],
    'F4': [((0.43, 0), (0.43, 0.5)), ((0.43, 0.5), (1, 0)), ((0.43, 0.5), (0, 1)),
           ((0.43, 0.5), (1, 0.53)), ((0.71, 0), (0.71, 0.25)), ((0.71, 0.25), (1, 0.26))],
    'F5': [((0, 0), (1, 1)), ((0.47, 0), (0, 0.53)), ((1, 0.42), (0.46, 1))],
    'F6': [((0, 1), (1, 0.65))],
}

def fold():
    """以F4为前面，BFS折叠。返回每个面: (O, ex, ey, n) 使得 3D点 = O + X*ex + Y*ey (X,Y为展开图平面坐标)"""
    A = np.array
    maps = {'F4': (A([-2., 2., 1.]), A([1., 0, 0]), A([0, -1., 0]), A([0, 0, -1.]))}
    pos = {v: k for k, v in FACES.items()}
    queue = ['F4']
    while queue:
        f = queue.pop(0)
        O, ex, ey, n = maps[f]
        cx, cy = FACES[f]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            g = pos.get((cx + dx, cy + dy))
            if g is None or g in maps: continue
            if dx == 1:
                X1 = cx + 1; O2 = O + X1 * ex - X1 * n; maps[g] = (O2, n, ey, -ex)
            elif dx == -1:
                X0 = cx; O2 = O + X0 * ex + X0 * n; maps[g] = (O2, -n, ey, ex)
            elif dy == 1:
                Y1 = cy + 1; O2 = O + Y1 * ey - Y1 * n; maps[g] = (O2, ex, n, -ey)
            else:
                Y0 = cy; O2 = O + Y0 * ey + Y0 * n; maps[g] = (O2, ex, -n, ey)
            queue.append(g)
    return maps

MAPS = fold()

def face_segments_3d():
    segs = {}
    for f, lines in LINES.items():
        O, ex, ey, n = MAPS[f]
        cx, cy = FACES[f]
        P = lambda u, v: O + (cx + u) * ex + (cy + v) * ey
        segs[f] = [(P(*a), P(*b)) for a, b in lines]
        # 面的外法向 = -n
    return segs

SEGS = face_segments_3d()
NORMALS = {f: -MAPS[f][3] for f in MAPS}

def check_cube():
    # 各面四角应落在单位正方体的同一个面上
    for f in FACES:
        O, ex, ey, n = MAPS[f]; cx, cy = FACES[f]
        corners = [O + (cx + a) * ex + (cy + b) * ey for a in (0, 1) for b in (0, 1)]
        assert all(np.all((c > -1e-9) & (c < 1 + 1e-9)) for c in corners), f
    ns = sorted(tuple(np.round(v, 6)) for v in NORMALS.values())
    assert len(set(ns)) == 6, ns

check_cube()

def rotations():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = np.zeros((3, 3))
            for i in range(3): m[i, perm[i]] = signs[i]
            if round(np.linalg.det(m)) == 1: mats.append(m)
    return mats
ROTS = rotations()

S, K = 58.0, 19.5   # 选项图：前面边长约58px，进深偏移约(19.5,-19.5)
def project(p):
    x, y, z = p   # x右, y上, z朝向观察者(前面 z=1)
    return (S * x + K * (1 - z), S * (1 - y) + K * z)   # 前面左上角为(0,K)

def render(R, size=(82, 82), scale=1, width=2):
    img = Image.new('L', (int(size[0] * scale), int(size[1] * scale)), 255)
    d = ImageDraw.Draw(img)
    c = np.array([0.5, 0.5, 0.5])
    vis = []
    for f, segs in SEGS.items():
        nrm = R @ NORMALS[f]
        if nrm[2] > 0.5 or nrm[1] > 0.5 or nrm[0] > 0.5:
            vis.append(f)
            for a, b in segs:
                pa = R @ (a - c) + c; pb = R @ (b - c) + c
                A = project(pa); B = project(pb)
                d.line([(A[0] * scale, A[1] * scale), (B[0] * scale, B[1] * scale)], fill=0, width=width)
    # 立方体轮廓
    cube = [((0,0,1),(1,0,1)),((1,0,1),(1,1,1)),((1,1,1),(0,1,1)),((0,1,1),(0,0,1)),
            ((0,1,1),(0,1,0)),((0,1,0),(1,1,0)),((1,1,0),(1,1,1)),((1,1,0),(1,0,0)),((1,0,0),(1,0,1))]
    for a, b in cube:
        A = project(np.array(a, float)); B = project(np.array(b, float))
        d.line([(A[0] * scale, A[1] * scale), (B[0] * scale, B[1] * scale)], fill=0, width=width)
    return img, vis

def face_in_view(R):
    """返回 (前, 上, 右) 三个可见面名称"""
    out = {}
    for f in SEGS:
        nrm = R @ NORMALS[f]
        if nrm[2] > 0.5: out['前'] = f
        if nrm[1] > 0.5: out['上'] = f
        if nrm[0] > 0.5: out['右'] = f
    return out['前'], out['上'], out['右']

if __name__ == '__main__':
    for f in FACES:
        print(f, '外法向', np.round(NORMALS[f], 3))
