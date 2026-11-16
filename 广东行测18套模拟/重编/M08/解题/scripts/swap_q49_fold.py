"""M08第49题（借第24季第48题，折纸剪纸）：由题图量出的剪切线还原展开后的卡片。

圆形卡片沿两条互相垂直的直径各折一次，得到四层叠合的四分之一圆（直角顶点O＝圆心，
两条直边是两条折痕）。题图里虚线从左直边上的P点剪到圆弧上的Q点，再剪到内部的M点，
最后剪到圆弧与下直边的交点S；剪下的卡片是含圆心O的那一块（O→P→Q→M→S→O）。
坐标以O为原点、半径为1，按题图像素量取（左直边x＝223，下直边y＝56，半径约53像素）。
展开＝把这块关于两条折痕（x轴、y轴）各作对称，得到整张卡片的外轮廓。
"""
import math
from pathlib import Path

R = 53.0
O = (223, 56)
def pt(x_px, y_px):
    return ((x_px - O[0]) / R, (O[1] - y_px) / R)

P = pt(223, 32)      # 左直边上
Q = pt(249, 12)      # 圆弧上
M = pt(255, 42)      # 内部
S = (1.0, 0.0)       # 圆弧与下直边的交点
print("P,Q,M,S =", [tuple(round(v, 2) for v in p) for p in (P, Q, M, S)], "；|OQ|≈", round(math.hypot(*Q), 2))

# 第一象限的轮廓 S→M→Q→P，依次关于y轴、x轴对称拼成整圈
q1 = [S, M, Q, P]
q2 = [(-x, y) for x, y in reversed(q1)][1:]           # P→Q'→M'→S'
q3 = [(x, -y) for x, y in reversed(q1 + q2)][1:]      # 下半圈
poly = (q1 + q2 + q3)[:-1]
print("展开后轮廓顶点数：", len(poly))

def turn(a, b, c):
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])

tips, notches = [], []
for i, b in enumerate(poly):
    a, c = poly[i - 1], poly[(i + 1) % len(poly)]
    (tips if turn(a, b, c) > 0 else notches).append(b)      # 逆时针走向：左转为凸顶点（尖角）
ang = lambda p: round(math.degrees(math.atan2(p[1], p[0])) % 360)
print("尖角", len(tips), "个，方向（度）：", sorted(ang(p) for p in tips))
print("凹角", len(notches), "个，方向（度）：", sorted(ang(p) for p in notches))

on_x = [p for p in poly if abs(p[1]) < 1e-9]
on_y = [p for p in poly if abs(p[0]) < 1e-9]
print("水平折痕上的顶点：", ["尖角" if p in tips else "凹角" for p in on_x])
print("竖直折痕上的顶点：", ["尖角" if p in tips else "凹角" for p in on_y])
assert len(tips) == 6 and len(notches) == 6
assert all(p in tips for p in on_x) and all(p in notches for p in on_y)
print("结论：六角星，左右两端是尖角，正上、正下是凹口 → 对应C项（A、D正上方是尖角，B不对称）")

# 画出展开图，供与选项对照
try:
    from PIL import Image, ImageDraw
    out = Path(__file__).with_name("swap_q49_unfold.png")
    im = Image.new("L", (220, 220), 255)
    d = ImageDraw.Draw(im)
    d.polygon([(110 + 90 * x, 110 - 90 * y) for x, y in poly], outline=0)
    im.save(out)
    print("展开图：", out.name)
except ImportError:
    pass
