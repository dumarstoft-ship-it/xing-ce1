"""Material regions (0-based page, y0, y1 in PDF points) for ZL3A's 22 materials. 'auto' entries are resolved by locate():
from the header line (regex) found after the end of question q0-1, down to the start of question q0."""
import json, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
W = '/home/user/work'
SPEC = {
 'ZLM-HB2022-1':  dict(tag='HB2022_xc', q0=111, hdr=r'^\(一\)', label='(一)'),
 'ZLM-GD2016Z-2': dict(tag='GD2016Z', q0=91, hdr=r'^\(二\)', label='(二)'),
 'ZLM-GK2016D-2': dict(tag='GK2016D', q0=116, hdr=r'^\(二\)', label='(二)'),
 'ZLM-SC2021H-3': dict(tag='SC2021H_xc', segs=[[15, 685.0, 800.0], [16, 40.0, 437.0]], label='(三)'),
 'ZLM-SC2023-1':  dict(tag='SC2023_xc', segs=[[23, 505.0, 685.0], [24, 72.0, 336.0]], label='材料（资料第1则，无序号）'),
 'ZLM-GK2024D-1': dict(tag='GK2024D', q0=111, hdr=r'^\(一\)', label='(一)'),
 'ZLM-GD2015X-3': dict(tag='GD2015X', segs=[[11, 692.0, 712.0], [12, 30.0, 249.0]], label='(三)'),
 'ZLM-SZ20201-3': dict(tag='SZ20201_xc', segs=[[12, 318.0, 580.0]], label='(材料3)'),
 'ZLM-GD2014Z-3': dict(tag='GD2014Z', segs=[[9, 443.0, 718.0]], label='(材料3)'),
 'ZLM-GK2015D-2': dict(tag='GK2015D', q0=116, hdr=r'^\(二\)', label='(二)'),
 'ZLM-SD2023-3':  dict(tag='SD2023_xc', q0=86, hdr=r'^\(三\)', label='(三)'),
 'ZLM-GD2014Z-2': dict(tag='GD2014Z', segs=[[8, 548.0, 841.9], [9, 30.0, 247.0]], label='(材料2)'),
 'ZLM-GK2014-4':  dict(tag='GK2014', q0=131, hdr=r'^四、根据以下资料', label='四、'),
 'ZLM-GK2015D-4': dict(tag='GK2015D', q0=126, hdr=r'^\(四\)', label='(四)'),
 'ZLM-ZJ2016A-3': dict(tag='ZJ2016A', segs=[[14, 433.0, 721.0]], label='(材料3)'),
 'ZLM-GK2015D-1': dict(tag='GK2015D', q0=111, hdr=r'^\(一\)', label='(一)'),
 'ZLM-JS2022A-4': dict(tag='JS2022A_xc', segs=[[22, 338.3, 841.0], [23, 0.0, 47.0]], label='（资料第4则，无序号）'),
 'ZLM-ZJ2019A-2': dict(tag='ZJ2019A', q0=121, hdr=r'^\(二\)', label='(二)'),
 'ZLM-SD2023-1':  dict(tag='SD2023_xc', q0=76, hdr=r'^\(一\)', label='(一)'),
 'ZLM-SZ20201-2': dict(tag='SZ20201_xc', segs=[[11, 370.0, 810.0]], label='(材料2)'),
 'ZLM-JS2021A-4': dict(tag='JS2021A_xc', segs=[[18, 142.0, 421.0]], label='（卷面误标“(材料3)”，按资料部分顺序为第4则）'),
 'ZLM-ZJ2019A-3': dict(tag='ZJ2019A', q0=126, hdr=r'^\(三\)', label='(三)'),
}
def _q(tag):
    return {x['qno']: x for x in json.load(open(f'{W}/index/{tag}.json')) if x['kind'] == 'q'}
def locate(mid):
    s = SPEC[mid]
    if 'segs' in s: return s['segs']
    qs = _q(s['tag']); first = qs[s['q0']]; prev = qs.get(s['q0'] - 1)
    doc = pymupdf.open('/home/user/' + first['file'])
    ps, ys = (prev['segs'][-1][0], prev['segs'][-1][2]) if prev else (first['segs'][0][0], 0)
    pe, ye = first['segs'][0][0], first['segs'][0][1]
    hy = None
    for p in range(ps, pe + 1):
        for b in doc[p].get_text('dict')['blocks']:
            for li in b.get('lines', []):
                t = unicodedata.normalize('NFKC', ''.join(sp['text'] for sp in li['spans'])).strip()
                y = li['bbox'][1]
                if (p > ps or y >= ys - 2) and (p < pe or y < ye) and re.search(s['hdr'], t):
                    if hy is None: hy = (p, y - 3)
    assert hy, (mid, 'header not found')
    segs = []
    for p in range(hy[0], pe + 1):
        y0 = hy[1] if p == hy[0] else 0
        y1 = ye - 1 if p == pe else doc[p].rect.height
        if y1 - y0 > 4: segs.append([p, round(y0, 1), round(y1, 1)])
    return segs
if __name__ == '__main__':
    for mid in SPEC:
        print(mid, locate(mid))
