import pymupdf, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
pymupdf.TOOLS.mupdf_display_errors(False)
P='/home/user/xing-ce1/题源补充/真题_江苏浙江2015-2020/2017年江苏公务员考试《行测》真题（A类）参考答案及解析.pdf'
O='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/ocr_js2017'
d=pymupdf.open(P); n=d.page_count
pages=[int(x) for x in sys.argv[1:]] or list(range(n))
def run(i):
    out=f'{O}/p{i+1:03d}'
    if os.path.exists(out+'.txt') and os.path.getsize(out+'.txt')>0: return
    dd=pymupdf.open(P); pix=dd[i].get_pixmap(dpi=200); pix.save(out+'.png')
    subprocess.run(['tesseract',out+'.png',out,'-l','chi_sim','--psm','6'],capture_output=True,timeout=600,env=dict(os.environ,OMP_THREAD_LIMIT='1'))
with ThreadPoolExecutor(4) as ex: list(ex.map(run,pages))
print('done',len(pages))
