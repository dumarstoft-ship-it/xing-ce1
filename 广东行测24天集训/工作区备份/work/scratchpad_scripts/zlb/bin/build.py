import json, re, os, sys, shutil
sys.path.insert(0, os.path.dirname(__file__))
import pymupdf
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
from qdata1 import B1
from qdata2 import B2
from qdata3 import B3
from qrepl import R as REPL
from mats import M, F, seg_text, render
from mat_meta import OVR
SCR='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zlb'
OUT='/home/user/work/out/ZL-B'; MATD='/home/user/work/out/zl_materials'
raw={f"{r['tag']}-{r['qno']}":r for r in json.load(open(f'{SCR}/items_raw.json'))}
GROUPS=[('ZL01-B1','统计口径辨析',list(B1)),('ZL01-B2','长文字定位与口径判断',list(B2)),('ZL01-B3','轻计算、快速读数与能否推出',list(B3))]
_gl={g:items for g,_,items in GROUPS}
for gid,pos,rec in REPL:
    old=_gl[gid][pos-1]
    ok=old['key'].replace('_xc','')
    assert ok==rec['replaced_from'], (gid,pos,ok,rec['replaced_from'])
    _gl[gid][pos-1]=rec
CIRC={'1':'①','2':'②','3':'③','4':'④'}
def clean(t):
    t=re.sub(r'· 本试卷由粉笔用户[^\n]*\n?','',t)
    t=re.sub(r'\d{4}年[^\n]*\(网友回忆版\)[^\n]*\n?','',t)
    return t.strip()
STMT_ITEMS={'GK2019F-135','SC2024_xc-90','SC2022H_xc-100','GK2024F-135','GD2025_xc-79'}
def tidy(x):
    x=re.sub(r'(?<=[0-9A-Za-z%）)])\s+(?=[\u4e00-\u9fff])','',x)
    x=re.sub(r'(?<=[\u4e00-\u9fff，。、；：）])\s+(?=[0-9A-Za-z\u4e00-\u9fff（(“])','',x)
    x=re.sub(r'(?<=[0-9])\s+(?=[0-9])','',x) if False else x
    return x.strip()
def parse(key,t):
    t=clean(t)
    t=re.sub(r'^\s*\d{1,3}\s*[\.、．]?\s*','',t,count=1)
    t=re.sub(r'^\(单选题\)','',t)
    lines=[l.strip() for l in t.split('\n') if l.strip()]
    out=[]
    for l in lines:
        if key in STMT_ITEMS and re.match(r'^[1-4](?=20|[\u4e00-\u9fff])',l) and not re.match(r'^[A-D][\.．、]',l):
            out.append('\n'+CIRC[l[0]]+l[1:])
        else:
            out.append(l)
    s=''
    for l in out:
        if not s: s=l; continue
        if l.startswith('\n'): s+=l; continue
        # option markers start new tokens
        if re.match(r'^[A-D]\s*[\.．、]',l): s+=' '+l
        else: s+=l if (re.search(r'[\u4e00-\u9fff，。、；：）)]$',s) or re.match(r'^[\u4e00-\u9fff]',l)) else ' '+l
    parts=re.split(r'(?:(?<=\s)|(?<=^)|(?<=[\u4e00-\u9fff%）)]))([A-D])\s*[\.．、]\s*',s)
    stem=tidy(parts[0]); opts={}
    for i in range(1,len(parts)-1,2): opts[parts[i]]=tidy(parts[i+1])
    return stem,opts
OVERRIDE={
 'GD2025_xc-77':dict(opts={'B':'2023年我国已有超过1/2的人口用上了天然气'}),
 'GD2017-94':dict(opts={'B':'广东民营经济占GDP的比重从2011年开始超过50%'}),
 'GD2026_xc-80':dict(opts={k:'见图' for k in 'ABCD'}),
 'GK2019D-114':dict(opts={k:'见图' for k in 'ABCD'}),
 'GK2024F-135':dict(opts={'A':'0项','B':'1项','C':'2项','D':'3项'}),
 'GD2025_xc-79':dict(opts={'A':'①②③','B':'①③④','C':'②③④','D':'①②③④'}),
 'SC2025_xc-90':dict(stem='在①2023年6月末除汽车驾驶人之外的机动车驾驶人数量同比增速和②2022年下半年全国新领证驾驶人数量两个指标中：',opts={'A':'仅①能够从上述资料中推出','B':'仅②能够从上述资料中推出','C':'两者均能从上述资料中推出','D':'两者均不能从上述资料中推出'}),
 'GD2022X_xc-89':dict(opts={'D':'职工医保基金(含生育保险)支出>职工医保统筹基金(含生育保险)支出>职工医保基金(含生育保险)收入'}),
}
NEED_IMG={'GD2025_xc-77','GD2017-94','GD2026_xc-80','GK2019D-114'}
VN={'GD2026_xc':'网友回忆版（粉笔导出）','GD2025_xc':'网友回忆版（粉笔导出）','GD2024_xc':'网友回忆版（粉笔导出）','GD2023X_xc':'网友回忆版（粉笔导出）','GD2022X_xc':'网友回忆版（粉笔导出）',
    'GK2022F_xc':'网友回忆版（xingce）；本版资料题号与 xing-ce1 版 GK2022F 不同，认领键用 GK2022F_xc-<题号>','SC2024_xc':'网友回忆版','SZ2024_xc':'','SD2020_xc':'','SC2022H_xc':'',
    'GD2020Z':'','GD2018':'','GD2017':'','GK2019D':'','GK2021D':'','GK2019F':'','GK2024F':'','GK2023F':'','GK2025F':'',
    'GK2018D':'','ZJ2021A_xc':'网友回忆版（粉笔导出）','SZ2023_xc':'','SD2024_xc':'','SC2025_xc':''}
