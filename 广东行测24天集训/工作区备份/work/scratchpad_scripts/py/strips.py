from PIL import Image
import numpy as np
im = np.array(Image.open('/home/user/work/build/pkg_r2/assets/PD2A/GD2020X-45.png').convert('L')).astype(int)
# find strip rows: look at x range 360..1250, rows where many dark pixels (horizontal edges)
H, W = im.shape
dark = im < 128
rows = [y for y in range(320, H) if dark[y, 360:1250].sum() > 600]
print('edge rows', rows)
