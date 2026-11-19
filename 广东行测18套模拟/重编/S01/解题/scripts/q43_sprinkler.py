"""S01 第43题：直角三角形AOB，OA=6、OB=8，C为AB中点，洒水区域是以OC为直径的圆，π取3.14，求面积。
选项 A7.85 B15.72 C19.63 D21.51"""
from math import hypot, isclose
A, O, B = (0, 6), (0, 0), (8, 0)
C = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
OC = hypot(*C)
area = 3.14 * (OC / 2) ** 2
print('AB=%.1f OC=%.1f 半径%.2f 面积%.4f' % (hypot(8, 6), OC, OC / 2, area))
assert isclose(OC, 5) and isclose(area, 19.625)
opts = {'A': 7.85, 'B': 15.72, 'C': 19.63, 'D': 21.51}
print('最接近：', min(opts, key=lambda k: abs(opts[k] - area)))
print('若把OC当半径：', 3.14 * OC ** 2, '；若算成π×r（未平方）：', 3.14 * OC / 2)
