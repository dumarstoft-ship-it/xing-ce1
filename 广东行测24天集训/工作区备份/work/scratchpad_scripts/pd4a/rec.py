"""draft record helper.  from rec import save
save(key='GD2019X-33', tag='GD2019X', qno=33, ans_page=4, src='A', ans='A', topic=..., sol=..., comp=..., val=..., notes=..., flags=[], space=False, img_dups=[], stem=None, version_note='', group=None, order=None, rate=None, options=None)
"""
import json, os, re, unicodedata
W='/home/user/work'; D=os.path.dirname(os.path.abspath(__file__))+'/draft'
_idx={}
def idx(tag):
    if tag not in _idx: _idx[tag]={x['qno']:x for x in json.load(open(f'{W}/index/{tag}.json')) if x['kind']=='q'}
    return _idx[tag]
def ansfile(tag):
    p=f'{W}/answers/{tag}.json'
    if os.path.exists(p): return json.load(open(p))['file']
    p=f'{W}/ocr/{tag}_ans/_meta.json'
    if os.path.exists(p): return json.load(open(p))['file']
    return None
def clean_stem(t, qno):
    t=re.sub(r'\s+',' ',t).strip()
    t=re.sub(r'^\s*%d\s*[、\.．]?\s*'%qno,'',t)
    t=re.sub(r'^[\(（]单选题[\)）]\s*','',t)
    t=re.split(r'\s*A\s*[、\.．]',t)[0].strip()
    for a,b in ((',','，'),(':','：'),('?','？'),('(','（'),(')','）'),(';','；')): t=t.replace(a,b)
    t=re.sub(r'(?<=[\u4e00-\u9fff，：？（）、。；])\s+(?=[\u4e00-\u9fff，：？（）、。；①-⑩0-9A-Za-z])','',t)
    t=re.sub(r'(?<=[0-9A-Za-z①-⑩])\s+(?=[\u4e00-\u9fff，：？（）、。；])','',t)
    t=t.replace('（ ）','（ ）').replace('（）','（ ）')
    return t
def save(key, tag, qno, ans_page, src, ans, topic, sol, comp, val, notes, flags=None, space=False, img_dups=None,
         stem=None, version_note='', rate=None, options=None, file=None, pages=None, ans_file=None, check_status='已核验', extra=None):
    if file is None:
        q=idx(tag)[qno]; file=q['file']; pages=sorted({p+1 for p,_,_ in q['segs']})
        if stem is None: stem=clean_stem(q['text'],qno)
    if ans_file is None: ans_file=ansfile(tag)
    paper=tag.replace('_xc','')
    r=dict(id=None, module='判断', day='D12', group=None, group_title=None, topic=topic, order=None,
           source=dict(paper=paper, file=file, page=pages[0], pages=pages, qno=qno, ans_file=ans_file, ans_page=ans_page, version_note=version_note),
           done_status='已做情况未知', stem=stem, options=options or {k:'见图' for k in 'ABCD'}, material_or_article=None,
           assets=[f'assets/{key}.png'], source_answer=src, checked_answer=ans, brief_solution=sol, competing=comp,
           selection_value=val, variant_of=None, check_status=check_status, flags=flags or [], notes=notes,
           replaced_from=None, img_dups=img_dups or [], space=space)
    if rate is not None: r['source_rate']=rate
    if extra: r.update(extra)
    os.makedirs(D,exist_ok=True)
    json.dump(r,open(f'{D}/{key}.json','w'),ensure_ascii=False,indent=1)
    print('saved',key,'|',r['stem'][:40],'| pages',pages,'| ans_file',(ans_file or '')[-40:])

CIRC={'1':'①','2':'②','3':'③','4':'④','5':'⑤','6':'⑥'}
def clsopts(tag,q):
    """options of a 分组分类 question from the index text, digits normalised to circled numbers"""
    t=re.sub(r'\s+','',idx(tag)[q]['text'])
    m=re.search(r'A[、\.．](.*?)B[、\.．](.*?)C[、\.．](.*?)D[、\.．](.*)$',t)
    out={}
    for k,v in zip('ABCD',m.groups()):
        v=v.replace(',','，')
        v=''.join(CIRC.get(ch,ch) for ch in v)
        v=re.sub(r'[^①-⑥，]','',v)
        out[k]=v
    return out
