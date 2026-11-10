import json,pymupdf,unicodedata,re
pymupdf.TOOLS.mupdf_display_errors(False)
# key: (index tag, answers tag or None, anchor text in analysis)
spec={
'GK2022X-103':('GK2022X','GK2022X','电梯促销广告对于提高企业利润'),
'SC2020H-80':('SC2020H_xc','SC2020H_xc','葡萄酒具有保健功效'),
'GK2017F-107':('GK2017F','GK2017F','9 世纪的气候变化或许正是'),
'GDXD2019SW-47':('GDXD2019SW','GDXD2019SW','糟糕的口腔健康问题是令老年人'),
'GK2025D-105':('GK2025D','GK2025D','采样不足'),
'GK2023F-106':('GK2023F','GK2023F','嗅觉中枢'),
'GD2023X-66':('GD2023X','GD2023X','第66 题'),
'GK2024F-113':('GK2024F','GK2024F','人为特征'),
'GDXD2020SW-39':('GDXD2020SW','GDXD2020SW','E 商城服务质量'),
'SD2020-70':('SD2020_xc','SD2020_xc','最善于站立的祖先'),
'GD2022X-67':('GD2022X','GD2022X','67.解析'),
'GK2025D-101':('GK2025D','GK2025D','拔河'),
'GDXD2020SW-20':('GDXD2020SW','GDXD2020SW','重复投稿'),
'GK2024F-110':('GK2024F','GK2024F','多巴胺'),
'SZ2020SW-76':('SZ2020SW_xc','SZ2020SW_xc','新型号CPU 可以显著提升'),
'GD2023X-68':('GD2023X','GD2023X','第68 题'),
'GD2019X-53':('GD2019X',None,None),
'SC2024-81':('SC2024_xc','SC2024_xc','【题目81】'),
'GK2019D-105':('GK2019D','GK2019D','P 波与S 波之间的间隔越短'),
'SD2020-72':('SD2020_xc','SD2020_xc','足迹化石显得尤为重要'),
'GDXD2020SW-5':('GDXD2020SW','GDXD2020SW','为避免罚款'),
'GDXD2019SW-2':('GDXD2019SW','GDXD2019SW','唯一原因'),
'GD2017-57':('GD2017',None,None),
'GD2021Z-64':('GD2021Z',None,None),
'GD2022X-65':('GD2022X','GD2022X','65.解析'),
'GK2019D-102':('GK2019D','GK2019D','心安理得'),
'JS2022A-100':('JS2022A_xc','JS2022A_xc','麦饭'),
'SZ2024-42':('SZ2024_xc','SZ2024_xc','【解析42】'),
'GDXD2020SW-15':('GDXD2020SW','GDXD2020SW','空座率'),
'GD2023X-69':('GD2023X','GD2023X','第69 题'),
'GD2021Z-65':('GD2021Z',None,None),
'GD2020X-65':('GD2020X',None,None),
'GD2017-59':('GD2017',None,None),
'GD2019X-60':('GD2019X',None,None),
'GD2018-57':('GD2018',None,None),
'SD2024-95':('SD2024_xc','SD2024_xc','【解析95'),
'JS2025A-92':('JS2025A_xc','JS2025A_xc','题目92 解析'),
'HB2025-108':('HB2025_xc','HB2025_xc','题目108 解析'),
'GD2020X-57':('GD2020X',None,None),
'GD2017-54':('GD2017',None,None),
'GD2021Z-62':('GD2021Z',None,None),
'GD2018-51':('GD2018',None,None),
}
out={}
for k,(tag,atag,anc) in spec.items():
    pid,q=k.rsplit('-',1); q=int(q)
    d=json.load(open(f'/home/user/work/index/{tag}.json'))
    x=[e for e in d if e['kind']=='q' and e['qno']==q][0]
    rec=dict(file=x['file'],pages=sorted(set(s[0]+1 for s in x['segs'])))
    if atag:
        a=json.load(open(f'/home/user/work/answers/{atag}.json'))
        rec['ans_file']=a['file']
        doc=pymupdf.open('/home/user/'+a['file'])
        pg=None
        for i,p in enumerate(doc):
            t=unicodedata.normalize('NFKC',p.get_text())
            if anc in t: pg=i+1; break
        rec['ans_page']=pg
    out[k]=rec
    print(k,rec)
json.dump(out,open('pages.json','w'),ensure_ascii=False,indent=1)
