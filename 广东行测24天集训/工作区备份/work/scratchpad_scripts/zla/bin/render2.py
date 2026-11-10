"""Faithful material renderer: crops segments, masks page furniture (page numbers, exam-title banners,
seller/watermark ad lines) and compresses large blank gaps. Content pixels are never altered."""
import json, os, re, sys, unicodedata, pymupdf
import numpy as np
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
JUNK = re.compile(r'(本试卷由粉笔|认准淘宝|通关达人|免费获取更多考公|添加微信|TB:Seeyee|Seeyee智库|^\s*-\s*\d+\s*-\s*$|^\s*\d+\s*/\s*\d+\s*$|^\s*第\s*\d+\s*页|第\s*\d+\s*页\s*[,，]?\s*共\s*\d+\s*页|^\s*\d{1,2}\s*$|公务员录用考试《行测》题|公务员考试《行测》真题|网友回忆版\)\s*$)')
def junk_rects(page, clip):
    rs = []
    for b in page.get_text('blocks', clip=clip):
        t = unicodedata.normalize('NFKC', b[4]).strip()
        if b[6] != 0 or not JUNK.search(t):
            continue
        r = pymupdf.Rect(b[:4])
        # pure page-number-like blocks are masked only in the top/bottom page margins
        if re.fullmatch(r'\s*(?:-\s*)?\d{1,3}(?:\s*-)?(?:\s*/\s*\d+)?\s*', t) and 70 < r.y0 < page.rect.height - 70:
            continue
        rs.append(r)
    for im in page.get_image_info():
        r = pymupdf.Rect(im['bbox'])
        if r.height < 32 and r.width > 400 and r.y0 < 90:   # exam-title banner image at page top
            rs.append(r)
    return rs
def render_seg(page, y0, y1, dpi, margin_x=20):
    clip = pymupdf.Rect(margin_x, max(0, y0), page.rect.width - margin_x, min(page.rect.height, y1))
    pix = page.get_pixmap(clip=clip, dpi=dpi)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    s = dpi / 72.0
    a = np.array(im)
    for r in junk_rects(page, clip):
        x0 = int((r.x0 - clip.x0) * s) - 2; x1 = int((r.x1 - clip.x0) * s) + 2
        yy0 = int((r.y0 - clip.y0) * s) - 2; yy1 = int((r.y1 - clip.y0) * s) + 2
        a[max(0, yy0):max(0, yy1), max(0, x0):max(0, x1)] = 255
    return a, page.get_text('text', clip=clip)
def squeeze(a, maxgap=36, thr=246):
    dark = (a.min(axis=2) < thr).sum(axis=1) > 2
    keep = []; run = 0
    idx = np.where(dark)[0]
    if len(idx) == 0: return a
    top, bot = max(0, idx[0] - 10), min(len(dark), idx[-1] + 10)
    for y in range(top, bot):
        if dark[y]: run = 0; keep.append(y)
        else:
            run += 1
            if run <= maxgap: keep.append(y)
    return a[keep]
def render_material(path, segs, dpi=200):
    doc = pymupdf.open('/home/user/' + path)
    parts = []; texts = []
    for (p, y0, y1) in segs:
        a, t = render_seg(doc[p], y0, y1, dpi)
        parts.append(squeeze(a)); texts.append(t)
    W = max(x.shape[1] for x in parts)
    parts = [np.pad(x, ((0, 0), (0, W - x.shape[1]), (0, 0)), constant_values=255) for x in parts]
    out = np.concatenate(parts, axis=0)
    return Image.fromarray(out), '\n'.join(texts)
