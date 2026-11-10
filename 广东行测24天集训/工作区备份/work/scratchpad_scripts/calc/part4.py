def pct(x): return f"{x*100:.3f}%"
def nearest(val, opts):
    return sorted(((abs(val-v), k, v) for k, v in opts.items()))

print("==== Z27")
r19=2707-125; r18=2774-(125+70)
g=r19/r18-1
print("rest19", r19, "rest18", r18, "g", pct(g))
print(nearest(g*100,{'A':-2.4,'B':0.1,'C':1.7,'D':4.1}))
print("manufacturing 2019 g from text", pct(125/195-1), "chart -35.9")
print("total g", pct(2707/2774-1))

print("==== Z28")
m18=195; l18=49/(1-0.21)
m17=m18/1.258; l17=l18/1.348
rest18=2774-m18-l18; rest17=2690-m17-l17
g=rest18/rest17-1
print("m18",m18,"l18",l18,"m17",m17,"l17",l17,"rest18",rest18,"rest17",rest17,"g",pct(g))
print(nearest(g*100,{'A':1.1,'B':3.1,'C':5.3,'D':7.2}))
print("check via 2019 text: comm18+ground18 =", 1230+35+1303/1.041)
print("total 2018 g", pct(2774/2690-1))
# rounding sensitivity of launch -21.0, 34.8, 25.8
import itertools
vals=[]
for lg19,lg18,mg18 in itertools.product([-0.2105,-0.2095],[0.3475,0.3485],[0.2575,0.2585]):
    l18_=49/(1+lg19); m17_=195/(1+mg18); l17_=l18_/(1+lg18)
    vals.append((2774-195-l18_)/(2690-m17_-l17_)-1)
print("range", pct(min(vals)), pct(max(vals)))

print("==== Z35")
tot=[2309,2466,2548,2605,2690,2774,2707]
launch=[-6.9,9.3,-8.5,1.9,-16.4,34.8,-21]
manu=[7.5,0.3,1.6,-13.1,11.5,25.8,-35.9]
cnt=0;cntm=0
for i in range(1,7):
    gt=(tot[i]/tot[i-1]-1)*100; f=gt>launch[i]; cnt+=f; fm=gt>manu[i]; cntm+=fm
    print(2013+i, "total g", round(gt,3), "launch", launch[i], f, "| manu", manu[i], fm)
print("count vs launch", cnt, "| (if lines swapped) vs manu", cntm)

print("==== Z29")
q={'16Q1':(56.15,4.73,20.52,33.90),'16Q2':(75.80,3.75,28.97,41.58),'17Q1':(78.61,6.45,41.48,47.76),'17Q2':(109.24,3.68,49.29,21.70)}
vas16=q['16Q1'][2]+q['16Q2'][2]; tot16=sum(q['16Q1'])+sum(q['16Q2'])
vas17=q['17Q1'][2]+q['17Q2'][2]; tot17=sum(q['17Q1'])+sum(q['17Q2'])
s16=vas16/tot16; s17=vas17/tot17
print("H1 2016 vas", vas16, "tot", tot16, pct(s16)); print("H1 2017 vas", vas17, "tot", tot17, pct(s17))
print("chg pp", (s17-s16)*100, "relative chg", pct(s17/s16-1))
print("Q2 only: 2016Q2", pct(q['16Q2'][2]/sum(q['16Q2'])), "2017Q2", pct(q['17Q2'][2]/sum(q['17Q2'])), "chg pp", (q['17Q2'][2]/sum(q['17Q2'])-q['16Q2'][2]/sum(q['16Q2']))*100)
print("Q1 only chg pp", (q['17Q1'][2]/sum(q['17Q1'])-q['16Q1'][2]/sum(q['16Q1']))*100)
print("total online video revenue H1 growth", pct(tot17/tot16-1), "vas growth", pct(vas17/vas16-1))
# share of VAS in revenue excluding others? alt base
for nm,idx in [("ad+copyright+vas (excl. other)",[0,1,2])]:
    t16=sum(q['16Q1'][i]+q['16Q2'][i] for i in idx); t17=sum(q['17Q1'][i]+q['17Q2'][i] for i in idx)
    print(nm, pct(vas16/t16), pct(vas17/t17), (vas17/t17-vas16/t16)*100)

print("==== Z30")
print("A arts/lecture participants", 31379/441, "| activity count ratio", 74.06/2.36)
print("B 2012 staff", 164355-8127)
print("C 2013/2006", 249.1/123.5)
s13=34343/44260; s12=(34343-242)/(44260-384)
print("D township share 13", pct(s13), "12", pct(s12), s13>s12)

print("==== Z33")
tot=[214433,242843,271896,300931,332316]
print("A sum 2012-2016", sum(tot), ">1400000?", sum(tot)>1400000)
u15=285814/1.104; print("B urban15", u15, "share", pct(u15/300931))
c16=35799/332316; c15=(35799/1.108)/300931
print("D catering share 16", pct(c16), "15", pct(c15), "chg pp", (c16-c15)*100)
print("   alt with total15 from urban+rural", (c16-(35799/1.108)/(285814/1.104+46503/1.109))*100)
print("   alt with total15 from goods+catering", (c16-(35799/1.108)/(296518/1.104+35799/1.108))*100)

print("==== Z34")
circ=[2.52,2.61,2.81,3.22,3.28,3.74,4.34,4.92,5.30]
print("A 11th FYP sum 2006-2010", sum(circ[:5]))
print("B seats per library", 855500/3117)
area=[54.7,56.1,58.7,63.7,67.1,73.8,78.2,85.1,90.0]
for i in range(2,9):
    print("  C", 2006+i, pct(area[i]/area[i-1]-1))
books=[0.38,0.39,0.41,0.44,0.46,0.47,0.51,0.55,0.58]
print("D area incr 2008", round(area[2]-area[1],2), "2011", round(area[5]-area[4],2), "| books incr 2008", round(books[2]-books[1],3), "2011", round(books[5]-books[4],3))
