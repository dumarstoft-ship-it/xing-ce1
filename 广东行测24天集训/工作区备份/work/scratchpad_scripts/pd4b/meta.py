import json, sys, os, re, unicodedata
sys.path.insert(0,'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd4b')
from ans_lib import load, ansfile
W='/home/user/work'
FW={',':'，',';':'；',':':'：','?':'？','!':'！','(':'（',')':'）'}
def norm(s):
    s=s.replace('　',' ')
    s=''.join(FW.get(ch,ch) for ch in s)
    s=re.sub(r'(?<=[一-鿿，。；：？！（）“”、《》])\s+(?=[一-鿿0-9A-Za-z，。；：？！（）“”、%《》])','',s)
    s=re.sub(r'(?<=[0-9A-Za-z%])\s+(?=[一-鿿，。；：？！（）“”、《》])','',s)
    s=re.sub(r'[ \t]+',' ',s).strip()
    return s
def parse(text):
    t=text
    t=re.sub(r'^\s*\d+\s*[\.、．]?\s*','',t)
    t=re.sub(r'^（单选题）','',t.strip()); t=re.sub(r'^\(单选题\)','',t)
    m=re.search(r'(?:^|\n|\s)A\s*[\.、．]',t)
    stem=t[:m.start()] if m else t
    opts={}
    if m:
        rest=t[m.start():]
        parts=re.split(r'(?:^|\n|\s)([A-D])\s*[\.、．]',rest)
        for i in range(1,len(parts)-1,2):
            opts[parts[i]]=norm(''.join(x.strip() for x in parts[i+1].split('\n')))
    lines=[l.strip() for l in stem.strip().split('\n') if l.strip()]
    s=norm(''.join(lines))
    return s,opts
def pats(q):
    return [r'【\s*题目\s*%d\s*】'%q, r'【解析\s*%d\s*[—\-–]'%q, r'题目\s*%d\s*解析'%q, r'【\s*%d\s*】'%q, r'(?:^|\n)\s*第\s*%d\s*题'%q,
            r'(?:^|\n)\s*%d\s*[\.、．:：]\s*(?:正确答案|【答案】|答案|解析|第一步|\n)'%q,
            r'(?:^|\n)\s*%d\s*(?:\n|\s)\s*(?:正确答案|【答案】|答案|解析|第一步)'%q,
            r'(?:^|\n)\s*%d\s*[\.、．:：]'%q]
out={}
keys=[l.strip() for f in sys.argv[2:] for l in open(f) if l.strip()]
for key in keys:
    pid,q=key.rsplit('-',1); q=int(q)
    info={'key':key}
    tags=[t for t in (pid,pid+'_xc') if os.path.exists(f'{W}/index/{t}.json')]
    vers={}
    for t in tags:
        for x in json.load(open(f'{W}/index/{t}.json')):
            if x.get('kind')=='q' and x['qno']==q:
                s,o=parse(x['text'])
                vers[t]=dict(file=x['file'],pages=sorted(set(sg[0]+1 for sg in x['segs'])),stem=s,options=o,raw=x['text'],images=x.get('images'))
    info['versions']=vers
    f=ansfile(pid); info['ans_file']=f
    ap=None
    if f:
        _,full,offs=load(pid)
        if full and len(full)>2000:
            for p in pats(q):
                for m in re.finditer(p,full):
                    seg=full[m.start():m.start()+500]
                    if re.search(r'答案|解析|正确|第一步|论点|题干|排除|当选',seg):
                        ap=max(i for i,o in enumerate(offs) if o<=m.start())+1; break
                if ap: break
    info['ans_page_auto']=ap
    out[key]=info
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
for k,v in out.items():
    print(k, list(v['versions'].keys()), [vv['pages'] for vv in v['versions'].values()], (v['ans_file'] or '')[-28:], v['ans_page_auto'])
