# Find frame lines in Q46 figure (row/col dark-pixel profiles)
import numpy as np
from PIL import Image
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i00.png').convert('L'))
H, W = im.shape
dark = im < 128
rows = dark.sum(1); cols = dark.sum(0)
print('H,W', H, W)
print('rows with many dark px (>150):', [ (i,int(rows[i])) for i in range(H) if rows[i] > 150])
# columns: compute dark count within top band and bottom band separately
top = dark[:120]; bot = dark[120:240]
print('top cols >60:', [ (j,int(top[:,j].sum())) for j in range(W) if top[:,j].sum() > 60])
print('bot cols >60:', [ (j,int(bot[:,j].sum())) for j in range(W) if bot[:,j].sum() > 60])
