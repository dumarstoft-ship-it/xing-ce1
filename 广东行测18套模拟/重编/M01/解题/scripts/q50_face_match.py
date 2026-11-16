# 第50题：逐面识别。把每个选项的前、上、右三面“拉正”为正方形（从外面看），
# 与展开图六个面的图案在4种旋转下比较（只比较面内线条，去掉边框），找出每个可见面是哪一面、转了多少度；
# 再用折叠结果检验三面的相对位置是否一致。
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from q50_fold import LINES, ROTS, SEGS, NORMALS, S, K, face_in_view
from PIL import Image, ImageDraw

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s16_p12_i01.png'
a = np.array(Image.open(IMG).convert('L')).astype(float)
BOX = {'A': (165, 22), 'B': (277, 21), 'C': (390, 22), 'D': (501, 21)}
M = 60  # 拉正后的分辨率

def sample(img, x, y):
    x0, y0 = int(np.floor(x)), int(np.floor(y)); fx, fy = x - x0, y - y0
    v = (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy) +
         img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)
    return v

def unwarp(k):
    x0, y0 = BOX[k]
    reg = a
    # 选项外接框左上角 (x0,y0)；前面左上角在 (x0, y0+K)
    faces = {}
    for name in ('前', '上', '右'):
        out = np.zeros((M, M))
        for j in range(M):
            for i in range(M):
                u = (i + 0.5) / M; v = (j + 0.5) / M
                if name == '前':
                    X, Y = u * S, K + v * S
                elif name == '上':
                    X, Y = u * S + (1 - v) * K, v * K
                else:
                    X, Y = S + u * K, (1 - u) * K + v * S
                out[j, i] = sample(reg, x0 + X, y0 + Y)
        faces[name] = out < 120
    return faces

def rot_uv(u, v, r):
    for _ in range(r):  # 顺时针转90°：(u,v)->(1-v,u)
        u, v = 1 - v, u
    return u, v

def pattern_points(face, r, step=0.01):
    P = []
    for (u1, v1), (u2, v2) in LINES[face]:
        L = max(abs(u2 - u1), abs(v2 - v1))
        n = max(2, int(L / step))
        for t in np.linspace(0, 1, n):
            u = u1 + (u2 - u1) * t; v = v1 + (v2 - v1) * t
            P.append(rot_uv(u, v, r))
    return np.array(P)

def interior_points(mask, margin=0.09):
    ys, xs = np.nonzero(mask)
    u = (xs + 0.5) / M; v = (ys + 0.5) / M
    keep = (u > margin) & (u < 1 - margin) & (v > margin) & (v < 1 - margin)
    return np.stack([u[keep], v[keep]], 1)

def score(P, Q, margin=0.09):
    Qi = Q[(Q[:, 0] > margin) & (Q[:, 0] < 1 - margin) & (Q[:, 1] > margin) & (Q[:, 1] < 1 - margin)]
    if len(P) == 0 or len(Qi) == 0:
        return 9.9
    D = np.sqrt(((P[:, None, :] - Qi[None, :, :]) ** 2).sum(-1))
    return (D.min(1).mean() + D.min(0).mean()) / 2

# 由折叠关系得到：给定 (前,上,右) 面及前面的旋转，上、右面的旋转应为多少 —— 直接从24种摆放中查
def expected_views():
    table = {}
    c = np.array([0.5, 0.5, 0.5])
    for R in ROTS:
        fr, tp, rt = face_in_view(R)
        table[(fr, tp, rt)] = R
    return table

summary = {}
for k in BOX:
    faces = unwarp(k)
    print(f'选项{k}:')
    best = {}
    for name in ('前', '上', '右'):
        P = interior_points(faces[name])
        cands = []
        for f in LINES:
            for r in range(4):
                cands.append((score(P, pattern_points(f, r)), f, r * 90))
        cands.sort()
        best[name] = cands[0]
        print(f'   {name}面: 最像 {cands[0][1]} 顺时针{cands[0][2]}°(误差{cands[0][0]:.3f}); 其次 '
              + '; '.join(f'{c[1]} {c[2]}°({c[0]:.3f})' for c in cands[1:4]))
    summary[k] = best
