"""用 pdftocairo 把原书上的一块区域裁成独立的小页面（只含这块的矢量内容和文字）。
pdftocairo 的裁切参数只接受整数点，上边界向下取整、高度向上取整。"""
import math, os, subprocess

def crop(src_pdf, page_no, top, bottom, out_path, width=595):
    t = int(math.floor(top)); h = int(math.ceil(bottom - t))
    if not os.path.exists(out_path):
        subprocess.run(["pdftocairo", "-pdf", "-f", str(page_no), "-l", str(page_no),
                        "-x", "0", "-y", str(t), "-W", str(width), "-H", str(h),
                        "-paperw", str(width), "-paperh", str(h), src_pdf, out_path],
                       check=True, capture_output=True)
    return out_path, h
