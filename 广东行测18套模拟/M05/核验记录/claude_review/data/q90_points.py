# -*- coding: utf-8 -*-
"""Q90 选项图点位提取（只读 blind_input.json 中给出的 abs_path 图片）。
方法：灰度阈值得到深色像素；用 5×5 窗口计数，圆点处计数显著高于 1-2px 折线；
对高计数像素做连通分量（4 邻域 BFS）并取加权质心作为点位。y 轴向下，数值越大位置越低。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
from blind_common import q

N = 90
res = {}
for k, v in q(N)["options"].items():
    p = v[0]["abs_path"]
    im = np.asarray(Image.open(p).convert("L"), dtype=np.int32)
    H, W = im.shape
    dark = (im < 128).astype(np.int32)
    pad = np.pad(dark, 2)
    cnt = sum(pad[dy:dy + H, dx:dx + W] for dy in range(5) for dx in range(5))
    mask = (cnt >= 17) & (dark == 1)
    seen = np.zeros_like(mask, dtype=bool)
    comps = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not seen[y, x]:
                st = [(y, x)]; seen[y, x] = True; pts = []
                while st:
                    a, b = st.pop(); pts.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        aa, bb = a + da, b + db
                        if 0 <= aa < H and 0 <= bb < W and mask[aa, bb] and not seen[aa, bb]:
                            seen[aa, bb] = True; st.append((aa, bb))
                if len(pts) >= 4:
                    ys = np.array([t[0] for t in pts], float); xs = np.array([t[1] for t in pts], float)
                    w = cnt[ys.astype(int), xs.astype(int)].astype(float)
                    comps.append((float((xs * w).sum() / w.sum()), float((ys * w).sum() / w.sum()), len(pts)))
    comps.sort()
    res[k] = comps
    print("选项%s：图 %dx%d，检测到 %d 个点：%s" % (k, W, H, len(comps),
          "  ".join("(x=%.1f, y=%.1f, n=%d)" % c for c in comps)))
    if len(comps) == 4:
        ys = [c[1] for c in comps]
        lo, hi = max(ys), min(ys)
        norm = [(lo - y) / (lo - hi) for y in ys]
        print("     归一化高度（最低=0，最高=1）：", ["%.3f" % t for t in norm])
        steps = ["升" if ys[i + 1] < ys[i] else "降" for i in range(3)]
        print("     走势：", "→".join(steps))

import json
json.dump({k: [[round(c[0], 2), round(c[1], 2)] for c in v] for k, v in res.items()},
          open(os.path.join(os.path.dirname(__file__), "q90_points.json"), "w"), ensure_ascii=False, indent=1)
