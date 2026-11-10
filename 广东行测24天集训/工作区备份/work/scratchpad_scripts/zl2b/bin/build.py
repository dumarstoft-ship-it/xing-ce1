import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from qdata1 import G1, Q1
from qdata2 import G2, Q2
from qdata3 import G3, Q3
from qparse import parse
import verify
OUT='/home/user/work/out2/ZL2B'; IDX='/home/user/work/index'
PAPERS={
 'HB2023': dict(tag='HB2023_xc', file='xingce/2023年河北省公务员录用考试《行测》题.pdf', ans='xingce/2023年河北省公务员录用考试《行测》答案解析.pdf', vnote=''),
 'HB2025': dict(tag='HB2025_xc', file='xingce/2025年河北省公务员录用考试《行测》题.pdf', ans='xingce/2025年河北省公务员录用考试《行测》答案及解析.pdf', vnote=''),
 'SC2020S': dict(tag='SC2020S_xc', file='xingce/2020年0725四川公务员考试《行测》真题.pdf', ans='xingce/2020年0725四川公务员考试《行测》真题参考答案及解析_decrypted.pdf', vnote=''),
 'SD2025': dict(tag='SD2025_xc', file='xingce/2025年山东省公务员录用考试《行测》试题（网友回忆版）.pdf', ans='xingce/2025年山东省公务员录用考试《行测》试题（网友回忆版）（解析）.pdf', vnote='网友回忆版'),
 'GD2022Z': dict(tag='GD2022Z', file='xing-ce1/真题/2022年广东公务员考试行测试题（乡镇）.pdf', ans='xing-ce1/答案解析/2022年广东公务员考试行测试题（乡镇）答案解析.pdf', vnote=''),
 'GD2022X': dict(tag='GD2022X_xc', file='xingce/2022年广东省公务员录用考试《行测》题（县级卷）（网友回忆版）.pdf', ans='xingce/2022年广东公务员考试行测试题（县级）答案解析.pdf', vnote='网友回忆版（粉笔导出），已与xing-ce1真题版逐字对照一致'),
 'GK2020D': dict(tag='GK2020D', file='xing-ce1/国考/真题/2020年国家公务员考试《行测》真题（地市级）.pdf', ans='xing-ce1/国考/答案解析/2020年国家公务员考试《行测》真题（地市级）答案及解析...pdf', vnote=''),
 'GK2023D': dict(tag='GK2023D', file='xing-ce1/国考/真题/2023年国家公务员录用考试《行测》真题（地市级）.pdf', ans='xing-ce1/国考/答案解析/2023年国家公务员录用考试《行测》真题（地市级）（解析）.pdf', vnote=''),
 'GK2025D': dict(tag='GK2025D', file='xing-ce1/国考/真题/2025年国家公务员录用考试《行测》题（地市级）.pdf', ans='xing-ce1/国考/答案解析/2025年国考《行测》（地市级）答案+解析.pdf', vnote=''),
 'HB2020': dict(tag='HB2020_xc', file='xingce/2020年0822河北公务员考试《行测》真题.pdf', ans='xingce/2020年0822河北公务员考试《行测》真题参考答案及解析.pdf', vnote=''),
 'GD2026': dict(tag='GD2026', file='xing-ce1/真题/2026年广东省公务员录用考试《行测》题（网友回忆版）(1).pdf', ans=None, vnote='网友回忆版（粉笔导出）；用户已做卷，原题不入包，此处仅作改编母题'),
}
ANSPAGE={'HB2023':{126:43,127:44,128:44,129:44,130:45},
 'HB2025':{111:66,112:66,113:67,114:67,115:67},
 'SC2020S':{96:25,97:26,99:26,100:26},
 'SD2025':{112:31,114:32,115:32,116:32,117:32,119:33,120:33},
 'GD2022Z':{87:40,89:41,90:41,96:43,98:44,99:44,100:44},
 'GD2022X':{96:49,98:50,99:50,100:51},
 'GK2020D':{126:27,127:27,129:27,130:27},
 'GK2023D':{126:38,127:38,129:38,130:38},
 'GK2025D':{127:43,129:43,130:44},
 'HB2020':{127:34,128:34,129:34,130:35}}
SRCANS_OVERRIDE={'HB2025-111':'A','HB2025-112':'D','HB2025-113':'C','HB2025-114':'C','HB2025-115':'B','GK2023D-126':'B'}
NO_ANS={'HB2025-126','HB2025-127','HB2025-128','HB2025-129','HB2025-130'}
def qpage(tag,qno):
    d=json.load(open(f'{IDX}/{tag}.json'))
    q=[x for x in d if x['kind']=='q' and int(x['qno'])==qno][0]
    return q['segs'][0][0]+1
