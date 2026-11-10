import pymupdf, re, json, os, sys, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0,'/home/user/work/tools')
QMARK = re.compile(r'(?:^|\n)\s*(?:第\s*(\d{1,3})\s*题|【\s*(?:解析\s*)?(\d{1,3})\s*(?:[—\-－]|】)|题目\s*(\d{1,3})|(\d{1,3})\s*[、\.．](?!\d)|(\d{1,3})[ \t]*\n(?!\s*\d))')
def segs(path):
    doc = pymupdf.open(path)
    pages=[unicodedata.normalize('NFKC', p.get_text()) for p in doc]
    offs=[];o=0
    for p in pages: offs.append(o); o+=len(p)+1
    t='\n'.join(pages)
    t2 = t  # keep offsets
    marks=[]
    for m in QMARK.finditer(t2):
        n=int(next(g for g in m.groups() if g)); marks.append((m.start(),n))
    seq,last=[],0
    for pos,n in marks:
        if last<n<=last+3: seq.append((pos,n)); last=n
    res={}
    import bisect
    for i,(pos,n) in enumerate(seq):
        end=seq[i+1][0] if i+1<len(seq) else len(t2)
        pg=bisect.bisect_right(offs,pos)  # 1-based page
        res[n]=dict(text=re.sub(r'[ \t]+',' ',t2[pos:end]), page=pg)
    return res
if __name__=='__main__':
    out={}
    for f in sorted(os.listdir('/home/user/work/answers')):
        tag=f[:-5]
        a=json.load(open('/home/user/work/answers/'+f))
        try:
            s=segs('/home/user/'+a['file'])
        except Exception as e:
            print('ERR',tag,e); continue
        out[tag]={'file':a['file'],'segs':{str(k):v for k,v in s.items()}}
    json.dump(out,open('anaseg.json','w'),ensure_ascii=False)
    print(len(out))
