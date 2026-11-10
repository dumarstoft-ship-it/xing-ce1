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
    m=re.search(r'第\s*%d\s*题'%q, full)
    if not m: print('=====',q,'NA'); continue
    n=re.search(r'第\s*%d\s*题'%(q+1), full[m.end():])
    s=full[m.start(): m.end()+(n.start() if n else 1800)]
    print('=====',q,'page',pg(m.start())); print(s[:1600])
