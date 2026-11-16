# 渲染原卷页面（200dpi）并按 source.regions 的 bbox 裁剪第16—30题；只读仓库与原卷克隆
import json, subprocess, sys, os
from PIL import Image
WD = os.path.dirname(os.path.abspath(__file__))
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
XC = "/home/user/dumarstoft-ship-it/xingce"
DPI = 200; S = DPI / 72.0
sel = {q["number"]: q for q in json.load(open(f"{M05}/selection.json", encoding="utf-8"))}
short = {"2025年浙江省公务员录用考试《行测》题（A类）（网友回忆版）.pdf": "zj2025",
         "2023年浙江省公务员录用考试《行测》题（A类）（网友回忆版）.pdf": "zj2023",
         "2023年江苏公务员考试《行测》真题（A类）.pdf": "js2023",
         "2022年江苏公务员考试《行测》真题（A类）....pdf": "js2022"}
rendered = {}
def page_png(fname, page):
    key = (fname, page)
    if key in rendered: return rendered[key]
    prefix = os.path.join(WD, "pages", f"{short[fname]}_p{page}")
    subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(page), "-l", str(page), "-png", "-singlefile",
                    os.path.join(XC, fname), prefix], check=True)
    rendered[key] = prefix + ".png"
    return rendered[key]
for n in range(16, 31):
    src = sel[n]["source_question"]["source"]
    for i, r in enumerate(src["regions"]):
        png = page_png(src["file"], r["page"])
        im = Image.open(png)
        x0, y0, x1, y1 = r["bbox"]
        m = 6  # pt 边距
        box = (max(0, int((x0 - m) * S)), max(0, int((y0 - m) * S)), min(im.width, int((x1 + m) * S)), min(im.height, int((y1 + m) * S)))
        out = os.path.join(WD, "crops", f"q{n}_{short[src['file']]}_p{r['page']}_{i}.png")
        im.crop(box).save(out)
        print(n, src["file"], r["page"], [round(v, 1) for v in r["bbox"]], "->", os.path.basename(out), im.size)
