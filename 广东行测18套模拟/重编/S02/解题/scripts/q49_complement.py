"""S02 第49题（SYDW2023-Q073）：十字形5块 + 选项 拼成长方体。

题干：中间一块（被挡住），向左、右、上、前各伸出一块，共5块，外形3×2×2。
把十字形竖起来放进 2×2×3 的长方体：竖柱占左前一列(0,0,z)，中层向右、向后各伸一块。
余下7块即应补的形状；C项按题图读出（x 向右，y 向里，z 向上）。
"""
import itertools
box = set(itertools.product(range(2), range(2), range(3)))
cross = {(0, 0, 0), (0, 0, 1), (0, 0, 2), (1, 0, 1), (0, 1, 1)}
rest = box - cross
C = {(1, 0, 2), (0, 1, 2), (1, 1, 2),      # 上层：前右、后左、后右（L形，拐角在后右竖柱）
     (1, 1, 1),                            # 中层：只有后右一块（缩在后面）
     (1, 0, 0), (0, 1, 0), (1, 1, 0)}      # 下层：同上层
print('十字形', len(cross), '块，余下', len(rest), '块')
for z in (2, 1, 0):
    layer = lambda S: ''.join('■' if (x, y, z) in S else '□' for y in (1, 0) for x in (0, 1))
    print(f'第{z}层（后排左右、前排左右）：余下 {layer(rest)}  C项 {layer(C)}')
print('C 与余下部分完全相同：', C == rest, '；十字形+C 恰好填满：', (C | cross) == box and not (C & cross))

# B项按题图读出：竖柱在右后，上、下两层另有左前、左后两块（左前那块与竖柱只是斜对着）
B = {(1, 1, 0), (1, 1, 1), (1, 1, 2), (0, 0, 2), (0, 1, 2), (0, 0, 0), (0, 1, 0)}
gap = box - B
print('B 块数', len(B), '；B 空出的位置', sorted(gap))
def is_cross(cells):
    # 十字：3块一列，中间那块向两个互相垂直的方向各伸一块
    for col in itertools.product(range(2), range(2)):
        line = {(col[0], col[1], z) for z in range(3)}
        if line <= cells:
            arms = cells - line
            mid = (col[0], col[1], 1)
            if len(arms) == 2 and all(sum(abs(a - b) for a, b in zip(arm, mid)) == 1 for arm in arms):
                return True
    return False
print('B 空出的位置是不是十字：', is_cross(gap), '；余下部分（C）对应的空位是不是十字：', is_cross(box - C))
