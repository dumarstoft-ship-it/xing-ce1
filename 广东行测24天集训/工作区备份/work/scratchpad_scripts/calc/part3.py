def rng(v, h): return [v-h, v, v+h]
print("==== W10 ====")
o,m,f=264,315,215
p=(o-f)/(m-f); print("male share=%.4f male count=%.0f"%(p,48580*p))
vals=[]
for oo in rng(o,0.5):
  for mm in rng(m,0.5):
    for ff in rng(f,0.5):
      vals.append(48580*(oo-ff)/(mm-ff))
print("  perturb range %.0f .. %.0f"%(min(vals),max(vals)))
# consistency checks
male_unpaid=(162-228*(1-p))/p; fem_part=(70.2-55.3*p)/(1-p); male_hw=(58.5-75.6*(1-p))/p
print("  implied male unpaid=%.1f min, female unpaid participation=%.1f%%, male housework part=%.1f%%"%(male_unpaid,fem_part,male_hw))
print("  traps: 48580*0.553=%.0f 48580*0.59=%.0f 48580*0.6=%.0f"%(48580*0.553,48580*0.59,48580*0.6))

print("==== W11 ====")
w=(264-199)/(290-199); print("weekday weight from paid labor = %.5f (5/7=%.5f)"%(w,5/7))
rest=(162-154*w)/(1-w); print("A: rest-day unpaid = %.2f min (>180? %s)"%(rest,rest>180))
vals=[]
for po in rng(264,0.5):
 for pw in rng(290,0.5):
  for pr in rng(199,0.5):
   ww=(po-pr)/(pw-pr)
   for uo in rng(162,0.5):
    for uw in rng(154,0.5):
      vals.append((uo-uw*ww)/(1-ww))
print("   perturb (all minute figures +-0.5): %.2f .. %.2f"%(min(vals),max(vals)))
vals2=[(uo-uw*5/7)/(2/7) for uo in rng(162,0.5) for uw in rng(154,0.5)]
print("   with exact 5/7 weights, unpaid figures +-0.5: %.2f .. %.2f"%(min(vals2),max(vals2)))
print("   needed weekday weight for rest>180: %.4f"%((180-162)/(180-154)))
print("B: female unpaid participation must exceed overall 70.2%% (male 55.3%% < overall); with p=0.49 -> %.1f%%"%fem_part)
print("C: both paid&unpaid min = %.1f%%, max = %.1f%%"%(59.0+70.2-100, 59.0))
import statistics
t=[86,36,9,8,4,3]; r=[58.5,18.9,10.2,5.0,2.2,4.1]
mt,mr=statistics.mean(t),statistics.mean(r)
cov=sum((a-mt)*(b-mr) for a,b in zip(t,r)); vt=sum((a-mt)**2 for a in t); vr=sum((b-mr)**2 for b in r)
print("D: pearson r=%.4f"%(cov/(vt*vr)**0.5))
def ranks(x):
    s=sorted(x); return [s.index(v)+1 for v in x]
rt,rr=ranks(t),ranks(r); d2=sum((a-b)**2 for a,b in zip(rt,rr)); n=6
print("   spearman rho=%.4f ; rank pairs time/part: %s"%(1-6*d2/(n*(n*n-1)), list(zip(rt,rr))))
print("   counterexample: 看病就医 4min 2.2%% vs 公益活动 3min 4.1%%; 购买商品或服务 no data")

print("==== W14 ====")
print("base 1980末 9.9: %.3f%% ; base 1981末 10.0: %.3f%% ; 1971-80 decade (8.3->9.9): %.3f%% ; 8.5->9.9: %.3f%%"%((11.4/9.9-1)*100,(11.4/10-1)*100,(9.9/8.3-1)*100,(9.9/8.5-1)*100))
vals=[(a/b-1)*100 for a in rng(11.4,0.05) for b in rng(9.9,0.05)]
print("  perturb range %.3f .. %.3f"%(min(vals),max(vals)))
opts={'A':14.0,'B':15.2,'C':16.4,'D':19.3}
for a in rng(11.4,0.05):
  for b in rng(9.9,0.05):
    v=(a/b-1)*100; print("   11.4->%.2f 9.9->%.2f : %.2f%% nearest %s"%(a,b,v,min(opts,key=lambda k:abs(opts[k]-v))))

print("==== W15 ====")
print("28y & 18y: %.1f"%((878*28-711*18)/10))
print("28y & 17y (2002-18), /10: %.1f ; /11: %.1f"%((878*28-711*17)/10,(878*28-711*17)/11))
print("27y & 18y (/9): %.1f"%((878*27-711*18)/9))
print("simple mean (878+711)/2=%.1f"%((878+711)/2))
vals=[(a*28-b*18)/10 for a in rng(878,0.5) for b in rng(711,0.5)]
print("  perturb range %.1f .. %.1f"%(min(vals),max(vals)))

print("==== W16 ====")
p1990=114000; inc9100=(878*28-711*18)
p2000a=p1990+inc9100; p2010a=p2000a+7110
p2018=140000; p2000b=p2018-711*18; p2010b=p2018-711*8
for nm,(a,b) in {"from 1990末11.4亿":(p2000a,p2010a),"back from 14亿":(p2000b,p2010b),"actual NBS":(126743,134091)}.items():
    ratio=0.089*b/(0.036*a); print("  %s: P2000=%d P2010=%d ratio=%.4f growth=%.4f倍"%(nm,a,b,ratio,ratio-1))
vals=[]
for s0 in rng(3.6,0.05):
  for s1 in rng(8.9,0.05):
    for a,b in ((p2000a,p2010a),(p2000b,p2010b)):
      vals.append(s1*b/(s0*a)-1)
print("  perturb growth range %.3f .. %.3f 倍 ; pop-constant growth=%.3f"%(min(vals),max(vals),8.9/3.6-1))

print("==== W17 ====")
for tot in (13.86,13.9,14.0):
    print("  C: 8.97/%.2f=%.2f%%"%(tot,8.97/tot*100))
print("  2018末 via 1990末+28*878万 = %.4f亿"%(11.4+0.0878*28))
print("  D: high-school-only share 2010=%.1f%% 2018=%.1f%%"%(22.9-8.9,29.3-13.0))
print("     P2010 (from 14亿 back)=%.0f P2018<=14亿; count2010=%.0f count2018(lower, P=13.86亿)=%.0f 万"%(p2010b,0.14*p2010b,0.163*138584))
