import numpy as np
from PIL import Image, ImageDraw
im=Image.open('r/gd23z46_raw.png'); a=np.array(im)<140
H,W=a.shape
# find option panel borders: vertical lines spanning most of height
cols=[x for x in range(W) if a[:,x].sum()>0.8*H]
print('vlines',cols[:50])
