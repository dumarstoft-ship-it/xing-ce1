# 第49题：按读出的虚线端点（极坐标）把含圆心的那块沿两条折痕镜像展开，画出预测图形
import math
from PIL import Image, ImageDraw
# 原图像素：圆心(223.5,56.5)，半径约53
C = (223.5, 56.5); R = 53.0
pts = {'P1(左边上)': (223.5, 32.0), 'P2(弧上)': (246.0, 11.0), 'P3(内部拐点)': (252.5, 40.0), 'P4(底边上)': (273.0, 56.5)}
polar = []
for k, (x, y) in pts.items():
    dx, dy = x - C[0], C[1] - y
    r = math.hypot(dx, dy) / R; a = math.degrees(math.atan2(dy, dx))
    polar.append((r, a)); print(f'{k}: r={r:.2f}R, 角度={a:.1f}°')
# 第一象限路径 P4->P3->P2->P1，再关于 y 轴、x 轴镜像
q1 = list(reversed(polar))          # 从 x 轴到 y 轴
q2 = [(r, 180 - a) for r, a in reversed(q1)]
q3 = [(r, 180 + a) for r, a in q1]
q4 = [(r, 360 - a) for r, a in reversed(q1)]
outline = q1 + q2[1:] + q3[1:] + q4[1:-1]
print('展开后顶点（r, 角度）：')
for r, a in outline:
    print(f'  {r:.2f}R  {a % 360:6.1f}°  {"外凸尖角" if r > 0.85 else "内凹点"}')
S = 300; im = Image.new('RGB', (S, S), 'white'); d = ImageDraw.Draw(im)
xy = [(S / 2 + 130 * r * math.cos(math.radians(a)), S / 2 - 130 * r * math.sin(math.radians(a))) for r, a in outline]
d.polygon(xy, outline='black', width=3)
im.save('/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m08x/x49_pred.png')
