"""第82题：量出四个饼图各扇区的圆心角，与2024年各地区旅客吞吐量占比对照。

做法：读取选项图，按非白像素外接框定圆心与半径；从12点方向起顺时针每0.05°取样，
在0.45R、0.6R、0.75R三个半径上按灰度分为 白/浅灰/深灰/黑 四类（取多数），
把短于3°的零碎段视为扇区分界线（抗锯齿），平分给两侧，统计每块扇区所占角度。
"""
import os
import math
from PIL import Image
import numpy as np

ASSET_DIR = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets"
OPTIONS = {"A": "s20_p22_i01.png", "B": "s20_p22_i02.png",
           "C": "s20_p22_i03.png", "D": "s20_p23_i00.png"}

# 材料数据：2024年各地区旅客吞吐量（亿人次）
PAX = {"东部": 7.57, "中部": 1.61, "西部": 4.49, "东北": 0.93}
TOTAL = 14.60


def classify(v):
    if v >= 235:
        return "白"
    if v >= 180:
        return "浅灰"
    if v >= 70:
        return "深灰"
    return "黑"


def measure(path):
    img = np.asarray(Image.open(path).convert("L"), dtype=float)
    h, w = img.shape
    ys, xs = np.where(img < 200)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = ((x1 - x0) + (y1 - y0)) / 4
    step = 0.05
    n = int(round(360 / step))
    labels = []
    for i in range(n):
        th = math.radians(i * step)
        votes = {}
        for f in (0.45, 0.6, 0.75):
            r = f * R
            x = cx + r * math.sin(th)
            y = cy - r * math.cos(th)
            v = img[int(round(y)), int(round(x))]
            c = classify(v)
            votes[c] = votes.get(c, 0) + 1
        labels.append(max(votes, key=votes.get))
    # 连续段
    runs = []
    start = 0
    for i in range(1, n + 1):
        if i == n or labels[i] != labels[start]:
            runs.append([labels[start], start, i])
            start = i
    # 首尾同类则合并（环形）
    if len(runs) > 1 and runs[0][0] == runs[-1][0]:
        runs[0][1] = runs[-1][1] - n
        runs.pop()
    # 各连续段的角度（度）与起点
    angles = []
    for lab, s, e in runs:
        angles.append([lab, (e - s) * step, s * step])
    merged = []
    k = len(angles)
    extra = [0.0] * k
    keep = [True] * k
    # 分界线是1—2像素的黑线，抗锯齿后在取样中表现为短于3°的零碎段（黑、浅灰、深灰都有），
    # 把这些短段平分给前后两个长段。
    long_idx = [i for i, (lab, ang, st) in enumerate(angles) if ang >= 3]
    for idx, (lab, ang, st) in enumerate(angles):
        if ang < 3:
            keep[idx] = False
            prev = max((i for i in long_idx if i < idx), default=long_idx[-1])
            nxt = min((i for i in long_idx if i > idx), default=long_idx[0])
            extra[prev] += ang / 2
            extra[nxt] += ang / 2
    for idx, (lab, ang, st) in enumerate(angles):
        if keep[idx]:
            merged.append((lab, ang + extra[idx], st))
    return (cx, cy, R), merged


def main():
    target = sorted((v / TOTAL * 100 for v in PAX.values()), reverse=True)
    print("材料占比：")
    for k, v in PAX.items():
        print(f"  {k}: {v}/{TOTAL} = {v / TOTAL * 100:.2f}%  (圆心角 {v / TOTAL * 360:.1f}°)")
    print("  从大到小：", " / ".join(f"{t:.2f}%" for t in target))
    print()
    for opt, fn in OPTIONS.items():
        (cx, cy, R), segs = measure(os.path.join(ASSET_DIR, fn))
        tot = sum(a for _, a, _ in segs)
        print(f"选项{opt} {fn}: 圆心({cx:.1f},{cy:.1f}) 半径{R:.1f}，扇区数{len(segs)}（自12点方向顺时针）")
        for lab, ang, st in segs:
            print(f"  起点{st:6.1f}° {lab:<3} {ang:6.1f}°  {ang / tot * 100:5.1f}%")
        shares = sorted((ang / tot * 100 for _, ang, _ in segs), reverse=True)
        if len(shares) == len(target):
            dev = max(abs(a - b) for a, b in zip(shares, target))
            print(f"  按大小对应后最大偏差 {dev:.1f} 个百分点")
        else:
            print(f"  只有{len(shares)}个扇区，与4个地区不符")
        print()


if __name__ == "__main__":
    main()
