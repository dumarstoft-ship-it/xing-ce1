import json,re,sys,unicodedata,pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
def check(tag, qnos, nextq):
    a=json.load(open(f'/home/user/work/answers/{tag}.json')); f=a['file']
    doc=pymupdf.open('/home/user/'+f)
    pages=[unicodedata.normalize('NFKC',p.get_text()) for p in doc]
    full=''; offs=[]
    for i,t in enumerate(pages): offs.append(len(full)); full+=t+'\n'
    def page_of(pos):
        import bisect; return bisect.bisect_right(offs,pos)
    res={}
    for q in qnos:
        pats=[rf'【{q}】\s*解析', rf'题目\s*{q}\s*解析', rf'(^|\n)\s*{q}\s*[\.、．]?\s*\n?\s*(【|根据|第一步|定位|本题|结合|由)', rf'(^|\n)\s*{q}\s*[\.、．]']
        starts=[]
        for p in pats:
            starts+= [m.start() for m in re.finditer(p,full)]
        starts=sorted(set(starts))
        # choose the last start that is followed by "正确答案为" before next q's start
        best=None
        for s in starts:
            m=re.search(r'(正确答案[为是]\s*[:：]?\s*([A-D]))|(答案[为是:：]\s*([A-D]))',full[s:s+3000])
            if m: best=(s,m.group(2) or m.group(4), page_of(s)); 
        res[q]=best[1:] if best else None
    return f,res
if __name__=='__main__':
    for a in sys.argv[1:]:
        tag,qs=a.split(':'); qs=[int(x) for x in qs.split(',')]
        f,res=check(tag,qs,None)
        print(tag, f); print('   ', res)
