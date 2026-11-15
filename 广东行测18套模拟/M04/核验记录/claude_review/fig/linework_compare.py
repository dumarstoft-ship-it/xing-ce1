"""Line weight / grey fill / triangle-apex comparison between original and redrawn figures, in mm at the print
size each would get (original: bbox_pt print size; redrawn: 120 mm width as in the review PDF)."""
import numpy as np, json
from PIL import Image
R='/home/user/xing-ce1/'
def runs(mask):
    out=[];s=None
    for i,v in enumerate(mask):
        if v and s is None: s=i
        if not v and s is not None: out.append((s,i-1)); s=None
    if s is not None: out.append((s,len(mask)-1))
    return out
def line_widths_px(path, y0, y1, x0, x1, thr):
    a=np.array(Image.open(path).convert('L'))<128
    cs=a[y0:y1,x0:x1].sum(axis=0)
    return [b-a_+1 for a_,b in runs(cs>thr)]
cases={
 'Q46 grid lines': (R+'模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i00.png',(60,70,10,100,6),117.7/600,
                    R+'广东行测18套模拟/M04/assets/q46_pixel_shift.png',(300,340,60,500,30),120/3600),
 'Q47 grid lines': (R+'模考/2026下半年广东卷_16-33季_AI可读/assets/s25_p11_i00.png',(20,30,40,95,6),117.7/600,
                    R+'广东行测18套模拟/M04/assets/q47_growing_path.png',(100,140,160,500,30),120/3600),
 'Q49 net lines':  (R+'模考/2026下半年广东卷_16-33季_AI可读/assets/s22_p13_i01.png',(40,62,95,225,15),117.7/600,
                    R+'广东行测18套模拟/M04/assets/q49_cube_nets.png',(330,420,820,1400,60),120/3720),
 'Q50 stem lines': (R+'模考/2026下半年广东卷_16-33季_AI可读/assets/s26_p13_i00.png',(70,95,180,300,18),98.1/500,
                    R+'广东行测18套模拟/M04/assets/q50_solids.png',(700,780,1380,1900,60),120/3600),
}
for k,(op,(y0,y1,x0,x1,t),omm,rp,(ry0,ry1,rx0,rx1,rt),rmm) in cases.items():
    ow=line_widths_px(op,y0,y1,x0,x1,t); rw=line_widths_px(rp,ry0,ry1,rx0,rx1,rt)
    print(f'{k}: original px {ow} -> mm {[round(w*omm,2) for w in ow]} | redrawn px {rw} -> mm {[round(w*rmm,3) for w in rw]}')
# grey fill of right faces in Q50
o=np.array(Image.open(R+'模考/2026下半年广东卷_16-33季_AI可读/assets/s26_p13_i00.png').convert('L')).astype(int)
r=np.array(Image.open(R+'广东行测18套模拟/M04/assets/q50_solids.png').convert('L')).astype(int)
ov,oc=np.unique(o[(o>120)&(o<245)],return_counts=True); rv,rc=np.unique(r[(r>120)&(r<245)],return_counts=True)
print('Q50 grey fill: original dominant', ov[np.argmax(oc)], '| redrawn dominant', rv[np.argmax(rc)])
