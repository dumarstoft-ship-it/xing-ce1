# 第48题：由左图还原小立方体组合体，再把它的24种旋转（及24种镜像）按题图的斜二测画法渲染，
# 与四个选项逐一比对线条。匹配误差小（几百像素，与左图自身重渲染相当）= 同一物体。
import itertools
import numpy as np
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p11_i02.png'
U, K, SC = 20.5, 0.488, 3          # 正面边长(px)、进深缩短系数、放大倍数


def render(cubes, origin, size):
    """斜二测：X=ox+U(x+Kz), Y=oy-U(y+Kz)；z越小越靠前。返回棱线掩膜"""
    W, H = size[0] * SC, size[1] * SC
    S = set(map(tuple, cubes))
    zbuf = np.full((H, W), np.inf); fid = np.full((H, W), -1, int)
    ys, xs = np.mgrid[0:H, 0:W]; Xo = xs / SC; Yo = ys / SC
    faces = []
    for (x, y, z) in S:
        if (x, y, z - 1) not in S: faces.append(('F', x, y, z))
        if (x, y + 1, z) not in S: faces.append(('T', x, y, z))
        if (x + 1, y, z) not in S: faces.append(('R', x, y, z))
    for i, (t, x, y, z) in enumerate(faces):
        if t == 'F':
            a = (Xo - origin[0]) / U - K * z; b = (origin[1] - Yo) / U - K * z
            m = (a >= x) & (a <= x + 1) & (b >= y) & (b <= y + 1); d = np.full(a.shape, float(z))
        elif t == 'T':
            c = ((origin[1] - Yo) / U - (y + 1)) / K; a = (Xo - origin[0]) / U - K * c
            m = (a >= x) & (a <= x + 1) & (c >= z) & (c <= z + 1); d = c
        else:
            c = ((Xo - origin[0]) / U - (x + 1)) / K; b = (origin[1] - Yo) / U - K * c
            m = (b >= y) & (b <= y + 1) & (c >= z) & (c <= z + 1); d = c
        upd = m & (d < zbuf - 1e-9); zbuf[upd] = d[upd]; fid[upd] = i
    e = np.zeros((H, W), bool)
    e[:-1, :] |= fid[:-1, :] != fid[1:, :]; e[:, :-1] |= fid[:, :-1] != fid[:, 1:]
    return e


def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def extent(cs):
    xs = [(x + dx + K * (z + dz)) * U for (x, y, z) in cs for dx in (0, 1) for dz in (0, 1)]
    ys = [-(y + dy + K * (z + dz)) * U for (x, y, z) in cs for dy in (0, 1) for dz in (0, 1)]
    return min(xs), max(xs), min(ys), max(ys)


def load(box, m=2):
    x0, y0, x1, y1 = box
    im = Image.open(IMG).convert('L').crop((x0 - m, y0 - m, x1 + m + 1, y1 + m + 1))
    return np.array(im.resize((im.size[0] * SC, im.size[1] * SC), Image.NEAREST)) < 110


def score(cs, a, offsets=(0,)):
    H, W = a.shape; ys, xs = np.where(a)
    ex0, ex1, ey0, ey1 = extent(cs)
    best = None
    for dx in offsets:
        for dy in offsets:
            org = (xs.min() / SC + 0.7 - ex0 + dx, ys.min() / SC + 0.7 - ey0 + dy)
            e = render(cs, org, (W // SC, H // SC))
            s = (a & ~dilate(e, SC + 1)).sum() + (e & ~dilate(a, SC + 1)).sum()
            best = s if best is None else min(best, s)
    return best


def orientations():
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3), int)
            for i in range(3): M[i, perm[i]] = sg[i]
            yield M


def norm(cs):
    a = np.array(cs); a = a - a.min(0); return tuple(sorted(map(tuple, a)))


# 左图可见的10块（x向右、y向上、z向里；经重渲染与左图逐线吻合）
LEFT = [(0, 0, 0), (1, 0, 1), (2, 0, 1), (0, 2, 0), (0, 2, 1), (0, 1, 1), (2, 2, 0), (2, 2, 1), (3, 1, 1), (2, 1, 1)]
# 左图中完全被挡住、可能存在的位置（单独加入不改变左图画面）
HIDDEN = [(0, 0, 1), (0, 0, 2), (1, 0, 2), (1, 1, 2)]
OPTS = {'A': (160, 15, 253, 109), 'B': (279, 10, 362, 114), 'C': (382, 26, 486, 99), 'D': (494, 15, 578, 108)}

if __name__ == '__main__':
    print('左图自身重渲染误差：', score(LEFT, load((25, 21, 129, 104)), offsets=(-1, -0.5, 0, 0.5, 1)))
    shapes = {}
    for r in range(len(HIDDEN) + 1):
        for sub in itertools.combinations(HIDDEN, r):
            for M in orientations():
                key = norm([tuple(M @ np.array(c)) for c in LEFT + list(sub)])
                shapes.setdefault(key, (int(round(np.linalg.det(M))), sub))
    for k, box in OPTS.items():
        a = load(box); ys, xs = np.where(a)
        bw, bh = (xs.max() - xs.min()) / SC, (ys.max() - ys.min()) / SC
        cand = []
        for cs, (det, sub) in shapes.items():
            ex0, ex1, ey0, ey1 = extent(cs)
            if abs((ex1 - ex0) - bw) > 4 or abs((ey1 - ey0) - bh) > 4:
                continue
            cand.append((score(cs, a), det, sub, cs))
        cand.sort(key=lambda t: t[0])
        refined = sorted(((score(c[3], a, offsets=(-1, -0.5, 0, 0.5, 1)),) + c[1:3] for c in cand[:6]),
                         key=lambda t: t[0])
        if not refined:
            print(f'选项{k}: 没有任何旋转/镜像的外形尺寸与之相符')
            continue
        s, det, sub = refined[0]
        print(f'选项{k}: 最佳误差={s}  {"旋转(det=+1)" if det == 1 else "镜像(det=-1)"}  补入的隐藏块={sub}')
    # 选项A单独还原：可见9块（重渲染误差与其他吻合情形相当）
    A_VIS = [(0, 1, 0), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 2, 0), (1, 2, 2), (2, 0, 2), (2, 2, 0), (2, 2, 2)]
    A_HID = [(0, -1, 4), (0, 0, 2), (0, 0, 3), (0, 0, 4), (0, 1, 2), (1, 0, 2), (1, 1, 2)]  # A图中被挡住的位置
    print('A项还原（9块可见）重渲染误差：', score(A_VIS, load(OPTS['A']), offsets=(-1, -0.5, 0, 0.5, 1)))
    L11 = LEFT + [(0, 0, 1)]
    for rmL in L11:                       # 各去掉一块后能否重合（检验"挪动一块"）
        Lp = [c for c in L11 if c != rmL]
        for rmA in A_VIS:
            Ap = [c for c in A_VIS if c != rmA]
            for M in orientations():
                R = np.array([tuple(M @ np.array(c)) for c in Lp])
                for t in itertools.product(range(-5, 6), repeat=3):
                    S = set(map(tuple, R + np.array(t)))
                    if all(c in S for c in Ap) and all(c in Ap or c in A_HID for c in S):
                        print('  去掉原物体', rmL, '与A中', rmA, '后可重合，变换行列式=',
                              int(round(np.linalg.det(M))))
    print('结论：B、C、D 都与"左图10块+左下前方方块后面被挡住的1块(0,0,1)"共11块的物体经旋转后逐线吻合；'
          'A 与任何旋转都对不上（只能与镜像体再挪动一块对上），A 不是同一物体。')
