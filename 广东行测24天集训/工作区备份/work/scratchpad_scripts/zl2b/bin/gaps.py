import json,sys,re,unicodedata,pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
IDX='/home/user/work/index'
def gaps(tag, show=False, maxc=400):
    d=json.load(open(f'{IDX}/{tag}.json'))
    f=d[0]['file']; doc=pymupdf.open('/home/user/'+f)
    qs=sorted([x for x in d if x['kind']=='q'], key=lambda x:int(x['qno']))
    zq=[x for x in qs if x.get('section')=='资料']
    if not zq: return []
    first=int(zq[0]['qno'])
    allq={int(x['qno']):x for x in qs}
    out=[]
    for q in zq:
        n=int(q['qno']); prev=allq.get(n-1)
        if not prev: continue
        (p1,_,y1)=prev['segs'][-1]; (p2,y2,_)=q['segs'][0]
        txt=''; nimg=0
        for p in range(p1,p2+1):
            pg=doc[p]; H=pg.rect.height
            a=y1 if p==p1 else 0; b=y2 if p==p2 else H
            if b-a<5: continue
            clip=pymupdf.Rect(0,a,pg.rect.width,b)
            txt+=unicodedata.normalize('NFKC',pg.get_text(clip=clip))
            nimg+=sum(1 for im in pg.get_image_info() if im['bbox'][1]<b and im['bbox'][3]>a and (im['bbox'][3]-im['bbox'][1])>30)
        t=re.sub(r'\s+','',txt)
        if len(t)>60 or nimg>0:
            out.append((n,len(t),nimg,(p1,y1,p2,y2),txt))
    return out
if __name__=='__main__':
    for tag in sys.argv[1:]:
        if tag.startswith('-'): continue
        for n,L,ni,pos,txt in gaps(tag):
            print(f'{tag} before Q{n}: len={L} img={ni} pos={tuple(round(x) for x in pos)} :: {re.sub(chr(10)," ",txt)[:160]}')
