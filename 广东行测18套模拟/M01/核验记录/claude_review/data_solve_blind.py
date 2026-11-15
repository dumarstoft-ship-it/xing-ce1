# Blind solve of M01 Q71-90 (written before opening any answer/analysis file)
out=[]
def rec(n,ans,note): out.append((n,ans,note)); print(f'Q{n}: {ans} | {note}')
def near(val,opts):
    s=sorted(opts.items(),key=lambda kv:abs(kv[1]-val))
    (k1,v1),(k2,v2)=s[0],s[1]
    return k1, f'computed={val:.4f}; nearest {k1}={v1}, next {k2}={v2}; gap to next={abs(v2-val)/abs(val)*100:.1f}% of value'

print('==== Group 1 (s17-m1) ====')
cons23=26796; g_cons=0.092; tc23=3652; g_tc=0.143
ratio={2018:.703,2019:.701,2020:.659,2021:.686,2022:.665,2023:.683}
urb={'全国':[26112.31,28063.35,27007.45,30307.20,30390.80,32994.00],
     '上海':[46015.21,48271.57,44839.32,51294.60,48110.55,54918.77],
     '北京':[42925.65,46358.17,41726.26,46775.70,45616.87,50897.45],
     '广东':[30924.31,34424.12,33511.30,36621.10,36936.16,39333.34],
     '山东':[24798.38,26731.49,27291.10,29314.30,28555.15,30250.98]}
yrs=list(range(2018,2024))
# consistency: national urban 2023 growth vs text 8.6%
print('check urban national 2023 growth', urb['全国'][5]/urb['全国'][4]-1, '(text 8.6%)', 'text urban 32994 == table', urb['全国'][5])
inc23=cons23/ratio[2023]
k,n=near(inc23,{'A':42509,'B':39233,'C':33488,'D':29089}); rec(71,k,'income23=26796/0.683; '+n)
tc22=tc23/(1+g_tc); fam=5*tc22
k,n=near(fam,{'A':15976,'B':18260,'C':12780,'D':3195}); rec(72,k,f'tc22={tc22:.2f}, x5; '+n+' [B=3652*5, C=3195*4, D=per capita]')
inc22=cons23/(1+g_cons)/ratio[2022]; g_inc=inc23/inc22-1
k,n=near(g_inc*100,{'A':12.8,'B':9.2,'C':6.3,'D':5.1}); rec(73,k,f'inc22={inc22:.1f}, g=(1.092*0.665/0.683-1); '+n)
sh=urb['上海']; gs=[sh[i]/sh[i-1]-1 for i in range(1,6)]
print('  Shanghai growth 2019-23:',[f'{g*100:.2f}%' for g in gs])
cnt=sum(g>0.10 for g in gs); rec(74,{3:'A',2:'B',1:'C',0:'D'}[cnt],f'count>10% = {cnt}')
# Q75
a=18175/12
b_years=[y for y in range(2019,2024) if ratio[y]<ratio[y-1]]
c_fail=[y for i,y in enumerate(yrs) if not urb['山东'][i]<urb['全国'][i]]
d=(sh[5]-sh[4])/(urb['广东'][5]-urb['广东'][4])
print(f'  75A rural monthly={a:.1f} (claim ~2000) -> False')
print(f'  75B years cons growth<income growth (ratio fell) = {b_years} -> count {len(b_years)} (claim 2) -> False')
print(f'  75C years Shandong >= national urban = {c_fail} -> False')
print(f'  75D SH incr={sh[5]-sh[4]:.2f}, GD incr={urb["广东"][5]-urb["广东"][4]:.2f}, ratio={d:.4f} (<3) -> True')
rec(75,'D',f'only D true; SH/GD increment ratio={d:.3f}')

print('==== Group 2 (s21-m3) ====')
T={'总货运':(47950.8,.096,176583.3,.063),'进口':(30429.2,.108,117851.4,.068),'出口':(17521.6,.075,58731.9,.053),
   '工具总数':(3309354,.301,12808925,.511),'汽车':(2828439,.328,10946073,.556),'火车':(376851,.098,1470568,.205),
   '船舶':(34604,.109,127518,.142),'飞机':(69460,.793,264766,1.364)}
