import json, re, pymupdf, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
IDX='/home/user/work/index'
def qmap(tag):
    d=json.load(open(f'{IDX}/{tag}.json'))
    return {x['qno']:x for x in d if x['kind']=='q'}, d[0]['file']
DPAT=re.compile(r'(^|\s)D\s*[、\.．]|D、|D\.')
def mat_segs(tag, firstq):
    qm,f=qmap(tag)
    doc=pymupdf.open('/home/user/'+f)
    cur=qm[firstq]; (p2,y2,_)=cur['segs'][0]
    prev=qm.get(firstq-1)
    # search backwards from (p2,y2) for last block containing a D-option marker
    pages=[p2]+([p2-1] if p2>0 else [])
    for p in pages:
        blocks=doc[p].get_text('blocks')
        lim = y2 if p==p2 else doc[p].rect.height
        cands=[b for b in blocks if b[1] < lim-1 and DPAT.search(unicodedata.normalize('NFKC',b[4]))]
        if cands:
            b=max(cands,key=lambda b:b[3])
            ystart=b[3]+1
            if p==p2: return [[p2,ystart,y2]], f
            return [[p,ystart,doc[p].rect.height],[p2,0,y2]], f
    return None, f
if __name__=='__main__':
    import sys
    print(mat_segs(sys.argv[1], int(sys.argv[2])))
