"""第49题：程序折叠正方体并与四个选项逐像素比对。
1) 从题图中取出展开图的6个面（按格线位置采样为 N×N 灰度图）；
2) 按“滚动”规则把展开图折成正方体，记下每个面在立体上的法向和面内方向；
3) 对每个选项，按斜二测画法的角点把正面、顶面、右侧面反采样成 N×N 方图；
4) 枚举正方体的24种摆放，把展开图的面渲染到这三个可见面上，与选项逐像素比较，
   找出每个选项的最佳匹配及误差；同时单独比较每个可见面与6个面（8种对称变换）的最佳匹配。"""
from PIL import Image
import numpy as np
from scipy import ndimage
import itertools

PATH = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p12_i00.png'
img = np.array(Image.open(PATH).convert('L')).astype(float) / 255.0  # 1=白, 0=黑
N = 40

def bilinear(x, y):
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    H, W = img.shape
    x0c = np.clip(x0, 0, W - 2); y0c = np.clip(y0, 0, H - 2)
    v = (img[y0c, x0c] * (1 - fx) * (1 - fy) + img[y0c, x0c + 1] * fx * (1 - fy)
         + img[y0c + 1, x0c] * (1 - fx) * fy + img[y0c + 1, x0c + 1] * fx * fy)
    return v

def sample(fn):
    t = (np.arange(N) + 0.5) / N
    u, v = np.meshgrid(t, t)          # u 向右, v 向下
    x, y = fn(u, v)
    return 1.0 - bilinear(x, y)       # 返回“黑度”(1=黑)

# ---------- 展开图 ----------
XS = [19.5, 47.5, 76.0, 104.5, 132.5]
YS = [20.5, 48.5, 76.5, 105.0]
NET = {'P': (0, 2), 'Q': (0, 3), 'R': (1, 0), 'S': (1, 1), 'T': (1, 2), 'U': (2, 1)}

def net_face(r, c):
    x0, x1, y0, y1 = XS[c], XS[c + 1], YS[r], YS[r + 1]
    return sample(lambda u, v: (x0 + u * (x1 - x0), y0 + v * (y1 - y0)))

FACES = {k: net_face(*rc) for k, rc in NET.items()}

# ---------- 折叠 ----------
X, Y, Z = np.eye(3, dtype=int)
def fold():
    state = {'S': (Z, X, -Y)}   # (法向N, 面内向右R, 面内向下D)；S 作正面
    pos = {k: v for k, v in NET.items()}
    frontier = ['S']
    while frontier:
        k = frontier.pop()
        N_, R_, D_ = state[k]
        r, c = pos[k]
        for k2, (r2, c2) in pos.items():
            if k2 in state:
                continue
            if (r2, c2) == (r, c + 1):
                state[k2] = (R_, -N_, D_)
            elif (r2, c2) == (r, c - 1):
                state[k2] = (-R_, N_, D_)
            elif (r2, c2) == (r + 1, c):
                state[k2] = (D_, R_, -N_)
            elif (r2, c2) == (r - 1, c):
                state[k2] = (-D_, R_, N_)
            else:
                continue
            frontier.append(k2)
    return state

STATE = fold()
normals = [tuple(v[0]) for v in STATE.values()]
assert len(set(normals)) == 6, '折叠后6个面法向应互不相同'
OPP = {}
for a, b in itertools.combinations(STATE, 2):
    if tuple(STATE[a][0]) == tuple(-STATE[b][0]):
        OPP[a] = b; OPP[b] = a

# 24个旋转矩阵
def rotations():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3), dtype=int)
            for i in range(3):
                M[i, perm[i]] = signs[i]
            if round(np.linalg.det(M)) == 1:
                mats.append(M)
    return mats
ROTS = rotations()
assert len(ROTS) == 24

# 视图中三个可见面的 (法向, 视图u方向, 视图v方向)
VIEW = {'front': (Z, X, -Y), 'top': (Y, X, Z), 'right': (X, -Z, -Y)}

def render(M, which):
    n, U, V = VIEW[which]
    for k, (N_, R_, D_) in STATE.items():
        if tuple(M @ N_) == tuple(n):
            R2, D2 = M @ R_, M @ D_
            t = (np.arange(N) + 0.5) / N
            u, v = np.meshgrid(t, t)
            # 视图点相对面中心的三维位置 -> 面内坐标
            px = (u - 0.5)[..., None] * U + (v - 0.5)[..., None] * V
            a = px @ R2 + 0.5
            b = px @ D2 + 0.5
            ia = np.clip((a * N).astype(int), 0, N - 1)
            ib = np.clip((b * N).astype(int), 0, N - 1)
            return k, FACES[k][ib, ia]
    raise RuntimeError

