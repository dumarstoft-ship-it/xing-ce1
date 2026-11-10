"""Small local search: assign the 45 national + 3 selection-exam items to D10-D12 (GD anchors fixed) so that answer letters,
question types, topics and years are spread and near-topic pairs fall on different days. Only moves items between days; never touches options."""
import random, itertools, collections, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan4 import META
ANS={k:v[1] for k,v in META.items()}
ANS.update({'GD2016X-31':'D','GD2014X-32':'B'})
FIX={'D10':['GD2016X-27','GD2015X-20'],'D11':['GD2016X-31','GD2014X-23'],'D12':['GD2016X-30','GD2014X-32']}
XD=['GDXD2019XC-55','GDXD2020ZH-69','GDXD2019XC-45']
SCI=['GK2025X-65','GK2023D-55','GK2025D-52']
fixed={k for v in FIX.values() for k in v}
GK=[k for k in META if k.startswith('GK') and k not in SCI]
TG={'主旨':'旨','意图':'旨','观点':'旨','细节':'细','标题':'标','下文':'下','词句':'词','目的':'词','俗语':'特','名言':'特','关键词':'特'}
STRONG=[('GD2014X-23','GK2016F-47'),('GK2021D-57','GK2024F-41'),('GK2019D-59','GK2021D-48'),('GK2022X-54','GK2024X-60'),('GK2022X-54','GK2013-42'),('GK2024X-60','GK2013-42'),
 ('GDXD2019XC-45','GK2015F-59'),('GK2018F-39','GK2013-43'),('GK2013-43','GK2014-60'),('GK2017F-46','GK2023F-39'),('GD2014X-32','GK2016F-60'),('GK2015F-44','GK2016F-48'),
 ('GDXD2020ZH-69','GK2014-42'),('GK2018F-49','GK2024F-41'),('GK2018F-40','GK2021D-57'),('GK2021D-46','GK2018D-50'),('GK2018D-41','GK2014-44'),('GD2016X-30','GDXD2019XC-55')]
WEAK=[('GK2018F-40','GK2024F-41'),('GD2015X-20','GK2015F-46'),('GK2023F-39','GK2018D-41'),('GK2014-42','GK2016F-52'),('GD2016X-27','GK2014-42'),('GD2016X-27','GK2016F-52'),('GK2020D-54','GK2019D-55'),
 ('GK2020D-54','GK2015F-55'),('GK2018F-49','GK2021D-57'),('GD2016X-31','GK2013-58'),('GK2014-56','GK2014-60'),('GK2023F-44','GK2018F-42'),('GK2018F-36','GK2015F-48'),('GK2014-44','GK2015F-48'),
 ('GK2018F-36','GK2014-44'),('GK2018F-41','GK2015F-44'),('GK2018F-41','GK2015F-46'),('GK2015F-43','GK2014-60'),('GK2014-59','GK2015F-46'),('GD2014X-23','GDXD2019XC-55'),('GK2016F-47','GDXD2019XC-55')]
def year(k): return int(k[2:6]) if k.startswith('GK') else 0
def cost(asg):
    c=0; day={}
    for d,ks in asg.items():
        for k in ks: day[k]=d
        L=collections.Counter(ANS[k] for k in ks)
        c+=sum((L[x]-4.5)**2 for x in 'ABCD')*1.0
        T=collections.Counter(TG[META[k][0]] for k in ks)
        c+=4*abs(T['标']-2)+4*abs(T['下']-1)+3*abs(T['细']-3)+4*abs(T['词']-1)+2*max(0,T['特']-2)+3*(T['特']==0)
        tp=collections.Counter(META[k][2] for k in ks)
        c+=sum(max(0,v-4)**2 for v in tp.values())*2
        new=sum(1 for k in ks if year(k)>=2017); c+=0.6*(new-26/3)**2   # 23 non-science + 3 science of 2017-2025
        y=collections.Counter(year(k) for k in ks if year(k)); c+=sum(max(0,v-3) for v in y.values())*1.5
    for a,b in STRONG: c+=25*(day[a]==day[b])
    for a,b in WEAK: c+=4*(day[a]==day[b])
    return c
def run(seed):
    rnd=random.Random(seed)
    gk=GK[:]; rnd.shuffle(gk); xd=XD[:]; rnd.shuffle(xd); sc=SCI[:]; rnd.shuffle(sc)
    asg={}
    for i,d in enumerate(['D10','D11','D12']): asg[d]=FIX[d]+[xd[i],sc[i]]+gk[i*14:(i+1)*14]
    best=cost(asg)
    for it in range(60000):
        d1,d2=rnd.sample(['D10','D11','D12'],2)
        i=rnd.randrange(2,18); j=rnd.randrange(2,18)
        a,b=asg[d1][i],asg[d2][j]
        if (a in XD)!=(b in XD) or (a in SCI)!=(b in SCI): continue
        asg[d1][i],asg[d2][j]=b,a
        c=cost(asg)
        if c<=best or rnd.random()<0.002: best=c
        else: asg[d1][i],asg[d2][j]=a,b
    return cost(asg),asg
if __name__=='__main__':
    res=min((run(s) for s in range(12)), key=lambda x:x[0])
    c,asg=res; print('cost',round(c,2))
    for d,ks in asg.items():
        print(d, dict(sorted(collections.Counter(ANS[k] for k in ks).items())), dict(collections.Counter(TG[META[k][0]] for k in ks)), dict(collections.Counter(META[k][2] for k in ks)), 'new', sum(1 for k in ks if year(k)>=2017))
        print('   ', ks)
    day={k:d for d,ks in asg.items() for k in ks}
    print('strong same-day:',[p for p in STRONG if day[p[0]]==day[p[1]]], 'weak same-day:',[p for p in WEAK if day[p[0]]==day[p[1]]])
