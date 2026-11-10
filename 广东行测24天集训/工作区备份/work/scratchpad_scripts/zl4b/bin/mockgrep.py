"""grep 粉笔模考卷资料分析文本: mockgrep.py <regex> [ctx]  -> prints paper short name + question number + stem"""
import json, re, sys
S='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad'
d=json.load(open(S+'/zl3b/mock/mock_zl.json'))
pat=re.compile(sys.argv[1]); ctx=int(sys.argv[2]) if len(sys.argv)>2 else 0
for k,v in d.items():
    t=v['zl']
    t=re.sub(r'· 本试卷由粉笔用户.*?生成\n第 \d+ 页,共 \d+ 页\n.*?\n','',t)
    name=re.sub(r'行测模考大赛|\.pdf','',k)
    # questions: stem lines precede "NNN.\n A."
    for m in re.finditer(r'\n(1[1-3]\d)\.\n', t):
        qno=m.group(1)
        # stem = text after previous option D line (or start) up to m.start()
        prev=t[:m.start()]
        i=max(prev.rfind('\nD.'), prev.rfind('\n(') )
        j=prev.find('\n', i+1)
        stem=prev[j+1:] if i>=0 else prev[-200:]
        e=t.find('\n1', m.end()+1)
        opts=t[m.end(): m.end()+ (400 if ctx else 0)]
        body=stem.replace('\n','')
        if pat.search(body) or (ctx and pat.search(opts.split('\n(')[0][:300])):
            print(f'[{name} #{qno}] {body[-260:]}')
            if ctx: print('    ', ' | '.join(opts.split('\n')[:9])[:400])
