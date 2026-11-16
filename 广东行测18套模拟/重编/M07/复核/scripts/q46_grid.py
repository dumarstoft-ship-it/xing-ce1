# Q46: extract 4x4 black/white grids from each panel of the figure
from PIL import Image
import sys
P='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s22_p11_i07.png'
im=Image.open(P).convert('L')
W,H=im.size

def col_profile(y0,y1):
    return [sum(1 for y in range(y0,y1) if im.getpixel((x,y))<128) for x in range(W)]

def find_grids(y0,y1):
    # find vertical runs of dark columns within the rows y0..y1 -> grid outer borders
    prof=col_profile(y0,y1)
    return prof

def runs(arr,thr):
    out=[];s=None
    for i,v in enumerate(arr):
        if v>=thr and s is None: s=i
        if v<thr and s is not None: out.append((s,i-1)); s=None
    if s is not None: out.append((s,len(arr)-1))
    return out

# Row bands
for (y0,y1,name) in [(24,89,'top'),(149,214,'bottom')]:
    prof=col_profile(y0,y1)
    h=y1-y0
    r=runs(prof,int(h*0.9))
    print(name,'full-dark column runs:',r)

def grid(xlines,ylines):
    g=[]
    for i in range(4):
        row=''
        for j in range(4):
            x0=xlines[j][1]+1; x1=xlines[j+1][0]-1
            y0=ylines[i][1]+1; y1=ylines[i+1][0]-1
            tot=0;dk=0
            for x in range(x0+2,x1-1):
                for y in range(y0+2,y1-1):
                    tot+=1; dk+= im.getpixel((x,y))<128
            row+= '#' if dk/tot>0.5 else '.'
        g.append(row)
    return g

top_y=[(24,26),(40,42),(55,57),(71,73),(86,88)]
bot_y=[(149,151),(165,167),(180,182),(196,198),(211,213)]
panels={
 '1':[(24,26),(40,41),(55,57),(70,72),(86,88)],
 '2':[(122,124),(138,139),(153,155),(169,171),(184,186)],
 '3':[(219,221),(235,236),(250,252),(266,268),(281,283)],
 '4':[(316,318),(331,333),(347,349),(363,364),(378,380)],
 '5':[(414,416),(430,431),(445,447),(461,463),(476,478)],
}
opts={
 'A':[(121,123),(136,138),(152,153),(167,169),(183,185)],
 'B':[(218,220),(234,236),(249,251),(265,266),(280,282)],
 'C':[(317,319),(332,334),(348,349),(363,365),(379,381)],
 'D':[(414,416),(430,431),(445,447),(461,463),(476,478)],
}
G={}
for k,xl in panels.items(): G[k]=grid(xl,top_y)
for k,xl in opts.items(): G[k]=grid(xl,bot_y)
keys=list(G.keys())
for i in range(4):
    print('   '.join(G[k][i] for k in keys))
print('   '.join(k.ljust(4) for k in keys))
for k in keys:
    print(k,'black count',sum(r.count('#') for r in G[k]))
