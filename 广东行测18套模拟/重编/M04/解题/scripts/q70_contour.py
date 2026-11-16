"""第70题：滑雪场等高线图（assets/s19_p19_i00.png）判读。
做法：
1) 二值化，去掉图框、图例框和①②两个圈注，对黑色像素做8邻域连通分量标记；
   等高线是长分量，雪道虚线、文字是小分量。
2) 找出紧贴各高程注记（1200、1000、900、700、500、400）两端的等高线分量，确定每条线的高程，
   相邻两条线相差100米（1200与1000之间、700与500之间各夹一条线，验证等高距为100米）。
3) 甲点：黑点与最内层闭合线连成同一分量（点落在该线拐角上），该闭合线位于1200线之内，为1300米线。
4) 服务大厅：位于500米线低处一侧，与400米线（右缘伸入的窄舌形线）之间没有其他等高线，海拔400～500米。
5) 沿①、②雪道折线采样，统计穿越的等高线条数和平均间距（像素/100米）。
"""
import math
from collections import deque
import numpy as np
from PIL import Image

PATH = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p19_i00.png"
a = np.array(Image.open(PATH).convert("L"))
H, W = a.shape
dark = a < 140
dark[:, 0:6] = False; dark[:, 593:] = False; dark[0:7, :] = False; dark[384:, :] = False  # 图框
dark[249:, :196] = False  # 图例框
C1, C2 = (277.2, 130.6), (377.0, 120.3)  # ①②圈注中心
yy, xx = np.mgrid[0:H, 0:W]
for (cx, cy) in (C1, C2):
    dark[(xx - cx) ** 2 + (yy - cy) ** 2 <= 16.5 ** 2] = False

