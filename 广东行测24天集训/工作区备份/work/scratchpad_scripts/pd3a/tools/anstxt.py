"""print analysis text for questions: anstxt.py TAG Q [Q...]  (text-layer analysis PDFs)"""
import sys, json, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
tag=sys.argv[1]
a=json.load(open(f'/home/user/work/answers/{tag}.json'))
doc=pymupdf.open('/home/user/'+a['file'])
pages=[unicodedata.normalize('NFKC',pg.get_text()) for pg in doc]
t='\n'.join(pages)
offs=[];o=0
for p in pages: offs.append(o); o+=len(p)+1
def page_of(i):
    k=0
    for j,s in enumerate(offs):
        if s<=i: k=j
    return k+1
for q in sys.argv[2:]:
    q=int(q)
    ms=[m for m in re.finditer(r'(?m)^\s*%d\s*[\.、．]'%q, t)] or [m for m in re.finditer(r'第\s*%d\s*题'%q, t)] or [m for m in re.finditer(r'【%d】\s*解析'%q, t)] or [m for m in re.finditer(r'(?m)^\s*%d\s*$'%q, t)]
    if not ms: print('==',q,'not found'); continue
    # choose the match followed by 答案/解析 within 400 chars, else last
    best=None
    for m in ms:
        seg=t[m.start():m.start()+400]
        if re.search(r'答案|解析|【', seg): best=m
    m=best or ms[-1]
    nx=re.search(r'(?m)^\s*%d\s*[\.、．]'%(q+1), t[m.end():]) or re.search(r'第\s*%d\s*题'%(q+1), t[m.end():]) or re.search(r'【%d】\s*解析'%(q+1), t[m.end():]) or re.search(r'(?m)^\s*%d\s*$'%(q+1), t[m.end():])
    end=m.end()+(nx.start() if nx else 1500)
    print('== %s-%d (page %d)'%(tag,q,page_of(m.start())))
    print(t[m.start():min(end,m.start()+1500)].strip())
