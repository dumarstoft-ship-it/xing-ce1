# Build the proposed whitespace-only fixes for M05 Q51-65 on in-memory copies (repo untouched) and verify that
# every change is whitespace-only. Writes proposed_fixes.json (full corrected text blocks) next to this script.
import json, re, copy
REPO='/home/user/xing-ce1'
rows={}
for l in open(f'{REPO}/广东行测18套模拟/M05/题目.jsonl',encoding='utf-8'):
    r=json.loads(l); rows[r['number']]=r
SPLIT={52:'要使上述观点成立',55:'要使上述推理成立',57:'下列选项最能指出',59:'下列选项如果为真',61:'下列选项的逻辑结构',63:'中标结果出来后发现'}
SOFT={56:['白玉\n隧道'],60:['交替领\n先','张\n全猜错了'],64:['成\n为','心仪\n的商品','追\n捧'],65:['人类\n的灭绝','人群\n的过程']}
DIGIT_CJK=re.compile(r'(?<=[0-9])[ ]+(?=[一-鿿])|(?<=[一-鿿])[ ]+(?=[0-9])')
out={}
def fix_text(n,where,t):
    new=t
    if n in SPLIT and where=='题干':
        mk=SPLIT[n]; assert ('\n'+mk) not in new and mk in new; new=new.replace(mk,'\n'+mk,1)
    for s in SOFT.get(n,[]):
        if s in new: new=new.replace(s,s.replace('\n',''))
    new=DIGIT_CJK.sub('',new)
    return new
for n in range(51,66):
    r=rows[n]; changes=[]
    for i,b in enumerate(r['stem']):
        if b['type']=='text':
            nt=fix_text(n,'题干',b['text'])
            if nt!=b['text']: changes.append({'位置':'题干','块':i,'原':b['text'],'改为':nt})
    for k,v in r['options'].items():
        for i,b in enumerate(v):
            if b['type']=='text':
                nt=fix_text(n,'选项'+k,b['text'])
                if nt!=b['text']: changes.append({'位置':'选项'+k,'块':i,'原':b['text'],'改为':nt})
    for m in r.get('materials') or []:
        for i,b in enumerate(m['blocks']):
            if b['type']=='text':
                nt=fix_text(n,'材料',b['text'])
                if nt!=b['text']: changes.append({'位置':'材料'+m['id'],'块':i,'原':b['text'],'改为':nt})
    for c in changes:
        assert re.sub(r'\s','',c['原'])==re.sub(r'\s','',c['改为']), (n,c['位置'])  # whitespace-only
    if changes: out[n]=changes
json.dump(out,open('proposed_fixes.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for n,cs in out.items():
    for c in cs:
        print(f'== 第{n}题 {c["位置"]}（只改空白：已校验去空白后逐字相同）')
        print('   改为：'+c['改为'].replace('\n','⏎'))
print('涉及题号:', sorted(out))
