import json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from matspec import MATS
from render2 import render_material
IDX='/home/user/work/index'; ROOT='/home/user/work/out/zl_materials'
PAPER={'HB2023_xc':'HB2023','HB2025_xc':'HB2025','SC2020S_xc':'SC2020S','SD2025_xc':'SD2025','GD2022X_xc':'GD2022X'}
JUNK=re.compile(r'(本试卷由粉笔|认准淘宝|通关达人|公考,事业编|^\s*第\s*\d+\s*页|^\s*-\s*\d+\s*-\s*$|^\s*\d{1,2}\s*$|公务员录用考试《行测》题|网友回忆版\)\s*$)')
def build(mid, preview_dir=None, write=False):
    s=MATS[mid]; f=json.load(open(f"{IDX}/{s['tag']}.json"))[0]['file']
    im, txt = render_material(f, s['segs'], dpi=200)
    lines=[l for l in unicodedata.normalize('NFKC',txt).split('\n') if l.strip() and not JUNK.search(l)]
    text='\n'.join(lines)
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True); im.save(f'{preview_dir}/{mid}.png')
    if write:
        d=f'{ROOT}/{mid}'; os.makedirs(d, exist_ok=True); im.save(f'{d}/{mid}.png')
    return im, text, f
if __name__=='__main__':
    for mid in sys.argv[1:]:
        im,text,f=build(mid, preview_dir='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2b/matprev')
        print('=====',mid,im.size,f); print(text[:3000])
