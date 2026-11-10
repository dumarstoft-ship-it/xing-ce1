# Sutherland-Hodgman clipping of subject polygon by convex clip polygon
def clip(subject, clipper):
    def inside(p,a,b):
        return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])>=0
    def inter(p1,p2,a,b):
        x1,y1=p1;x2,y2=p2;x3,y3=a;x4,y4=b
        den=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
        t=((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/den
        return (x1+t*(x2-x1),y1+t*(y2-y1))
    # ensure clipper is CCW in math orientation for inside test
    def area(P): return sum(P[i][0]*P[(i+1)%len(P)][1]-P[(i+1)%len(P)][0]*P[i][1] for i in range(len(P)))/2
    if area(clipper)<0: clipper=clipper[::-1]
    out=subject
    for i in range(len(clipper)):
        a,b=clipper[i],clipper[(i+1)%len(clipper)]
        inp=out; out=[]
        if not inp: break
        s=inp[-1]
        for e in inp:
            if inside(e,a,b):
                if not inside(s,a,b): out.append(inter(s,e,a,b))
                out.append(e)
            elif inside(s,a,b): out.append(inter(s,e,a,b))
            s=e
    # remove near-duplicate / collinear points
    res=[]
    for p in out:
        if not res or abs(p[0]-res[-1][0])+abs(p[1]-res[-1][1])>1e-6: res.append(p)
    if len(res)>1 and abs(res[0][0]-res[-1][0])+abs(res[0][1]-res[-1][1])<1e-6: res.pop()
    def col(a,b,c): return abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))<1e-6
    changed=True
    while changed and len(res)>3:
        changed=False
        for i in range(len(res)):
            if col(res[i-1],res[i],res[(i+1)%len(res)]): res.pop(i); changed=True; break
    return res
# coordinates in screen px (y down); orientation irrelevant after normalisation
box2_sq=[(400,48),(568,48),(568,220),(400,220)]; box2_tri=[(420,157),(548,157),(483,265)]
box3_rect=[(704,107),(920,107),(920,240),(704,240)]; box3_pent=[(775,45),(884,65),(902,177),(803,225),(723,145)]
box4_sq=[(1040,103),(1210,103),(1210,255),(1040,255)]; box4_pent=[(1126,37),(1224,108),(1188,230),(1066,230),(1028,108)]
A_tri=[(67,292),(122,398),(14,398)]; A_quad=[(20,341),(118,362),(68,397),(44,385)]
B_rect=[(380,90),(600,90),(600,217),(380,217)]; B_tri=[(383,65),(593,65),(487,250)]
C_rect=[(720,102),(922,102),(922,228),(720,228)]; C_dia=[(785,70),(877,165),(785,258),(693,165)]
for name,s,c in [('box2',box2_tri,box2_sq),('box3',box3_pent,box3_rect),('box4',box4_pent,box4_sq),('A',A_quad,A_tri),('B',B_tri,B_rect),('C',C_dia,C_rect)]:
    r=clip(s,c); print(name,len(r),[(round(x),round(y)) for x,y in r])
