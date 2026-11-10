import pymupdf, json, sys
pymupdf.TOOLS.mupdf_display_errors(False)
W='/home/user/work'
def raw(tag, qno):
    for q in json.load(open(f'{W}/index/{tag}.json')):
        if q['kind']=='q' and q['qno']==qno:
            d=pymupdf.open('/home/user/'+q['file']); out=[]
            for p,y0,y1 in q['segs']:
                pg=d[p]; out.append(pg.get_text('text',clip=pymupdf.Rect(0,y0-1,pg.rect.width,y1+1)))
            return q['file'], [s[0]+1 for s in q['segs']], ''.join(out)
if __name__=='__main__':
    for a in sys.argv[1:]:
        tag,q=a.rsplit(':',1); f,pages,t=raw(tag,int(q))
        print(f'##### {tag}:{q} pages={pages} file={f}\n{t}')
