# 第50题：检查每个选项识别出的(前,上,右)三面组合能否由展开图折出；若能，给出每面应有的旋转角
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from q50_fold import ROTS, SEGS, NORMALS, MAPS, FACES, face_in_view

def face_frame_in_view(R, f, view):
    """返回面 f 在该视图中(从外面看、拉正成正方形)的旋转角：展开图中该面的 u 轴方向变成了视图中的哪个方向"""
    O, ex, ey, n = MAPS[f]
    e_u = R @ ex   # 展开图中向右的方向
    e_v = R @ ey   # 展开图中向下的方向
    # 各视图面内的“右”“下”方向（3D）
    frames = {'前': (np.array([1, 0, 0]), np.array([0, -1, 0])),
              '上': (np.array([1, 0, 0]), np.array([0, 0, 1])),     # 从上往下看，后边在上、前边在下
              '右': (np.array([0, 0, -1]), np.array([0, -1, 0]))}   # 从右往左看，前边在左、后边在右
    right, down = frames[view]
    # 展开图的(右,下)转到视图的(右,下)需要顺时针旋转几个90°
    for r in range(4):
        # 顺时针转r次后，原“右”方向变为：0:右 1:下 2:左 3:上
        target = [right, down, -right, -down][r]
        if np.allclose(e_u, target):
            # 检查不是镜像
            target_v = [down, -right, -down, right][r]
            return r * 90 if np.allclose(e_v, target_v) else None
    return None

table = {}
for R in ROTS:
    tri = face_in_view(R)
    table[tri] = R

identified = {  # 由逐面识别得到（旋转为顺时针角度）
    'A': {'前': ('F1', 270), '上': ('F6', 90), '右': ('F3', 180)},
    'B': {'前': ('F5', 90), '上': ('F2', 0), '右': ('F4', 270)},
    'C': {'前': ('F6', 90), '上': ('F5', 180), '右': ('F4', 270)},
    'D': {'前': ('F6', 0), '上': ('F4', 0), '右': ('F5', 90)},
}
for k, idf in identified.items():
    tri = (idf['前'][0], idf['上'][0], idf['右'][0])
    if tri not in table:
        print(f'选项{k}: 前/上/右 = {tri} —— 展开图折不出这种排列（三面绕公共顶点的顺序相反）')
        continue
    R = table[tri]
    exp = {v: face_frame_in_view(R, idf[v][0], v) for v in ('前', '上', '右')}
    print(f'选项{k}: 前/上/右 = {tri} 可以出现；按展开图应有的旋转: ' +
          ', '.join(f'{v}{idf[v][0]}={exp[v]}°(图中识别为{idf[v][1]}°)' for v in ('前', '上', '右')))

print()
print('全部可出现的(前,上,右)组合及各面旋转：')
for tri, R in sorted(table.items()):
    print('   ', tri, [face_frame_in_view(R, f, v) for f, v in zip(tri, ('前', '上', '右'))])
