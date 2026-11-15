import math, json
# Analytical checks on the q67 v0.2.0 geometry vs source
O=(195,13)
new={'A':((195,13),(156,13),(117,69)),'B':((195,13),(166,13),(137,84))}
src={'A':((195,13),(163,13),(123,28),(117,69)),'B':((195,13),(170,17),(149,39),(137,84))}
def qb(p0,p1,p2,t):
    return tuple((1-t)**2*p0[i]+2*(1-t)*t*p1[i]+t*t*p2[i] for i in range(2))
def cb(p0,p1,p2,p3,t):
    return tuple((1-t)**3*p0[i]+3*(1-t)**2*t*p1[i]+3*(1-t)*t*t*p2[i]+t**3*p3[i] for i in range(2))
res={}
for k in 'AB':
    p0,p1,p2=new[k]
    dx=p0[0]-p2[0]; dy=p2[1]-p0[1]
    # parabola check: sample points, compare to y=13+dy*((195-x)/dx)^2
    err=max(abs(qb(p0,p1,p2,t)[1]-(13+dy*((195-qb(p0,p1,p2,t)[0])/dx)**2)) for t in [i/50 for i in range(51)])
    end_slope_new=2*(p2[1]-p1[1])/(2*(p1[0]-p2[0]))  # derivative at end ~ (p2-p1)
    q=src[k]
    end_slope_src=(q[3][1]-q[2][1])/(q[2][0]-q[3][0])
    start_slope_src=(q[1][1]-q[0][1])/(q[0][0]-q[1][0])
    phys_end_slope=2*dy/dx
    res[k]=dict(landing=p2,dx=dx,drop=dy,parabola_max_err=round(err,6),
                end_slope_new=round(end_slope_new,3),phys_end_slope=round(phys_end_slope,3),
                end_angle_new_deg=round(math.degrees(math.atan(end_slope_new)),1),
                src_start_slope=round(start_slope_src,3),src_end_slope=round(end_slope_src,3),
                src_end_angle_deg=round(math.degrees(math.atan(end_slope_src)),1),
                v_rel=round(dx/math.sqrt(dy),3), t_rel=round(math.sqrt(dy),3))
# A height when crossing x=137 (corner x)
pA=new['A']; t=(195-137)/78; res['A_y_at_corner_x']=round(13+56*t*t,2)
# source A at x=137 (cubic, solve numerically)
q=src['A']
lo,hi=0,1
for _ in range(60):
    m=(lo+hi)/2
    if cb(*q,m)[0]>137: lo=m
    else: hi=m
res['src_A_y_at_corner_x']=round(cb(*q,lo)[1],2)
# do new curves intersect (other than O)?
kA=56/78**2; kB=71/58**2
res['kA,kB']=(round(kA,6),round(kB,6))
# distance from label boxes to curves (Arial cap height ~0.716em, 'A' width ~0.667em, 'B' ~0.667em)
def mind(box,curve):
    x0,y0,x1,y1=box
    best=1e9
    for i in range(2001):
        t=i/2000
        x,y=qb(*curve,t)
        dx=max(x0-x,0,x-x1); dy=max(y0-y,0,y-y1)
        best=min(best,math.hypot(dx,dy))
    return best
fs=9.5
boxA=(147,26-0.716*fs,147+0.667*fs,26)
boxB=(154,64-0.716*fs,154+0.667*fs,64)
res['labelA_to_curveA']=round(mind(boxA,new['A']),2)
res['labelA_to_curveB']=round(mind(boxA,new['B']),2)
res['labelB_to_curveB']=round(mind(boxB,new['B']),2)
res['labelB_to_curveA']=round(mind(boxB,new['A']),2)
print(json.dumps(res,ensure_ascii=False,indent=1))
