# render pages: python3 rp.py <key> <page1based>[,<page>...] [dpi] [y0frac] [y1frac]
import pymupdf, sys
pymupdf.TOOLS.mupdf_display_errors(False)
base='/home/user/xing-ce1/'
files = {
 'A17':'答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
 'A18':'答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
 'A19X':'答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
 'A19Z':'答案解析/2019年广东公务员考试《行测》真题（乡镇级）答案及解析.pdf',
 'A20X':'答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',
 'A20Z':'答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
 'A21Z':'答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
 'A21X':'答案解析/2021年0314广东公务员考试《行测》真题（县级）参考答案及解析.pdf',
 'A22X':'答案解析/2022年广东公务员考试行测试题（县级）答案解析.pdf',
 'A22Z':'答案解析/2022年广东公务员考试行测试题（乡镇）答案解析.pdf',
 'A23X':'答案解析/2023年广东省公务员录用考试《行测》题（县级卷）答案解析.pdf',
 'A23Z':'答案解析/2023年广东省公务员录用考试《行测》题（乡镇卷）答案解析.pdf',
 'Q17':'真题/2017年广东公务员考试《行测》真题.pdf',
 'Q18':'真题/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）.pdf',
 'Q19X':'真题/2019年广东公务员考试《行测》真题（县级）.pdf',
 'Q19Z':'真题/2019年广东公务员考试《行测》真题（乡镇级）.pdf',
 'Q20X':'真题/2020年0809广东公务员考试《行测》真题（县级以上）（7道题暂缺）.pdf',
 'Q20Z':'真题/2020年0809广东公务员考试《行测》真题（乡镇）.pdf',
 'Q21Z':'真题/2021年0314广东公务员考试《行测》真题（乡镇）.pdf',
 'Q21X':'真题/2021年0314广东公务员考试《行测》真题（县级）.pdf',
 'Q22X':'真题/2022年广东公务员考试行测试题（县级).pdf',
 'Q22Z':'真题/2022年广东公务员考试行测试题（乡镇）.pdf',
 'Q23X':'真题/2023年广东省公务员录用考试《行测》题（县级卷）.pdf',
 'Q23Z':'真题/2023年广东省公务员录用考试《行测》题（乡镇卷）.pdf',
 'A22X_xc':None, 
}
key = sys.argv[1]; pages = [int(x) for x in sys.argv[2].split(',')]
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 120
y0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
y1 = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
d = pymupdf.open(base + files[key])
for p in pages:
    pg = d[p-1]
    r = pg.rect
    clip = pymupdf.Rect(0, r.height*y0, r.width, r.height*y1)
    pix = pg.get_pixmap(dpi=dpi, clip=clip)
    out = f'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yy4a/{key}_p{p}_{dpi}_{int(y0*100)}_{int(y1*100)}.png'
    pix.save(out); print(out, pix.width, pix.height)