lab = np.zeros((H, W), dtype=np.int32)
n = 0
for y in range(H):
    for x in range(W):
        if dark[y, x] and lab[y, x] == 0:
            n += 1
            q = deque([(y, x)]); lab[y, x] = n
            while q:
                cy, cx = q.popleft()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and dark[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = n; q.append((ny, nx))
size = np.bincount(lab.ravel())
big = {k for k in range(1, n + 1) if size[k] > 100}

def comps_near(box, pad=7, min_size=100):
    x0, y0, x1, y1 = box
    sub = lab[max(0, y0 - pad):y1 + pad + 1, max(0, x0 - pad):x1 + pad + 1]
    return sorted({int(k) for k in np.unique(sub) if k and size[k] > min_size})

def comp_at(x, y):
    return int(lab[y, x])

# ---- 1) 每条等高线的代表像素（用于识别分量；坐标取自该线经过的点）----
lines = {
    1300: [(95, 91)],                    # 最内层闭合线（含甲点）
    1200: [(202, 100), (97, 107), (241, 116)],  # 注记1200所在线：注记下段 + “甲”字左侧段；①北侧小山包闭合线
    1100: [(56, 90), (323, 103)],         # ①圈左侧段 + ①圈右上段
    1000: [(46, 77), (154, 149), (357, 102)],  # 注记1000左段、右段（至①圈）、①圈右侧段
    900: [(120, 160), (497, 80)],         # 注记900左段 + 右段（绕②所在山脊东端）
    800: [(510, 90)],
    700: [(450, 147), (529, 91)],         # 注记700左段、右段
    600: [(492, 161)],
    500: [(459, 225), (578, 150)],        # 注记500左段、右段
    400: [(560, 302)],                    # 右缘伸入的窄舌形线
}
comp_of = {}
for elev, pts in lines.items():
    ks = []
    for (x, y) in pts:
        # 在 5×5 邻域里找最大的非背景分量，避免恰好落在线边缘
        cand = [(int(lab[y + dy, x + dx]), int(size[lab[y + dy, x + dx]])) for dy in range(-2, 3) for dx in range(-2, 3) if lab[y + dy, x + dx] > 0]
        assert cand, (elev, x, y)
        ks.append(max(cand, key=lambda t: t[1])[0])
    comp_of[elev] = ks
print("各高程线对应的连通分量:", comp_of)

# ---- 2) 注记两端紧贴的分量 ----
label_boxes = {"1200": (151, 7, 181, 71), "1000": (78, 128, 118, 151), "900": (329, 126, 359, 141),
               "700": (495, 121, 525, 135), "500": (548, 199, 578, 213), "400": (550, 272, 570, 286)}
for nm, box in label_boxes.items():
    print(f"注记{nm}附近的等高线分量:", comps_near(box))

# ①圈处四个线头的方位角（度，x向右为0，逆时针为正）
def ends_on_ring(c):
    cx, cy = c
    ring = ((xx - cx) ** 2 + (yy - cy) ** 2 <= 19.5 ** 2) & ((xx - cx) ** 2 + (yy - cy) ** 2 > 16.5 ** 2)
    out = {}
    for k in np.unique(lab[ring & (lab > 0)]):
        if size[k] < 100:
            continue
        ys, xs = np.where(ring & (lab == k))
        out[int(k)] = round(float(np.median(np.degrees(np.arctan2(-(ys - cy), xs - cx)))))
    return out
e1 = ends_on_ring(C1)
print("①圈边缘的线头方位角:", e1)
# 1100线：左(约170°)↔右上(约46°)；1000线：左下(约-133°)↔右(约5°)；两弦不相交，配对唯一。

# ---- 3) 甲点 ----
jia = (141, 83)
k_jia = comp_at(*jia)
print("甲点所在分量:", k_jia, "；1300线分量:", comp_of[1300][0], "；同一分量:", k_jia == comp_of[1300][0])

# ---- 4) 服务大厅 ----
hall = (466, 285)
def ray_hits(start, angle_deg, max_len=60):
    x0, y0 = start
    hits = []
    last = None
    for i in range(1, max_len * 2):
        t = i / 2
        x = int(round(x0 + t * math.cos(math.radians(angle_deg))))
        y = int(round(y0 - t * math.sin(math.radians(angle_deg))))
        if not (0 <= x < W and 0 <= y < H):
            break
        k = int(lab[y, x])
        if k and k in big and k not in (comp_at(472, 252), comp_at(466, 290)) and k != last:
            hits.append((k, x, y)); last = k
    return hits
k500 = set(comp_of[500])
for ang in (90, 120, 135, 150, 180):
    h = ray_hits((466, 248), ang, 80)
    first = h[0] if h else None
    print(f"从大厅屋顶向{ang}°方向遇到的第一条线:", first, "是500米线" if first and first[0] in k500 else "")

# ---- 5) 雪道坡度 ----
trail1 = [(255, 108), (262, 120), (284, 150), (295, 162), (305, 176), (313, 189), (322, 202), (330, 215), (333, 222)]
trail2_crest = [(377, 120), (396, 122), (412, 121), (426, 114), (441, 107), (455, 99), (469, 91), (475, 85)]
trail2_desc = [(470, 100), (473, 116), (478, 132), (482, 147), (484, 155), (484, 171), (484, 179), (482, 195), (483, 200)]

def crossings(poly, skip_circle=None):
    seq = []
    length = 0.0
    last = None
    for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
        L = math.hypot(x1 - x0, y1 - y0); length += L
        steps = int(L * 4) + 1
        for i in range(steps + 1):
            x = int(round(x0 + (x1 - x0) * i / steps)); y = int(round(y0 + (y1 - y0) * i / steps))
            k = int(lab[y, x])
            if k and k in big and k != last:
                seq.append(k); last = k
            elif not k:
                last = None if last is None else last
    return seq, length

contour_comps = {k: e for e, ks in comp_of.items() for k in ks}
s1, L1 = crossings(trail1)
s1e = [contour_comps.get(k, "?") for k in s1]
print("①雪道折线（坡面段）穿越的等高线（圈外部分）:", s1e, "；另①圈内穿越1100、1000两条线；折线长", round(L1, 1), "像素")
s2c, L2c = crossings(trail2_crest)
print("②雪道山脊段穿越:", [contour_comps.get(k, "?") for k in s2c], "；长", round(L2c, 1), "像素")
s2d, L2d = crossings(trail2_desc)
print("②东端下坡支线穿越:", [contour_comps.get(k, "?") for k in s2d], "；长", round(L2d, 1), "像素")

# ①：从小山包(≥1200)到700～600之间，穿越1200、1100、1000、900、800、700共6条线
n1 = len(set(e for e in s1e if e != "?")) + 2
print(f"①：{n1}条线/{L1:.0f}像素 → 平均{L1 / n1:.0f}像素一条（越小越陡）")
print(f"②山脊段：{len(s2c)}条线/{L2c:.0f}像素（不穿越等高线，平缓）")
n2d = len(set(e for e in [contour_comps.get(k, '?') for k in s2d] if e != "?"))
print(f"②东端下坡支线：{n2d}条线/{L2d:.0f}像素 → 平均{L2d / max(n2d, 1):.0f}像素一条")
print(f"②全程（山脊段+下坡）：{len(s2c) + n2d}条线/{L2c + L2d:.0f}像素 → 平均{(L2c + L2d) / max(len(s2c) + n2d, 1):.0f}像素一条")

# ---- 6) 高差 ----
jia_lo, jia_hi = 1300, 1400
hall_lo, hall_hi = 400, 500
print(f"甲：1300米线上（最多不到1400米）；服务大厅：{hall_lo}～{hall_hi}米")
print(f"高差：甲取1300时 {jia_lo - hall_hi}～{jia_lo - hall_lo} 米；甲放宽到1300～1400时 {jia_lo - hall_hi}～{jia_hi - hall_lo} 米")
print("C（超过900米）不能确定成立、D（不足700米）一定不成立；A错（①等高线密、坡陡）；B对（②沿900米线向东凸出的舌形区域，即山脊）")
