def rng(v, h): return [v-h, v, v+h]
import itertools
print("==== W07 ====")
# A
tr14=318/379; tr13=(318/0.911)/(379/0.935)
print("A: truck share 2014=%.3f%% 2013=%.3f%% (up? %s)"%(tr14*100,tr13*100,tr14>tr13))
# B
pc13=1970/1.0989; sed13=1238/1.031
print("B: 2013 sedan share (growth)=%.3f%%, (share-pp)=%.1f%%"%(sed13/pc13*100,62.8+4.2))
# C
suv13=408/1.364; mpv13=191/1.468
g=(408+191)/(suv13+mpv13)-1
print("C: SUV13=%.2f MPV13=%.2f sum13=%.2f sum14=599 growth=%.3f%%"%(suv13,mpv13,suv13+mpv13,g*100))
vals=[]
for a in rng(408,0.5):
  for b in rng(191,0.5):
    for ra in rng(36.4,0.05):
      for rb in rng(46.8,0.05):
        vals.append(((a+b)/(a/(1+ra/100)+b/(1+rb/100))-1)*100)
print("   perturb range %.3f .. %.3f"%(min(vals),max(vals)))
alt13=(0.207-0.04+0.097-0.03)*pc13; alt14=(0.207+0.097)*1970
print("   share-pp method: 2013=%.1f 2014=%.1f growth=%.2f%%"%(alt13,alt14,(alt14/alt13-1)*100))
print("   implied MPV share change from growth data: %.2f pp (material says 3)"%((191/1970-mpv13/pc13)*100))
print("   implied SUV share change from growth data: %.2f pp (material says 4)"%((408/1970-suv13/pc13)*100))
cross13=133/0.819
print("   implied cross share change: %.2f pp (material says -2.4)"%((133/1970-cross13/pc13)*100))
print("   implied sedan share change: %.2f pp (material says -4.2)"%((1238/1970-sed13/pc13)*100))
# D
print("D: 2013 non-sedan = %.2f (pc13 %.2f - sed13 %.2f)"%(pc13-sed13,pc13,sed13))
print("   sum of parts 2013 = %.2f"%(suv13+mpv13+cross13))
print("   share method: %.2f"%(0.33*pc13))
vals=[]
for p in rng(1970,0.5):
  for rp in rng(9.89,0.005):
    for s in rng(1238,0.5):
      for rs in rng(3.1,0.05):
        vals.append(p/(1+rp/100)-s/(1+rs/100))
print("   perturb range %.2f .. %.2f"%(min(vals),max(vals)))
print("   2014 sum of types =",1238+408+191+133)

print("==== W08 ====")
print("equip2012=%.1f hitech2012=%.1f diff=%.1f ; 2023 diff=%.1f"%(33.6-5.4,15.7-6.3,(33.6-5.4)-(15.7-6.3),33.6-15.7))

print("==== W09 ====")
p10q1=336.7/1.3052; p10q4=336.7/0.75
print("B: 2010Q1 profit=%.2f 2010Q4=%.2f  Q4>Q1? %s"%(p10q1,p10q4,p10q4>p10q1))
m11=336.7/4572.78; m10=p10q1/(4572.78/1.3074)
print("D: margin 2011Q1=%.4f%% 2010Q1=%.4f%% (2010 lower? %s)"%(m11*100,m10*100,m10<m11))

print("==== W12 ====")
pr14=4997.3/0.92
print("B: profit 2014=%.1f decrease=%.1f"%(pr14,pr14-4997.3))
for r in (7.5,8.0,8.49):
    print("   r=%.2f%% decrease=%.1f"%(r,4997.3*r/100/(1-r/100)))
c14=63191.3/0.93; t14=103155.5/0.94; l14=39964.2/(1-0.042)
print("D: central share 2015=%.3f%% 2014=%.3f%% (2014 lower? %s)"%(63191.3/103155.5*100,c14/t14*100,c14/t14<63191.3/103155.5))
print("   check total via parts: 2014 total=%.1f, implied decline=%.3f%%"%(c14+l14,(1-103155.5/(c14+l14))*100))
print("   check sum 2015 parts:",63191.3+39964.2)

print("==== W13 ====")
ti=685766.3*0.119/1.119; ci=363304*0.104/1.104; li=322462.3*0.137/1.137
print("total inc=%.1f central inc=%.1f local inc=%.1f sum parts=%.1f"%(ti,ci,li,ci+li))
print("local share: /total=%.3f%%  /sumparts=%.3f%%"%(li/ti*100,li/(ci+li)*100))
vals=[]
for rl in rng(13.7,0.05):
  for rt in rng(11.9,0.05):
    vals.append(322462.3*rl/100/(1+rl/100)/(685766.3*rt/100/(1+rt/100))*100)
print("   perturb range %.3f .. %.3f"%(min(vals),max(vals)))
print("   liabilities sum check:",363304+322462.3)
