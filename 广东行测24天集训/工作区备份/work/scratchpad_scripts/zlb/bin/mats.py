import pymupdf, json, os, re, sys
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
ROOT='/home/user'; OUT='/home/user/work/out/zl_materials'
F = {
 'GD2026_xc':'xingce/2026年广东省公务员录用考试《行测》题（网友回忆版）(1).pdf',
 'GD2025_xc':'xingce/2025年广东省公务员录用考试《行测》题（网友回忆版）.pdf',
 'GD2024_xc':'xingce/2024年广东省公务员录用考试《行测》题（网友回忆版）.pdf',
 'GD2023X_xc':'xingce/2023年广东省公务员录用考试《行测》题（县级卷）（网友回忆版）.pdf',
 'GD2022X_xc':'xingce/2022年广东省公务员录用考试《行测》题（县级卷）（网友回忆版）.pdf',
 'GD2020Z':'xing-ce1/真题/2020年0809广东公务员考试《行测》真题（乡镇）.pdf',
 'GD2018':'xing-ce1/真题/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）.pdf',
 'GD2017':'xing-ce1/真题/2017年广东公务员考试《行测》真题.pdf',
 'GK2022F_xc':'xingce/2022年国家公务员录用考试《行测》题（副省级网友回忆版）.pdf',
 'SZ2024_xc':'xingce/2024年深圳市考公务员录用考试《行测》真题.pdf',
 'SD2020_xc':'xingce/2020年0719山东公务员考试《行测》真题.pdf',
 'GK2019D':'xing-ce1/国考/真题/2019年国家公务员考试行测真题（地市级）.pdf',
 'GK2021D':'xing-ce1/国考/真题/2021年国家公务员考试《行测》真题（市地级）.pdf',
 'GK2019F':'xing-ce1/国考/真题/2019年国家公务员考试行测真题（省级）.pdf',
 'SC2024_xc':'xingce/2024年四川省公务员录用考试《行测》试题（网友回忆版）.pdf',
 'SC2022H_xc':'xingce/2022年四川下半年公务员录用考试《行测》 试题_decrypted.pdf',
 'GK2024F':'xing-ce1/国考/真题/2024年国家公务员录用考试《行测》题（副省级）.pdf',
 'GK2023F':'xing-ce1/国考/真题/2023年国家公务员录用考试《行测》真题（副省级）.pdf',
 'GK2025F':'xing-ce1/国考/真题/2025年国家公务员录用考试《行测》题（副省级）.pdf',
 'GK2018D':'xing-ce1/国考/真题/2018年国家录用公务员考试《行测》真题卷（地市级）.pdf',
 'ZJ2021A_xc':'xingce/2021年浙江省公务员录用考试《行测》题（A类）（网友回忆版）.pdf',
 'SZ2023_xc':'xingce/2023年深圳市考公务员录用考试《行测》真题.pdf',
 'SD2024_xc':'xingce/2024年山东省公务员录用考试《行测》试题 .pdf',
 'SC2025_xc':'xingce/2025年四川省考公务员&选调公务员录用考试《行测》试题.pdf',
}
# mid: (tag, paper, segs[(page0,y0,y1)], version_note)
M = {
 'ZLM-GD2026-1':('GD2026_xc','GD2026',[(13,601.9,841.9),(14,0,221.3)],'网友回忆版'),
 'ZLM-GD2026-2':('GD2026_xc','GD2026',[(14,507.4,790.0)],'网友回忆版'),
 'ZLM-GD2026-3':('GD2026_xc','GD2026',[(15,666.8,841.9),(16,0,408.5)],'网友回忆版'),
 'ZLM-GD2026-4':('GD2026_xc','GD2026',[(16,662.5,841.9),(17,0,400.5)],'网友回忆版'),
 'ZLM-GD2025-1':('GD2025_xc','GD2025',[(12,123.2,361.6)],'网友回忆版'),
 'ZLM-GD2025-2':('GD2025_xc','GD2025',[(12,599.5,841.9),(13,0,189.2)],'网友回忆版'),
 'ZLM-GD2024-1':('GD2024_xc','GD2024',[(12,411.1,643.3)],'网友回忆版'),
 'ZLM-GD2024-3':('GD2024_xc','GD2024',[(14,692.7,841.9),(15,0,459.2)],'网友回忆版'),
 'ZLM-GD2024-4':('GD2024_xc','GD2024',[(16,644.6,841.9),(17,0,514.2)],'网友回忆版'),
 'ZLM-GD2023X-1':('GD2023X_xc','GD2023X',[(15,277.0,605.6)],'网友回忆版'),
 'ZLM-GD2022X-1':('GD2022X_xc','GD2022X',[(18,330.8,563.0)],'网友回忆版'),
 'ZLM-GD2022X-2':('GD2022X_xc','GD2022X',[(19,225.7,738.4)],'网友回忆版'),
 'ZLM-GD2020Z-3':('GD2020Z','GD2020Z',[(17,300.0,841.9),(18,0,326.0)],''),
 'ZLM-GD2018-1':('GD2018','GD2018',[(12,393.7,841.9),(13,0,429.9)],''),
 'ZLM-GD2017-2':('GD2017','GD2017',[(10,496.2,841.9),(11,0,256.9)],''),
 'ZLM-GD2017-3':('GD2017','GD2017',[(11,488.4,841.9),(12,0,73.4)],''),
 'ZLM-GK2022F_xc-1':('GK2022F_xc','GK2022F',[(21,408.6,841.9),(22,0,325.1)],'网友回忆版（xingce版；资料题号与 xing-ce1 版 GK2022F 不同）'),
 'ZLM-SZ2024-2':('SZ2024_xc','SZ2024',[(16,137.0,682.2)],''),
 'ZLM-SD2020-3':('SD2020_xc','SD2020',[(11,98.0,315.0)],''),
 'ZLM-GK2019D-1':('GK2019D','GK2019D',[(11,407.5,794.0)],''),
 'ZLM-GK2021D-4':('GK2021D','GK2021D',[(17,59.0,277.0)],''),
 'ZLM-GK2019F-4':('GK2019F','GK2019F',[(15,205.5,396.1)],''),
 'ZLM-SC2024-1':('SC2024_xc','SC2024',[(16,543.5,727.4)],'网友回忆版'),
 'ZLM-SC2022H-3':('SC2022H_xc','SC2022H',[(22,262.3,519.8)],''),
 'ZLM-GK2024F-4':('GK2024F','GK2024F',[(24,123.2,339.1)],''),
 'ZLM-GK2023F-4':('GK2023F','GK2023F',[(27,648.0,665.0),(28,72.0,290.0)],''),
 'ZLM-GK2025F-2':('GK2025F','GK2025F',[(22,107.1,436.0)],''),
 'ZLM-GK2018D-5':('GK2018D','GK2018D',[(12,748.4,841.9),(13,0,99.9)],'与GK2018F资料（第131-135题）为同一材料'),
 'ZLM-SZ2024-1':('SZ2024_xc','SZ2024',[(15,272.4,530.4)],''),
 'ZLM-ZJ2021A-1':('ZJ2021A_xc','ZJ2021A',[(18,293.1,750.1)],'网友回忆版'),
 'ZLM-ZJ2021A-2':('ZJ2021A_xc','ZJ2021A',[(19,356.7,841.9),(20,0,237.4)],'网友回忆版'),
 'ZLM-SZ2023-1':('SZ2023_xc','SZ2023',[(18,493.8,727.8)],''),
 'ZLM-SD2024-4':('SD2024_xc','SD2024',[(21,629.9,841.9),(22,0,124.9)],''),
 'ZLM-SC2025-1':('SC2025_xc','SC2025',[(16,158.3,358.3)],''),
}
WM = re.compile(r'(第\s*\d+\s*页，共\s*\d+\s*页|本试卷由粉笔用户|网友回忆版\)|网友回忆版）|^\s*-?\s*\d{1,2}\s*-?\s*$|^\s*\d{1,2}\s*$|【认准|淘宝)')
def seg_text(doc, segs):
    out=[]
    for p,y0,y1 in segs:
        pg=doc[p]; r=pymupdf.Rect(0,y0,pg.rect.width,y1)
        t=pg.get_text('text',clip=r)
        for l in t.split('\n'):
            if WM.search(l): continue
            out.append(l.rstrip())
    return '\n'.join(out).strip()
