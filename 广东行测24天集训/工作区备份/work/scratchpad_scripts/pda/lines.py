import sys
from PIL import Image
import numpy as np
im=np.array(Image.open(sys.argv[1]).convert('L'))<150
H,W=im.shape
x0,x1,y0,y1=[int(v) for v in sys.argv[2].split(',')]
sub=im[y0:y1,x0:x1]
# horizontal segments: rows where long runs exist
def hsegs(sub,minlen=6):
    out=[]
    for r in range(sub.shape[0]):
        row=sub[r]; c=0
        while c<len(row):
            if row[c]:
                s=c
                while c<len(row) and row[c]: c+=1
                if c-s>=minlen: out.append((r,s,c-1))
            else: c+=1
    return out
def vsegs(sub,minlen=6):
    return [(c,s,e) for (c,s,e) in hsegs(sub.T,minlen)]
hs=hsegs(sub); vs=vsegs(sub)
# merge adjacent rows
def merge(segs):
    segs=sorted(segs); out=[]
    for r,s,e in segs:
        if out and r-out[-1][0][1]<=1 and abs(s-out[-1][1])<=2 and abs(e-out[-1][2])<=2:
            out[-1]=((out[-1][0][0],r),min(s,out[-1][1]),max(e,out[-1][2]))
        else: out.append(((r,r),s,e))
    return out
print('H segs (rows, x-from, x-to) offset', x0, y0)
for (a,b),s,e in merge(hs): print('  y=%d-%d  x=%d..%d len=%d'%(a+y0,b+y0,s+x0,e+x0,e-s+1))
print('V segs (cols, y-from, y-to)')
for (a,b),s,e in merge(vs): print('  x=%d-%d  y=%d..%d len=%d'%(a+x0,b+x0,s+y0,e+y0,e-s+1))
