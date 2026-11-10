import pymupdf,unicodedata,re,sys,json
pymupdf.TOOLS.mupdf_display_errors(False)
tag=sys.argv[1]; pat=sys.argv[2]; n=int(sys.argv[3]) if len(sys.argv)>3 else 1500
a=json.load(open(f'/home/user/work/answers/{tag}.json'))
d=pymupdf.open('/home/user/'+a['file'])
pages=[unicodedata.normalize('NFKC',p.get_text()) for p in d]
t='\n'.join(pages)
offs=[];o=0
for p in pages: offs.append(o); o+=len(p)+1
import bisect
for m in re.finditer(pat,t):
    pg=bisect.bisect_right(offs,m.start())-1
    print(f'----- pos {m.start()} page {pg+1}/{len(pages)}'); print(t[max(0,m.start()-100):m.start()+n])
