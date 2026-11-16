"""第49题：按直观图（斜二测，纵深缩半）读出的多面体（单位=小正方体棱长，x向右、y向后、z向上）：
  前矮块 x0-3,y0-1,z0-1；x2-3,y1-2,z0-1 也实（顶面z=1）；
  x0-2,y0-2 区域顶面是斜坡 z=1+y/2（前沿y=0,z=1 → 后沿y=2,z=2）；
  后平台 x0-3,y2-3,z0-2；平台左上小正方体 x0-1,y2-3,z2-3；右侧高块 x3-4,y1-3,z0-2。
Q=(0,0,0)，R=(3,0,0)，P=(1,3,3)（小正方体后右上顶点）→ 截面 z=y。
在截面上取参数 (x,t)，点(x,t,t)，逐列求属于实体的 t 区间。"""
import numpy as np

def inside(x, y, z):
    if z < 0: return False
    if 0 <= x <= 3 and 0 <= y <= 1 and z <= 1: return True
    if 2 <= x <= 3 and 1 <= y <= 2 and z <= 1: return True
    if 0 <= x <= 2 and 0 <= y <= 2 and z <= 1 + y / 2: return True
    if 0 <= x <= 3 and 2 <= y <= 3 and z <= 2: return True
    if 0 <= x <= 1 and 2 <= y <= 3 and 2 <= z <= 3: return True
    if 3 <= x <= 4 and 1 <= y <= 3 and z <= 2: return True
    return False

# check plane through Q,R,P
Q, R, P = np.array([0, 0, 0]), np.array([3, 0, 0]), np.array([1, 3, 3])
n = np.cross(R - Q, P - Q)
print('平面法向量', n, '→ 平面方程', f'{n[1]}*y + {n[2]}*z = 0', '即 z = y')
for x0 in [0.5, 1.5, 2.5, 3.5]:
    ts = [t for t in np.linspace(0, 3, 301) if inside(x0, t, t)]
    # compress into intervals
    iv = []
    for t in ts:
        if iv and abs(t - iv[-1][1] - 0.01) < 1e-6:
            iv[-1][1] = t
        else:
            iv.append([t, t])
    print(f'x≈{x0}: 截面在 t∈', [(round(a, 2), round(b, 2)) for a, b in iv])
