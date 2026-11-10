import itertools
def rng(v, h):  # value with rounding half-width
    return [v-h, v, v+h]

print("==== W01 ====")
gdp = 29319.97/0.514
print("GD GDP 2012 =", round(gdp,1), "亿; national max (share>=1/10) =", round(gdp*10/1e4,2), "万亿; min (share<=1/8) =", round(gdp*8/1e4,2), "万亿")
for p in rng(51.4,0.05):
    g=29319.97/(p/100); print("  p=%.2f GDP=%.1f  national max=%.3f万亿"%(p,g,g*10/1e4))
print("A: 2011年首次突破5000 (5049) -> 2012首次? False")
print("B: 增长49.5倍 -> 是%.1f倍 -> False"%(1+49.5))
print("D: 13.3/9.8 = %.4f  (>=1.5? %s)"%(13.3/9.8, 13.3/9.8>=1.5))

print("==== W02 ====")
tax_total = 6467.82/0.491
non = tax_total-6467.82
print("tax_total=%.2f non-private=%.2f GDP=%.2f ratio=%.4f%%"%(tax_total,non,gdp,non/gdp*100))
print("  traps: private tax/GDP=%.3f%%, total tax/GDP=%.3f%%"%(6467.82/gdp*100, tax_total/gdp*100))
vals=[]
for p1 in rng(49.1,0.05):
    for p2 in rng(51.4,0.05):
        r = 6467.82*(1-p1/100)/(p1/100) / (29319.97/(p2/100))*100
        vals.append(r)
print("  perturb range: %.3f%% .. %.3f%%"%(min(vals),max(vals)))
opts={'A':11.3,'B':11.8,'C':23.1,'D':24.2}
for v in (min(vals),max(vals)):
    print("   nearest:", min(opts,key=lambda k:abs(opts[k]-v)))

print("==== W03 ====")
inc = 5524-5049
v=5524
for y in range(2013,2019):
    v+=inc; print(" ",y,v, ">7000" if v>7000 else "")

print("==== W04 ====")
for a in rng(67.0,0.05):
    print("  tap %.2f%% -> %.3f"%(a,391*a/100))
for b in rng(59.8,0.05):
    print("  road %.2f%% -> %.3f"%(b,391*b/100))
print("  min both = 262+234-391 =", 262+234-391, " (raw %.2f)"%(391*0.67+391*0.598-391))

print("==== W05 ====")
s14=2107.7/2349; t13=2107.7/1.089; a13=2349/1.069; s13=t13/a13
print("share14=%.4f%% share13=%.4f%% diff=%.4f pp"%(s14*100,s13*100,(s14-s13)*100))
vals=[]
for r1 in rng(8.9,0.05):
    for r2 in rng(6.9,0.05):
        for top in rng(2107.7,0.05):
            for tot in rng(2349,0.5):
                ss14=top/tot; ss13=(top/(1+r1/100))/(tot/(1+r2/100)); vals.append((ss14-ss13)*100)
print("  perturb range: %.3f .. %.3f pp"%(min(vals),max(vals)))

print("==== W06 ====")
cb13=757/1.041; cs13=277/(1-0.174)
print("2013 CN-brand PC=%.2f sedans=%.2f ratio=%.3f%%"%(cb13,cs13,cs13/cb13*100))
pc13=1970/1.0989; sed13=1238/1.031
print("  share-method: %.3f%%"%(0.28*sed13/(0.405*pc13)*100))
vals=[]
for g1 in rng(4.1,0.05):
    for g2 in rng(17.4,0.05):
        for x in rng(757,0.5):
            for y in rng(277,0.5):
                vals.append((y/(1-g2/100))/(x/(1+g1/100))*100)
print("  perturb range %.3f .. %.3f"%(min(vals),max(vals)))
print("  traps: 2014 ratio 277/757=%.2f%%"%(277/757*100))
