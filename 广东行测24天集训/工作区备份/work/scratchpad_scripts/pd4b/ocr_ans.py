import pymupdf, os, sys, json, subprocess
from concurrent.futures import ThreadPoolExecutor
pymupdf.TOOLS.mupdf_display_errors(False)
BASE='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd4b/ocr'
FILES={
 'SD2021_ans':'xingce/2021年山东公务员考试《行测》真题参考答案及解析.pdf',
 'SC2022S_ans':'xingce/2022年0326四川公务员考试（行测）答案解析.pdf',
 'SZ2023_ans':'xingce/2023年深圳市考公务员录用考试《行测》真题（解析）.pdf',
 'GK2021F_ans':'xing-ce1/国考/答案解析/2021年国家公务员考试《行测》真题（副省级）参考答案及解析...pdf',
 'JS2017A_ans':'xing-ce1/题源补充/真题_江苏浙江2015-2020/2017年江苏公务员考试《行测》真题（A类）参考答案及解析.pdf',
}
jobs=[]
for tag,path in FILES.items():
    if len(sys.argv)>1 and tag not in sys.argv[1:]: continue
    d=pymupdf.open('/home/user/'+path)
    os.makedirs(f'{BASE}/{tag}',exist_ok=True)
    json.dump(dict(file=path,pages=d.page_count),open(f'{BASE}/{tag}/_meta.json','w'),ensure_ascii=False)
    for i in range(d.page_count): jobs.append((tag,path,i))
def run(job):
    tag,path,i=job
    out=f'{BASE}/{tag}/p{i+1:03d}'
    if os.path.exists(out+'.txt') and os.path.getsize(out+'.txt')>0: return
    d=pymupdf.open('/home/user/'+path)
    pix=d[i].get_pixmap(dpi=200); pix.save(out+'.png')
    subprocess.run(['tesseract',out+'.png',out,'-l','chi_sim','--psm','6'],capture_output=True,timeout=600,env=dict(os.environ,OMP_THREAD_LIMIT='1'))
print(len(jobs),'pages')
with ThreadPoolExecutor(6) as ex: list(ex.map(run,jobs))
print('done')
