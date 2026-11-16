# 第70题：读极地投影经纬网图，求A、B、C、D的经纬度并逐项判断。
# 图中：纬线圈由内到外标 70°、60°、50°；左侧 0°、右侧 180°；右下箭头沿圆周顺时针（箭头在下端）。
# 顺时针自转 => 俯视南极 => 南半球；自 0° 顺时针方向为东经。
from PIL import Image
import numpy as np
import math

IMG = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p18_i12.png"
im = np.array(Image.open(IMG).convert("L"))
dark = im < 100
H, W = im.shape

def box_count(mask, k):
    p = np.pad(mask.astype(int), ((k, k), (k, k)))
    c = p.cumsum(0).cumsum(1)
    h, w = mask.shape
    r = k // 2
    y0, x0 = np.arange(h) + k - r - 1, np.arange(w) + k - r - 1
    y1, x1 = y0 + k, x0 + k
    return c[np.ix_(y1, x1)] - c[np.ix_(y0, x1)] - c[np.ix_(y1, x0)] + c[np.ix_(y0, x0)]

# 圆心：竖直、水平虚线所在的列和行（中部区域黑点最多的行/列）
cx = int(np.argmax(dark[40:180, 60:200].sum(axis=0))) + 60
cy = int(np.argmax(dark[30:170, 40:220].sum(axis=1))) + 30
# 纬线圈半径：黑像素到圆心距离的直方图峰值（实线圆周）
ys, xs = np.nonzero(dark[:, 20:250]); xs = xs + 20
d = np.hypot(xs - cx, ys - cy)
hist = np.bincount(d.astype(int))
peaks = sorted(int(i) for i in np.argsort(hist)[::-1][:12] if i > 20)
radii = []
for p in peaks:
    if not radii or p - radii[-1] > 5:
        radii.append(p)
radii = radii[:3]
print("圆心", (cx, cy), "纬线圈半径(内→外)", radii)
lat_of = dict(zip(radii, [70, 60, 50]))

# 实心圆点：5×5 邻域几乎全黑且离圆心较远（排除文字、箭头：只在三个圆周上找）
cnt = box_count(dark, 5)
cand = np.argwhere(cnt >= 22)
blobs = []
for y, x in cand:
    r = math.hypot(x - cx, y - cy)
    if min(abs(r - R) for R in radii) > 4:
        continue
    for b in blobs:
        if abs(b[0] - x) < 6 and abs(b[1] - y) < 6:
            b[2].append((x, y)); break
    else:
        blobs.append([x, y, [(x, y)]])
points = []
for b in blobs:
    x = np.mean([p[0] for p in b[2]]); y = np.mean([p[1] for p in b[2]])
    r = math.hypot(x - cx, y - cy)
    R = min(radii, key=lambda R: abs(R - r))
    theta = math.degrees(math.atan2(-(y - cy), x - cx)) % 360   # 数学角，逆时针，y向上
    lon_e = (180 - theta + 180) % 360 - 180                   # 自左侧0°顺时针为东经
    lon_e = round(lon_e / 45) * 45
    points.append((round(x), round(y), lat_of[R], lon_e))
# 按位置贴标签：图中 A 在正下方、B 在左下、C 在左上、D 在右上
def label(p):
    x, y = p[0] - cx, p[1] - cy
    if abs(x) < 6 and y > 0: return "A"
    if x < 0 and y > 0: return "B"
    if x < 0 and y < 0: return "C"
    return "D"
coords = {}
for p in points:
    L = label(p)
    lon = "%d°%s" % (abs(p[3]), "E" if p[3] > 0 else "W") if p[3] not in (0, 180, -180) else "%d°" % abs(p[3])
    coords[L] = (p[2], p[3])
    print(L, "像素", (p[0], p[1]), "=> %d°S, %s" % (p[2], lon))
assert set(coords) == set("ABCD")
assert coords == {"A": (50, -90), "B": (60, -45), "C": (70, 45), "D": (70, 135)}, coords

def in_west_hemisphere(lon):  # 20°W 以西到 160°E
    return lon <= -20 or lon >= 160
judg = {
    "①全在南半球": True,
    "②全在中纬度(30°-60°)": all(30 <= v[0] <= 60 for v in coords.values()),
    "③全在温带(23.5°-66.5°)": all(23.5 <= v[0] <= 66.5 for v in coords.values()),
    "④A(50°S,90°W) D(70°S,135°E)": coords["A"] == (50, -90) and coords["D"] == (70, 135),
    "⑤B(60°S,45°E) C(70°S,45°W)": coords["B"] == (60, 45) and coords["C"] == (70, -45),
    "⑥A、B西半球，C、D东半球": in_west_hemisphere(coords["A"][1]) and in_west_hemisphere(coords["B"][1])
                              and not in_west_hemisphere(coords["C"][1]) and not in_west_hemisphere(coords["D"][1]),
}
for k, v in judg.items():
    print(k, "正确" if v else "错误")
correct = {k[0] for k, v in judg.items() if v}
options = {"A": "①③⑤", "B": "①⑤⑥", "C": "②④⑥", "D": "①④⑥"}
ans = [o for o, s in options.items() if set(s) == correct]
print("正确说法", "".join(sorted(correct)), "=> 选项", ans)
assert ans == ["D"]