# ---------- 选项 ----------
OPT_GEOM = {  # 正面左x, 右x, 上y, 下y, 进深dx, dy（由像素轮廓测得）
    'A': (178.5, 232.5, 47.5, 101.0, 17.0, 17.5),
    'B': (285.5, 339.5, 47.5, 101.0, 17.0, 17.5),
    'C': (396.5, 450.5, 46.5, 99.5, 18.0, 18.0),
    'D': (497.0, 550.5, 47.5, 101.0, 18.0, 17.5),
}

def opt_faces(k):
    x0, x1, y0, y1, dx, dy = OPT_GEOM[k]
    front = sample(lambda u, v: (x0 + u * (x1 - x0), y0 + v * (y1 - y0)))
    top = sample(lambda u, v: (x0 + u * (x1 - x0) + (1 - v) * dx, y0 - (1 - v) * dy))
    right = sample(lambda u, v: (x1 + u * dx, y0 + v * (y1 - y0) - u * dy))
    return {'front': front, 'top': top, 'right': right}

def blur(a):
    return ndimage.gaussian_filter(a, 1.5)

def dist(a, b):
    m = np.zeros_like(a); m[3:-3, 3:-3] = 1   # 忽略边框附近
    return float(((blur(a) - blur(b)) ** 2 * m).sum() / m.sum())

def d8(a):
    out = []
    for flip in (False, True):
        b = a[:, ::-1] if flip else a
        for r in range(4):
            out.append((('镜像' if flip else '') + f'转{90*r}', np.rot90(b, -r)))
    return out

if __name__ == '__main__':
    print('相对面:', {k: OPP[k] for k in sorted(OPP)})
    for k in 'ABCD':
        of = opt_faces(k)
        print(f'\n===== 选项{k} =====')
        # 每个可见面单独找最像的展开面
        for w in ('top', 'front', 'right'):
            cands = []
            for fk, F in FACES.items():
                for name, G in d8(F):
                    cands.append((dist(of[w], G), fk, name))
            cands.sort()
            print(f'  {w:5s} 最像:', ', '.join(f'{fk}{name}:{d:.4f}' for d, fk, name in cands[:4]))
        # 整体：24种摆放
        res = []
        for i, M in enumerate(ROTS):
            tot = 0; used = []
            for w in ('top', 'front', 'right'):
                fk, R = render(M, w)
                tot += dist(of[w], R); used.append(fk)
            res.append((tot, i, used))
        res.sort()
        for tot, i, used in res[:3]:
            print(f'  摆放#{i}: 顶={used[0]} 前={used[1]} 右={used[2]}  总误差={tot:.4f}')

# ---------- 结论汇总（解析中的编号：上排①②，中排③④⑤，下方⑥）----------
LABEL = {'P': '①', 'Q': '②', 'R': '③', 'S': '④', 'T': '⑤', 'U': '⑥'}
if __name__ == '__main__':
    print('\n===== 汇总 =====')
    print('相对面:', sorted({tuple(sorted((LABEL[a], LABEL[b]))) for a, b in OPP.items()}))
    for k in 'ABCD':
        of = opt_faces(k)
        ids = {}
        indiv = 0.0
        for w in ('top', 'front', 'right'):
            best = min((dist(of[w], G), fk) for fk, F in FACES.items() for _, G in d8(F))
            ids[w] = best[1]; indiv += best[0]
        opp_pairs = [(a, b) for a in ids.values() for b in ids.values() if OPP.get(a) == b]
        best_tot, best_used = min(
            (sum(dist(of[w], render(M, w)[1]) for w in ('top', 'front', 'right')),
             [render(M, w)[0] for w in ('top', 'front', 'right')]) for M in ROTS)
        print(f'选项{k}: 单看各面 顶={LABEL[ids["top"]]} 前={LABEL[ids["front"]]} 右={LABEL[ids["right"]]}'
              f'（①⑥图案相同，单看分不出）；三面单独最佳误差之和={indiv:.3f}；'
              f'按折叠整体最佳摆放 顶{LABEL[best_used[0]]}前{LABEL[best_used[1]]}右{LABEL[best_used[2]]} 误差={best_tot:.3f}'
              + ('；可见面中有一组相对面→不可能' if opp_pairs else ''))
