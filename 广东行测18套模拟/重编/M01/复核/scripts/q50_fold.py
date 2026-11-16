"""第50题：展开图折叠核对。
1. 从展开图取出 6 个面（按边框中心线裁切），重采样成 N x N 的“线条图”（局部坐标 u 向右, v 向下）。
2. 每个选项立方体：按测得的正面方框与进深向量，把正面/顶面/右面反投影成 N x N 正方形
   （正面: s 右 t 下；顶面: s 右, t 从后棱(0)到前棱(1)；右面: s 从前棱(0)到后棱(1), t 下）。
3. 展开图在三维中折叠（F4 作正面），对 24 种旋转，求出三个可见面分别是哪一面、以何种二面体变换出现，
   与选项反投影图比较（对称倒角距离，单位=面边长的百分比，去掉贴边 8% 的边框带）。
用法: python3 q50_fold.py <png> [outdir]
"""
import sys
import itertools
import numpy as np
from PIL import Image

img = np.array(Image.open(sys.argv[1]).convert("L")).astype(float)
outdir = sys.argv[2] if len(sys.argv) > 2 else None
H, W = img.shape
N = 60


def sample(x, y):
    """双线性取灰度"""
    x = np.clip(x, 0, W - 1.001); y = np.clip(y, 0, H - 1.001)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    v = (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
         + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)
    return v


grid = (np.arange(N) + 0.5) / N
S_, T_ = np.meshgrid(grid, grid)  # S_ 列方向, T_ 行方向

# ---- 展开图各面（边框中心线坐标由投影测得）----
VX = [17.0, 46.8, 75.8, 105.4, 134.8]
HY = [18.0, 47.2, 76.2, 105.5]
net_cells = {"F1": (0, 0), "F2": (1, 0), "F3": (1, 1), "F4": (2, 1), "F5": (3, 1), "F6": (2, 2)}


def net_face(col, row):
    x0, x1 = VX[col], VX[col + 1]
    y0, y1 = HY[row], HY[row + 1]
    return sample(x0 + S_ * (x1 - x0), y0 + T_ * (y1 - y0))


faces = {k: net_face(*v) for k, v in net_cells.items()}

# ---- 选项几何：正面左/右/上/下边框中心与后棱位置 ----
opts = {
    "A": dict(L=166.0, R=224.0, T=42.0, B=99.5, back_x=242.5, back_y=22.5),
    "B": dict(L=278.0, R=335.5, T=41.5, B=99.5, back_x=354.5, back_y=22.0),
    "C": dict(L=390.5, R=448.0, T=42.5, B=99.5, back_x=467.0, back_y=22.5),
    "D": dict(L=502.0, R=560.0, T=41.5, B=98.5, back_x=578.5, back_y=22.0),
}


def opt_faces(g):
    X0, Y0 = g["L"], g["T"]
    Sx, Sy = g["R"] - g["L"], g["B"] - g["T"]
    dx, dy = g["back_x"] - g["R"], g["back_y"] - g["T"]
    front = sample(X0 + S_ * Sx, Y0 + T_ * Sy)
    top = sample(X0 + S_ * Sx + (1 - T_) * dx, Y0 + (1 - T_) * dy)
    right = sample(X0 + Sx + S_ * dx, Y0 + T_ * Sy + S_ * dy)
    return {"front": front, "top": top, "right": right}


def to_mask(a, thr=150, border=0.08):
    m = a < thr
    b = int(round(border * N))
    m[:b, :] = False; m[-b:, :] = False; m[:, :b] = False; m[:, -b:] = False
    return m


def chamfer(m1, m2):
    p1 = np.argwhere(m1).astype(float); p2 = np.argwhere(m2).astype(float)
    if len(p1) == 0 and len(p2) == 0:
        return 0.0
    if len(p1) == 0 or len(p2) == 0:
        return 99.0
    d = np.sqrt(((p1[:, None, :] - p2[None, :, :]) ** 2).sum(-1))
    return float((d.min(1).mean() + d.min(0).mean()) / 2 / N * 100)


