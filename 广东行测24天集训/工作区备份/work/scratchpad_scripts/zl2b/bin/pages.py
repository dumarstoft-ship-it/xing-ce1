import json,sys,re,unicodedata,pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
IDX='/home/user/work/index'
tag=sys.argv[1]
d=json.load(open(f'{IDX}/{tag}.json'))
f=d[0]['file']
doc=pymupdf.open('/home/user/'+f)
if len(sys.argv)>2:
    pages=[int(x) for x in sys.argv[2].split(',')] if ',' in sys.argv[2] or '-' not in sys.argv[2] else list(range(int(sys.argv[2].split('-')[0]),int(sys.argv[2].split('-')[1])+1))
else:
    zq=[x for x in d if x['kind']=='q' and x.get('section')=='资料']
    ps=sorted({s[0] for q in zq for s in q['segs']})
    pages=list(range(max(0,ps[0]-1),ps[-1]+1)) if ps else []
print(f, 'npages',len(doc), 'pages',pages)
for p in pages:
    t=unicodedata.normalize('NFKC',doc[p].get_text())
    print(f'######## page {p} (0-based) imgs={len(doc[p].get_images())}')
    print(t)