def src_answer(paper,qno):
    k=f'{paper}-{qno}'
    if k in SRCANS_OVERRIDE: return SRCANS_OVERRIDE[k]
    if k in NO_ANS: return None
    tag=PAPERS[paper]['tag']
    a=json.load(open(f'/home/user/work/answers/{tag}.json'))['answers']
    return (a.get(str(qno)) or {}).get('ans')
recs=[]; n=0; problems=[]
for (gid,gtitle),Q in [(G1,Q1),(G2,Q2),(G3,Q3)]:
    for order,q in enumerate(Q,1):
        n+=1; rid=f'ZL2B-{n:03d}'
        ad=q.get('adapted')
        if ad:
            paper=ad['paper']; qno=ad['qno']; P=PAPERS[paper]
            stem=ad['stem']; opts=ad['options']
            vkey='ZL2B-'+q['key']
            source=dict(paper=paper, file=P['file'], page=qpage(P['tag'],qno), qno=qno, ans_file=None, ans_page=None,
                        version_note=('ZL2B改编：沿用母题材料，设问与四个选项均为ZL2B新拟；'+P['vnote']).rstrip('；'))
            sa=None; claim=None; qimg=None; status='已核验-改编'
            flags=['改编']+(['网友回忆版'] if '网友回忆版' in P['vnote'] else [])+(['母题为已做卷','无官方解析'] if paper=='GD2026' else [])
            variant_of=ad['variant_of']
        else:
            paper,qno=q['key'].rsplit('-',1); qno=int(qno); P=PAPERS[paper]
            stem,opts,_=parse(P['tag'],qno)
            if q.get('opt_override'): opts=q['opt_override']
            if q.get('stem_override'): stem=q['stem_override']
            vkey=q['key']
            source=dict(paper=paper, file=P['file'], page=qpage(P['tag'],qno), qno=qno,
                        ans_file=(P['ans'] if q['key'] not in NO_ANS else None),
                        ans_page=ANSPAGE.get(paper,{}).get(qno), version_note=P['vnote'])
            sa=src_answer(paper,qno); claim=q['key']; qimg=f'assets/q/{P["tag"]}_q{qno}.png'
            status='已核验'; variant_of=None
            flags=(['网友回忆版'] if '网友回忆版' in P['vnote'] else [])+(['无原解析（编者定答案）'] if q['key'] in NO_ANS else [])
        flags=flags+q.get('extra_flags',[])
        # verification
        va,_d=verify.R[vkey]()
        if va!=q['ans']: problems.append(f'{rid} {vkey}: verify {va} != data {q["ans"]}')
        if sa and sa!=q['ans']: problems.append(f'{rid} {vkey}: source {sa} != checked {q["ans"]}')
        if not opts or sorted(opts)!=['A','B','C','D'] or any(not v for v in opts.values()): problems.append(f'{rid} bad options {opts}')
        if qimg and not os.path.exists(f'{OUT}/{qimg}'): problems.append(f'{rid} missing {qimg}')
        rec=dict(id=rid, module='资料', day='D05', group=gid, group_title=gtitle, topic=q['topic'], order=order,
                 source=source, claim_key=claim, done_status='已做情况未知', stem=stem, options=opts,
                 material_or_article=q['mid'], assets=q.get('assets',[]), q_image=qimg,
                 source_answer=sa, checked_answer=q['ans'], brief_solution=q['brief'], selection_value=q['value'],
                 variant_of=variant_of, check_status=status, flags=flags, notes=q['notes'])
        recs.append(rec)
with open(f'{OUT}/questions.jsonl','w') as f:
    for r in recs: f.write(json.dumps(r, ensure_ascii=False)+'\n')
users={}
for r in recs: users.setdefault(r['material_or_article'],[]).append(r['id']+('（改编，variant_of '+r['variant_of']+'）' if r['variant_of'] else '（'+r['claim_key']+'）'))
json.dump({k:'；'.join(v) for k,v in users.items()}, open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2b/mat_users.json','w'), ensure_ascii=False, indent=1)
print(len(recs),'records'); print('\n'.join(problems) or 'no problems')
import collections
print(collections.Counter(r['checked_answer'] for r in recs))
print(collections.Counter(r['group'] for r in recs))
