"""Compare GPT redraws (M04/assets/q66_blocks.png, q67_circuit.png) with original embedded images.
Outputs (work dir/img): overlay_q66.png, overlay_q67.png (red=original only, blue=redraw only, black=both),
print_size_q66.png, print_size_q67.png (both at the physical size they print, rendered at 300 dpi),
and figure_compare.json with sizes, print sizes and a coarse stroke-agreement score.
Read-only on repo. Run: python3 figure_compare.py
"""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = '/home/user/xing-ce1/'
import os
W = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(W, 'img'), exist_ok=True)
pairs = {
    'q66': dict(orig='模考/2026下半年广东卷_16-33季_AI可读/assets/s33_p18_i00.png',
                redraw='广东行测18套模拟/M04/assets/q66_blocks.png',
                orig_bbox_pt=[67.951, 319.181, 270.569, 394.545],
                built_mm=(120.0, 42.5)),
    'q67': dict(orig='模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p18_i00.png',
                redraw='广东行测18套模拟/M04/assets/q67_circuit.png',
                orig_bbox_pt=[67.951, 90.0, 234.741, 265.438],
                built_mm=(88.6, 100.0)),
}

def dark_mask(img, thr=128):
    g = np.asarray(img.convert('L'), dtype=np.uint8)
    return g < thr

def crop_to_ink(mask):
    ys, xs = np.nonzero(mask)
    return mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (xs.min(), ys.min(), xs.max(), ys.max())

def dilate(mask, r):
    im = Image.fromarray((mask * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.MaxFilter(2 * r + 1))) > 0

report = {}
for key, p in pairs.items():
    o = Image.open(REPO + p['orig']); r = Image.open(REPO + p['redraw'])
    om, obox = crop_to_ink(dark_mask(o))
    rm, rbox = crop_to_ink(dark_mask(r))
    # resample redraw ink-crop to original ink-crop size (independent x/y scale)
    rm_s = np.asarray(Image.fromarray((rm * 255).astype(np.uint8)).resize((om.shape[1], om.shape[0]), Image.BOX)) > 40
    tol = 3
    o_in_r = float((om & dilate(rm_s, tol)).sum() / om.sum())
    r_in_o = float((rm_s & dilate(om, tol)).sum() / rm_s.sum())
    # overlay
    k = 4
    H, Wd = om.shape
    rgb = np.full((H, Wd, 3), 255, np.uint8)
    rgb[om & ~rm_s] = (220, 30, 30)
    rgb[rm_s & ~om] = (30, 80, 230)
    rgb[om & rm_s] = (0, 0, 0)
    Image.fromarray(rgb).resize((Wd * k, H * k), Image.NEAREST).save(f'{W}/img/overlay_{key}.png')
    b = p['orig_bbox_pt']
    orig_mm = ((b[2] - b[0]) / 72 * 25.4, (b[3] - b[1]) / 72 * 25.4)
    # physical-size side-by-side at 300 dpi
    dpi = 300
    def px(mm): return int(round(mm / 25.4 * dpi))
    o_print = o.convert('RGB').resize((px(orig_mm[0]), px(orig_mm[1])), Image.BICUBIC)
    r_print = r.convert('RGB').resize((px(p['built_mm'][0]), px(p['built_mm'][1])), Image.LANCZOS)
    pad = 60
    canvas = Image.new('RGB', (o_print.width + r_print.width + 3 * pad, max(o_print.height, r_print.height) + 2 * pad + 40), 'white')
    canvas.paste(o_print, (pad, pad + 40)); canvas.paste(r_print, (2 * pad + o_print.width, pad + 40))
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 28)
    except Exception:
        font = ImageFont.load_default()
    d.text((pad, 10), f'original {orig_mm[0]:.1f}x{orig_mm[1]:.1f}mm', fill='black', font=font)
    d.text((2 * pad + o_print.width, 10), f'redraw as built {p["built_mm"][0]:.1f}x{p["built_mm"][1]:.1f}mm', fill='black', font=font)
    canvas.save(f'{W}/img/print_size_{key}.png', dpi=(dpi, dpi))
    report[key] = dict(
        original=p['orig'], original_px=o.size, original_print_mm=[round(x, 1) for x in orig_mm],
        original_effective_dpi=round(o.size[0] / (orig_mm[0] / 25.4), 1),
        redraw=p['redraw'], redraw_px=r.size, redraw_built_mm=list(p['built_mm']),
        linear_enlargement_vs_original=[round(p['built_mm'][0] / orig_mm[0], 2), round(p['built_mm'][1] / orig_mm[1], 2)],
        area_ratio=round(p['built_mm'][0] * p['built_mm'][1] / (orig_mm[0] * orig_mm[1]), 2),
        ink_bbox_aspect_original=round(om.shape[1] / om.shape[0], 3), ink_bbox_aspect_redraw=round(rm.shape[1] / rm.shape[0], 3),
        coarse_stroke_agreement_tol3px=dict(original_ink_near_redraw=round(o_in_r, 3), redraw_ink_near_original=round(r_in_o, 3)),
    )
json.dump(report, open(f'{W}/figure_compare.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(report, indent=1, ensure_ascii=False))