def render(doc, segs, path, dpi=170, xc=False):
    ims=[]
    for p,y0,y1 in segs:
        if xc: y0=max(y0,70.0); y1=min(y1,790.0)
        pg=doc[p]; clip=pymupdf.Rect(20,max(0,y0-2),pg.rect.width-20,min(pg.rect.height,y1+2))
        pix=pg.get_pixmap(clip=clip,dpi=dpi); ims.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    W=max(i.width for i in ims); H=sum(i.height for i in ims)
    c=Image.new('RGB',(W,H),'white'); y=0
    for i in ims: c.paste(i,(0,y)); y+=i.height
    c.save(path); return path
if __name__=='__main__':
    only=sys.argv[1:]
    for mid,(tag,paper,segs,vn) in M.items():
        if only and mid not in only: continue
        doc=pymupdf.open(os.path.join(ROOT,F[tag]))
        os.makedirs(f'{OUT}/{mid}',exist_ok=True)
        png=render(doc,segs,f'{OUT}/{mid}/{mid}.png', 170, xc=F[tag].startswith('xingce/'))
        txt=seg_text(doc,segs)
        json.dump(dict(mid=mid,tag=tag,paper=paper,file=F[tag],segs=segs,raw_text=txt),open(f'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zlb/mat_raw_{mid}.json','w'),ensure_ascii=False)
        print('##',mid, png, len(txt))
