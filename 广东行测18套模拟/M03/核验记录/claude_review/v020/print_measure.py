import sys, json
from PIL import Image
import numpy as np

def load(p):
    return np.array(Image.open(p).convert('L'))
out={}
# ---------- Q67 ----------
p67="/home/user/xing-ce1/广东行测18套模拟/M03/assets/q67_projectile_v020.png"
a=load(p67); H,W=a.shape; S=W/216.0
for Wmm in (42.5,60,70):
    mmpp=Wmm/W
    d=a<128
    # label glyph boxes (search windows in svg units -> px)
    res={}
    for name,(x0,y0,x1,y1) in {'O':(199,6,214,19),'A':(145,16,156,28),'B':(152,54,163,66)}.items():
        sub=d[int(y0*S):int(y1*S),int(x0*S):int(x1*S)]
        ys,xs=np.nonzero(sub)
        res[name+'_glyph_h_mm']=round((ys.max()-ys.min()+1)*mmpp,2)
        res[name+'_glyph_w_mm']=round((xs.max()-xs.min()+1)*mmpp,2)
    res['dash_stroke_mm']=round(1.1*S*mmpp,3)
    res['dash_len_mm']=round(3.2*S*mmpp,2); res['dash_gap_mm']=round(1.8*S*mmpp,2)
    res['wall_thickness_mm']=(round(9*S*mmpp,2),round(8*S*mmpp,2))
    res['O_dot_diam_mm']=round(4.2*S*mmpp,2)
    res['A_land_left_of_corner_mm']=round(20*S*mmpp,2)
    res['B_land_below_top_mm']=round(15*S*mmpp,2)
    res['B_land_below_bar_underside_mm']=round(6*S*mmpp,2)
    res['labelA_clear_to_curveA_mm']=round((2.38-0.55)*S*mmpp,2)
    res['A_visible_end_gap_mm']=round(1.57*S*mmpp,2)
    res['fig_h_mm']=round(H*mmpp,1); res['dpi']=round(W/(Wmm/25.4))
    out[f'q67@{Wmm}mm']=res
# ---------- Q68 ----------
p68="/home/user/xing-ce1/广东行测18套模拟/M03/assets/q68_particles_v020.png"
b=load(p68); H2,W2=b.shape; S2=W2/1200.0
for Wmm in (120,130,140,150):
    mmpp=Wmm/W2; d=b<128
    res={}
    texts={'反应前':(200,5,320,45),'反应后':(885,5,1005,45),'点燃':(560,145,640,185),'碳原子':(335,370,420,410),'氧原子':(585,370,670,410),'氢原子':(835,370,920,410)}
    for name,(x0,y0,x1,y1) in texts.items():
        sub=d[int(y0*S2):int(y1*S2),int(x0*S2):int(x1*S2)]
        ys,xs=np.nonzero(sub)
        res[name+'_h_mm']=round((ys.max()-ys.min()+1)*mmpp,2)
    res['font_em_mm']=round(26*S2*mmpp,2); res['font_em_pt']=round(26*S2*mmpp/25.4*72,1)
    res['H_diam_mm']=round(24*S2*mmpp,2); res['C_O_diam_mm']=round(44*S2*mmpp,2)
    res['outline_stroke_mm']=round(2.5*S2*mmpp,3)
    res['hatch_stroke_mm']=round(1.5*S2*mmpp,3)
    res['hatch_pitch_mm']=round(8/2**0.5*S2*mmpp,2)
    res['arrow_stroke_mm']=round(3*S2*mmpp,3)
    res['fig_h_mm']=round(H2*mmpp,1); res['dpi']=round(W2/(Wmm/25.4))
    out[f'q68@{Wmm}mm']=res
# measure actual hatch stroke width in px: scan a horizontal line through an O atom center (svg 333,135)
row=b[int(135*S2), int((333-20)*S2):int((333+20)*S2)]
dark=row<128
runs=[];cur=0
for v in dark:
    if v: cur+=1
    elif cur: runs.append(cur); cur=0
if cur: runs.append(cur)
out['q68_hatch_horizontal_runs_px_through_O_center']=runs
# outline thickness px: vertical scan through C atom top edge (svg 150, 113)
col=b[int((135-30)*S2):int((135-15)*S2), int(150*S2)]
out['q68_C_top_edge_profile']=[int(v) for v in col]
# 'gray level' of hatched disc vs white disc (mean darkness inside r<18)
yy,xx=np.mgrid[0:H2,0:W2]
def mean_dark(cx,cy,r=18):
    m=np.hypot(xx-cx*S2,yy-cy*S2)<r*S2
    return round(float((255-b[m]).mean()/255),3)
out['q68_mean_ink_O_disc']=mean_dark(333,135); out['q68_mean_ink_C_disc']=mean_dark(150,135,16)
print(json.dumps(out,ensure_ascii=False,indent=1))
