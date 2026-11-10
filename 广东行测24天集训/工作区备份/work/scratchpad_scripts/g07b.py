import itertools
from fractions import Fraction as F
G=[(3,4,5),(6,6,12),(12,8,28),(21,24,51)]
O={'A':(33,48,63),'B':(27,32,85),'C':(36,48,108),'D':(33,64,95)}
# cross-group linear: next[j] = x*a+y*b+z*c+w*n + v
print("cross-group linear relations (3 transitions) with small coeffs:")
for j,nm in enumerate('abc'):
    for x,y,z in itertools.product(range(-3,4),repeat=3):
        for v in range(-12,13):
            ok=all(G[i+1][j]==x*G[i][0]+y*G[i][1]+z*G[i][2]+v for i in range(3))
            if ok:
                pred=x*G[3][0]+y*G[3][1]+z*G[3][2]+v
                hits=[k for k,o in O.items() if o[j]==pred]
                print("  next_%s = %d*a+%d*b+%d*c%+d -> %d  options:%s"%(nm,x,y,z,v,pred,hits))
# within-group: c = x*a + y*b + v (small), b = ..., a = ...
print("within-group linear relations:")
for (ti,tj,tk) in [(0,1,2),(0,2,1),(1,2,0)]:
    for x,y in itertools.product([F(p,q) for p in range(-6,7) for q in (1,2,3)],repeat=2):
        for v in range(-20,21):
            ok=all(g[tk]==x*g[ti]+y*g[tj]+v for g in G)
            if ok:
                hits=[k for k,o in O.items() if o[tk]==x*o[ti]+y*o[tj]+v]
                print("  pos%d = %s*pos%d + %s*pos%d %+d  options:%s"%(tk,x,ti,y,tj,v,hits))
# within-group multiplicative-ish: c = a*b/k + m*a + ...
print("within-group nonlinear relations:")
exprs={
 'a*b':lambda a,b,c:a*b,'a*c':lambda a,b,c:a*c,'b*c':lambda a,b,c:b*c,'a^2':lambda a,b,c:a*a,'b^2':lambda a,b,c:b*b,'c^2':lambda a,b,c:c*c,
 'a':lambda a,b,c:a,'b':lambda a,b,c:b,'c':lambda a,b,c:c,
}
names=list(exprs)
vals={n:[F(exprs[n](*g)) for g in G] for n in names}
ovals={k:{n:F(exprs[n](*o)) for n in names} for k,o in O.items()}
coefs=[F(p,q) for p in range(-4,5) for q in (1,2,3,4) if p!=0]
coefs=sorted(set(coefs))
found=0
for n1,n2,n3 in itertools.combinations(names,3):
    for c1 in coefs:
        for c2 in coefs:
            # c3 fixed to -1 normalization: c1*n1 + c2*n2 = n3 + const
            consts=[c1*vals[n1][i]+c2*vals[n2][i]-vals[n3][i] for i in range(4)]
            if all(x==consts[0] for x in consts):
                hits=[k for k in O if c1*ovals[k][n1]+c2*ovals[k][n2]-ovals[k][n3]==consts[0]]
                print("  %s*%s + %s*%s - %s = %s  options:%s"%(c1,n1,c2,n2,n3,consts[0],hits)); found+=1
print("found",found)
