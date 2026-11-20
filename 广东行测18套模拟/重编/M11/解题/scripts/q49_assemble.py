"""M11 第49题（GDXD2019-SW-Q071）：三块图形拼成什么。

顶点坐标读自三块各自的3倍放大图（各自坐标系）。拼法：
图3的上顶点嵌进图2下方的凹口（两条边重合），图1顺时针转90°后，凹口卡住图3左侧的尖角，
图1原来的上边贴图2的竖边。检验：对应顶点重合、外轮廓为直角等腰三角形、面积相等。
"""
import numpy as np

P1 = np.array([(245, 285), (555, 290), (622, 355), (718, 245), (712, 742)], float)   # A1..E1
P2 = np.array([(150, 312), (293, 160), (905, 775), (390, 505), (148, 632)], float)   # A2..E2
P3 = np.array([(115, 625), (185, 550), (425, 440), (940, 712), (215, 718)], float)   # A3..E3

def area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

# 图3平移：C3→D2、D3→C2（两条长边重合）
t3 = ((P2[3] - P3[2]) + (P2[2] - P3[3])) / 2
Q3 = P3 + t3
# 图1：图像坐标里 (x,y)→(-y,x) 即顺时针转90°，再平移使 C1→Q3的A3（凹口卡住尖角）
R = np.array([[0, -1], [1, 0]], float)
Q1 = P1 @ R.T
Q1 = Q1 + (Q3[0] - Q1[2])
pairs = {
 '图3的C3—图2的D2': (Q3[2], P2[3]), '图3的D3—图2的C2': (Q3[3], P2[2]), '图3的B3—图2的E2': (Q3[1], P2[4]),
 '图1的A1—图2的A2': (Q1[0], P2[0]), '图1的B1—图2的E2': (Q1[1], P2[4]), '图1的D1—图3的E3': (Q1[3], Q3[4]),
}
for k, (a, b) in pairs.items():
    print(f'{k} 相差 {np.linalg.norm(a - b):.0f} 像素')
outer = np.array([Q1[4], P2[1], P2[2]])   # 图1的E1、图2的B2、图2的C2
v1, v2 = outer[0] - outer[1], outer[2] - outer[1]
ang = np.degrees(np.arccos(np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)))
print('外轮廓三顶点', outer.round().tolist(), f'顶角 {ang:.1f}°，两腰 {np.linalg.norm(v1):.0f} 与 {np.linalg.norm(v2):.0f}')
# 图1的E1A1边与图2的A2B2边是否在同一直线上
d = outer[1] - outer[0]; n = np.array([-d[1], d[0]]) / np.linalg.norm(d)
print('图1的A1、图2的A2到左腰的距离', abs(np.dot(Q1[0] - outer[0], n)).round(1), abs(np.dot(P2[0] - outer[0], n)).round(1))
s = area(P1) + area(P2) + area(P3)
print(f'三块面积和 {s:.0f}，外轮廓三角形面积 {area(outer):.0f}，相差 {abs(s - area(outer)) / area(outer):.1%}')