os.makedirs(f'{OUT}/assets/q',exist_ok=True)
docs={}
def doc(f):
    if f not in docs: docs[f]=pymupdf.open('/home/user/'+f)
    return docs[f]
recs=[]; n=0
for gid,gtitle,items in GROUPS:
    for order,it in enumerate(items,1):
        n+=1; key=it['key']
        adapted=it.get('adapted',False)
        if adapted:
            r=raw[it['mother']]; tag=r['tag']; stem,opts=it['stem'],dict(it['options']); qpng=None
        else:
            r=raw[key]; tag=r['tag']
            stem,opts=parse(key,r['text'])
            ov=OVERRIDE.get(key,{})
            if 'opts' in ov: opts.update(ov['opts'])
            if 'stem' in ov: stem=ov['stem']
            qpng=f'assets/q/{tag}_q{r["qno"]}.png'
            segs=[tuple(s) for s in r['segs']]
            if key=='GD2026_xc-90': segs=[(17,569.7,700.0)]
            if not os.path.exists(f'{OUT}/{qpng}'):
                render(doc(r['file']),segs,f'{OUT}/{qpng}',200,xc=r['file'].startswith('xingce/'))
        assert set(opts)=={'A','B','C','D'}, (key,opts)
        paper=tag.replace('_xc','')
        rec=dict(id=f'ZL-B-{n:03d}',module='资料',day='ZL01',group=gid,group_title=gtitle,topic=it['topic'],order=order,
          source=dict(paper=paper,file=r['file'],page=r['segs'][0][0]+1,qno=r['qno'],ans_file=it.get('ans_file'),ans_page=it.get('ans_page'),version_note=VN[tag]),
          claim_key=(None if adapted else (f'GK2022F_xc-{r["qno"]}' if tag=='GK2022F_xc' else f'{paper}-{r["qno"]}')),
          done_status='已做情况未知',stem=stem,options=opts,material_or_article=it['mid'],
          assets=[qpng] if (qpng and key in NEED_IMG) else [], q_image=qpng,
          source_answer=it.get('src_ans'),checked_answer=it['ans'],brief_solution=it['brief'],selection_value=it['value'],
          variant_of=it.get('variant_of'),check_status=('已核验-改编' if adapted else '已核验'),flags=it['flags'],notes=it['notes'],
          replaced_from=it.get('replaced_from'))
        recs.append(rec)
with open(f'{OUT}/questions.jsonl','w') as fo:
    for rec in recs: fo.write(json.dumps(rec,ensure_ascii=False)+'\n')
print('questions',len(recs))
# ---------------- materials ----------------
used=sorted({r['material_or_article'] for r in recs})
ZLA=set()
if os.path.exists('/home/user/work/out/ZL-A/questions.jsonl'):
    ZLA={json.loads(l).get('material_or_article') for l in open('/home/user/work/out/ZL-A/questions.jsonl') if l.strip()}
mlines=[]
for mid in used:
    tag,paper,segs,vn=M[mid]
    d=doc(F[tag]); o=OVR.get(mid,{})
    txt=seg_text(d,segs)
    if o.get('text_override'): txt=o['text_override']
    if o.get('text_insert_after'):
        i=txt.find(o['text_insert_after']); assert i>=0, mid
        i+=len(o['text_insert_after']); txt=txt[:i]+o['insert']+txt[i:]
    if o.get('text_append'): txt=txt+o['text_append']
    png=f'zl_materials/{mid}/{mid}.png'
    qs=[x['id']+' '+(x['claim_key'] or ('改编，variant_of '+x['variant_of'])) for x in recs if x['material_or_article']==mid]
    m=dict(mid=mid,source=dict(paper=paper,file=F[tag],pages=sorted({p+1 for p,_,_ in segs}),segs_0based=[list(s) for s in segs],version_note=vn),
           text=txt,assets=[png],transcription=o.get('transcription'),
           notes=(o.get('notes','')+(' ' if o.get('notes') else '')+'建档：ZL-B（2026-11-07建，11-08更新）。图片由 render 同法按原页坐标截取（170dpi），粉笔导出版去掉了页眉页脚水印。ZL-B 使用本材料的题：'+'；'.join(qs)))
    if mid in ZLA:
        m['notes']+='（本材料目录 ZL-A 也在使用；11-08 起 ZL-B 不再改写该目录，以本行记录为准。）'
    else:
        os.makedirs(f'{MATD}/{mid}',exist_ok=True)
        render(d,segs,f'{MATD}/{mid}/{mid}.png',170,xc=F[tag].startswith('xingce/'))
        json.dump(m,open(f'{MATD}/{mid}/material.json','w'),ensure_ascii=False,indent=1)
    mlines.append(m)
with open(f'{OUT}/materials.jsonl','w') as fo:
    for m in mlines: fo.write(json.dumps(m,ensure_ascii=False)+'\n')
print('materials',len(mlines))
