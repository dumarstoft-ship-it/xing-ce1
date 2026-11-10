import json, re, sys, glob, os, unicodedata
IDX='/home/user/work/index'
def norm(s): return unicodedata.normalize('NFKC', s)
def split_opts(t):
    # find option markers A B C D
    t2=t
    pos={}
    for L in 'ABCD':
        ms=[m for m in re.finditer(r'(?<![A-Za-z])'+L+r'\s*[、\.．。:：]', t2)]
        if ms: pos[L]=ms[-1].start() if L!='A' else None
    # robust: find last 'A' marker such that B,C,D follow in order
    best=None
    for ma in re.finditer(r'(?<![A-Za-z])A\s*[、\.．:：]', t2):
        a=ma.start()
        mb=re.search(r'(?<![A-Za-z])B\s*[、\.．:：]', t2[a:]); 
        if not mb: continue
        b=a+mb.start()
        mc=re.search(r'(?<![A-Za-z])C\s*[、\.．:：]', t2[b:])
        if not mc: continue
        c=b+mc.start()
        md=re.search(r'(?<![A-Za-z])D\s*[、\.．:：]', t2[c:])
        if not md: continue
        d=c+md.start()
        best=(a,b,c,d)
    if not best: return t, None
    a,b,c,d=best
    def strip(s): return re.sub(r'^[A-D]\s*[、\.．:：]\s*','',s).strip()
    opts={'A':strip(t2[a:b]),'B':strip(t2[b:c]),'C':strip(t2[c:d]),'D':strip(t2[d:])}
    return t2[:a], opts
def classify(stem, opts):
    s=stem.replace('\n','').replace(' ','')
    if re.search(r'重新排列|语序|排序|排列顺序', s): return '排序'
    if opts is None: return '无选项'
    L=[len(re.sub(r'\s','',v)) for v in opts.values()]
    avg=sum(L)/4
    # blank markers in body (exclude last parenthesis of the question line)
    body=s
    blanks=len(re.findall(r'_{2,}|（\s*）|\(\s*\)|＿{2,}', stem.replace('\n','')))
    q_line = re.search(r'(这段文字|上述文字|文段|作者|以下|下列|对这段|最能|主要|意在|旨在|用意|标题|接下来|下文|后文|填入)[^。]*?[\(（]\s*[\)）]', s)
    if re.search(r'填入.{0,10}(句子|一句)|最恰当的一句|填入划线部分的句子|填入画线部分的句子', s): return '语句填空'
    if re.search(r'依次填入|填入.{0,6}(横线|划线|画线|括号)', s):
        return '选词填空' if avg<=14 else '语句填空?'
    if blanks>=2 or (blanks>=1 and not q_line):
        return '选词填空' if avg<=14 else '语句填空?'
    return '片段'
if __name__=='__main__':
    tags=sorted(os.path.basename(p)[:-5] for p in glob.glob(IDX+'/GD20*.json'))
    res=[]
    for tag in tags:
        d=json.load(open(f'{IDX}/{tag}.json'))
        for x in d:
            if x['kind']!='q': continue
            t=norm(x.get('text') or '')
            stem,opts=split_opts(t)
            c=classify(stem,opts)
            sec=x.get('section')
            if sec=='言语' or (sec is None):
                res.append(dict(tag=tag,qno=x['qno'],sec=sec,cls=c,stem=stem,opts=opts,file=x['file'],segs=x['segs'],nimg=len(x.get('images',[]))))
    json.dump(res,open(sys.argv[1],'w'),ensure_ascii=False)
    import collections
    for tag in tags:
        cc=collections.Counter(r['cls'] for r in res if r['tag']==tag)
        print(tag, dict(cc))
