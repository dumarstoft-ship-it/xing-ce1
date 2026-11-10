import sys, os, json, pymupdf, numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
import clean_render
pymupdf.TOOLS.mupdf_display_errors(False)
OUT = '/home/user/work/out4/PD4C/assets'
os.makedirs(OUT, exist_ok=True)
def trim(im, pad=12, thr=245):
    a = np.asarray(im.convert('L')); rows = np.where((a <= thr).any(axis=1))[0]; cols = np.where((a <= thr).any(axis=0))[0]
    return im.crop((max(0, cols[0] - pad), max(0, rows[0] - pad), min(im.width, cols[-1] + pad), min(im.height, rows[-1] + pad)))
def from_index(tag, qno, name, cut_bottom=None):
    tmp = f'a200/{tag}_q{qno}.png'
    clean_render.render(tag, qno, tmp, dpi=200)
    im = Image.open(tmp).convert('RGB')
    if cut_bottom: im = im.crop((0, 0, im.width, cut_bottom))
    im = trim(im); im.save(f'{OUT}/{name}'); print(name, im.size)
def from_pdf(rel, segs, name, dpi=200, gap=30):
    doc = pymupdf.open('/home/user/' + rel); ims = []
    for (p, x0, y0, x1, y1) in segs:
        page = doc[p]; clip = pymupdf.Rect(x0, y0, x1 if x1 else page.rect.width - 18, y1)
        pix = page.get_pixmap(clip=clip, dpi=dpi); ims.append(trim(Image.frombytes('RGB', (pix.width, pix.height), pix.samples), pad=6))
    W = max(i.width for i in ims); H = sum(i.height for i in ims) + gap * (len(ims) - 1)
    canvas = Image.new('RGB', (W, H), 'white'); y = 0
    for i in ims: canvas.paste(i, (0, y)); y += i.height + gap
    im = trim(canvas); im.save(f'{OUT}/{name}'); print(name, im.size)
if __name__ == '__main__':
    from_index('GD2016Z', 63, 'PD4C-031_GD2016Z-63.png')
    from_index('GD2018', 64, 'PD4C-032_GD2018-64.png')
    from_index('GD2016Z', 68, 'PD4C-033_GD2016Z-68.png')
    from_index('GD2021Z', 74, 'PD4C-034_GD2021Z-74.png')
    from_index('GD2019X', 62, 'PD4C-037_GD2019X-62.png')
    from_index('GD2022X', 77, 'PD4C-039_GD2022X-77.png')
    from_index('GD2020Z', 75, 'PD4C-044_GD2020Z-75.png')
