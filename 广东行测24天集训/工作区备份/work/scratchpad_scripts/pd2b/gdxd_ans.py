import json,pymupdf,unicodedata,re,sys
pymupdf.TOOLS.mupdf_display_errors(False)
tag=sys.argv[1]; qs=[int(x) for x in sys.argv[2:]]
a=json.load(open(f'/home/user/work/answers/{tag}.json'))
d=pymupdf.open('/home/user/'+a['file'])
pages=[unicodedata.normalize('NFKC',p.get_text()) for p in d]
full='\n'.join(pages); starts=[];acc=0
for p in pages: starts.append(acc); acc+=len(p)+1
for q in qs:
    m=None
    for mm in re.finditer(r'(?:^|\n)\s*%d\s*[、\.．]'%q, full):
        if re.search(r'第一步|翻译|找出|分析|解析',full[mm.end():mm.end()+40]): m=mm;break
    if not m: print('=====',q,'NA'); continue
    n=re.search(r'\n\s*%d\s*[、\.．]'%(q+1), full[m.end():])
    s=full[m.start(): m.end()+(n.start() if n else 1500)]
    pg=max(i for i in range(len(starts)) if starts[i]<=m.start())+1
    s=re.sub(r'\n+','\n',s); s=re.sub(r'\n- \d+ -\n','\n',s)
    print('=====',tag,q,'page',pg); print(s[:1400])
