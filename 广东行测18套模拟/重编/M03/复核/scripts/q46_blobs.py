# Q46: locate the filled dot / triangle and the diamond center in each panel
from PIL import Image
import numpy as np
from scipy import ndimage
P='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p11_i00.png'
im=np.array(Image.open(P).convert('L'))
H,W=im.shape
dark=im<128
# find panel separators: vertical lines that are dark across most of the top row strip
def panels(y0,y1):
    col=dark[y0:y1].mean(axis=0)
    xs=[x for x in range(W) if col[x]>0.9]
    # group
    groups=[]
    for x in xs:
        if groups and x-groups[-1][-1]<=2: groups[-1].append(x)
        else: groups.append([x])
    return [ (g[0],g[-1]) for g in groups]
def rows():
    row=dark.mean(axis=1)
    ys=[y for y in range(H) if row[y]>0.3]
    groups=[]
    for y in ys:
        if groups and y-groups[-1][-1]<=2: groups[-1].append(y)
        else: groups.append([y])
    return [(g[0],g[-1]) for g in groups]
print('rows',rows())
for (y0,y1) in [(5,105),(135,225)]:
    seps=panels(y0,y1)
    print('seps',seps)
    for i in range(len(seps)-1):
        x0=seps[i][1]+2; x1=seps[i+1][0]-2
        sub=dark[y0+3:y1-3, x0:x1]
        # filled blobs: erode to remove thin lines
        er=ndimage.binary_erosion(sub, structure=np.ones((3,3)), iterations=1)
        lab,n=ndimage.label(er)
        objs=[]
        for k in range(1,n+1):
            ys,xs=np.where(lab==k)
            if len(ys)<3: continue
            objs.append((len(ys), round(xs.mean()+x0,1), round(ys.mean()+y0+3,1), xs.min()+x0, xs.max()+x0, ys.min()+y0+3, ys.max()+y0+3))
        # diamond & hexagon: lines. Get bounding boxes of line components
        lab2,n2=ndimage.label(sub)
        comps=[]
        for k in range(1,n2+1):
            ys,xs=np.where(lab2==k)
            if len(ys)<40: continue
            comps.append((len(ys), xs.min()+x0, xs.max()+x0, ys.min()+y0+3, ys.max()+y0+3, round((xs.min()+xs.max())/2+x0,1), round((ys.min()+ys.max())/2+y0+3,1)))
        print('panel',i,'filled blobs',objs)
        print('    line comps',comps)
