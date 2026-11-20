"""M11 第70题：加酶洗衣粉（曲线A）与普通洗衣粉（曲线B）去污力随温度的变化。读题图像素，检验四个选项。
标定：纵轴0在x轴（y≈505像素）、80在y≈87像素；横轴10℃在x≈88、80℃在x≈660像素（按刻度标签位置）。"""
from PIL import Image
import numpy as np
im = Image.open('/home/user/xing-ce1/广东/行测/2013-2021/assets/GD2016-XZ/GD2016-XZ-p09-i01.png').convert('L')
a = np.array(im)
y0, y80 = 505, 87
x10, x80 = 88, 660
val = lambda y: (y0 - y) * 80 / (y0 - y80)
temp = lambda x: 10 + (x - x10) * 70 / (x80 - x10)
pts = []
for x in range(80, 705, 4):
    col = a[95:500, x] < 110                 # 跳过顶部“80”刻度线与字母A所在高度以上的部分
    ys = np.where(col)[0] + 95
    if 380 <= x <= 440:                      # 字母B（约y 295—315）附近剔除
        ys = ys[(ys < 290) | (ys > 320)]
    runs, cur = [], []
    for y in ys:
        if cur and y - cur[-1] > 2:
            runs.append(cur); cur = []
        cur.append(y)
    if cur:
        runs.append(cur)
    cs = [sum(r) / len(r) for r in runs]
    if len(cs) >= 2:
        pts.append((temp(x), val(min(cs)), val(max(cs))))
for t, A, B in pts[::10]:
    print('%5.1f℃  A=%5.1f  B=%5.1f' % (t, A, B))
assert all(A > B for t, A, B in pts), '曲线A应始终在B之上'
tA = max(pts, key=lambda p: p[1]); tB = max(pts, key=lambda p: p[2])
print('A峰值约%.0f（%.0f℃），B峰值约%.0f（%.0f℃）' % (tA[1], tA[0], tB[2], tB[0]))
rngA = max(p[1] for p in pts) - min(p[1] for p in pts); rngB = max(p[2] for p in pts) - min(p[2] for p in pts)
print('去污力变化幅度：A约%.0f，B约%.0f' % (rngA, rngB))
# A项：先升后降，不成正比；B项：A随温度变化幅度更大，敏感性更大；C项：高温段A仍高于B；
# D项：低温时A的去污力与B接近、远低于峰值——低温抑制酶的活性（不失活），正确
assert rngA > rngB
print('A、B、C与图不符，D符合酶的特性。')
