"""Count enclosed white regions and black connected components inside panels.
usage: python3 regions.py IMG x0,y0,x1,y1 [x0,y0,x1,y1 ...]
Each box should be the panel's INTERIOR (inside the frame border)."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

def analyze(arr, thr=160, min_area=4):
    dark = arr < thr
    # black components
    lab_b, nb = ndimage.label(dark, structure=np.ones((3,3)))
    sizes_b = ndimage.sum(dark, lab_b, range(1, nb+1))
    # white components (4-connectivity so thin diagonal lines separate)
    white = ~dark
    lab_w, nw = ndimage.label(white)
    sizes = ndimage.sum(white, lab_w, range(1, nw+1))
    # outside = components touching the border
    border = set(np.unique(np.concatenate([lab_w[0,:], lab_w[-1,:], lab_w[:,0], lab_w[:,-1]]))) - {0}
    inner = [(i+1, int(s)) for i, s in enumerate(sizes) if (i+1) not in border and s >= min_area]
    return nb, [int(s) for s in sizes_b], inner

if __name__ == '__main__':
    img = np.array(Image.open(sys.argv[1]).convert('L'))
    for box in sys.argv[2:]:
        x0, y0, x1, y1 = map(int, box.split(','))
        nb, sb, inner = analyze(img[y0:y1, x0:x1])
        print(box, 'black comps:', nb, sorted(sb, reverse=True)[:6], '| enclosed regions:', len(inner), sorted([s for _, s in inner], reverse=True))
