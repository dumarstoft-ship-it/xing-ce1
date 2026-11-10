"""Material regions (0-based page, y0, y1 in PDF points) for ZL4A's new materials. Entries without 'segs' are resolved by locate():
from the header line (regex) found after the end of question q0-1, down to the start of question q0."""
import json, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
W = '/home/user/work'
SPEC = {
 'ZLM-GK2018D-1':  dict(tag='GK2018D', q0=111, hdr=r'^\(一\)', label='(一)'),
 'ZLM-GK2019D-3':  dict(tag='GK2019D', q0=121, hdr=r'^\(三\)', label='(三)'),
 'ZLM-GK2021F-1':  dict(tag='GK2021F', q0=116, hdr=r'^\(材料1\)', label='(材料1)'),
 'ZLM-GK2013-4':   dict(tag='GK2013', q0=131, hdr=r'^\(四\)', label='(四)'),
 'ZLM-ZJ2023A-1':  dict(tag='ZJ2023A_xc', q0=111, hdr=r'^\(一\)', label='(一)'),
 'ZLM-GK2016F-5':  dict(tag='GK2016F', q0=131, hdr=r'^\(五\)', label='(五)'),
 'ZLM-GK2024F-3':  dict(tag='GK2024F', q0=126, hdr=r'^\(三\)', label='(三)'),
 'ZLM-ZJ2018A-2':  dict(tag='ZJ2018A', q0=126, hdr=r'^\(二\)', label='(二)'),
 'ZLM-ZJ2015A-1':  dict(tag='ZJ2015A', q0=111, hdr=r'^\(材料1\)', label='(材料1)'),
 'ZLM-SZ2023-2':   dict(tag='SZ2023_xc', q0=91, hdr=r'^\(二\)', label='(二)'),
 'ZLM-SD2024-2':   dict(tag='SD2024_xc', q0=106, hdr=r'^\(二\)', label='(二)'),
 'ZLM-GK2025D-1':  dict(tag='GK2025D', q0=111, hdr=r'^\(一\)', label='(一)'),
 'ZLM-GK2023D-4':  dict(tag='GK2023D', q0=121, hdr=r'^\(四\)', label='(四)'),
 'ZLM-GK2026F-4':  dict(tag='GK2026F_xc', q0=131, hdr=r'^\(四\)', label='(四)'),
}
def _q(tag):
    return {x['qno']: x for x in json.load(open(f'{W}/index/{tag}.json')) if x['kind'] == 'q'}
def locate(mid):
    s = SPEC[mid]
    if 'segs' in s: return s['segs']
    qs = _q(s['tag']); first = qs[s['q0']]; prev = qs.get(s['q0'] - 1)
    doc = pymupdf.open('/home/user/' + first['file'])
    if prev and prev['segs'][-1][0] <= first['segs'][0][0] and (first['segs'][0][0] - prev['segs'][0][0]) <= 3:
        ps, ys = prev['segs'][0][0], prev['segs'][0][1]
    else:
        ps, ys = max(0, first['segs'][0][0] - 1), 0
    pe, ye = first['segs'][0][0], first['segs'][0][1]
    hy = None
    for p in range(ps, pe + 1):
        for b in doc[p].get_text('dict')['blocks']:
            for li in b.get('lines', []):
                t = unicodedata.normalize('NFKC', ''.join(sp['text'] for sp in li['spans'])).strip()
                y = li['bbox'][1]
                if (p > ps or y >= ys - 2) and (p < pe or y < ye) and re.search(s['hdr'], t):
                    hy = (p, y - 3)      # keep the LAST matching header before the first question
    assert hy, (mid, 'header not found')
    segs = []
    for p in range(hy[0], pe + 1):
        y0 = hy[1] if p == hy[0] else 0
        y1 = ye - 1 if p == pe else doc[p].rect.height
        if y1 - y0 > 4: segs.append([p, round(y0, 1), round(y1, 1)])
    return segs
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from render2 import render_material
    for mid in SPEC:
        segs = locate(mid)
        f = _q(SPEC[mid]['tag'])[SPEC[mid]['q0']]['file']
        im, txt = render_material(f, segs, dpi=200)
        im.save(f'../r/mat_{mid}.png')
        print(mid, segs, im.size)
