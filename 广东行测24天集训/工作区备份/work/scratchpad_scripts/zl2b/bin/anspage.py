import json,re,sys,unicodedata,pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
def find(tag, qnos):
    a=json.load(open(f'/home/user/work/answers/{tag}.json')); f=a['file']
    doc=pymupdf.open('/home/user/'+f)
    texts=[unicodedata.normalize('NFKC',p.get_text()) for p in doc]
    out={}
    for q in qnos:
        pats=[rf'【{q}】\s*解析', rf'(^|\n)\s*{q}\s*[\.、．]', rf'题目\s*{q}\s*解析', rf'(^|\n)\s*{q}\s*\n', rf'【例\s*{q}\s*】', rf'(^|\n)\s*第\s*{q}\s*题']
        hits=[]
        for i,t in enumerate(texts):
            for p in pats:
                for m in re.finditer(p,t):
                    hits.append((i,m.start()))
        out[q]=sorted(set(h[0] for h in hits))
    return f,len(doc),out
if __name__=='__main__':
    tag=sys.argv[1]; qs=[int(x) for x in sys.argv[2].split(',')]
    f,n,o=find(tag,qs); print(tag,f,n); 
    for q,v in o.items(): print('  ',q,[x+1 for x in v])
