# Read-only: further crops of Q70 contour map.
from PIL import Image
A = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/'
im0 = Image.open(A + 's23_p19_i11.png')
jobs = [
    ((0, 0, 330, 240), 3, 'q70_topleft_x3.png'),
    ((310, 0, 643, 240), 3, 'q70_topright_x3.png'),
    ((0, 200, 330, 450), 3, 'q70_botleft_x3.png'),
    ((310, 200, 643, 450), 3, 'q70_botright_x3.png'),
]
for box, s, out in jobs:
    im = im0.crop(box)
    im = im.resize((im.width * s, im.height * s), Image.LANCZOS)
    im.save(out)
    print(out, im.size)
