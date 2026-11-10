import pymupdf,unicodedata,re,sys,json,bisect
pymupdf.TOOLS.mupdf_display_errors(False)
Q=[('GD2024',[71,72,73,75,83,85,87]),('GD2023X',[86,88]),('GD2022X',[87,89,90,91]),('SZ2024_xc',[91]),('SD2020_xc',[86]),
   ('GK2019D',[112,114]),('GK2021D',[126,128]),('GK2024F',[135]),('GK2023F',[122]),('GK2025F',[122,123]),('GK2019F',[135]),('SC2024_xc',[90]),('SC2022H_xc',[100])]
for tag,qs in Q:
    a=json.load(open(f'/home/user/work/answers/{tag}.json'))
    d=pymupdf.open('/home/user/'+a['file'])
    pages=[unicodedata.normalize('NFKC',p.get_text()) for p in d]
    t='\n'.join(pages); offs=[];o=0
    for p in pages: offs.append(o); o+=len(p)+1
    print('#####',tag,a['file'])
    for q in qs:
        pats=[rf'第\s*{q}\s*题',rf'【题目\s*{q}】',rf'题目\s*{q}\s*解析',rf'(?:^|\n)\s*{q}\s*[、\.．]\s*(?:【|正确|根据|定位|本题|A|第)',rf'(?:^|\n)\s*{q}\s*\n']
        hit=None
        for pt in pats:
            ms=list(re.finditer(pt,t))
            # take the last match in the second half (analysis section of data analysis is near the end)
            ms=[m for m in ms if m.start()>len(t)*0.5]
            if ms: hit=ms[0]; break
        if not hit: print(q,'NOT FOUND'); continue
        pg=bisect.bisect_right(offs,hit.start())
        seg=t[hit.start():hit.start()+900]
        am=re.search(r'(?:正确答案(?:是|为)?\s*[:：]?\s*【?\s*([A-D])|故正确答案为\s*([A-D])|故(?:本题)?选\s*([A-D])|选择\s*([A-D])\s*选项|因此,?选择\s*([A-D]))',seg)
        ans=next((g for g in am.groups() if g),None) if am else None
        print(q,'page',pg,'ans',ans,'|',re.sub(r'\s+',' ',seg[:160]))
