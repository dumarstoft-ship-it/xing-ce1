# 第49题：立体拼合 —— 模型数据与斜二测渲染（用于把重建结果画出来与原图对照）
# 坐标 (c, d, l)：c=列(左→右)，d=进深(0为最前排，越大越靠后)，l=层(1为底层)
from PIL import Image, ImageDraw

# 题干多面体（由前、后两面直观图重建；16块，3块灰色）
SOLID = {
    (1,0,1):'W', (2,0,1):'W',
    (0,1,1):'W', (1,1,1):'W', (2,1,1):'W', (3,1,1):'W',
    (1,2,1):'W', (2,2,1):'W', (3,2,1):'W',
    (1,1,2):'W', (2,1,2):'G', (1,2,2):'W', (2,2,2):'W', (3,2,2):'G',
    (2,1,3):'G', (2,2,3):'W',
}
# 四个选项（由选项图读出；B中(0,1,1)被遮住，但为保证连成一体必须存在）
PIECES = {
    'A': {(2,0,1):'G', (2,1,1):'W', (1,1,1):'W', (1,1,2):'W', (0,1,2):'W'},
    'B': {(0,0,1):'W', (0,1,1):'W', (0,1,2):'W', (1,1,1):'G'},
    'C': {(0,0,3):'G', (0,1,3):'W', (0,1,2):'W', (0,1,1):'W', (1,1,2):'W', (1,1,1):'W', (1,0,1):'W'},
    'D': {(1,0,1):'G', (1,0,2):'W', (0,1,1):'W', (0,1,2):'W', (1,1,1):'W', (1,1,2):'W', (1,1,3):'W'},
}

def back_view(cubes):
    """从背面看：左右颠倒、前后颠倒"""
    mc = max(c for c, d, l in cubes); md = max(d for c, d, l in cubes)
    return {(mc - c, md - d, l): v for (c, d, l), v in cubes.items()}

def render(cubes, S=22, K=7, pad=10):
    mc = max(c for c, d, l in cubes); md = max(d for c, d, l in cubes); ml = max(l for c, d, l in cubes)
    Wd = pad * 2 + S * (mc + 1) + K * (md + 1)
    Ht = pad * 2 + S * ml + K * (md + 1)
    img = Image.new('RGB', (Wd, Ht), 'white')
    dr = ImageDraw.Draw(img)
    col = {'W': ((255,255,255), (255,255,255), (215,215,215)),
           'G': ((125,125,125), (150,150,150), (95,95,95))}
    for (c, d, l) in sorted(cubes, key=lambda t: (-t[1], t[2], t[0])):
        f, t, r = col[cubes[(c, d, l)]]
        x0 = pad + S * c + K * d
        y0 = Ht - pad - K - S * l - K * d + K   # 前面左上角
        dr.polygon([(x0, y0), (x0 + S, y0), (x0 + S, y0 + S), (x0, y0 + S)], fill=f, outline='black')
        dr.polygon([(x0, y0), (x0 + K, y0 - K), (x0 + S + K, y0 - K), (x0 + S, y0)], fill=t, outline='black')
        dr.polygon([(x0 + S, y0), (x0 + S + K, y0 - K), (x0 + S + K, y0 + S - K), (x0 + S, y0 + S)], fill=r, outline='black')
    return img

if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    imgs = [render(SOLID), render(back_view(SOLID))] + [render(p) for p in PIECES.values()]
    Wt = sum(i.width for i in imgs) + 10 * len(imgs)
    Ht = max(i.height for i in imgs)
    canvas = Image.new('RGB', (Wt, Ht), 'white')
    x = 0
    for i in imgs:
        canvas.paste(i, (x, Ht - i.height)); x += i.width + 10
    canvas = canvas.resize((canvas.width * 3, canvas.height * 3), Image.NEAREST)
    canvas.save(f'{out}/q49_render.png')
    print('saved', f'{out}/q49_render.png')
