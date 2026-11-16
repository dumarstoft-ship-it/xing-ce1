# 第50题：把展开图折成立方体，记下每个面上的图案（用三维坐标表示），
# 再对24种旋转逐一检验能否得到各选项中看得见的三个面（前、上、右）。
# 坐标：立方体[0,1]^3，x向右、y向上、z向里；画法中可见面为 前(z=0)、上(y=1)、右(x=1)。
import itertools
import numpy as np

C0 = np.array([0.5, 0.5, 0.5])

# 展开图折叠结果（S2为前面，S1左、S3右、S4上、S5下，四个三角形拼成后面）
CUBE = {
    'back_quarters': {'黑': (0.5, 0.85, 1), '白': (0.5, 0.15, 1), '点': (0.15, 0.5, 1), '横线': (0.85, 0.5, 1)},
    'segments': [((0, 1, 0), (1, 1, 1)),            # 上面S4：前左角-后右角对角线
                 ((0, 0, 0), (1, 0, 1)),            # 下面S5：前左角-后右角对角线
                 ((0, 1, 0.325), (0, 0, 0.625)),    # 左面S1：上棱靠前1/3处 - 下棱靠后处
                 ((1, 1, 0.36), (1, 0, 0.67))],     # 右面S3：同上
}

# 各选项可见三个面上的图案（按图量取，斜线端点为近似值）
OPTS = {
    'A': {'tri_face': 'top', 'quarters': {'黑': (0.5, 1, 0.85), '白': (0.5, 1, 0.15), '点': (0.85, 1, 0.5), '横线': (0.15, 1, 0.5)},
          'segments': [((0, 1, 0), (1, 0, 0)), ((1, 0.82, 0), (1, 0.22, 1))]},
    'B': {'tri_face': 'front', 'quarters': {'黑': (0.15, 0.5, 0), '点': (0.5, 0.85, 0), '白': (0.85, 0.5, 0), '横线': (0.5, 0.15, 0)},
          'segments': [((0, 1, 0.70), (1, 1, 0.24)), ((1, 1, 1), (1, 0, 0))]},
    'C': {'tri_face': 'front', 'quarters': {'黑': (0.15, 0.5, 0), '横线': (0.5, 0.85, 0), '白': (0.85, 0.5, 0), '点': (0.5, 0.15, 0)},
          'segments': [((0, 1, 0.32), (1, 1, 0.86)), ((1, 1, 1), (1, 0, 0))]},
    'D': {'tri_face': 'right', 'quarters': {'黑': (1, 0.85, 0.5), '点': (1, 0.5, 0.85), '白': (1, 0.15, 0.5), '横线': (1, 0.5, 0.15)},
          'segments': [((0, 1, 1), (1, 1, 0)), ((0.30, 1, 0), (0.77, 0, 0))]},
}


def visible(p):
    p = np.asarray(p)
    return abs(p[2]) < 1e-6 or abs(p[1] - 1) < 1e-6 or abs(p[0] - 1) < 1e-6


def on_visible_face(seg):
    a, b = np.asarray(seg[0]), np.asarray(seg[1])
    for axis, val in ((2, 0), (1, 1), (0, 1)):
        if abs(a[axis] - val) < 1e-6 and abs(b[axis] - val) < 1e-6:
            return True
    return False


def seg_match(s, t, tol=0.25):
    a, b = np.asarray(s[0]), np.asarray(s[1]); c, d = np.asarray(t[0]), np.asarray(t[1])
    return (np.abs(a - c).max() < tol and np.abs(b - d).max() < tol) or \
           (np.abs(a - d).max() < tol and np.abs(b - c).max() < tol)


def rotations(proper=True):
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3))
            for i in range(3): M[i, perm[i]] = sg[i]
            if (round(np.linalg.det(M)) == 1) == proper:
                yield M


def check(opt, M):
    f = lambda p: M @ (np.asarray(p, float) - C0) + C0
    quarters = {k: f(v) for k, v in CUBE['back_quarters'].items()}
    if not all(np.abs(quarters[k] - np.asarray(v)).max() < 1e-6 for k, v in opt['quarters'].items()):
        return False
    segs = [(f(a), f(b)) for a, b in CUBE['segments']]
    vis = [s for s in segs if on_visible_face(s)]
    if len(vis) != len(opt['segments']):
        return False
    return all(any(seg_match(s, t) for s in vis) for t in opt['segments'])


for k, opt in OPTS.items():
    good = [M for M in rotations(True) if check(opt, M)]
    mirror = [M for M in rotations(False) if check(opt, M)]
    print(f'选项{k}: 可由旋转得到的方式 {len(good)} 种；仅镜像才能得到 {len(mirror)} 种',
          '-> 能折成' if good else '-> 不能折成')