print('  check import+export: Apr',T['进口'][0]+T['出口'][0],'vs',T['总货运'][0],' 1-4',round(T['进口'][2]+T['出口'][2],1),'vs',T['总货运'][2])
s4=sum(T[k][0] for k in ['汽车','火车','船舶','飞机']); s14=sum(T[k][2] for k in ['汽车','火车','船舶','飞机'])
print('  check 4 tools sum: Apr',s4,'vs',T['工具总数'][0],' 1-4',s14,'vs',T['工具总数'][2])
b23a=sum(T[k][0]/(1+T[k][1]) for k in ['汽车','火车','船舶','飞机']); print('  check 2023Apr base: components',round(b23a),'vs total',round(T['工具总数'][0]/1.301))
b23b=sum(T[k][2]/(1+T[k][3]) for k in ['汽车','火车','船舶','飞机']); print('  check 2023Jan-Apr base: components',round(b23b),'vs total',round(T['工具总数'][2]/1.511))
print('  check freight base Apr: imp+exp',round(T['进口'][0]/1.108+T['出口'][0]/1.075,1),'vs total',round(T['总货运'][0]/1.096,1))
print('  check freight base 1-4: imp+exp',round(T['进口'][2]/1.068+T['出口'][2]/1.053,1),'vs total',round(T['总货运'][2]/1.063,1))
v=T['总货运'][2]/(1+T['总货运'][3])/1e4
k,n=near(v,{'A':16.6,'B':17.1,'C':17.4,'D':17.9}); rec(76,k,'176583.3/1.063/1e4 亿吨; '+n)
up=[k for k in ['汽车','火车','船舶','飞机'] if T[k][1]>T['工具总数'][1]]
rec(77,{0:'A',1:'B',2:'C',4:'D'}.get(len(up),'?'),f'share up iff growth>30.1%: {up}')
v=T['出口'][2]/(1+T['出口'][3])-T['出口'][0]/(1+T['出口'][1])
k,n=near(v,{'A':39477,'B':41210,'C':43562,'D':45941}); rec(78,k,'58731.9/1.053-17521.6/1.075; '+n+' [B=2024 Jan-Mar]')
hi=[]
for kk in ['汽车','火车','船舶','飞机']:
    avg=(T[kk][2]-T[kk][0])/3; print(f'  {kk}: Apr {T[kk][0]} vs Jan-Mar avg {avg:.1f} ({(T[kk][0]/avg-1)*100:.1f}% above)'); hi.append(T[kk][0]>avg)
rec(79,{0:'A',1:'B',2:'C',4:'D'}.get(sum(hi),'?'),f'{sum(hi)} of 4 above avg')
pa=T['飞机'][0]/30; pb=T['飞机'][2]/T['船舶'][2]; pc=T['进口'][2]-T['进口'][2]/(1+T['进口'][3]); pd=T['进口'][0]-T['出口'][0]
print(f'  80A planes/day={pa:.2f} (claim <=2300) -> False; 80B planes/ships={pb:.4f} => 多{pb-1:.3f}倍 (claim 多2.1倍) -> False')
print(f'  80C import increase={pc:.1f} 万吨 (claim >7000) -> True; 80D import-export={pd:.1f} (claim export more) -> False')
rec(80,'C',f'import Jan-Apr increase={pc:.1f}万吨>7000')

print('==== Group 3 (s25-m4) ====')
R={'运输':(21101.0,25.4,9745.3,18.8,11355.7,31.8),'旅行':(8559.8,8.4,644.4,-12.2,7915.3,10.5),'建筑':(2410.0,-7.2,1899.0,-3.4,510.9,-19.1),
   '保险':(1704.8,24.4,300.1,-10.5,1404.6,None),'金融':(594.0,-10.8,341.8,6.5,252.2,-26.9),'电信':(8352.7,8.3,5794.6,13.0,2558.1,-1.2),
   '知识产权':(3881.2,2.5,892.8,17.5,2988.4,-1.2),'个人文化':(295.5,-11.4,119.8,-2.2,175.7,-16.8),'维护维修':(847.1,12.4,None,9.5,None,18.3),
   '加工':(1459.9,8.6,1403.9,8.2,56.0,21.9),'其他商业':(10240.3,9.1,6711.7,12.6,3528.6,2.8),'政府':(355.6,15.2,113.0,13.0,242.5,16.2)}
