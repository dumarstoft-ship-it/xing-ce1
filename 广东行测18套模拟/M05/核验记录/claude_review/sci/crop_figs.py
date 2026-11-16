# Read-only: crops/zooms question figures from the repo into the scratch dir.
from PIL import Image
import sys
A = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/'
jobs = [
    # (src, box, scale, outname)
    ('s32_p17_i01.png', (300, 0, 600, 161), 3, 'q66_graph_x3.png'),
    ('s32_p17_i01.png', (0, 40, 220, 161), 3, 'q66_box_x3.png'),
    ('s27_p18_i01.png', (180, 0, 420, 130), 4, 'q67_rheostat_x4.png'),
    ('s27_p18_i01.png', (380, 200, 574, 599), 2, 'q67_right_x2.png'),
    ('s27_p18_i01.png', (0, 200, 220, 599), 2, 'q67_left_x2.png'),
    ('s27_p18_i01.png', (180, 320, 450, 440), 3, 'q67_battery_switch_x3.png'),
    ('s23_p19_i11.png', (180, 0, 420, 120), 4, 'q70_B_x4.png'),
    ('s23_p19_i11.png', (400, 60, 643, 220), 3, 'q70_CD_x3.png'),
    ('s23_p19_i11.png', (180, 120, 420, 420), 3, 'q70_EF_x3.png'),
    ('s23_p19_i11.png', (0, 60, 260, 280), 3, 'q70_G_x3.png'),
    ('s23_p19_i11.png', (520, 0, 643, 100), 5, 'q70_north_x5.png'),
    ('s23_p19_i11.png', (180, 60, 420, 220), 3, 'q70_A_x3.png'),
]
for src, box, s, out in jobs:
    im = Image.open(A + src).crop(box)
    im = im.resize((im.width * s, im.height * s), Image.LANCZOS)
    im.save(out)
    print(out, im.size)
