"""helpers to read n x n cell patterns inside framed panels"""
from panels import *
def cellgrid(a, box, n=3, margin=8, thr=128):
    """inside a framed panel: find the content bbox (the small n x n figure) and sample n x n cells -> list of strings 'B'/'W'"""
    sub=crop(a,box,margin); m=sub<150; ys,xs=np.where(m)
    if len(ys)<50: return None
    x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    w=(x1-x0)/n; h=(y1-y0)/n; out=[]
    for i in range(n):
        row=''
        for j in range(n):
            cy=y0+(i+0.5)*h; cx=x0+(j+0.5)*w
            v=sub[int(cy-h*0.2):int(cy+h*0.2)+1, int(cx-w*0.2):int(cx+w*0.2)+1].mean()
            row+='B' if v<thr else 'W'
        out.append(row)
    return out
def xor(p,q,same='W',diff='B'):
    return [''.join(same if a==b else diff for a,b in zip(r1,r2)) for r1,r2 in zip(p,q)]
