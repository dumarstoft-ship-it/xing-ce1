"""Q50: render the voxel readings in the same oblique projection as the original
drawing, next to the original crops, for a visual check of the reading."""
import sys
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit('/', 1)[0])
src = open(__file__.replace('q50_render.py', 'q50_assembly.py')).read().split('assert sum')[0]
ns = {}
exec(src, ns)
SOLID, P1, P2, OPTS = ns['SOLID'], ns['P1'], ns['P2_variants']['P2 + hidden (0,1,0)'], ns['OPTS']

U, DX, DY = 16.3 * 4, 5 * 4, -5.5 * 4
FILL = {'W': (255, 255, 255), 'G': (128, 128, 128)}
SIDE = {'W': (215, 215, 215), 'G': (95, 95, 95)}


def render(vox, size=(420, 420), origin=(40, 380)):
    img = Image.new('RGB', size, 'white')
    d = ImageDraw.Draw(img)
    ox, oy = origin
    P = lambda x, y, z: (ox + U * x + DX * y, oy - U * z + DY * y)
    for (x, y, z) in sorted(vox, key=lambda p: (-p[1], p[2], p[0])):
        c = vox[(x, y, z)]
        front = [P(x, y, z), P(x + 1, y, z), P(x + 1, y, z + 1), P(x, y, z + 1)]
        top = [P(x, y, z + 1), P(x + 1, y, z + 1), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)]
        right = [P(x + 1, y, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)]
        for poly, col in [(right, SIDE[c]), (top, FILL[c]), (front, FILL[c])]:
            d.polygon(poly, fill=col, outline='black', width=3)
    return img


orig = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p13_i01.png').convert('RGB')
back = {(2 - x, 2 - y, z): c for (x, y, z), c in SOLID.items()}
tiles = [orig.crop((25, 20, 100, 95)).resize((300, 300)), render(SOLID).resize((300, 300)),
         orig.crop((140, 20, 220, 95)).resize((320, 300)), render(back).resize((300, 300))]
W = sum(t.size[0] for t in tiles) + 30
canvas = Image.new('RGB', (W, 300), (200, 200, 200))
x = 0
for t in tiles:
    canvas.paste(t, (x, 0)); x += t.size[0] + 10
out = sys.argv[1] if len(sys.argv) > 1 else 'q50_render_check.png'
canvas.save(out)
print('saved', out)
