import json, re, sys
M=json.load(open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3b/meta.json'))
FW={',':'，',';':'；',':':'：','?':'？','!':'！','(':'（',')':'）'}
def norm(s):
    s=s.replace('　',' ')
    # half->full punctuation (not inside numbers like 0.5)
    out=[]
    for i,ch in enumerate(s):
        if ch in FW:
            out.append(FW[ch])
        else: out.append(ch)
    s=''.join(out)
    # remove spaces between CJK and digits/latin, and among CJK
    s=re.sub(r'(?<=[一-鿿，。；：？！（）“”、])\s+(?=[一-鿿0-9A-Za-z，。；：？！（）“”、%])','',s)
    s=re.sub(r'(?<=[0-9A-Za-z%])\s+(?=[一-鿿，。；：？！（）“”、])','',s)
    s=re.sub(r'[ \t]+',' ',s).strip()
    return s
def parse(text):
    t=text
    t=re.sub(r'^\s*\d+\s*[\.、．]?\s*','',t)  # leading qno
    # find options
    m=re.search(r'(?:^|\n|\s)A\s*[\.、．]',t)
    stem=t[:m.start()] if m else t
    opts={}
    if m:
        rest=t[m.start():]
        parts=re.split(r'(?:^|\n|\s)([A-D])\s*[\.、．]',rest)
        # parts: ['', 'A', text, 'B', text...]
        for i in range(1,len(parts)-1,2):
            opts[parts[i]]=parts[i+1]
    stem=stem.strip()
    # join lines: keep a newline before the question prompt (last sentence)
    lines=[l.strip() for l in stem.split('\n') if l.strip()]
    s=''.join(lines)
    s=norm(s)
    # split prompt
    pm=re.search(r'(以下|下列|如果以下|若以下|补充以下|上述|要使|要得出|这项|由此)[^。]*?(是|？|\?|：|:|（\s*）|\(\s*\))\s*(（\s*）)?\s*$',s)
    o={k:norm(' '.join(x.split())) for k,x in opts.items()}
    return s,o
for k,v in M.items():
    if 'text' not in v: continue
    s,o=parse(v['text'])
    print('=====',k); print(s)
    for kk in 'ABCD': print(kk,':',o.get(kk))
