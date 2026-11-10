"""Locate question N in a scanned (no text layer) Guangdong analysis PDF and crop that region for eye-reading.
OCR (tesseract TSV on the 250dpi page PNGs in /home/user/work/ocr/<tag>_ans) is used ONLY to find where the item sits on the page;
the answer letter itself is read by the editor from the cropped image.
usage: scanq.py <tag> <qno> [<qno> ...]   -> writes scan/<tag>_q<N>.png and prints the path + OCR'd first line (locator only)"""
import os, re, sys, json, subprocess, csv, io
from PIL import Image
OCR='/home/user/work/ocr'
SP=os.path.dirname(os.path.abspath(__file__))
os.makedirs(f'{SP}/scan', exist_ok=True); os.makedirs(f'{SP}/tsv', exist_ok=True)
def tsv(tag, page):
    out=f'{SP}/tsv/{tag}_p{page:03d}'
    if not os.path.exists(out+'.tsv'):
        subprocess.run(['tesseract', f'{OCR}/{tag}_ans/p{page:03d}.png', out, '-l', 'chi_sim', '--psm', '6', 'tsv'], capture_output=True, timeout=900, env=dict(os.environ, OMP_THREAD_LIMIT='2'))
    lines={}
    for r in csv.DictReader(open(out+'.tsv', encoding='utf8'), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r['level']!='5' or not r['text'].strip(): continue
        key=(int(r['block_num']),int(r['par_num']),int(r['line_num']))
        l=lines.setdefault(key, dict(top=int(r['top']), left=int(r['left']), bottom=int(r['top'])+int(r['height']), text=''))
        l['top']=min(l['top'],int(r['top'])); l['bottom']=max(l['bottom'],int(r['top'])+int(r['height'])); l['left']=min(l['left'],int(r['left'])); l['text']+=r['text']
    return sorted(lines.values(), key=lambda l:l['top'])
def npages(tag): return json.load(open(f'{OCR}/{tag}_ans/_meta.json'))['pages']
def starts(tag):
    """all (page, top, qno, text) for lines that look like the start of item N"""
    res=[]
    for p in range(1, npages(tag)+1):
        L=tsv(tag,p)
        if not L: continue
        minleft=min(l['left'] for l in L)
        for l in L:
            m=re.match(r'^(\d{1,3})\s*[、,，.．。:：;]', l['text'])
            if m and l['left']<=minleft+60: res.append((p,l['top'],int(m.group(1)),l['text'][:40]))
    return res
_S={}
def locate(tag,q):
    if tag not in _S: _S[tag]=starts(tag)
    S=_S[tag]
    c=[x for x in S if x[2]==q]
    return c, S
def crop(tag,q,pad_top=25):
    c,S=locate(tag,q)
    if not c: return None
    # choose the candidate consistent with sequence (neighbors q-1/q+1 nearby)
    def score(x):
        i=S.index(x); near=[y[2] for y in S[max(0,i-3):i+4]]
        return sum(1 for d in (-2,-1,1,2) if q+d in near)
    c.sort(key=score, reverse=True); p,top,_,txt=c[0]
    i=S.index(c[0]); nxt=None
    for y in S[i+1:]:
        if y[2] in (q+1,q+2,q+3): nxt=y; break
    im=Image.open(f'{OCR}/{tag}_ans/p{p:03d}.png'); W,H=im.size
    parts=[]
    if nxt and nxt[0]==p: parts.append(im.crop((0,max(0,top-pad_top),W,min(H,nxt[1]+10))))
    else:
        parts.append(im.crop((0,max(0,top-pad_top),W,H-120)))
        if nxt and nxt[0]==p+1:
            im2=Image.open(f'{OCR}/{tag}_ans/p{p+1:03d}.png'); parts.append(im2.crop((0,120,W,min(H,nxt[1]+10))))
    Wm=max(x.width for x in parts); Hm=sum(x.height for x in parts)
    cv=Image.new('RGB',(Wm,Hm),'white'); y=0
    for x in parts: cv.paste(x,(0,y)); y+=x.height
    # downscale to ~1300px wide for reading
    sc=1300/Wm; cv=cv.resize((1300,int(Hm*sc)))
    out=f'{SP}/scan/{tag}_q{q}.png'; cv.convert('L').save(out, optimize=True)
    return out,p,txt,(nxt[0] if nxt else None)
if __name__=='__main__':
    tag=sys.argv[1]
    for q in sys.argv[2:]:
        r=crop(tag,int(q)); print(tag,q,r)
