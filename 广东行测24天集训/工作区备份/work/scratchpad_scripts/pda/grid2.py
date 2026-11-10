import sys
from PIL import Image
import numpy as np
im=np.array(Image.open('r/z_gk19d74_42.png').convert('L')).astype(float)
def panel(x0,x1,y0,y1):
    sub=im[y0:y1,x0:x1]<140
    # bounding box of content excluding borders: find rows/cols with dark pixels after removing 3px border
    sub2=sub[3:-3,3:-3]
    ys=np.where(sub2.any(1))[0]; xs=np.where(sub2.any(0))[0]
    by0,by1=ys[0]+3+y0, ys[-1]+3+y0; bx0,bx1=xs[0]+3+x0, xs[-1]+3+x0
    g=np.zeros((5,5),int)
    for r in range(5):
        for c in range(5):
            cy=by0+(r+0.5)*(by1-by0)/5; cx=bx0+(c+0.5)*(bx1-bx0)/5
            v=im[int(cy)-1:int(cy)+2,int(cx)-1:int(cx)+2].mean()
            g[r,c]=1 if v<128 else 0
    def comps(g,diag):
        seen=set(); n=0
        for r in range(5):
            for c in range(5):
                if g[r,c] and (r,c) not in seen:
                    n+=1; st=[(r,c)]; seen.add((r,c))
                    while st:
                        a,b=st.pop()
                        for da in (-1,0,1):
                            for db in (-1,0,1):
                                if (da,db)==(0,0) or (not diag and da and db): continue
                                x,y=a+da,b+db
                                if 0<=x<5 and 0<=y<5 and g[x,y] and (x,y) not in seen: seen.add((x,y)); st.append((x,y))
        return n
    n=comps(g,False); n8=comps(g,True)
    return g,n,n8,(bx0,bx1,by0,by1)
P={'s1':(10,64,2,60),'s2':(64,119,2,60),'s3':(119,173,2,60),'t1':(221,275,2,60),'t2':(275,330,2,60),
   'A':(88,143,76,134),'B':(143,197,76,134),'C':(197,252,76,134),'D':(252,306,76,134)}
for k,v in P.items():
    g,n,n8,bb=panel(*v)
    print(k,'parts4=',n,'parts8=',n8,'black=',g.sum(),bb)
    for row in g: print('   ',''.join('#' if x else '.' for x in row))
