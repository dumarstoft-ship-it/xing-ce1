#!/usr/bin/env python3
"""Exact arithmetic and finite models. Models are editorial, not an external review."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations,permutations,product
import json,hashlib,math
D=Path(__file__).resolve().parents[1]
Q={q['number']:q for q in json.loads((D/'selection.json').read_text())}
records=[]
contract=json.loads((D/'核验记录/math_input_contract.json').read_text())['sha256']
for number,expected in contract.items():
 s=Q[int(number)]['source_question']
 payload={'stem':s.get('stem'),'options':s.get('options'),'material':s.get('material'),'materials':s.get('materials')}
 assert hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()==expected, ('Input changed; re-solve model',number)
def encode(x):
 if isinstance(x,F):return {'fraction':str(x),'decimal':float(x)}
 if isinstance(x,set):return sorted(x)
 raise TypeError(type(x))
def check(n,got,details):
 assert got==Q[n]['answer'],(n,got,Q[n]['answer'],details)
 s=Q[n].get('source_question',{})
 payload={'stem':s.get('stem'),'options':s.get('options'),'material':s.get('material'),'materials':s.get('materials')}
 records.append({'number':n,'computed_answer':got,'agrees':True,'details':details,'source_input_sha256':hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()})
def optnum(n,key):
 val=(Q[n].get('options') or Q[n]['source_question']['options'])[key]  # 0.2.0第41题选项另行登记
 s=val if isinstance(val,str) else ''.join(x.get('text','') for x in val)
 s=s.strip().strip('$').strip()
 import re
 m=re.fullmatch(r'\\frac\{(\d+)\}\{(\d+)\}',s)
 return F(int(m[1]),int(m[2])) if m else F(s.rstrip('%'))
def exactopt(n,value):
 a=[k for k in 'ABCD' if optnum(n,k)==value];assert len(a)==1,(n,a,value);return a[0]
def nearest(n,value):
 distances={k:abs(optnum(n,k)-value) for k in 'ABCD'}
 answer=min(distances,key=distances.get);assert sum(x==distances[answer] for x in distances.values())==1
 return answer
# Q31-35: simple structural rules, not a proof of unique infinite continuation.
a=[3,16,43,88,155]; dif=[y-x for x,y in zip(a,a[1:])];dd=[y-x for x,y in zip(dif,dif[1:])]
v=a[-1]+dif[-1]+dd[-1]+4;check(31,exactopt(31,v),{'first_differences':dif,'second_differences':dd,'next':v})
odd=[(5,4),(10,8),(20,16)];even=[(9,1),(18,2)]
assert all(t[0]==s[0]*2 and t[1]==s[1]*2 for seq in [odd,even] for s,t in zip(seq,seq[1:]))
check(32,exactopt(32,F('36.4')),{'method':'odd/even digit-pair doubling, not decimal multiplication','next_pair':[36,4]})
nums=[2,4,7,12,19];dens=[15,18,22,27,33]
assert [F(x,y) for x,y in zip(nums,dens)]==[F(2,15),F(2,9),F(7,22),F(4,9),F(19,33)]
v=F(nums[-1]+11,dens[-1]+7);check(33,exactopt(33,v),{'numerators':nums,'denominators':dens,'next':v})
a=[F(48),F(32),F(56),F(72),F(100),F(136),F(186)]
assert all(a[i]==a[i-1]+a[i-2]/2 for i in range(2,len(a)))
check(34,exactopt(34,a[5]),{'recurrence_values':a})
a=[15,19,28,53];d=[y-x for x,y in zip(a,a[1:])];assert d==[4,9,25]
check(35,exactopt(35,a[-1]+49),{'odd_differences':d,'even_values':[12,14,26,40],'next':102})
balls=[]
for r in range(1,100):
 w=3*r;g=4;rest=r+w+g
 if F(14,9)*rest==int(F(14,9)*rest):
  y=int(F(14,9)*rest)
  if rest+y<=100:balls.append({'red':r,'yellow':y,'white':w,'green':g})
assert len(balls)==1;b=balls[0];check(36,exactopt(36,b['yellow']-b['red']),balls)
a,b=F(1,20),F(1,30);u,v=F(2,5),F(3,5)
assert a+b==F(1,12) and 8*a+18*b==1 and 12*(u+v)==12 and 8*u+18*v==14
check(37,exactopt(37,u/a),{'daily_efficiencies':[a,b],'daily_costs':[u,v],'solo_cost':u/a})
L=F(72,1)/F(8,5);assert (L+20)/(L-20)==F(13,5)
check(38,exactopt(38,L),{'distance':L,'travel_time_ratio':2,'speed_ratio':F(13,10)})
rect=[]
for k in range(1,5):
 per=12*k
 assert per<50
 for a in range(1,per//2):
  b=per//2-a
  if 0<a<b:rect.append((a*b,a,b,per))
best=max(rect);check(39,exactopt(39,best[0]),{'best_area_sides_perimeter':best})
scores=[]
for x in range(1,101):
 y=160-x
 if not 0<=y<x:continue
 for b in range(x+1,min(101,x+6)):
  for a in range(b+1,min(101,b+6)):
   for z in range(max(0,y-5),y):
    if a+b+x+y+z==415:scores.append((a,b,x,y,z))
assert scores;v=min(s[2] for s in scores)
check(40,exactopt(40,v),{'minimum_third':v,'witness':[s for s in scores if s[2]==v],'bound':'415 <= x+334'})
ages=[24,26,29,32,34,36];sets=[c for c in combinations(ages,3) if sum(c)>84 and max(c)-min(c)<=10]
check(41,exactopt(41,len(sets)*math.factorial(3)),{'unordered_sets':sets,'orders_per_set':6,'total':len(sets)*6})
def cost(total):return min(total,30)/F(3)+max(0,min(total-30,20))*F(2,5)+max(0,min(total-50,10))*F(1,5)+max(0,total-60)
v=cost(75)-cost(45)-cost(30)
check(42,exactopt(42,v),{'plan_one':cost(75),'plan_two':cost(45)+cost(30),'difference':v})
off=[0];monthlens=[31,31,30,31,30]
for n in monthlens:off.append((off[-1]+n)%7)
counts=[sum((w+d)%7<5 for d in off) for w in range(7)]
check(43,exactopt(43,max(counts)),{'weekday_offsets':off,'counts_monday_to_sunday':counts})
none=12//3;union=40-none;two=25+27+21-union-2*12;v=two+12
check(44,exactopt(44,v),{'none':none,'at_least_one':union,'exactly_two':two,'at_least_two':v})
t1=F(1,30)*3600;t2=F(4,10)/10*3600
# options include s suffix
assert Q[45]['source_question']['options']['C'][0]['text']=='264s'
check(45,'C',{'acceleration_seconds':t1,'deceleration_seconds':t2,'total_seconds':t1+t2});assert t1+t2==264
# Q51 truth-table, Q56 and Q60 all orders, Q63 truth assignments.
valid=[]
for S,N,R,T in product([False,True],repeat=4):
 if ((S or T) and ((not S) or (N and R))):valid.append((S,N,R,T))
truths={'A':[not(N and R) or not T for S,N,R,T in valid], 'B':[not(N and R) or S for S,N,R,T in valid],
'C':[not T or not S for S,N,R,T in valid], 'D':[R or T for S,N,R,T in valid]}
keys=[k for k,x in truths.items() if all(x)];assert len(keys)==1;check(51,keys[0],{'model_count':len(valid),'entailed_options':keys})
models=[]
for a in permutations('长大青绿彩白'):
 p={x:a.index(x) for x in a}
 if p['白']+1==p['彩'] and p['大']<p['白']-1 and abs(p['长']-p['青'])==2 and abs(p['绿']-p['白'])==1:models.append(a)
assert len(models)==2
truths={'A':[a.index('彩')==4 for a in models],'B':[a.index('大')==1 for a in models],'C':[a.index('长')==2 for a in models],'D':[a.index('青')==3 for a in models]}
keys=[k for k,x in truths.items() if all(x)];assert len(keys)==1;check(56,keys[0],{'all_north_south_orders':models,'entailed_options':keys})
preds=[[4,3,2,1],[3,2,4,1],[4,2,1,3],[2,3,1,4]];models=[]
for ranks in permutations([1,2,3,4]):
 hits=[sum(a==b for a,b in zip(ranks,p)) for p in preds]
 if hits==[0,1,1,1] and ranks[0]==3:models.append(ranks)
assert models==[(3,4,1,2)]
check(60,'B',{'ranks_by_jia_yi_bing_ding':models,'predictions':preds})
models=[]
for a,b,c in product([False,True],repeat=3):
 truths=[a and b,not c or a,not(a and b)]
 if sum(truths)==1:models.append((a,b,c))
assert models==[(False,False,True),(False,True,True)]
check(63,'C',{'valid_jia_yi_bing_assignments':models,'note':'乙可真可假；非唯一品牌中标'})
# Q67 illustrative ideal-circuit values: monotonic signs do not depend on these particular resistances.
U,R0,R1,R2=map(F,[12,4,6,8]);cases=[]
for Rv in map(F,[1,3,6,12,24]):
 rp=Rv*R1/(Rv+R1);i=U/(R0+rp);vl=i*rp;total=i+U/R2
 cases.append({'Rv':Rv,'A1':total,'A2':U/R2,'L1_voltage':vl,'L2_voltage':U})
assert all(b['A1']<a['A1'] and b['L1_voltage']>a['L1_voltage'] and b['A2']==a['A2'] for a,b in zip(cases,cases[1:]))
check(67,'D',{'ideal_circuit_examples':cases,'algebra':'Rp=Rv*R1/(Rv+R1); VL1=U*Rp/(R0+Rp), strictly increases with Rv'})
# Data questions. Values are read from source tables when tables exist.
def blocks(n):return Q[n]['source_question']['material']['blocks']
def table(n):return next(x for x in blocks(n) if x['type']=='table')['rows']
tour={int(row[0]):[F(row[1]),F(row[2])] for row in table(71)}
rate=F('2.403')/F('1.933')-1;check(71,'B' if rate>F(1,5) else 'A',{'per_trip_growth':rate})
v=F('4.2')/F('2.475')/(F('.7')/F('2.064'))-1;check(72,nearest(72,v),{'times_more_not_total_multiple':v})
cur=F('4.2')*10000/F('37.6');old=cur*F('1.949')/F('2.475');diff=cur-old
check(73,'D' if diff>100 else 'C',{'current_yuan':cur,'prior_yuan':old,'increase_yuan':diff})
changes={year:tour[year][1]/tour[year-1][1]-1 for year in range(2018,2024)};v=sum(abs(x)>F(1,2) for x in changes.values())
check(74,exactopt(74,v),{'yearly_change':changes,'number_exceed_50pct':v})
monthly=sum(tour[y][0] for y in range(2016,2021))/60
profit=F('37.4')*10000/56275
maxlevel=max(range(2018,2023),key=lambda y:tour[y][1]);maxinc=max(range(2018,2023),key=lambda y:tour[y][1]-tour[y-1][1])
assert profit<60 and F('1.949')>F('1.933') and F('3.9')<monthly<F('4.1') and maxlevel!=maxinc
check(75,'C',{'monthly_trips_100m':monthly,'profit_10k_yuan':profit,'highest_spend_year':maxlevel,'largest_positive_increment_year':maxinc})
custom={row[0]:[F(v.replace('−','-')) for v in row[2:]] for row in table(76)}
imp=custom['监管进口货运量'];exp=custom['监管出口货运量'];total=custom['监管运输工具总数'];border=custom['监管进出境总数']
auto=custom['其中：进出境汽车'];train=custom['进出境火车'];ship=custom['进出境船舶'];air=custom['进出境飞机']
v=imp[0]-imp[1]+exp[0]-exp[1];check(76,exactopt(76,v),{'last_september_total':v})
rates={'A':train[3]/(train[2]-train[3]),'B':auto[3]/(auto[2]-auto[3]),'C':ship[3]/(ship[2]-ship[3]),'D':air[3]/(air[2]-air[3])}
order=sorted(rates,key=rates.get,reverse=True);check(77,order[1],{'rates':rates,'ranking':order})
comparisons={k:9*x[0]<x[2] for k,x in zip('ABCD',[imp,exp,ship,air])};ans=[k for k,v in comparisons.items() if v];assert len(ans)==1
check(78,ans[0],{'below_jan_aug_average':comparisons,'method':'9*September < Jan-Sep cumulative'})
v=(imp[2]-imp[3])/(exp[2]-exp[3]);check(79,nearest(79,v),{'prior_import_export_ratio':v})
a=(auto[0]-auto[1])/(border[0]-border[1]);b=total[3]-total[1];c=train[1]/total[1];d=total[2]-border[2]
booleans=[a<F('.8'),b<7000000,c>F('.07'),d>2430000];assert booleans==[False,False,False,True]
check(80,'D',{'A_share':a,'B_increment':b,'C_contribution':c,'D_nonborder':d,'D_margin_units':d-2430000})
v=F('829.6')*F('1.038');check(81,nearest(81,v),{'next_year_return':v})
v=(F('1.038')*F('1.029')-1)*100;check(82,nearest(82,v),{'two_year_growth_percent':v})
hk=F('811.4')/F('.791');foreign=F('811.4')/F('.736');v=hk-foreign
check(83,'B' if v<-70 else 'A',{'hk_return':hk,'foreign_return':foreign,'hk_minus_foreign':v})
v=F('811.4')*F('1.068')/F('1.227');check(84,nearest(84,v),{'other_domestic_return':v})
rates={row[0]:[F(v.rstrip('%')) for v in row[1:]] for row in table(85)}
booleans=[all(r[-1]/r[0]>=F('1.2') for r in rates.values()),rates['小型企业'][-1]-rates['小型企业'][-2]==F('8.6') and rates['微型企业'][-1]-rates['微型企业'][-2]==F('11.8'),F('51.3')-F('3.2')==F('48.1')]
gaps=[rates['中型企业'][i]-rates['小型企业'][i] for i in [1,2,3]];booleans.append(gaps[0]<gaps[1]<gaps[2]);assert booleans==[False,True,True,True]
check(85,'A',{'option_truth':booleans,'large_2023_2019_ratio':rates['大型企业'][-1]/rates['大型企业'][0],'medium_small_gaps_pp':gaps})
v=F('704.88')/(F('113.33')/20);check(86,nearest(86,v),{'per_person_water_m3':v})
v=F('99.36')/F('1.0432');check(87,nearest(87,v),{'prior_drainage_10k_km':v})
rail={int(row[0]):[F(x) for x in row[1:]] for row in table(88)}
means=[rail[y][3]/rail[y][2] for y in [2022,2023,2024]];assert means[0]<means[1]>means[2];check(88,'D',{'in_progress_per_city_2022_2024':means})
share=F('92.09')/F('117.93');prior=share*F('1.0305')/F('1.0687');v=(share-prior)*100
check(89,'B' if v>1 else 'A',{'current_share':share,'prior_share':prior,'increase_pp':v})
new={y:rail[y][1]-rail[y-1][1] for y in range(2019,2025)}
inc={y:new[y]-new[y-1] for y in range(2020,2025)};vals=[inc[y] for y in range(2021,2025)]
assert vals==list(map(F,['-738.46','81.50','-218.30','-66.96']))
# The four option diagrams were visually read; exact point rank is an independent numeric check.
rank=sorted(range(4),key=lambda i:vals[i]);assert rank==[0,2,3,1]
check(90,'D',{'newly_built_lengths':new,'newly_built_yoy_increments':inc,'point_rank_ascending':rank,'option_image_matching':'原四幅图实际查看；D的纵向点序为第1<第3<第4<第2。'})
assert {r['number'] for r in records}==set(range(31,46))|set(range(71,91))|{51,56,60,63,67}
out={'status':'PASS','checked_version':json.loads((D/'paper.json').read_text())['version'],'checks':len(records),'quantitative_and_data_questions':35,'records':records,
 'limits':['有限枚举验证的是已写明模型；模型仍需外审。','数字推理没有无限延拓唯一性保证。','原表缺图的转写风险不由复算消除。','第90题选项形状为人工原图识别，数值序列由脚本独立算出。']}
(D/'核验记录/数学逻辑复算.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=encode)+'\n')
print(json.dumps({'status':'PASS','checks':len(records),'quant_data':35},ensure_ascii=False))
