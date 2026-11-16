"""第50题：把重建的立体、①、②、③（剩余部分）按斜二测（纵深向右上）画出来，
与原图正、反两面直观图目测比对，检验重建是否正确。"""
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, '/home/user/xing-ce1/广东行测18套模拟/重编/M08/复核/scripts')

def render(cells, path, view='front', a=60, b=20):
    # view 'back': rotate 180 deg about z: x->2-x, y->2-y (bounding box 0..2)
    if view == 'back':
        mx = max(p[0] for p in cells); my = max(p[1] for p in cells)
        cells = {(mx - x, my - y, z): c for (x, y, z), c in cells.items()}
    img = Image.new('RGB', (400, 400), 'white')
    d = ImageDraw.Draw(img)
    ox, oy = 60, 340
    def P(x, y, z):
        return (ox + a * x + b * y, oy - a * z - b * y)
    # painter: draw back-to-front: larger y first, then lower z first?, then x ascending
    order = sorted(cells.items(), key=lambda kv: (-kv[0][1], kv[0][0], kv[0][2]))
    for (x, y, z), c in order:
        front = [P(x, y, z), P(x + 1, y, z), P(x + 1, y, z + 1), P(x, y, z + 1)]
        top = [P(x, y, z + 1), P(x + 1, y, z + 1), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)]
        right = [P(x + 1, y, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)]
        fc = (128, 128, 128) if c == 'G' else (255, 255, 255)
        sc = (100, 100, 100) if c == 'G' else (220, 220, 220)
        d.polygon(right, fill=sc, outline='black')
        d.polygon(top, fill=fc, outline='black')
        d.polygon(front, fill=fc, outline='black')
    img.save(path)

S = {
 (0,0,0):'W',(1,0,0):'W',(0,1,0):'W',(1,1,0):'W',(2,1,0):'W',(0,2,0):'W',(1,2,0):'W',(2,2,0):'W',
 (1,0,1):'G',(1,1,1):'W',(2,1,1):'G',(0,2,1):'W',(1,2,1):'W',(2,2,1):'W',
 (1,0,2):'W',(1,1,2):'W',(0,2,2):'W',(1,2,2):'G',
}
out = sys.argv[1]
render(S, out + '/q50_S_front.png', 'front')
render(S, out + '/q50_S_back.png', 'back')
P1 = {(0,1,0):'W',(1,0,0):'W',(2,0,0):'W',(2,0,1):'G',(1,1,0):'W',(2,1,0):'W',(2,1,1):'W'}
P2 = {(0,0,0):'W',(0,0,1):'W',(0,1,1):'G',(1,1,0):'W',(1,1,1):'W',(0,1,0):'W'}
render(P1, out + '/q50_P1.png'); render(P2, out + '/q50_P2.png')
