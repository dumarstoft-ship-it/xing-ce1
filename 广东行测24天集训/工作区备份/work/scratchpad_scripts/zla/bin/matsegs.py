import json
IDX='/home/user/work/index'
def qmap(tag):
    d=json.load(open(f'{IDX}/{tag}.json'))
    return {x['qno']:x for x in d if x['kind']=='q'}, d[0]['file']
def mat_segs(tag, firstq, pageh=841.9):
    qm,f=qmap(tag)
    prev=qm.get(firstq-1); cur=qm[firstq]
    (p1,_,y1)=prev['segs'][-1]
    (p2,y2,_)=cur['segs'][0]
    segs=[]
    if p1==p2: segs.append([p1,y1,y2])
    else:
        segs.append([p1,y1,pageh])
        for p in range(p1+1,p2): segs.append([p,0,pageh])
        segs.append([p2,0,y2])
    return segs, f
if __name__=='__main__':
    import sys
    print(mat_segs(sys.argv[1], int(sys.argv[2])))
