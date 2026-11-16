"""第37题：正方形ABCD面积10，△ACE为等边三角形，求四边形ADCE（凹四边形）面积。
建立坐标：D(0,0)，C(s,0)，A(0,s)，B(s,s)，s=√10。E在AC的垂直平分线（即直线BD）上，位于D一侧。
用鞋带公式直接算多边形A→D→C→E的面积，并与 5√3−5 比较。
"""
import math

s = math.sqrt(10)
A, B, C, D = (0.0, s), (s, s), (s, 0.0), (0.0, 0.0)
mx, my = s / 2, s / 2  # AC 中点
ac = math.dist(A, C)
h = math.sqrt(3) / 2 * ac
# BD 方向（从中点指向D）单位向量
ux, uy = (D[0] - mx), (D[1] - my)
n = math.hypot(ux, uy)
ux, uy = ux / n, uy / n
E = (mx + h * ux, my + h * uy)
print("AC =", ac, "AE =", math.dist(A, E), "CE =", math.dist(C, E))

def shoelace(pts):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2

def inside(p, tri):
    (x1, y1), (x2, y2), (x3, y3) = tri
    def sgn(a, b, c):
        return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])
    d1, d2, d3 = sgn(p, tri[0], tri[1]), sgn(p, tri[1], tri[2]), sgn(p, tri[2], tri[0])
    return (d1 < 0) == (d2 < 0) == (d3 < 0)

print("D 在 △ACE 内部:", inside(D, [A, C, E]))
area_ADCE = shoelace([A, D, C, E])
area_ACE = shoelace([A, C, E])
print("S△ACE =", area_ACE, "(=5√3 =", 5 * math.sqrt(3), ")")
print("S四边形ADCE =", area_ADCE, "(=5√3−5 =", 5 * math.sqrt(3) - 5, ")")
options = {"A": 3.66, "B": 4.25, "C": 5.32, "D": 8.66}
best = min(options, key=lambda k: abs(options[k] - area_ADCE))
print("最接近选项:", best)
assert best == "A" and abs(area_ADCE - 3.66) < 0.01
