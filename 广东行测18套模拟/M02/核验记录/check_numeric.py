"""Finite enumerations and exact arithmetic. No network, source banks unmodified."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations,permutations,product
import json,math
HERE=Path(__file__).resolve().parent
checks={}
def put(n,v):checks[str(n)]=v
assert [9,7,11,3,19,-13]==[9]+[9+sum(-2*(-2)**k for k in range(i)) for i in range(1,6)]
put(31,{'differences':[-2,4,-8,16,-32],'answer_value':19})
pairs=[(x//100,x%100) for x in [1015,1816,2221,1933]]
assert [a+b for a,b in pairs]==[25,34,43,52]
candidates=[2977,5831,3726,4615];totals=[x//100+x%100 for x in candidates]
assert totals==[106,89,63,61]
put(32,{'pairs':pairs,'sums':[a+b for a,b in pairs],'option_sums':totals,'answer_value':4615})
assert [i**3+(-1)**j for j,i in enumerate([2,4,6,8,10])]==[9,63,217,511,1001]
put(33,{'even_cubes_plus_alternating_one':[9,63,217,511,1001]})
put(34,{'rewritten_fractions':['4/1','6/3','8/5','10/7','12/9','14/11'],'next':str(F(14,11))})
a=3;seq=[a]
for k in range(2,7):a=a*k+k-1;seq.append(a)
assert seq==[3,7,23,95,479,2879];put(35,seq)
assert (F(1,10)*300+F(3,10)*200)/500==F(18,100)
put(36,{'A_to_B_ml':300,'B_final_ml':500,'final_concentration':str(F(18,100))})
counts=[]
for total in range(1,100):
 selected=F(15,26)*total;male=F(7,13)*total;sm=F(4,9)*selected
 if all(x.denominator==1 for x in [selected,male,sm]):counts.append([total,int(selected),int(male-sm)])
assert counts==[[78,45,22]];put(37,counts)
L=2640;vA=F(L,55);vB=F(L,30)-vA
assert vA/vB==F(6,5)
x1=30*vA;x2=2*L-90*vA
assert abs(x1-x2)==480;put(38,{'L':L,'speeds_m_per_min':[str(vA),str(vB)],'positions_from_A':[str(x1),str(x2)],'meeting_times_min':[30,90]})
assert F(260,1)/F(13,10)==200;assert (260-200)/F(1,4)==240
put(39,{'costs':[200,240],'selling_prices':[260,180],'total_revenue':440})
wall=[]
for length in range(15,301,15):
 x=set(range(0,length+1,3));y=set(range(0,length+1,5));cost=80*len(x-y)+150*len(y-x)+700*len(x&y)
 if cost==8620:wall.append({'length_m':length,'washing':len(x-y),'flood':len(y-x),'laser':len(x&y),'cost':cost})
assert [x['length_m'] for x in wall]==[90];put(40,wall)
assert 4*6+2*3+4*10==70;assert (70-10*3)/10==4
put(41,{'efficiencies':[6,3,10],'work':70,'max_elapsed_days':10,'min_C_days':4})
men={0,1,2};women={3,4,5,6,7};valid=[]
for host in women:
 for award in combinations(set(range(8))-{host},4):
  if len(set(award)&women)>=len(set(award)&men):valid.append((host,award))
assert len(valid)==155;put(42,{'group_assignments':len(valid)})
ops=list(combinations(range(5),2));down=sum(sum(0 in op for op in trip)%2==0 for trip in product(ops,repeat=3))
assert F(down,1000)==F(63,125);put(43,{'all_equal_probability_sequences':1000,'target_cup_down':down,'probability':str(F(down,1000))})
cert=[12,16,20,26,28,30,32,34,36]
assert sum(cert)==234 and cert[-1]==3*cert[0] and cert[1]+cert[2]==cert[-1] and min(b-a for a,b in zip(cert,cert[1:]))>=2
put(44,{'lower_bound':str(F(234+30,22)),'feasible_sorted_months':cert,'total':sum(cert)})
def area(poly):return abs(sum(x1*y2-x2*y1 for (x1,y1),(x2,y2) in zip(poly,poly[1:]+poly[:1])))/2
big=area([(F(0),F(2)),(F(-1),F(0)),(F(1),F(0))]);yellow=area([(F(0),F(2)),(F(-1,2),F(1)),(F(0),F(2,3)),(F(1,2),F(1))])
assert yellow/(big-yellow)==F(1,2);put(45,{'total_area':str(big),'yellow_area':str(yellow),'yellow_blue_ratio':str(yellow/(big-yellow))})
models=[(f,h,p) for f,h,p in product([False,True],repeat=3) if not f or h and p]
logical=[all(not(h and p) or f for f,h,p in models),all(not f or h and p for f,h,p in models),all(h and p or not f for f,h,p in models),all(f or not h or not p for f,h,p in models)]
assert logical==[False,True,True,False];put(51,{'all_premise_models':models,'entailed_1_to_4':logical})
valid=[]
for s in permutations('ABCDEF'):
 d={c:s.index(c)+1 for c in s}
 if d['C']!=2 or d['E']!=4:continue
 if abs(d['A']-d['C'])==1 or abs(d['F']-d['C'])==1:continue
 if sum(d[c] in [1,6] for c in 'AB')!=1:continue
 valid.append(''.join(s))
assert sorted(valid)==['BCDEAF','DCBEFA'];put(53,{'valid_assignments':valid})
solutions=[]
for x in permutations(['人事','财务','办公室']):
 if sum([x[0]=='人事',x[1]!='财务',x[2]!='人事'])==1:solutions.append(x)
assert solutions==[('财务','办公室','人事')];put(56,solutions)
balloons=[('红','圆'),('蓝','星'),('黄','心'),('蓝','圆'),('红','心')];sol=[]
for b in permutations(balloons):
 ming,jun,hua,fei,ya=b
 if not all(x[1]!='圆' and x[0]!='蓝' for x in [hua,ya]):continue
 if jun[0]==ya[0] or jun[1]==ya[1]:continue
 if ya[0]!='黄' or ming[0]!='蓝':continue
 if jun[0]!=hua[0] or fei[1]=='星':continue
 sol.append(b)
assert len(sol)==1 and sol[0][0]==('蓝','星');put(59,{'names':['明','军','花','飞','雅'],'assignments':sol})
mods=[(a,p,s,c) for a,p,s,c in product([False,True],repeat=4) if (a or p) and (not a or not s) and s]
pred=[lambda a,p,s,c:not a,lambda a,p,s,c:not p,lambda a,p,s,c:not c or p,lambda a,p,s,c:c or not p]
res=[]
for f in pred:
 ms=[m for m in mods if f(*m)];res.append({'compatible_count':len(ms),'entails_cutting':bool(ms) and all(m[3] for m in ms)})
assert [i for i,r in enumerate(res) if r['entails_cutting']]==[3];put(62,res)
for U,r,rp in product([2,6],[1,4],[1,5]):
 I=F(U,r+rp);assert F(U,r+rp+1)<I;assert F(U,1)/(F(r,2)+rp)>I;assert F(U,r)>I;assert F(2*U,r)>I
cases=0
for u,r,a,b in product([2,6],[1,4],[1,5],[2,7]):
 for joined in [False,True]:
  parallel=F(r,2) if joined else F(r*(r+b),2*r+b)
  initial=F(u,a+r)
  assert F(u,a+r+1)<initial and F(u,1)/(a+parallel)>initial and F(u,r)>initial and F(u,1)/parallel>initial
  cases+=1
put(67,{'initial':'U/(a+R)','joined_parallel':'R/2','unjoined_parallel':'R(R+b)/(2R+b)','both_topologies_parameter_cases':cases,'false_option':'A'})
put(68,{'assumptions':['no_initial_undissolved_sugar','A_B_C_same_temperature','heating_no_evaporation_no_decomposition'],'sugar_and_water_unchanged_during_heating':True})
put(70,{'day_minus_night_h':[1.5,0,3,-2],'latitude_absolute_order':'丙>丁>甲>乙','false_statement':'甲地的纬度高于丁地'})
inc_web=1215*.264/1.264;inc_off=154*.182/1.182
put(71,{'kind':'text_retrieval','option_checks':{'A':'matches_bank_registration','B':'reverses_direction_and_subject','C':'changes_target_enterprises','D':'confuses_quota_and_flow'},'editor_answer':'A','limit':'人工语义核验，不伪称数值程序证明政策理解'})
put(72,{'current_share_percent':1215/23000*100,'prior_share_percent':(1215/1.264)/(23000/1.161)*100,'delta_pp':(1215/23000-(1215/1.264)/(23000/1.161))*100})
put(73,{'national_increment_trillion_rmb':9.1*.098/1.098/.387})
put(74,{'prior_offshore_100m_usd':154/1.182})
put(75,{'hosts_to_beneficiaries_percent':103/1213*100,'QFLP_QDLP_ratio':10/5,'prior_crossborder_trillion_usd':2.3/1.161})
travel=[8.57/.634,8.57,9.07,5.2,12.6,14.6];put(76,{'2019':travel[0],'six_year_average':sum(travel)/6})
put(77,{'east_central_west_northeast_percent':[x/14.6*100 for x in [7.57,1.61,4.49,.93]],'image_match':'C'})
put(78,{'more_times':1376.68/(240.19+325.27)-1})
put(79,{'passenger_share_rises':['东部'],'cargo_share_rises':['中部','西部'],'intersection_count':0})
put(80,{'cargo_median':sorted([1607.49,1782.8,1453.05,1683.31,2006.19])[2],'cargo_2021_vs2019':.94*1.109-1,'rate_difference_pp':42.7-18.5,'max_growth_passenger_year':2023,'max_growth_cargo_year':2024})
years=list(range(2014,2025));outputs=[12089,11215,11176,11379,11937,12169,12014,11454,11236,11376,11457];areas=[2606,2359,2333,2318,2434,2416,2353,2187,2180,2123,2220]
yields={y:outputs[i]/areas[i] for i,y in enumerate(years) if 2016<=y<=2020};assert max(yields,key=yields.get)==2020;put(81,yields)
forecast=11457**2/11376;put(82,{'2025_forecast':forecast,'2021_2025_total':sum(outputs[-4:])+forecast})
put(83,{'top3':6929.81+1687.15+1227.16,'rank6to8':80.77+77.18+59.79,'ratio':(6929.81+1687.15+1227.16)/(80.77+77.18+59.79)})
put(84,{'Yunnan_increment':1687.15*.063/1.063,'national_increment':11457-11376,'contribution_percent':1687.15*.063/1.063/(11457-11376)*100})
rates={y:(areas[i]/areas[i-1]-1)*100 for i,y in enumerate(years) if i};put(85,rates)
assert rates[2015]<rates[2016]<rates[2017]<rates[2018]
assets=[49889.6,50392.7,50472.4,50496.1,50906.0];liabilities=[19651.4,20093.6,20183.7,20126.9,20405.4]
sales=[634.4,1008.2,1320.8,1635.1,2025.6];admin=[260.5,408.3,535.8,663.9,809.0];finance=[14,15.5,16.3,24.6,22.2]
diff=lambda a:[round(y-x,4) for x,y in zip(a,a[1:])]
put(86,{'average_asset':50906/9660});br=[l/a for l,a in zip(liabilities,assets)];assert max(range(1,5),key=lambda i:br[i])==4;put(87,{'months2_to6_debt_ratios':br})
put(88,{'monthly_sales':diff(sales),'monthly_finance':diff(finance),'growth_in_min_sales_month':diff(finance)[1]/diff(finance)[0]-1})
put(89,{'ratio':(sales[-1]+admin[-1]+finance[-1])/(sales[0]+admin[0]+finance[0])})
assert all(s>2*a for s,a in zip(diff(sales),diff(admin)))
put(90,{'monthly_sales':diff(sales),'monthly_admin':diff(admin),'monthly_finance':diff(finance),'equity_months2_to6':[round(a-l,3) for a,l in zip(assets,liabilities)],'sales_all_more_than_two_times_admin':True})
put(61,{'premise_form':'P -> not Q; Q','conclusion':'not P','matched_option':'A','option_B':'affirming_consequent','option_C':'predicate_scope_shift','option_D':'denying_antecedent','logic_check':all(not((not p or not q) and q) or not p for p,q in product([False,True],repeat=2))})
report={'version':'0.2.0','status':'PASS','paper_id':'M02','checks':checks,'limits':['有限枚举核验计数和条件模型，不能证明政策表述、言语最优项或图形规律的绝对唯一性。','本脚本不是Claude独立审核；原材料统计事实未作为外部经济数据逐项核实。']}
(HERE/'numeric_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: numerical/logical checks',len(checks))
