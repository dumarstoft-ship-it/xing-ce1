"""第49题核验：把四个展开图折成正方体，比较是否为同一个正方体。

方法：在展开图上"滚动"正方体（正方体在纸面下方，图案朝外、朝向读者），
记录每个格子对应正方体的哪个面、格子的"右""上"方向落到该面的哪个方向；
再枚举正方体的24种旋转，比较两个展开图得到的正方体是否一致。

图案记法（屏幕坐标：x 向右，y 向上）：
  "3" 上下对称，只记"凸出方向" bump：正常3凸向右(1,0)，ω凸向下(0,-1)，ε凸向左(-1,0)，m凸向上(0,1)。
  "7" 没有对称性，记它自身的"上"方向 up 和"右"方向 right：
      正7 up=(0,1) right=(1,0)；顺时针90° up=(1,0) right=(0,-1)；
      逆时针90° up=(-1,0) right=(0,1)；镜像(上下翻) up=(0,-1) right=(1,0)。
各格图案由题图放大后逐格辨认（见解析）。
"""
import itertools
import numpy as np

NETS = {
    "A": {(0, 0): ("3", (0, -1)), (0, 1): ("7", (0, 1), (1, 0)), (1, 1): ("3", (0, -1)),
          (1, 2): ("7", (-1, 0), (0, 1)), (1, 3): ("blank",), (2, 2): ("blank",)},
    "B": {(0, 3): ("3", (-1, 0)), (1, 0): ("blank",), (1, 1): ("blank",), (1, 2): ("3", (-1, 0)),
          (1, 3): ("7", (1, 0), (0, -1)), (2, 1): ("7", (1, 0), (0, -1))},
    "C": {(0, 2): ("3", (-1, 0)), (0, 3): ("blank",), (1, 0): ("blank",), (1, 1): ("3", (-1, 0)),
          (1, 2): ("7", (1, 0), (0, -1)), (2, 1): ("7", (0, -1), (1, 0))},   # (2,1) 为上下翻转的"7"
    "D": {(0, 2): ("7", (1, 0), (0, -1)), (0, 3): ("3", (0, 1)), (1, 1): ("blank",),
          (1, 2): ("7", (-1, 0), (0, 1)), (2, 0): ("blank",), (2, 1): ("3", (0, -1))},
}


def rot(axis, deg):
    c, s = round(np.cos(np.radians(deg))), round(np.sin(np.radians(deg)))
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


# 正方体挂在纸面下方，贴着格子的是正方体的"顶面"(世界法向 +z)。
# 向右滚(列+1)：原来法向+x的面转到+z → 绕y轴 -90°
# 向左滚：-x → +z → 绕y轴 +90°
# 向上滚(行-1，世界+y)：+y → +z → 绕x轴 +90°
# 向下滚(行+1)：-y → +z → 绕x轴 -90°
MOVES = {(0, 1): rot("y", -90), (0, -1): rot("y", 90), (-1, 0): rot("x", 90), (1, 0): rot("x", -90)}


def fold(net):
    start = next(iter(net))
    R = {start: np.eye(3, dtype=int)}
    stack = [start]
    while stack:
        cell = stack.pop()
        for d, M in MOVES.items():
            nb = (cell[0] + d[0], cell[1] + d[1])
            if nb in net and nb not in R:
                R[nb] = M @ R[cell]
                stack.append(nb)
    faces = {}
    for cell, Rc in R.items():
        RT = Rc.T
        normal = tuple(RT @ np.array([0, 0, 1]))
        ex, ey = RT @ np.array([1, 0, 0]), RT @ np.array([0, 1, 0])
        to3 = lambda v: tuple(int(x) for x in v[0] * ex + v[1] * ey)
        g = net[cell]
        if g[0] == "blank":
            faces[normal] = ("blank",)
        elif g[0] == "3":
            faces[normal] = ("3", to3(g[1]))
        else:
            faces[normal] = ("7", to3(g[1]), to3(g[2]))
    assert len(faces) == 6, "不是合法展开图"
    return faces


def all_rotations():
    mats = set()
    gens = [rot("x", 90), rot("y", 90), rot("z", 90)]
    frontier = [np.eye(3, dtype=int)]
    seen = {np.eye(3, dtype=int).tobytes(): np.eye(3, dtype=int)}
    while frontier:
        m = frontier.pop()
        for g in gens:
            n = g @ m
            k = n.tobytes()
            if k not in seen:
                seen[k] = n
                frontier.append(n)
    return list(seen.values())


ROTS = all_rotations()
assert len(ROTS) == 24


def apply(Q, faces):
    out = {}
    for n, g in faces.items():
        n2 = tuple(int(x) for x in Q @ np.array(n))
        if g[0] == "blank":
            out[n2] = g
        else:
            out[n2] = (g[0],) + tuple(tuple(int(x) for x in Q @ np.array(v)) for v in g[1:])
    return out


def same_cube(f1, f2):
    return any(apply(Q, f1) == f2 for Q in ROTS)


if __name__ == "__main__":
    F = {k: fold(v) for k, v in NETS.items()}
    for k, f in F.items():
        print(k, f)
    print()
    for a, b in itertools.combinations("ABCD", 2):
        print(f"{a} 与 {b} 是同一正方体：", same_cube(F[a], F[b]))
    # 对照：若把C中(2,1)的"7"当作正常方向的7（旋转180°）
    netC2 = dict(NETS["C"]); netC2[(2, 1)] = ("7", (0, -1), (-1, 0))
    FC2 = fold(netC2)
    print("\n对照：C的(2,1)若为正常7旋转180°：与A同一正方体？", same_cube(FC2, F["A"]))
    # 相对面检查：两个"7"、两个"3"、两个空白各自的位置关系
    for k, f in F.items():
        kinds = {}
        for n, g in f.items():
            kinds.setdefault(g[0], []).append(n)
        rel = {t: ("相对" if tuple(-x for x in v[0]) == v[1] else "相邻") for t, v in kinds.items()}
        print(k, "同类面位置关系：", rel)
