import json, os, re, sys, importlib.util
sys.path.insert(0,'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd2a')
spec=importlib.util.spec_from_file_location('content','content.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); C=m.C
ana=json.load(open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd2a/anaseg.json'))
ANS={}
for f in os.listdir('/home/user/work/answers'): ANS[f[:-5]]=json.load(open('/home/user/work/answers/'+f))['answers']
IDX='/home/user/work/index'
ORDER=[
 ('G1',['GK2017D-72','GD2020Z-47','GD2021Z-49','GK2025D-77','GD2019Z-27','GD2020Z-48','GK2025F-82','GK2021D-71','GD2018-35','GD2023X-49','GD2022X-45','GD2020Z-46','GD2020X-50','GK2019D-79','GDXD2020SW-64']),
 ('G2',['GD2017-32','GD2023X-48','GD2018-32','SC2023-57','GK2025F-84','JS2022A-79','GD2022Z-53','GD2023Z-50','GD2022X-49','HB2020-79','GK2017D-78','GK2025F-88','GK2022D-74','GD2018-38','GD2023Z-46']),
 ('G3',['GD2021Z-51','GDXD2019SW-72','GK2022F-80','GD2019X-36','GDXD2019SW-74','GDXD2019SW-73','GK2018D-75','ZJ2022A-80','GDXD2020SW-69','GD2020X-45','HB2020-77','GDXD2020SW-67','GK2017D-76','GK2022D-76','GDXD2020SW-70']),
]
GT={'G1':'平面类图推（第2组·上）：先看元素组成，再定看法',
    'G2':'平面类图推（第2组·下）：先看元素组成，再定看法',
    'G3':'空间类图推（第2组）：折叠·截面·视图·旋转·纸条'}
# scanned GD analyses: key -> (ocr tag, page, official answer read from page image/OCR)
SCAN={'GD2017-32':('GD2017_ans',5,'B'),'GD2018-32':('GD2018_ans',6,'A'),'GD2018-35':('GD2018_ans',6,'B'),'GD2018-38':('GD2018_ans',6,'C'),
      'GD2019Z-27':('GD2019Z_ans',3,'B'),'GD2019X-36':('GD2019X_ans',5,'B'),'GD2020X-45':('GD2020X_ans',12,'C'),'GD2020X-50':('GD2020X_ans',13,'C'),
      'GD2020Z-46':('GD2020Z_ans',12,'B'),'GD2020Z-47':('GD2020Z_ans',12,'A'),'GD2020Z-48':('GD2020Z_ans',12,'A'),
      'GD2021Z-49':('GD2021Z_ans',12,'C'),'GD2021Z-51':('GD2021Z_ans',12,'B')}
TEXTOPT={
 'GK2019D-79':{'A':'①④⑤，②③⑥','B':'①②⑤，③④⑥','C':'①④⑥，②③⑤','D':'①③④，②⑤⑥'},
 'GK2017D-78':{'A':'①④⑥，②③⑤','B':'①②③，④⑤⑥','C':'①⑤⑥，②③④','D':'①③⑤，②④⑥'},
 'GK2025F-88':{'A':'①②④，③⑤⑥','B':'①③⑤，②④⑥','C':'①③④，②⑤⑥','D':'①③⑥，②④⑤'},
 'GDXD2019SW-72':{'A':'1和6','B':'2和5','C':'3和4','D':'4和5'},
}
DUPS={'GK2017D-72':['GK2017F-77'],'GD2021Z-49':['GD2021X-44'],'GK2025D-77':['GK2025F-81'],'GK2025F-82':['GK2025X-78'],'GK2021D-71':['GK2021F-76'],
      'GK2019D-79':['GK2019F-84'],'GD2023X-49':['GD2023Z-54'],'GK2025F-84':['GK2025X-79'],'GK2017D-78':['GK2017F-83'],'GD2022X-49':['GD2022Z-55'],
      'GK2025F-88':['GK2025X-83'],'GK2022D-74':['GK2022F-79'],'GD2019X-36':['GD2019Z-32'],'GK2018D-75':['GK2018F-80'],'GD2020X-45':['GD2020Z-55'],
      'GK2017D-76':['GK2017F-81'],'GK2022D-76':['GK2022X-75']}
def tagof(pid):
    return pid if os.path.exists(f'{IDX}/{pid}.json') else pid+'_xc'
def stem_clean(t, qno):
    t=t.replace('\n','')
    t=re.sub(r'^\s*%d\s*[、\.．]?\s*'%qno,'',t)
    t=re.sub(r'^\s*[（(]单选题[)）]','',t)
    t=re.sub(r'A[、\.．]\s*B[、\.．]\s*C[、\.．]\s*D[、\.．]\s*$','',t)
    t=re.sub(r'·\s*本试卷由.*$','',t)
    t=re.sub(r'(A[\.、．]\s*A\s*B[\.、．]\s*B.*$)','',t)
    t=re.sub(r'A[、\.．]\s*如上图所示.*$','',t)
    t=re.sub(r'A[、\.．]\s*[①1].*$','',t)  # text options handled separately
    t=re.sub(r'A[、\.．]\s*$','',t)
    t=re.sub(r'\s+',' ',t).strip()
    return t
out=[]; n=0
for g,keys in ORDER:
    for o,key in enumerate(keys,1):
        n+=1
        pid,q=key.rsplit('-',1); q=int(q); tag=tagof(pid)
        rec=[x for x in json.load(open(f'{IDX}/{tag}.json')) if x['kind']=='q' and x['qno']==q][0]
        pages=sorted({s[0]+1 for s in rec['segs']})
        c=C[key]
        # answer source
        if key in SCAN:
            ot,ap,sa=SCAN[key]; meta=json.load(open(f'/home/user/work/ocr/{ot}/_meta.json'))
            ans_file=meta['file']; ans_page=ap; src_ans=sa; ansnote='扫描件解析（OCR定位、看页面图核对字母）'
        else:
            a=ana.get(tag) or ana.get(pid)
            seg=a['segs'][str(q)]; ans_file=a['file']; ans_page=seg['page']
            src_ans=(ANS.get(tag) or ANS.get(pid) or {}).get(str(q),{}).get('ans'); ansnote=''
        fname=os.path.basename(rec['file'])
        vnote='网友回忆版' if '网友回忆' in fname else ''
        stem=stem_clean(rec['text'],q)
        opts=TEXTOPT.get(key,{k:'见图' for k in 'ABCD'})
        flags=list(c['flags'])
        if tag.endswith('_xc') and not pid.startswith(('GD','GK')): flags.append('外省题')
        if vnote: flags.append('网友回忆版')
        notes=c['notes']
        if key in DUPS: pass
        notes=(notes+(' ' if notes else '')+'核验：'+c['verify']).strip()
        if ansnote: notes+=' 解析为'+ansnote+'。'
        r=dict(id=f'PD2A-{n:03d}',module='判断',day='D06',group=f'D06-{g}',group_title=GT[g],topic=c['topic'],order=o,
               source=dict(paper=pid,file=rec['file'],page=pages[0],pages=pages,qno=q,ans_file=ans_file,ans_page=ans_page,version_note=vnote),
               done_status='已做情况未知',stem=stem,options=opts,material_or_article=None,assets=[f'assets/{key}.png'],
               source_answer=src_ans,checked_answer=c['ans'],brief_solution=c['sol'],selection_value=c['val'],variant_of=None,
               check_status='已核验',flags=flags,notes=notes,replaced_from=None,img_dups=DUPS.get(key,[]))
        out.append(r)
with open('/home/user/work/out2/PD2A/questions.jsonl','w') as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+'\n')
import collections
print(len(out), collections.Counter(r['checked_answer'] for r in out))
for r in out:
    flag='' if r['source_answer']==r['checked_answer'] else '  <<< MISMATCH'
    print(r['id'],r['source']['paper'],r['source']['qno'],'p',r['source']['pages'],'ans_p',r['source']['ans_page'],r['source_answer'],r['checked_answer'],flag,'|',r['stem'][:40])
