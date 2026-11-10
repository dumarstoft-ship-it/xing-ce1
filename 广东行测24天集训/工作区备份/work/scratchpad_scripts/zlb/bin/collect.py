import json, re
ITEMS = [
 # (group, tag, qno)
 ('G1','GK2022F_xc',116),('G1','GK2022F_xc',117),('G1','GK2022F_xc',118),
 ('G1','GD2025_xc',71),('G1','GD2025_xc',75),('G1','GD2026_xc',78),('G1','GD2026_xc',83),('G1','GD2026_xc',84),('G1','GD2026_xc',85),
 ('G1','GD2023X_xc',86),('G1','GD2022X_xc',89),('G1','GD2020Z',98),('G1','GD2020Z',100),('G1','SZ2024_xc',91),('G1','SD2020_xc',86),
 ('G1','GK2019D',112),('G1','GK2019D',114),('G1','GK2021D',126),('G1','GK2021D',128),('G1','GD2024_xc',87),
 ('G2','GD2026_xc',71),('G2','GD2026_xc',72),('G2','GD2026_xc',75),('G2','GD2026_xc',77),('G2','GD2026_xc',90),
 ('G2','GD2025_xc',76),('G2','GD2025_xc',77),('G2','GD2025_xc',79),('G2','GD2025_xc',80),
 ('G2','GD2024_xc',73),('G2','GD2024_xc',75),('G2','GD2024_xc',85),('G2','GD2022X_xc',90),
 ('G2','GD2017',94),('G2','GD2017',99),('G2','GD2017',100),('G2','GK2019F',135),('G2','SC2024_xc',90),('G2','SC2022H_xc',100),('G2','GK2024F',135),
 ('G3','GD2026_xc',73),('G3','GD2026_xc',74),('G3','GD2026_xc',80),('G3','GD2025_xc',74),('G3','GD2025_xc',78),('G3','GD2024_xc',71),('G3','GD2024_xc',72),
 ('G3','GD2024_xc',83),('G3','GD2022X_xc',87),('G3','GD2022X_xc',91),('G3','GD2023X_xc',88),('G3','GD2020Z',99),('G3','GD2018',89),
 ('G3','GK2023F',122),('G3','GK2025F',122),('G3','GK2025F',123),
]
out=[]
for g,tag,q in ITEMS:
    d=json.load(open(f'/home/user/work/index/{tag}.json'))
    x=[e for e in d if e['kind']=='q' and e['qno']==q][0]
    out.append(dict(group=g,tag=tag,qno=q,file=x['file'],segs=x['segs'],material=x.get('material'),text=x['text'],nimg=len(x['images'])))
json.dump(out,open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zlb/items_raw.json','w'),ensure_ascii=False,indent=0)
print(len(out))
for o in out: print(o['group'],o['tag'],o['qno'],'p',o['segs'][0][0]+1,o['material'],o['nimg'])