TOT=(59801.9,12.9,28522.4,12.1,31279.5,13.5)
print('  text check: export-import =',round(TOT[2]-TOT[4],1),'(text deficit 2757.1); exp+imp=',round(TOT[2]+TOT[4],1))
print('  sum 进出口 col =',round(sum(r[0] for r in R.values()),1),'vs',TOT[0])
se=sum(r[2] for r in R.values() if r[2] is not None); si=sum(r[4] for r in R.values() if r[4] is not None)
mx_e=TOT[2]-se; mx_i=TOT[4]-si
print(f'  residual 维护维修 export={mx_e:.1f}, import={mx_i:.1f}, sum={mx_e+mx_i:.1f} vs table 847.1')
for k,r in R.items():
    if r[2] is not None and r[4] is not None:
        rowsum=r[2]+r[4]
        g_mix=None
        if r[5] is not None:
            base=r[2]/(1+r[3]/100)+r[4]/(1+r[5]/100); g_mix=(r[0]/base-1)*100
        print(f'   {k}: exp+imp={rowsum:.1f} vs {r[0]} ; implied total growth from parts={g_mix if g_mix is None else round(g_mix,2)} vs {r[1]}')
# national growth check
base=TOT[2]/(1+TOT[3]/100)+TOT[4]/(1+TOT[5]/100); print('  national implied total growth',round((TOT[0]/base-1)*100,2),'vs 12.9')
r=R['保险']; t21=r[0]/(1+r[1]/100); e21=r[2]/(1+r[3]/100); i21=t21-e21; inc=r[4]-i21
k,n=near(inc,{'A(增加306)':306,'B(增加370)':370,'C(减少306)':-306,'D(减少370)':-370}); rec(81,'B',f'2021 total={t21:.2f}, export={e21:.2f}, import={i21:.2f}; incr={inc:.2f} (implied import growth {(r[4]/i21-1)*100:.1f}%); '+n)
dd=(R['电信'][0]-R['旅行'][0])/TOT[0]*100
rec(82,'A',f'(8352.7-8559.8)/59801.9 = {dd:.4f} pp -> 低0.3个百分点 (C is x10 trap)')
r=R['维护维修']; w=(r[5]-r[1])/(r[5]-r[3]); ratio_ie=(1-w)/w
t21=r[0]/(1+r[1]/100)
print(f'  mixture: 2021 export share={w:.4f}; import:export={ratio_ie:.4f}; via residual: {mx_i/(1+r[5]/100):.1f}:{mx_e/(1+r[3]/100):.1f} = {(mx_i/1.183)/(mx_e/1.095):.4f}')
# robustness to growth-rate rounding
lo=min(((r[5]+a)-(r[1]+b))/((r[5]+a)-(r[3]+c)) for a in (-.05,.05) for b in (-.05,.05) for c in (-.05,.05))
hi_=max(((r[5]+a)-(r[1]+b))/((r[5]+a)-(r[3]+c)) for a in (-.05,.05) for b in (-.05,.05) for c in (-.05,.05))
print(f'  rounding range of import:export = {(1-hi_)/hi_:.3f} .. {(1-lo)/lo:.3f}')
rec(83,'C',f'import:export(2021) ≈ {ratio_ie:.3f} ≈ 1:2')
sur={k:R[k][2]-R[k][4] for k in ['加工','金融','建筑','知识产权']}
print('  surplus:',sur)
rec(84,'C',f'建筑 {sur["建筑"]:.1f} > 加工 {sur["加工"]:.1f} (gap {sur["建筑"]-sur["加工"]:.1f})')
# Q85
ex_max=max(((k,r[2]) for k,r in R.items() if r[2] is not None),key=lambda x:x[1]); im_max=max(((k,r[4]) for k,r in R.items() if r[4] is not None),key=lambda x:x[1])
print(f'  85A max export {ex_max}, max import {im_max}; 维护维修 total 847.1 cannot exceed -> True')
print(f'  85B 运输 deficit={R["运输"][4]-R["运输"][2]:.1f} vs 保险 deficit={R["保险"][4]-R["保险"][2]:.1f} -> True')
print(f'  85C 政府 export g 13.0 > 12.1, import g 16.2 > 13.5 -> both shares up -> True')
p21=R['个人文化'][2]/(1-0.022); print(f'  85D 2021 个人文化 export={p21:.2f} (claim >125) -> False')
rec(85,'D',f'D false: 119.8/0.978={p21:.2f}<125; A,B,C true')

