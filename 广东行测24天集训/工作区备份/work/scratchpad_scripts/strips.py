import csv,glob,collections,sys,pymupdf
from PIL import Image, ImageDraw
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0,'.')
files = {
'GD2020X':'2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',
'GD2020Z':'2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
'GD2021Z':'2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
'GD2021X':'2021年0314广东公务员考试《行测》真题（县级）参考答案及解析.pdf',
}
base='/home/user/xing-ce1/答案解析/'
tag=sys.argv[1]; zoom=float(sys.argv[2]) if len(sys.argv)>2 else 3.5
doc=pymupdf.open(base+files[tag])
strips=[]
for f in sorted(glob.glob(f'tsv/{tag}_p*.tsv')):
    pg=int(f.split('_p')[1][:3])
    rows=list(csv.DictReader(open(f),delimiter='\t',quoting=csv.QUOTE_NONE))
    H=int(rows[0]['height']); W=int(rows[0]['width'])
    lines=collections.OrderedDict()
    for r in rows:
        if r['level']!='5': continue
        lines.setdefault((r['block_num'],r['par_num'],r['line_num']),[]).append(r)
    for k,ws in lines.items():
        txt=''.join(w['text'] for w in ws)
        if not ('确率' in txt or '错项' in txt or ('答案' in txt[:10] and '正' in txt[:8])): continue
        top=min(int(w['top']) for w in ws); bot=max(int(w['top'])+int(w['height']) for w in ws)
        p=doc[pg-1]; R=p.rect
        y0=(top-10)/H*R.height; y1=(bot+10)/H*R.height
        clip=pymupdf.Rect(R.width*0.05, y0, R.width*0.52, y1)
        pix=p.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom), clip=clip)
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        strips.append((pg,im))
lab=70
Wt=max(im.width for _,im in strips)+lab
Ht=sum(im.height+6 for _,im in strips)
canvas=Image.new('RGB',(Wt,Ht),'white'); d=ImageDraw.Draw(canvas)
y=0
for pg,im in strips:
    d.text((5,y+im.height//3),f'p{pg}',fill=(255,0,0))
    canvas.paste(im,(lab,y)); y+=im.height+6
    d.line([(0,y-3),(Wt,y-3)],fill=(200,200,255))
out=f'r/{tag}_headers.png'; canvas.save(out); print(out,canvas.size,len(strips))
