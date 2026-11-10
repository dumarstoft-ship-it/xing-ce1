import pymupdf, json, re, unicodedata, os
pymupdf.TOOLS.mupdf_display_errors(False)
W='/home/user/work'
EXTRA={
 'SD2021':'xingce/2021年山东公务员考试《行测》真题参考答案及解析.pdf',
 'SC2022S':'xingce/2022年0326四川公务员考试（行测）答案解析.pdf',
 'SZ2023':'xingce/2023年深圳市考公务员录用考试《行测》真题（解析）.pdf',
 'GD20131':'xing-ce1/答案解析/2013年广东公务员考试《行测》一卷答案及解析.pdf',
 'GD2014X':'xing-ce1/答案解析/2014年广东公务员考试《行测》真题（县级以上卷）答案及解析.pdf',
 'GD2017':'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
 'GD2018':'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
 'GD2019X':'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
 'GD2021Z':'xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
}
cache={}
def ansfile(pid):
    for t in (pid, pid+'_xc'):
        p=f'{W}/answers/{t}.json'
        if os.path.exists(p): return json.load(open(p))['file']
    return EXTRA.get(pid)
def load(pid):
    if pid in cache: return cache[pid]
    f=ansfile(pid)
    if not f: cache[pid]=(None,None,None); return cache[pid]
    doc=pymupdf.open('/home/user/'+f)
    pages=[unicodedata.normalize('NFKC',pg.get_text()) for pg in doc]
    full=''; offs=[]
    for t in pages: offs.append(len(full)); full+=t
    cache[pid]=(f,full,offs); return cache[pid]
