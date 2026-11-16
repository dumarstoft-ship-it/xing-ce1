# Q48: sample the 10x5 black/white tiling and the 3x3 options
from PIL import Image
P='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s22_p12_i01.png'
im=Image.open(P).convert('L')
W,H=im.size

def cellval(cx,cy,r=6):
    tot=dk=0
    for x in range(int(cx-r),int(cx+r)+1):
        for y in range(int(cy-r),int(cy+r)+1):
            tot+=1; dk+=im.getpixel((x,y))<128
    return dk/tot

x0,x1,y0,y1=65,429,4,189
nc,nr=10,5
cw=(x1-x0+1)/nc; ch=(y1-y0+1)/nr
print('cell',cw,ch)
G=[]
for r in range(nr):
    row=''
    for c in range(nc):
        cx=x0+(c+0.5)*cw; cy=y0+(r+0.5)*ch
        v=cellval(cx,cy)
        row+= '#' if v>0.6 else ('.' if v<0.4 else '?')
    G.append(row)
for row in G: print(row)

def runs(arr,f):
    out=[];s=None
    for i,v in enumerate(arr):
        if f(v) and s is None: s=i
        if not f(v) and s is not None: out.append((s,i-1)); s=None
    if s is not None: out.append((s,len(arr)-1))
    return out
# locate option inner squares: rows ~200..330
for y in [200,205,210,215,220,250,300,320,325,330]:
    row=[im.getpixel((x,y)) for x in range(W)]
    print(y, runs(row, lambda v:v<128)[:30])

# option inner squares (x ranges) and y range ~ 210..320
optx={'A':(11,121),'B':(133,242),'C':(255,364),'D':(377,486)}
oy0,oy1=210,320
O={}
for k,(ax,bx) in optx.items():
    cw=(bx-ax+1)/3; ch=(oy1-oy0+1)/3
    g=[]
    for r in range(3):
        s=''
        for c in range(3):
            v=cellval(ax+(c+0.5)*cw, oy0+(r+0.5)*ch)
            s+='#' if v>0.6 else ('.' if v<0.4 else '?')
        g.append(s)
    O[k]=g
    print(k,g)

# rule check: white iff (c - r) % 3 == 2 over the visible cells
ok=True
for r in range(5):
    for c in range(10):
        if 2<=r<=4 and 3<=c<=5: continue
        pred='.' if (c-r)%3==2 else '#'
        if G[r][c]!=pred: ok=False; print('mismatch',r,c)
print('diagonal-stripe rule fits all visible cells:',ok)
miss=[''.join('.' if (c-r)%3==2 else '#' for c in range(3,6)) for r in range(2,5)]
print('predicted missing block:',miss)
for k,g in O.items(): print(k,'match' if g==miss else 'no')
