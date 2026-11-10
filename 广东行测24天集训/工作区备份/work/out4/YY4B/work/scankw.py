"""Crop a scanned analysis page around the OCR line containing a keyword (locator only; reading is by eye).
usage: scankw.py <tag> <page> <keyword> <out_name> [lines_before=1] [height_px=520]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scanq
from PIL import Image
def crop_kw(tag,page,kw,name,before=60,height=560):
    L=scanq.tsv(tag,page)
    hit=[l for l in L if kw in l['text']]
    if not hit: return None
    top=hit[0]['top']
    im=Image.open(f'{scanq.OCR}/{tag}_ans/p{page:03d}.png'); W,H=im.size
    box=(0,max(0,top-before),W,min(H,top-before+height))
    cv=im.crop(box); sc=1300/W; cv=cv.resize((1300,int(cv.height*sc)))
    out=f'{scanq.SP}/scan/{name}.png'; cv.convert('L').save(out,optimize=True); return out,hit[0]['text'][:40]
if __name__=='__main__':
    tag,page,kw,name=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
    before=int(sys.argv[5]) if len(sys.argv)>5 else 60
    height=int(sys.argv[6]) if len(sys.argv)>6 else 560
    print(crop_kw(tag,page,kw,name,before,height))
