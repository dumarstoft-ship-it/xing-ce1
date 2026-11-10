import pymupdf, subprocess, os, sys, json
pymupdf.TOOLS.mupdf_display_errors(False)
FILES={
 'GD2017':'/home/user/xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
 'GD2018':'/home/user/xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
 'GD2019X':'/home/user/xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
 'GD2019Z':'/home/user/xing-ce1/答案解析/2019年广东公务员考试《行测》真题（乡镇级）答案及解析.pdf',
 'GD2020X':'/home/user/xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',
 'GD2020Z':'/home/user/xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
 'GD2021Z':'/home/user/xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
 'GD2021X':'/home/user/xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（县级）参考答案及解析.pdf',
}
OUT='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pda/ocr'
for tag in sys.argv[1:]:
    doc=pymupdf.open(FILES[tag])
    for i,pg in enumerate(doc):
        out=f'{OUT}/{tag}_p{i+1}.txt'
        if os.path.exists(out): continue
        pix=pg.get_pixmap(dpi=200); png=f'{OUT}/tmp_{tag}.png'; pix.save(png)
        r=subprocess.run(['tesseract',png,'-','-l','chi_sim','--psm','6'],capture_output=True,text=True)
        open(out,'w').write(r.stdout)
    print('done',tag, flush=True)
