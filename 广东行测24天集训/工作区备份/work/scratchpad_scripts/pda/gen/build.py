import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from items_g1 import G1
from items_g2 import G2
IDX='/home/user/work/index'
AP=json.load(open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pda/anspages.json'))
SCAN={
 'GD2018-34':('xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',6),
 'GD2019X-34':('xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',4),
 'GD2019X-37':('xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',5),
 'GD2019X-38':('xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',5),
 'GD2019X-39':('xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',6),
 'GD2019X-40':('xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',6),
 'GD2020X-41':('xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',11),
 'GD2020X-42':('xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',11),
 'GD2019X-35':('xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',4),
 'GD2019Z-29':('xing-ce1/答案解析/2019年广东公务员考试《行测》真题（乡镇级）答案及解析.pdf',3),
 'GD2020X-43':('xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',11),
 'GD2021Z-52':('xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',12),
 'GD2021Z-53':('xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',12),
 'GD2021Z-55':('xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',13),
}
SCANNOTE={'GD2018-34':'解析为图片版（无文字层），已出图核对','GD2019X':'解析为图片版，已出图核对','GD2020X':'解析为扫描件，已出图核对','GD2021Z':'解析为扫描件，已出图核对'}
def qrec(tag,qno):
    for q in json.load(open(f'{IDX}/{tag}.json')):
        if q['kind']=='q' and q['qno']==qno: return q
from replacements import REPL
REPLACED={}
def apply(items):
    res=[]
    for it in items:
        k=(it[0],it[1])
        if k in REPL:
            new=REPL[k]; res.append(new); REPLACED[(new[0],new[1])]=f"{k[0].replace('_xc','')}-{k[1]}"
        else: res.append(it)
    return res
G1=apply(G1); G2=apply(G2)
out=[]; n=0
for gid,gtitle,items in [('PD01-G1','平面类图推（第1组）：先认题型，再定维度',G1),('PD01-G2','空间类固定题型（第1组）：展开·截面·视图·拼合',G2)]:
    for order,(tag,qno,topic,stem,opts,src,chk,sol,val,flags,notes) in enumerate(items,1):
        n+=1; q=qrec(tag,qno); pid=tag.replace('_xc','')
        key=f'{tag}-{qno}'; skey=f'{pid}-{qno}'
        vnote=[]
        fn=os.path.basename(q['file'])
        if '网友回忆' in fn: vnote.append('网友回忆版（粉笔整理）')
        if '暂缺' in fn: vnote.append('原卷文件标注“7道题暂缺”，本题完整')
        if key in AP: af,ap=AP[key]['ans_file'],AP[key]['ans_page']
        elif skey in SCAN: af,ap=SCAN[skey]
        else: af,ap=None,None
        if skey in SCAN: vnote.append('解析为扫描/图片版，已出图核对答案')
        if pid=='GD2026': vnote.append('2026年度无解析')
        status='图像待复核' if '图像待复核' in flags else '已核验'
        checked=None if status=='图像待复核' else chk
        rec=dict(id=f'PD-A-{n:03d}',module='判断',day='PD01',group=gid,group_title=gtitle,topic=topic,order=order,
            source=dict(paper=pid,file=q['file'],page=q['segs'][0][0]+1,pages=sorted({s[0]+1 for s in q['segs']}),qno=qno,
                        ans_file=af,ans_page=ap,version_note='；'.join(vnote)),
            done_status='已做情况未知',stem=stem,
            options=opts if opts else {k:'见图' for k in 'ABCD'},
            material_or_article=None,assets=[f'assets/{pid}-{qno}.png'],
            source_answer=src,checked_answer=checked,brief_solution=sol,selection_value=val,variant_of=None,
            check_status=status,flags=flags,notes=notes,replaced_from=REPLACED.get((tag,qno)))
        out.append(rec)
with open('/home/user/work/out/PD-A/questions.jsonl','w') as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print(len(out))
# sanity
for r in out:
    a=r['assets'][0]
    if not os.path.exists('/home/user/work/out/PD-A/'+a): print('MISSING ASSET',a)
    if r['source_answer'] and r['checked_answer'] and r['source_answer']!=r['checked_answer']: print('CONFLICT',r['id'])
