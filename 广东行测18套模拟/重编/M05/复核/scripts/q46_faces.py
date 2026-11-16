"""Q46: reproducible face (closed-region) count for the 5 stem panels and 4 options,
using faces() from regions.py in this directory. Panel boxes are inside the frames."""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regions import faces

IMG = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s20_p11_i00.png"
BOXES = {
    "fig1": (6,9,101,105), "fig2": (105,9,199,105), "fig3": (203,9,298,105),
    "fig4": (302,9,396,105), "fig5": (401,9,495,105),
    "A": (107,126,201,236), "B": (205,126,299,236), "C": (304,126,398,236), "D": (403,126,497,236),
}
arr = np.array(Image.open(IMG).convert("L"))
for k, (x0, y0, x1, y1) in BOXES.items():
    print(k, len(faces(arr[y0:y1, x0:x1])))
