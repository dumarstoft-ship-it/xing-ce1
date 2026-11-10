import pymupdf, sys, json
pymupdf.TOOLS.mupdf_display_errors(False)
# usage: findy.py <tag> <page0> <anchor> [anchor2 ...]
tag=sys.argv[1]; p=int(sys.argv[2])
f=json.load(open(f'/home/user/work/index/{tag}.json'))[0]['file']
doc=pymupdf.open('/home/user/'+f)
pg=doc[p]
print(f, 'page', p, 'h=', pg.rect.height)
for a in sys.argv[3:]:
    r=pg.search_for(a)
    print(repr(a), [(round(x.y0,1), round(x.y1,1)) for x in r])
