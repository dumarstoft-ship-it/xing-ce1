# 第50题：把各选项三个可见面拉正放大，并在旁边画出“若该选项正确、按展开图应呈现的图案”，供目视核对
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from q50_fold import LINES, S, K
from PIL import Image, ImageDraw

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s16_p12_i01.png'
src = Image.open(IMG).convert('L')
BIG = 8
big = np.array(src.resize((src.width * BIG, src.height * BIG), Image.BICUBIC)).astype(float)
BOX = {'A': (165, 22), 'B': (277, 21), 'C': (390, 22), 'D': (501, 21)}
M = 200

def unwarp(k, name):
    x0, y0 = BOX[k]
    out = np.zeros((M, M))
    for j in range(M):
        for i in range(M):
            u = (i + 0.5) / M; v = (j + 0.5) / M
            if name == '前': X, Y = u * S, K + v * S
            elif name == '上': X, Y = u * S + (1 - v) * K, v * K
            else: X, Y = S + u * K, (1 - u) * K + v * S
            out[j, i] = big[int((y0 + Y) * BIG), int((x0 + X) * BIG)]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def rot_uv(u, v, r):
    for _ in range(r // 90):
        u, v = 1 - v, u
    return u, v

def draw_face(f, r):
    img = Image.new('L', (M, M), 255); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, M - 1, M - 1], outline=0, width=3)
    for p, q in LINES[f]:
        a = rot_uv(*p, r); b = rot_uv(*q, r)
        d.line([(a[0] * M, a[1] * M), (b[0] * M, b[1] * M)], fill=0, width=4)
    d.text((5, 5), f'{f} {r}', fill=0)
    return img

# 每个选项：三面原图拉正 + 对应“可折出的”候选摆放
cands = {
    'A': [('F1', 270, 'F6', 90, 'F3', 180), ('F1', 270, 'F2', 270, 'F3', 0)],   # 图中所见 vs 可折出的 (F1,F2,F3)
    'B': [('F5', 90, 'F2', 0, 'F4', 270), ('F5', 90, 'F4', 90, 'F2', 270)],     # 图中所见 vs 可折出的 (F5,F4,F2)
    'C': [('F6', 90, 'F5', 180, 'F4', 270), ('F6', 90, 'F3', 0, 'F4', 90)],     # 图中所见 vs 可折出的 (F6,F3,F4)
    'D': [('F6', 0, 'F4', 0, 'F5', 90)],
}
rows = []
for k in 'ABCD':
    row = Image.new('L', (M * 3 + 40, M * (1 + len(cands[k])) + 20 * len(cands[k])), 255)
    for j, nm in enumerate(('前', '上', '右')):
        row.paste(unwarp(k, nm), (j * (M + 20), 0))
    for i, c in enumerate(cands[k]):
        for j in range(3):
            row.paste(draw_face(c[2 * j], c[2 * j + 1]), (j * (M + 20), (i + 1) * (M + 20)))
    row.save(f'{sys.argv[1]}/q50_unwarp_{k}.png')
print('done')