print('==== Group 4 (s33-m1) ====')
Q={2020:(3526,-4.3),2021:(4271,21.1),2022:(4066,-4.8),2023:(3604,-11.4),2024:(3556,-1.3),'25JF':(535,6.1)}
V={2020:(15417.3,-8.1),2021:(20325.5,31.8),2022:(21949.1,8.0),2023:(16697.4,-23.9),2024:(20437.0,22.4),'25JF':(2657.3,7.1)}
for y in range(2021,2025):
    print(f'  {y}: qty growth calc {(Q[y][0]/Q[y-1][0]-1)*100:.2f} vs {Q[y][1]}; value growth calc {(V[y][0]/V[y-1][0]-1)*100:.2f} vs {V[y][1]}')
v19=V[2020][0]/(1+V[2020][1]/100); g=V[2021][0]/v19-1; g2=(1.318*0.919-1)
k,n=near(g*100,{'A':15.9,'B':21.1,'C':23.7,'D':26.3}); rec(86,k,f'2019={v19:.1f}; exact {g*100:.3f}%, formula (1.318*0.919-1)={g2*100:.3f}%; '+n+' [note: 21.1 also equals 2021 qty growth]')
jf24=Q['25JF'][0]/(1+Q['25JF'][1]/100); sh_=jf24/Q[2024][0]*100
k,n=near(sh_,{'A':16.6,'B':15.0,'C':14.2,'D':13.1}); rec(87,k,f'2024JF={jf24:.2f}; '+n+' [B=535/3556]')
p22=V[2022][0]/Q[2022][0]; p23=V[2023][0]/Q[2023][0]; ch=(p23/p22-1)*100; ch2=((1-.239)/(1-.114)-1)*100
rec(88,'D' if ch<-10 else '?',f'unit value change exact {ch:.2f}%, via rates {ch2:.2f}% -> 下降10%以上')
sv=sum(V[y][0] for y in range(2021,2025)); sq=sum(Q[y][0] for y in range(2021,2025)); avg=sv*1e6/(sq*1e4)
yearly=[V[y][0]*1e6/(Q[y][0]*1e4) for y in range(2021,2025)]
k,n=near(avg,{'A':512,'B':475,'C':674,'D':337}); rec(89,k,f'sum value={sv:.1f}百万$, sum qty={sq}万台, avg={avg:.2f}$; mean of yearly unit values={sum(yearly)/4:.2f} (yearly {[round(x,1) for x in yearly]}); '+n)
qdir=['up' if Q[y][1]>0 else 'down' for y in range(2020,2025)]; vdir=['up' if V[y][1]>0 else 'down' for y in range(2020,2025)]
print(f'  90A qty dirs 2020-24 {qdir}; value dirs {vdir} -> not consistent -> False')
print(f'  90B 2024/2020-1 = {(V[2024][0]/V[2020][0]-1)*100:.3f}% (claim >33.3%) -> False')
dec=v19-V[2020][0]; print(f'  90C 2020 decrease = {dec:.1f} 百万美元 (= {dec/100:.2f}亿美元), claim "约1359美元" -> unit wrong -> False')
q19=Q[2020][0]/(1+Q[2020][1]/100); print(f'  90D 2019 qty = {q19:.1f} 万台 (<3800) -> True')
rec(90,'D',f'2019 qty={q19:.1f}<3800')

import sys
with sys.stdout as f:
    f.write('# Blind answers for M01 Q71-90, written BEFORE opening 答案与解析_待审.md / selection answers / 核验记录\n')
    for n,a,note in out: f.write(f'Q{n}\t{a}\t{note}\n')

