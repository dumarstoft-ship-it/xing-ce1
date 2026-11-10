import json, re, difflib, unicodedata
s=json.load(open('/home/user/work/review/source_by_key.json'))
idx=json.load(open('/home/user/work/review/gpt_index.json'))
book=json.load(open('/home/user/work/gpt/gpt_book_parsed.json'))
asg=json.load(open('/home/user/work/review/assign.json'))['R1']
def norm(t):
    t=unicodedata.normalize('NFKC',t or '')
    t=re.sub(r'^\s*\d+\s*','',t)               # leading question number
    t=t.replace('(单选题)','')
    t=re.sub(r'[\s　]','',t)
    t=re.sub(r'[,，。、;；:：!！?？“”"\'()（）\[\]【】]','',t)
    t=t.replace('~','—').replace('-','—').replace('－','—').replace('∶',':')
    return t
print('book keys sample:', list(book.items())[0][1].keys() if isinstance(book,dict) else type(book))
for i in asg:
    e=idx[i]; src=s[e['source_key']]; g=book[i]
    a=norm(src['stem']); b=norm(g['stem'])
    sm=difflib.SequenceMatcher(None,a,b)
    ops=[(op,a[i1:i2],b[j1:j2]) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal']
    so=[norm(v) for v in src['options'].values()]; go=[norm(v) for v in (g['options'].values() if isinstance(g['options'],dict) else g['options'])]
    same_set = sorted(so)==sorted(go); same_order = so==go
    print(f"\n## {i} [{e['kind']}] {e['source_key']} ratio={sm.ratio():.3f} opts_same_set={same_set} same_order={same_order}")
    if e['kind']!='改编' or sm.ratio()>0.8:
        for op in ops: print('   ',op)
    if not same_order: print('    src opts:',so,'\n    gpt opts:',go)
