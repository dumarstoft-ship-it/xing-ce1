import sys, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
files = {
'GD2017':'2017年广东公务员考试《行测》真题答案及解析.pdf',
'GD2018':'2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
'GD2019X':'2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
'GD2019Z':'2019年广东公务员考试《行测》真题（乡镇级）答案及解析.pdf',
'GD2020X':'2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',
'GD2020Z':'2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
'GD2021Z':'2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
'GD2021X':'2021年0314广东公务员考试《行测》真题（县级）参考答案及解析.pdf',
}
base='/home/user/xing-ce1/答案解析/'
out='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/r/'
# usage: render.py TAG PAGE(1-based) y0frac y1frac [zoom] [x0frac x1frac]
tag=sys.argv[1]; pg=int(sys.argv[2]); y0=float(sys.argv[3]); y1=float(sys.argv[4])
zoom=float(sys.argv[5]) if len(sys.argv)>5 else 2.0
x0=float(sys.argv[6]) if len(sys.argv)>6 else 0.0
x1=float(sys.argv[7]) if len(sys.argv)>7 else 1.0
doc=pymupdf.open(base+files[tag])
p=doc[pg-1]
r=p.rect
clip=pymupdf.Rect(r.x0+x0*r.width, r.y0+y0*r.height, r.x0+x1*r.width, r.y0+y1*r.height)
pix=p.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom), clip=clip)
fn=f"{out}{tag}_p{pg:03d}_{int(y0*100):02d}_{int(y1*100):02d}.png"
pix.save(fn)
print(fn, pix.width, pix.height)
