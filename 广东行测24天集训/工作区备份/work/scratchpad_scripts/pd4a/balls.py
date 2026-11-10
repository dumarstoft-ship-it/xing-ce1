"""ball-lattice readers. All return dict or list of 'B'/'W' """
from panels import *
def bbox_content(sub, thr=150):
    m=sub<thr; ys,xs=np.where(m); return xs.min(),ys.min(),xs.max()+1,ys.max()+1
def sq(a, box, nr, nc, margin=8, thr=110, r=0.18):
    sub=crop(a,box,margin); x0,y0,x1,y1=bbox_content(sub); w=(x1-x0)/nc; h=(y1-y0)/nr; out=[]
    for i in range(nr):
        row=''
        for j in range(nc):
            cy=y0+(i+0.5)*h; cx=x0+(j+0.5)*w
            v=sub[int(cy-h*r):int(cy+h*r)+1, int(cx-w*r):int(cx+w*r)+1].mean()
            row+='B' if v<thr else 'W'
        out.append(row)
    return out
def hexrows(a, box, rows=(3,4,5,4,3), margin=8, thr=110, r=0.16):
    """hexagonal cluster with horizontal rows (pointy arrangement: widest row in the middle)"""
    sub=crop(a,box,margin); x0,y0,x1,y1=bbox_content(sub); n=max(rows); d=(x1-x0)/n; cx=(x0+x1)/2; k=len(rows); out=[]
    for i,mm in enumerate(rows):
        y=y0+d/2+i*((y1-y0)-d)/(k-1); row=''
        for j in range(mm):
            x=cx+(j-(mm-1)/2)*d
            v=sub[int(y-d*r):int(y+d*r)+1, int(x-d*r):int(x+d*r)+1].mean(); row+='B' if v<thr else 'W'
        out.append(row)
    return out
def hexcols(a, box, cols=(3,4,5,4,3), margin=8, thr=110, r=0.16):
    """hexagonal cluster with vertical columns (widest column in the middle); returns list of column strings top->bottom"""
    sub=crop(a,box,margin); x0,y0,x1,y1=bbox_content(sub); n=max(cols); d=(y1-y0)/n; cy=(y0+y1)/2; k=len(cols); out=[]
    for i,mm in enumerate(cols):
        x=x0+d/2+i*((x1-x0)-d)/(k-1); col=''
        for j in range(mm):
            y=cy+(j-(mm-1)/2)*d
            v=sub[int(y-d*r):int(y+d*r)+1, int(x-d*r):int(x+d*r)+1].mean(); col+='B' if v<thr else 'W'
        out.append(col)
    return out
def tri(a, box, n=5, margin=8, thr=110, r=0.16):
    """triangular cluster rows 1..n"""
    sub=crop(a,box,margin); x0,y0,x1,y1=bbox_content(sub); d=(x1-x0)/n; cx=(x0+x1)/2; out=[]
    for i in range(n):
        y=y0+d/2+i*((y1-y0)-d)/(n-1); row=''
        for j in range(i+1):
            x=cx+(j-i/2)*d
            v=sub[int(y-d*r):int(y+d*r)+1, int(x-d*r):int(x+d*r)+1].mean(); row+='B' if v<thr else 'W'
        out.append(row)
    return out
def op(p,q,table):
    return [''.join(table[a+b] for a,b in zip(r1,r2)) for r1,r2 in zip(p,q)]
