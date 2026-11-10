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
    ms=[m for m in re.finditer(r'(^|\n)\s*%d\s*[\.、．]'%q, full)]
    if not ms: print('=====',q,'NA'); continue
    # choose the match followed by 解析 or 正确答案 soonest
    best=None
    for m in ms:
        w=full[m.end():m.end()+80]
        if re.search(r'解析|答案|正确|第一步|【',w): best=m;break
    m=best or ms[-1]
    n=re.search(r'\n\s*%d\s*[\.、．]'%(q+1), full[m.end():])
    s=full[m.start(): m.end()+(n.start() if n else 1800)]
    print('=====',q,'page',pg(m.start()),'file',a['file']); print(s[:1800])
