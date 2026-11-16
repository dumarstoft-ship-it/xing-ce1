# 第46题：测量每幅图中小三角（在六边形内）与小黑点（在菱形内）相对中心的方位角
# 方位角按数学方向：0°=右，90°=上，逆时针为正
import math
from collections import deque
import numpy as np
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p11_i00.png'
a = np.array(Image.open(IMG).convert('L'))
panels = {'图1': (9, 9, 105, 104), '图2': (111, 9, 205, 104), '图3': (209, 9, 305, 104),
          '图4': (309, 9, 403, 104), '图5': (408, 9, 500, 104),
          'A': (115, 136, 206, 231), 'B': (211, 136, 303, 231), 'C': (307, 136, 399, 231), 'D': (404, 136, 496, 231)}


def comps(bw):
    h, w = bw.shape
    lab = np.zeros((h, w), int); n = 0; out = []
    for y in range(h):
        for x in range(w):
            if bw[y, x] and not lab[y, x]:
                n += 1; q = deque([(y, x)]); lab[y, x] = n; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and bw[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n; q.append((ny, nx))
                ys, xs = zip(*pts)
                out.append(dict(area=len(pts), cx=np.mean(xs), cy=np.mean(ys),
                                w=max(xs) - min(xs) + 1, h=max(ys) - min(ys) + 1))
    return out


def ang(dx, dy):
    return round(math.degrees(math.atan2(-dy, dx)) % 360)


for name, (x0, y0, x1, y1) in panels.items():
    cs = comps(a[y0:y1, x0:x1] < 110)
    cs.sort(key=lambda c: -c['w'] * c['h'])
    hexa, dia = cs[0], cs[1]           # 外框六边形、内部菱形（线框，外接框最大）
    small = cs[2:]
    tri = max(small, key=lambda c: c['area'])   # 三角面积略大于圆点
    dot = min(small, key=lambda c: c['area'])
    hc = (hexa['cx'], hexa['cy']); dc = (dia['cx'], dia['cy'])
    print(f"{name}: 三角方位 {ang(tri['cx'] - hc[0], tri['cy'] - hc[1]):>3}°  "
          f"黑点方位 {ang(dot['cx'] - dc[0], dot['cy'] - dc[1]):>3}°")
print('规律：三角 90→0→270→180→90（每次顺时针90°），下一幅应为0°（右侧顶点处）；'
      '黑点 90→225→0→135→270（每次逆时针135°），下一幅应为45°（右上）。只有C同时满足。')
