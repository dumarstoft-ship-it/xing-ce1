import json,re,unicodedata
IDX='/home/user/work/index'
JUNK=re.compile(r'(·\s*本试卷由粉笔.*|本试卷由粉笔用户\S*生成|\d{4}年\S*省\S*公务员录用考试《行测》题\S*|【认准淘宝店铺.*|^\s*第\s*\d+\s*页.*$)')
def norm(s):
    s=unicodedata.normalize('NFKC',s)
    s=re.sub(r'(?<=[一-鿿%）)])\s+(?=[一-鿿0-9（(A-Za-z])','',s)
    s=re.sub(r'(?<=[0-9A-Za-z.%])\s+(?=[一-鿿])','',s)
    s=re.sub(r'(?<=[一-鿿])\s+(?=[0-9])','',s)
    s=s.replace('(','（').replace(')','）')
    s=re.sub(r'（\s*）','（    ）',s)
    s=s.replace(',','，').replace(':','：').replace('?','？').replace(';','；')
    return s.strip()
def parse(tag,qno):
    d=json.load(open(f'{IDX}/{tag}.json'))
    q=[x for x in d if x['kind']=='q' and int(x['qno'])==qno][0]
    t='\n'.join(l for l in q['text'].split('\n') if not JUNK.search(l))
    t=JUNK.sub('',t)
    t=re.sub(r'^\s*'+str(qno)+r'\s*[\.、．]?\s*','',t.strip())
    # split options
    m=list(re.finditer(r'(?:(?<=\s)|^|(?<=[。）)\]]))([A-D])\s*[\.、．]\s*',t))
    # choose last occurrences of A,B,C,D in order
    pos={}
    for mm in m:
        L=mm.group(1)
        pos.setdefault(L,[]).append(mm)
    # find sequence A<B<C<D using last A that precedes a B...
    seq=None
    for a in pos.get('A',[]):
        b=[x for x in pos.get('B',[]) if x.start()>a.start()]
        if not b: continue
        b=b[0]; c=[x for x in pos.get('C',[]) if x.start()>b.start()]
        if not c: continue
        c=c[0]; dd=[x for x in pos.get('D',[]) if x.start()>c.start()]
        if not dd: continue
        seq=(a,b,c,dd[0])
    if not seq: return norm(t), None, q
    a,b,c,dd=seq
    stem=t[:a.start()]
    opts={'A':t[a.end():b.start()],'B':t[b.end():c.start()],'C':t[c.end():dd.start()],'D':t[dd.end():]}
    return norm(stem), {k:norm(v) for k,v in opts.items()}, q
if __name__=='__main__':
    import sys
    for a in sys.argv[1:]:
        tag,qs=a.split(':')
        for qn in qs.split(','):
            s,o,q=parse(tag,int(qn))
            print(f'[{tag}-{qn}] p{q["segs"][0][0]+1} {s}'); print('    ',o)
