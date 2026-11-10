import pymupdf, json, re, os, sys
pymupdf.TOOLS.mupdf_display_errors(False)
ANSD='/home/user/work/answers'
_cache={}
def load(tag):
    if tag in _cache: return _cache[tag]
    a=json.load(open(f'{ANSD}/{tag}.json')); doc=pymupdf.open('/home/user/'+a['file'])
    parts=[]; offs=[]; pos=0
    for i,pg in enumerate(doc):
        t=pg.get_text(); offs.append(pos); parts.append(t); pos+=len(t)+1
    T='\n'.join(parts)
    _cache[tag]=(a['file'],T,offs); return _cache[tag]
def page_of(offs,i):
    p=0
    for k,o in enumerate(offs):
        if o<=i: p=k
    return p+1
PATS=[lambda n: rf'【\s*{n}\s*】\s*解析', lambda n: rf'【解析\s*{n}\s*[—\-－]', lambda n: rf'第\s*{n}\s*题\s*\n\s*正确答案', lambda n: rf'(?m)^\s*{n}\s*[\.、．]\s*解析', lambda n: rf'(?m)^\s*{n}\s*[、\.．]\s*正确答案', lambda n: rf'(?m)^\s*{n}\s*$', lambda n: rf'(?m)^\s*{n}\s*[、\.．](?!\d)', lambda n: rf'(?m)^\s*【\s*{n}\s*】']
ANS=[r'故正确答案为\s*([A-D])', r'正确答案是[：:]\s*【\s*([A-D])\s*】', r'正确答案\s*([A-D])\s*】', r'因此[，,]?\s*选择\s*([A-D])\s*选项', r'正确答案[：:]\s*([A-D])', r'故本题答案为\s*([A-D])', r'答案为\s*([A-D])', r'【答案】\s*([A-D])', r'故选\s*([A-D])']
def seg(tag,n):
    f,T,offs=load(tag)
    for pi,P in enumerate(PATS):
        cands=[m for m in re.finditer(P(n),T)]
        nxt=[m.start() for m in re.finditer(P(n+1),T)]
        for m in cands:
            ends=[x for x in nxt if x>m.start()]
            end=min(ends) if ends else min(len(T), m.start()+4000)
            if end-m.start()>4000: end=m.start()+4000
            s=T[m.start():end]
            for A in ANS:
                a=re.search(A,s)
                if a: return dict(file=f, pat=pi, page=page_of(offs,m.start()), seg=s, ans=a.group(1))
    return None
def info(tag,n):
    r=seg(tag,n)
    if not r: return None
    s=r['seg']
    cc=re.search(r'(?:【文段出处】|文段出处[：:]|【文段来源】|文段来源[：:])[ \t]*\n?[ \t]*([^\n]+(?:\n(?!\s*\d{1,3}\s*$)(?!【)[^\n]{0,60}》[^\n]*)?)', s)
    rate=re.search(r'正确率[：:]?\s*(\d{1,3})\s*%', s); yc=re.search(r'易错项[：:]?\s*([A-D])', s)
    r.update(chuchu=re.sub(r'\s+','',cc.group(1)) if cc else None, rate=int(rate.group(1)) if rate else None, yicuo=yc.group(1) if yc else None)
    return r
if __name__=='__main__':
    for k in sys.argv[1:]:
        tag,n=k.rsplit('-',1); r=info(tag,int(n))
        if not r: print(k,'NOT FOUND'); continue
        print(k, 'pat',r['pat'],'p',r['page'],'ans',r['ans'],'rate',r['rate'],r['yicuo'],'|',r['chuchu'],'|',r['seg'][:60].replace('\n',' '))
