# 高倍渲染原卷局部：zoom.py <pdf短名> <页> <x0> <y0> <x1> <y1> <输出名> [dpi]
import sys, subprocess, os
from PIL import Image
WD = os.path.dirname(os.path.abspath(__file__))
XC = "/home/user/dumarstoft-ship-it/xingce"
files = {"zj2025": "2025年浙江省公务员录用考试《行测》题（A类）（网友回忆版）.pdf",
         "zj2023": "2023年浙江省公务员录用考试《行测》题（A类）（网友回忆版）.pdf",
         "js2023": "2023年江苏公务员考试《行测》真题（A类）.pdf",
         "js2022": "2022年江苏公务员考试《行测》真题（A类）....pdf",
         "zj2025jx": "2025年浙江省公务员录用考试《行测》题（A类）（网友回忆版）解析.pdf",
         "js2023jx": "2023年江苏公务员考试《行测》真题（A类）解析.pdf",
         "js2022jx": "2022年江苏公务员考试《行测》（A类）及解析.pdf",
         "zj2023jx": "2023年浙江省公务员录用考试《行测》真题（A类）（解析）.pdf"}
key, page, x0, y0, x1, y1, out = sys.argv[1:8]
dpi = int(sys.argv[8]) if len(sys.argv) > 8 else 400
page = int(page); s = dpi / 72.0
tmp = os.path.join(WD, "pages", f"{key}_p{page}_{dpi}")
if not os.path.exists(tmp + ".png"):
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-png", "-singlefile", os.path.join(XC, files[key]), tmp], check=True)
im = Image.open(tmp + ".png")
box = tuple(int(float(v) * s) for v in (x0, y0, x1, y1))
im.crop(box).save(os.path.join(WD, "crops", out))
print("saved", out, box, im.size)
