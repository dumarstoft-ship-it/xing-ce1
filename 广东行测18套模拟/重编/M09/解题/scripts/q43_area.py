"""M09 第43题：周长24米的平行四边形，a（上底，即平行四边形的边）∶b（斜边）∶c（高）=4∶2∶√3，
中间矩形草地的面积？ 选项 A6 B6√3 C12 D12√3
题图读法：a 标在上边，从左上顶点到右上顶点，是平行四边形的一条边；b 是左侧斜边；c 是两条平行边间的高。
矩形左边是过左上顶点的竖线，右边是过右下顶点的竖线，故矩形宽 = a − 斜边的水平投影。
核验：坐标法，鞋带公式算矩形面积，并与选项比较。"""
from math import sqrt, isclose
k = 24 / (2 * (4 + 2))          # 周长 = 2(a+b)
a, b, c = 4 * k, 2 * k, sqrt(3) * k
p = sqrt(b * b - c * c)          # 斜边水平投影
print(f'k={k}, a={a}, b={b}, c={c:.4f}(=2√3), 水平投影={p:.4f}')
# 坐标：左下(0,0)，左上(p,c)，右上(p+a,c)，右下(a,0)
BL, TL, TR, BR = (0, 0), (p, c), (p + a, c), (a, 0)
rect = [(p, 0), (a, 0), (a, c), (p, c)]
def shoelace(pts):
    s = 0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        s += x1 * y2 - x2 * y1
    return abs(s) / 2
S_par = shoelace([BL, BR, TR, TL])
S_rect = shoelace(rect)
print(f'平行四边形面积={S_par:.4f}(=16√3={16*sqrt(3):.4f})，矩形面积={S_rect:.4f}(=12√3={12*sqrt(3):.4f})')
assert isclose(2 * (a + b), 24) and isclose(S_rect, 12 * sqrt(3))
opts = {'A': 6, 'B': 6 * sqrt(3), 'C': 12, 'D': 12 * sqrt(3)}
print('答案：', [kk for kk, v in opts.items() if isclose(v, S_rect)])
# 斜边与高之比 2∶√3 → 斜边与底边夹角60°，水平投影=斜边的一半
assert isclose(p, b / 2)
# 常见误读：把a当成矩形的宽 → 16√3；宽减两个投影 → 8√3（都不在选项中）
print('a×c =', a * c / sqrt(3), '√3；(a−2p)×c =', (a - 2 * p) * c / sqrt(3), '√3')
