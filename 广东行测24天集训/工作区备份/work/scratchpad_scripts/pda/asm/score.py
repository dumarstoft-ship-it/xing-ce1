import json, numpy as np, itertools
from PIL import Image, ImageFilter
exec(open('asm.py').read().split('FULL=')[0])
from render import render
res=json.load(open('comps.json'))
comps=[[tuple(x) for x in c] for c in res["((0, 1, 0), (0, 2, 0))"]]
def edges(im):
    a=np.array(im.convert('L'))<128
    ys,xs=np.nonzero(a)
    a=a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return a
def dil(a,r=6):
    im=Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2*r+1))
    return np.array(im)>0
def sim(a,b):
    H=max(a.shape[0],b.shape[0]); W=max(a.shape[1],b.shape[1])
    A=np.zeros((H,W),bool); B=np.zeros((H,W),bool)
    A[:a.shape[0],:a.shape[1]]=a; B[:b.shape[0],:b.shape[1]]=b
    da,db=dil(A),dil(B)
    # precision/recall of edge pixels
    p=(A&db).sum()/max(1,A.sum()); r=(B&da).sum()/max(1,B.sum())
    return 2*p*r/max(1e-9,p+r)
opts={}
for c in 'ABCD':
    im=Image.open(f'../r/z_gd20x43_o{c}.png').convert('RGB')
    w,h=im.size
    im=im.crop((18,4,w-18,h-4))
    a=np.array(im.convert('L'))<128
    # drop columns/rows that are almost fully dark lines (panel borders)
    cols=a.sum(0)>0.8*a.shape[0]; a[:,cols]=False
    rows=a.sum(1)>0.8*a.shape[1]; a[rows,:]=False
    ys,xs=np.nonzero(a); a=a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    opts[c]=a
for ci,R in enumerate(comps):
    best={c:(0,None) for c in 'ABCD'}
    for o in orientations(R):
        im=render(list(o),X0=150,Y0=560,W=900,H=800)
        e=edges(im)
        for c in 'ABCD':
            s=sim(e,opts[c])
            if s>best[c][0]: best[c]=(s,o)
    print('complement',ci,{c:round(best[c][0],3) for c in 'ABCD'})
