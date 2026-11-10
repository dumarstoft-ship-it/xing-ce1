import json,pymupdf,unicodedata,re,sys
pymupdf.TOOLS.mupdf_display_errors(False)
tag=sys.argv[1]; anc=sys.argv[2]; n=int(sys.argv[3]) if len(sys.argv)>3 else 1600
a=json.load(open(f'/home/user/work/answers/{tag}.json'))
doc=pymupdf.open('/home/user/'+a['file'])
pages=[unicodedata.normalize('NFKC',p.get_text()) for p in doc]
full='\n'.join(pages)
starts=[];acc=0
for p in pages: starts.append(acc); acc+=len(p)+1
def pg(pos):
    for i in range(len(starts)-1,-1,-1):
        if pos>=starts[i]: return i+1
idx=[m.start() for m in re.finditer(re.escape(anc),full)]
print('#####',tag,anc,'hits',len(idx),'file',a['file'].split('/')[-1])
for i in idx[:2]:
    s=full[max(0,i-200):i+n]; s=re.sub(r'\n+','\n',s)
    print('--- page',pg(i)); print(s)
