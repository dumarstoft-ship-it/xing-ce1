# -*- coding: utf-8 -*-
"""Q49 立体拼合：把题图中每个立体读成小立方体坐标，并按题图的斜二测投影重新画出来，与原图并排比对。

坐标：x 向右，y 向后（纵深），z 向上。题图投影：屏幕 = (ox + s*x + dx*y, oy - s*z - dy*y)，
s≈21 像素，纵深每格 (dx,dy)≈(6.7,7.0) 像素（从大图量得）。
正面、顶面白色，右侧面灰色。
运行后生成 scratch 目录下的比对图 q49_render_check.png。
"""
import itertools
import numpy as np
from PIL import Image, ImageDraw

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p13_i00.png'
OUT = '/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m04/q49_render_check.png'

S, DX, DY = 21.1, 6.67, 6.97

# ---------------- 读图得到的模型 ----------------
BIG = {(x, y, z) for x in range(3) for y in range(3) for z in range(3)} | {
    (3, 1, 0), (3, 1, 1), (3, 2, 0), (3, 2, 1), (3, 2, 2)}
P1 = {(0, 1, 0), (0, 1, 1), (1, 1, 0), (1, 1, 1), (2, 1, 0), (2, 1, 1), (2, 1, 2), (1, 0, 0)}
P2_VISIBLE = {(x, 2, z) for x in range(3) for z in range(3)} | {(1, 1, 2), (2, 1, 1), (2, 1, 0), (1, 0, 1), (1, 0, 0)}
P2_HIDDEN = [(1, 1, 1), (1, 1, 0)]          # 被前面方块挡住、看不到的位置
OPT = {
    'A': ({(0, 2, 0), (0, 2, 1), (1, 2, 1), (2, 2, 0), (2, 2, 1), (1, 1, 0), (1, 0, 0)}, [(1, 2, 0)]),
    'B': ({(0, 2, 0), (0, 2, 1), (1, 2, 1), (2, 2, 0), (1, 1, 0), (1, 0, 0)}, [(1, 2, 0)]),
    'C': ({(2, 2, 0), (2, 2, 1), (1, 2, 1), (1, 1, 1), (1, 1, 0), (1, 0, 0), (0, 2, 0)}, [(1, 2, 0)]),
    'D': ({(1, 2, 1), (2, 2, 1), (0, 2, 0), (1, 0, 0), (1, 1, 0), (1, 2, 0)}, []),
}


def render(vox, size=(120, 120), origin=None):
    vox = set(vox)
    im = Image.new('L', size, 255)
    dr = ImageDraw.Draw(im)
    xs = [v[0] for v in vox]; ys = [v[1] for v in vox]; zs = [v[2] for v in vox]
    if origin is None:
        # 让包围盒居中
        minx = min(S * x + DX * y for x, y, z in vox); maxx = max(S * (x + 1) + DX * (y + 1) for x, y, z in vox)
        miny = min(-S * (z + 1) - DY * (y + 1) for x, y, z in vox); maxy = max(-S * z - DY * y for x, y, z in vox)
        origin = (size[0] / 2 - (minx + maxx) / 2, size[1] / 2 - (miny + maxy) / 2)
    ox, oy = origin

    def P(x, y, z):
        return (ox + S * x + DX * y, oy - S * z - DY * y)
    # 视线方向 d = (-DX/S, 1, -DY/S)，沿 d 越大越远，先画远的
    order = sorted(vox, key=lambda v: -(-DX / S * v[0] + v[1] - DY / S * v[2]))
    for (x, y, z) in order:
        if (x, y, z + 1) not in vox:   # 顶面
            dr.polygon([P(x, y, z + 1), P(x + 1, y, z + 1), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)], fill=255, outline=0)
        if (x + 1, y, z) not in vox:   # 右侧面
            dr.polygon([P(x + 1, y, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)], fill=200, outline=0)
        if (x, y - 1, z) not in vox:   # 正面
            dr.polygon([P(x, y, z), P(x + 1, y, z), P(x + 1, y, z + 1), P(x, y, z + 1)], fill=255, outline=0)
    return im


def hidden_cells(vox):
    """渲染时完全看不到的方块（三个可见面都被挡住）"""
    vox = set(vox)
    return sorted(v for v in vox if (v[0], v[1] - 1, v[2]) in vox and (v[0], v[1], v[2] + 1) in vox
                  and (v[0] + 1, v[1], v[2]) in vox)


if __name__ == '__main__':
    src = Image.open(IMG).convert('L')
    panels = [('大图', BIG, (9, 7, 128, 128)), ('①', P1, (129, 7, 249, 128)),
              ('②', P2_VISIBLE | set(P2_HIDDEN), (250, 7, 370, 128))]
    for k in 'ABCD':
        vis, hid = OPT[k]
        box = {'A': (9, 155, 128, 276), 'B': (129, 155, 249, 276), 'C': (250, 155, 370, 276), 'D': (371, 155, 491, 276)}[k]
        panels.append((k, vis | set(hid), box))
    tiles = []
    for name, vox, box in panels:
        orig = src.crop(box).resize((240, 242))
        ren = render(vox, size=(119, 121)).resize((240, 242))
        t = Image.new('L', (490, 250), 255)
        t.paste(orig, (0, 0)); t.paste(ren, (250, 0))
        tiles.append(t)
        print(name, '方块数', len(vox), '渲染时完全被挡住的方块', hidden_cells(vox))
    W = 490 * 2 + 10
    H = 250 * ((len(tiles) + 1) // 2)
    cv = Image.new('L', (W, H), 255)
    for i, t in enumerate(tiles):
        cv.paste(t, ((i % 2) * 500, (i // 2) * 250))
    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cv.save(OUT)
    print('saved', OUT)
