import pymupdf, unicodedata, re, sys, json
pymupdf.TOOLS.mupdf_display_errors(False)
def load(f):
    doc=pymupdf.open('/home/user/'+f)
    pages=[unicodedata.normalize('NFKC', p.get_text()) for p in doc]
    return pages
def find(f, n, nxt=None, maxlen=2500):
    pages=load(f)
    full=''; starts=[]
    for i,t in enumerate(pages):
        starts.append(len(full)); full+=t+'\n'
    pats=[rf'【解析\s*{n}\s*[—\-－]', rf'题目\s*{n}\s*解析', rf'(?m)^\s*{n}\s*[\.．、]', rf'第\s*{n}\s*题']
    for pat in pats:
        ms=list(re.finditer(pat, full))
        if ms:
            m=ms[0]
            # page
            pg=max(i for i,s in enumerate(starts) if s<=m.start())+1
            end=len(full)
            if nxt:
                for pat2 in [rf'【解析\s*{nxt}\s*[—\-－]', rf'题目\s*{nxt}\s*解析', rf'(?m)^\s*{nxt}\s*[\.．、]', rf'第\s*{nxt}\s*题']:
                    m2=re.search(pat2, full[m.end():])
                    if m2: end=m.end()+m2.start(); break
            seg=full[m.start():min(end, m.start()+maxlen)]
            ans=re.findall(r'(?:正确答案为|正确答案|故本题选|故选|答案为|选择)\s*([A-D]+)', seg)
            return pg, seg, ans
    return None, None, None
if __name__=='__main__':
    f=sys.argv[1]; 
    for n in sys.argv[2:]:
        n=int(n)
        pg,seg,ans=find(f,n,n+1)
        print(f'##### Q{n} page={pg} ans={ans}')
        print(seg)
