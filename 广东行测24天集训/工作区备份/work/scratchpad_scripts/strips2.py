import csv,glob,collections,sys,pymupdf,re
from PIL import Image, ImageDraw
pymupdf.TOOLS.mupdf_display_errors(False)
files = {
'GD2017':'2017年广东公务员考试《行测》真题答案及解析.pdf',
'GD2018':'2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
'GD2019X':'2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
'GD2019Z':'2019年广东公务员考试《行测》真题（乡镇级）答案及解析.pdf',
}
base='/home/user/xing-ce1/答案解析/'
tag=sys.argv[1]; zoom=float(sys.argv[2]) if len(sys.argv)>2 else 3.0
doc=pymupdf.open(base+files[tag])
strips=[]
for f in sorted(glob.glob(f'tsv/{tag}_p*.tsv')):
    pg=int(f.split('_p')[1][:3])
    rows=list(csv.DictReader(open(f),delimiter='\t',quoting=csv.QUOTE_NONE))
    H=int(rows[0]['height'])
    lines=collections.OrderedDict()
    for r in rows:
        if r['level']!='5': continue
        lines.setdefault((r['block_num'],r['par_num'],r['line_num']),[]).append(r)
    L=list(lines.values())
    for i,ws in enumerate(L):
        txt=''.join(w['text'] for w in ws)
        # answer line: short line containing 正确 / 答案 near start
        if not re.search(r'(正确|确答|答案|管案|答秦|答碌|答奈|答这|答款|答泰|答宗|答罕|管奈|管款|管泰|答认|答达|答康|答率|答过)', txt[:10]): continue
        top=min(int(w['top']) for w in ws); bot=max(int(w['top'])+int(w['height']) for w in ws)
        # include previous line for question-number context
        if i>0:
            pws=L[i-1]; ptop=min(int(w['top']) for w in pws)
            top2=max(ptop, top-120)
        else: top2=top
        p=doc[pg-1]; R=p.rect
        y0=(top2-6)/H*R.height; y1=(bot+8)/H*R.height
        clip=pymupdf.Rect(R.width*0.05, y0, R.width*0.95, y1)
        pix=p.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom), clip=clip)
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        strips.append((pg,im))
lab=50
Wt=max(im.width for _,im in strips)+lab
Ht=sum(im.height+6 for _,im in strips)
canvas=Image.new('RGB',(Wt,Ht),'white'); d=ImageDraw.Draw(canvas)
y=0
for pg,im in strips:
    d.text((5,y+im.height//3),f'p{pg}',fill=(255,0,0))
    canvas.paste(im,(lab,y)); y+=im.height+6
    d.line([(0,y-3),(Wt,y-3)],fill=(120,120,255))
out=f'r/{tag}_anslines.png'; canvas.save(out); print(out,canvas.size,len(strips))
