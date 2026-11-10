import json,pymupdf,unicodedata,re,sys
pymupdf.TOOLS.mupdf_display_errors(False)
tag=sys.argv[1]; qs=[int(x) for x in sys.argv[2:]]
a=json.load(open(f'/home/user/work/answers/{tag}.json'))
doc=pymupdf.open('/home/user/'+a['file'])
pages=[unicodedata.normalize('NFKC',p.get_text()) for p in doc]
full='\n'.join(pages)
starts=[];acc=0
for p in pages: starts.append(acc); acc+=len(p)+1
def pg(pos):
    for i in range(len(starts)-1,-1,-1):
        if pos>=starts[i]: return i+1
for q in qs:
    pats=[r'第\s*%d\s*题'%q, r'(?:^|\n)\s*%d\s*[\.、．]\s*(?:【|正确答案|答案|解析|\n)'%q, r'(?:^|\n)\s*%d\s*[\.、．]'%q]
    m=None
    for p in pats:
        ms=list(re.finditer(p, full))
        # choose match whose following 300 chars contain 正确答案/答案/解析
        for mm in ms:
            if re.search(r'正确答案|【答案】|答案|解析|故本题|故正确',full[mm.end():mm.end()+400]):
                m=mm;break
        if m: break
    if not m: print('=====',q,'NA'); continue
    nxt=None
    for p in [r'第\s*%d\s*题'%(q+1), r'(?:^|\n)\s*%d\s*[\.、．]'%(q+1)]:
        n=re.search(p, full[m.end():])
        if n: nxt=n; break
    s=full[m.start(): m.end()+(nxt.start() if nxt else 2000)]
    s=re.sub(r'\n+','\n',s)
    print('=====',tag,q,'page',pg(m.start())); print(s[:1700])
