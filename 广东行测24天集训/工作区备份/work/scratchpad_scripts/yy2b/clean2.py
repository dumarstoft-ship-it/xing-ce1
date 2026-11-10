import re, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yy2b')
from qx import get, raw, crop
CIRC='①②③④⑤⑥⑦⑧'
JUNK=[r'【认准淘宝店铺[^】]*】[^\n]*', r'TB[：:][^\n]*', r'·?\s*本试卷由粉笔用户[^\n]*?生成', r'免费获取更多考公资料[^\n]*',
      r'20\d\d\s*年?\s*国家公务员录用考试《行测》[^\n]*', r'20\d\d\s*年?国家公务员考试《行测》[^\n]*', r'20\d\d年[^\n]{0,8}省公务员录用考试《行测》[^\n]*', r'20\d\d年广东省公务员录用考试《行测》[^\n]*',
      r'\d{4}\s*江苏省公务员《行测》[^\n]*', r'第\s*\d+\s*页[，,]?\s*共\s*\d+\s*页', r'(?m)^\s*-\s*\d+\s*-\s*$', r'(?m)^\s*\d{1,3}\s*/\s*\d{1,3}\s*$', r'(?m)^\s*\d{1,3}\s*$',
      r'[（(]单选题[)）]']
def dejunk(t):
    for j in JUNK: t=re.sub(j,'',t)
    return t.replace('　',' ').replace('\xa0',' ')
def norm_text(s):
    s = re.sub(r'(?<=[0-9A-Za-z%])[ \t]+(?=[一-鿿“”（）《》])', '', s)
    s = re.sub(r'(?<=[一-鿿，。、”“：；（）《》])[ \t]+(?=[0-9A-Za-z])', '', s)
    s = re.sub(r'(?<=[一-鿿，。、”“：；])[ \t]+(?=[一-鿿，。、”“：；])', '', s)
    s = re.sub(r'[（(]\s*[）)]', '（    ）', s)
    s = s.replace('······', '……').replace('......', '……').replace('···', '…')
    return s.strip()
def find_opts(t):
    pos=[]
    for L in 'ABCD':
        pos.append(list(re.finditer(r'(?:(?<=\n)|(?<=\s)|(?<=^)|(?<=[。：:？?]))' + L + r'\s*[、\.．]\s*', t)))
    best=None
    for a in pos[0]:
        b=next((x for x in pos[1] if x.start()>a.start()),None)
        if not b: continue
        c=next((x for x in pos[2] if x.start()>b.start()),None)
        if not c: continue
        d=next((x for x in pos[3] if x.start()>c.start()),None)
        if not d: continue
        best=(a,b,c,d)
    return best
def j(s):
    s=re.sub(r'\s*\n\s*','',s.strip()); s=re.sub(r'[ \t]{2,}',' ',s); return norm_text(s.strip())
PROMPT=re.compile(r'(这段文字|这段话|上述文段|以上文段|本段文字|对这段|对上述|对于这段|根据这段|作者|下列|以下|与这段|最适合|最能|这是一篇|关于|将以上|这段|上述|本段)')
def clean_pd(t):
    t=dejunk(t)
    t=re.sub(r'^\s*\d{1,3}\s*[、\.．]?\s*', '', t.strip())
    best=find_opts(t)
    a,b,c,d=best
    body=t[:a.start()]
    opts={'A':j(t[a.end():b.start()]),'B':j(t[b.end():c.start()]),'C':j(t[c.end():d.start()]),'D':j(t[d.end():])}
    lines=[l.strip() for l in body.strip().split('\n') if l.strip()]
    k=None
    for i in range(len(lines)-1,-1,-1):
        if PROMPT.match(lines[i]): k=i; break
    if k is None: k=len(lines)-1
    passage=''.join(lines[:k]); prompt=''.join(lines[k:])
    return norm_text(passage)+'\n'+norm_text(prompt), opts
def clean_px(t):
    t=dejunk(t)
    t=re.sub(r'^\s*\d{1,3}\s*[、\.．]?\s*(?=[①-⑧])', '', t.strip())
    t=re.sub(r'^\s*\d{1,3}\s*[、\.．]\s*', '', t)
    om=list(re.finditer(r'([A-D])\s*[\.．、]\s*([①-⑧]{4,8})', t))
    opts={m.group(1):m.group(2) for m in om}
    body=t[:om[0].start()]
    pm=re.search(r'(将以上[^\n]*?(?:是|为)[^\n]*)', body)
    prompt=re.sub(r'\s+','',pm.group(1)) if pm else ''
    lead=body[:body.find('①')]
    body2=body.replace(pm.group(1),'') if pm else body
    chunks=[c for c in re.split(r'(?=[①-⑧])', body2) if c.strip() and c.strip()[0] in CIRC]
    sents=[norm_text(re.sub(r'\s+','',c)) for c in chunks]
    return sents, norm_text(prompt), norm_text(re.sub(r'\s+','',lead)), opts
if __name__=='__main__':
    for key in sys.argv[1:]:
        tag,q=key.rsplit('-',1); qq=get(tag,int(q)); r=raw(qq)
        print('=====',key)
        if '重新排' in r:
            s,p,lead,o=clean_px(r); print('LEAD:',lead); print('\n'.join(s)); print(p); print(o)
        else:
            st,o=clean_pd(r); print(st); print(json.dumps(o,ensure_ascii=False))
