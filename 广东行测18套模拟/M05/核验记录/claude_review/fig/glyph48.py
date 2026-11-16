# Q48: find glyphs in box row, and analyse each glyph's strokes via ASCII (downsampled)
import numpy as np, os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s31_p12_i00.png').convert('L')
im = np.array(img); dark = im < 128
# box interior: find box frame
r = dark[5:83]
print('box row profile >200:', [(y+5, int(r[y].sum())) for y in range(r.shape[0]) if r[y].sum() > 200])
cols = r.sum(0)
print('box col frame:', [(x, int(cols[x])) for x in range(dark.shape[1]) if cols[x] > 60])
