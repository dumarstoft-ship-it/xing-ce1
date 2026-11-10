import json, re, collections
inv=json.load(open('inv.json'))
ana=json.load(open('anaseg.json'))
ansj={}
import os
for f in os.listdir('/home/user/work/answers'):
    ansj[f[:-5]]=json.load(open('/home/user/work/answers/'+f))['answers']
POS = re.compile(r'平移|旋转|翻转|顺时针|逆时针|位置|移动|左右翻|上下翻|镜像|对称轴方向|走[一二三四五六七八九十\d]格|相对位置|移[一二三四五六七八九十\d]')
def anatag(r):
    tag=r['tag']
    cand=[tag, tag.replace('_xc',''), tag+'_xc' if not tag.endswith('_xc') else tag]
    for c in cand:
        if c in ana and str(r['qno']) in ana[c]['segs']:
            return c, ana[c]['segs'][str(r['qno'])]
    return None, None
rows=[]
for r in inv:
    if r['typ'] not in ('P','PS?','other'): continue
    c,s=anatag(r)
    txt=s['text'] if s else ''
    kw=sorted(set(POS.findall(txt)))
    rows.append(dict(r, ana=c, ana_page=s['page'] if s else None, poskw=kw, atext=txt[:600]))
json.dump(rows,open('planar_cls.json','w'),ensure_ascii=False)
for r in rows:
    if r['poskw'] and r['taken'] is None:
        yr=re.search(r'20\d\d',r['pid'])
        print(r['tag'],r['qno'],r['taken'],r['poskw'])
