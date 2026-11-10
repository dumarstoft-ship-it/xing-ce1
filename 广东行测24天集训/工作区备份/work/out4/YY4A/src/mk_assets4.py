# -*- coding: utf-8 -*-
"""Evidence crops for the 8 GD items (for checking only - they are NOT part of the questions and are not listed in
`assets`; the paths are recorded per question in `source_image`).
  assets/src/<paper>_q<no>.png        question region of the question paper, 200 dpi (the region of the index segment)
  assets/src/<paper>_q<no>_ans.png    the lines of the analysis that carry the reference answer (and 正确率 / 出处)
The analysis crops are cut by page fractions that were chosen by looking at the 110-dpi page renders.
Run: python3 mk_assets4.py"""
import json, os
import pymupdf
from PIL import Image

pymupdf.TOOLS.mupdf_display_errors(False)
OUT = '/home/user/work/out4/YY4A/assets/src'
IDX = '/home/user/work/index'
ROOT = '/home/user/'

# (paper, qno): [(analysis file key, page (1-based), y0 fraction, y1 fraction), ...]
A = {
 'A23X': 'xing-ce1/答案解析/2023年广东省公务员录用考试《行测》题（县级卷）答案解析.pdf',
 'A20X': 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',
 'A20Z': 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
 'A19X': 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
 'A19Z': 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（乡镇级）答案及解析.pdf',
 'A18': 'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
 'A17': 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
}
ANS = {
 ('GD2023X', 16): [('A23X', 5, 0.745, 0.94), ('A23X', 6, 0.06, 0.14)],
 ('GD2019X', 6): [('A19X', 1, 0.615, 0.775), ('A19Z', 1, 0.535, 0.665)],
 ('GD2017', 2): [('A17', 1, 0.175, 0.318)],
 ('GD2020X', 4): [('A20X', 1, 0.56, 0.785)],
 ('GD2018', 9): [('A18', 2, 0.345, 0.545)],
 ('GD2020Z', 1): [('A20Z', 1, 0.085, 0.30)],
 ('GD2018', 5): [('A18', 1, 0.695, 0.885)],
 ('GD2017', 5): [('A17', 1, 0.495, 0.668)],
}
EXTRA_Q = {('GD2023X', 16): [('GD2023X_xc', 16)], ('GD2019X', 6): [('GD2019Z', 5)]}   # other printings of the same item


def crop(path, page, y0, y1, dpi=200, absolute=False):
    doc = pymupdf.open(ROOT + path)
    pg = doc[page]
    r = pg.rect
    if absolute:
        clip = pymupdf.Rect(20, max(0, y0 - 2), r.width - 20, min(r.height, y1 + 2))
    else:
        clip = pymupdf.Rect(0, r.height * y0, r.width, r.height * y1)
    pix = pg.get_pixmap(clip=clip, dpi=dpi)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def stack(ims):
    W = max(i.width for i in ims); H = sum(i.height for i in ims)
    c = Image.new('RGB', (W, H), 'white'); y = 0
    for i in ims:
        c.paste(i, (0, y)); y += i.height
    return c


def q_region(tag, qno):
    for x in json.load(open(f'{IDX}/{tag}.json')):
        if x.get('kind') == 'q' and x['qno'] == qno:
            return stack([crop(x['file'], p, y0, y1, absolute=True) for p, y0, y1 in x['segs']])
    raise KeyError((tag, qno))


def main():
    os.makedirs(OUT, exist_ok=True)
    made = {}
    for (paper, qno), parts in ANS.items():
        names = []
        n = f'{paper}_q{qno}.png'; q_region(paper, qno).save(f'{OUT}/{n}'); names.append('assets/src/' + n)
        for tag, q2 in EXTRA_Q.get((paper, qno), []):
            n = f'{tag}_q{q2}.png'; q_region(tag, q2).save(f'{OUT}/{n}'); names.append('assets/src/' + n)
        n = f'{paper}_q{qno}_ans.png'
        stack([crop(A[k], p - 1, y0, y1) for k, p, y0, y1 in parts]).save(f'{OUT}/{n}'); names.append('assets/src/' + n)
        made[f'{paper}-{qno}'] = names
    json.dump(made, open(f'{OUT}/_index.json', 'w'), ensure_ascii=False, indent=1)
    for k, v in made.items():
        print(k, v)


if __name__ == '__main__':
    main()