# ---- 三维折叠 ----
def fold(root="F4"):
    frames = {root: (np.array([0, 1, 1.]), np.array([1, 0, 0.]), np.array([0, -1, 0.]), np.array([0, 0, 1.]))}
    pos = {v: k for k, v in net_cells.items()}
    queue = [root]
    while queue:
        f = queue.pop(0)
        O, U, V, Nn = frames[f]
        c, r = net_cells[f]
        for (dc, dr) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            g = pos.get((c + dc, r + dr))
            if g is None or g in frames:
                continue
            if (dc, dr) == (1, 0):
                fr = (O + U, -Nn, V, U)
            elif (dc, dr) == (-1, 0):
                fr = (O - Nn, Nn, V, -U)
            elif (dc, dr) == (0, 1):
                fr = (O + V, U, -Nn, V)
            else:
                fr = (O - Nn, U, Nn, -V)
            frames[g] = fr
            queue.append(g)
    return frames


frames = fold()
for k, (O, U, V, Nn) in sorted(frames.items()):
    print(k, "normal", Nn.astype(int), "u->", U.astype(int), "v->", V.astype(int), "origin", O)

VIS = {  # 选项可见面: (原点, s方向, t方向, 法向)
    "front": (np.array([0, 1, 1.]), np.array([1, 0, 0.]), np.array([0, -1, 0.]), np.array([0, 0, 1.])),
    "top": (np.array([0, 1, 0.]), np.array([1, 0, 0.]), np.array([0, 0, 1.]), np.array([0, 1, 0.])),
    "right": (np.array([1, 1, 1.]), np.array([0, 0, -1.]), np.array([0, -1, 0.]), np.array([1, 0, 0.])),
}


def rotations():
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            M = np.zeros((3, 3))
            for r in range(3):
                M[r, perm[r]] = signs[r]
            if round(np.linalg.det(M)) == 1:
                out.append(M)
    return out


c = np.array([0.5, 0.5, 0.5])


def predicted(face_img, O, U, V, Ov, Sv, Tv):
    """把展开图面 (u,v) 映射到可见面 (s,t)；返回在 (s,t) 网格上的图像。"""
    # P = O + u U + v V ;  s = (P-Ov).Sv ; t = (P-Ov).Tv  ->  解 u,v
    A = np.array([[U @ Sv, V @ Sv], [U @ Tv, V @ Tv]])
    b = np.array([(O - Ov) @ Sv, (O - Ov) @ Tv])
    Ainv = np.linalg.inv(A)
    st = np.stack([S_ - b[0], T_ - b[1]], axis=-1)
    uv = st @ Ainv.T
    u = np.clip(uv[..., 0], 0, 1 - 1e-9); v = np.clip(uv[..., 1], 0, 1 - 1e-9)
    iu = (u * N).astype(int); iv = (v * N).astype(int)
    return face_img[iv, iu]


results = {}
for name, g in opts.items():
    of = opt_faces(g)
    best = []
    for R in rotations():
        tot = 0
        detail = []
        for vis, (Ov, Sv, Tv, Nv) in VIS.items():
            for f, (O, U, V, Nn) in frames.items():
                if np.allclose(R @ Nn, Nv):
                    O2 = R @ (O - c) + c; U2 = R @ U; V2 = R @ V
                    pred = predicted(faces[f], O2, U2, V2, Ov, Sv, Tv)
                    d = chamfer(to_mask(pred), to_mask(of[vis]))
                    detail.append((vis, f, round(d, 1)))
                    tot += d
        best.append((round(tot, 1), detail))
    best.sort(key=lambda z: z[0])
    results[name] = best
    print(f"\n选项 {name} 最优 3 个旋转（总倒角距离，越小越吻合；各面: 可见面, 展开图面, 距离）:")
    for b in best[:3]:
        print("  ", b)

if outdir:
    # 输出拼图：每个选项的三面反投影 + 最优旋转下的预测图
    tiles = []
    for name, g in opts.items():
        of = opt_faces(g)
        row = [of["top"], of["front"], of["right"]]
        tiles.append(np.concatenate([np.pad(r, 2, constant_values=128) for r in row], axis=1))
    Image.fromarray(np.concatenate(tiles, axis=0).astype(np.uint8)).resize(((N + 4) * 3 * 4, (N + 4) * 4 * 4), Image.NEAREST).save(f"{outdir}/q50_opt_faces.png")
    nets = np.concatenate([np.pad(faces[k], 2, constant_values=128) for k in sorted(faces)], axis=1)
    Image.fromarray(nets.astype(np.uint8)).resize(((N + 4) * 6 * 4, (N + 4) * 4), Image.NEAREST).save(f"{outdir}/q50_net_faces.png")
    print("saved", outdir)
