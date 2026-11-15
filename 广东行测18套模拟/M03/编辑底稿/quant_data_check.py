#!/usr/bin/env python3
"""M03 quantity/data reproducible checks.

Read canonical selection.json when present, otherwise the module draft. Data
calculations read the displayed material tables. Enumeration supplies a second
route for integer constraints and the conditional exam probability. Structural
text judgments and reconstruction limits remain explicitly manual.
"""
from __future__ import annotations
import collections, datetime, itertools, json, math, re, statistics
from fractions import Fraction as F
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TARGET=HERE.parent/'selection.json'
if not TARGET.exists():TARGET=HERE/'quant_data.json'
ROWS={r['number']:r for r in json.loads(TARGET.read_text()) if r['section'] in ['数量关系','资料分析']}
expected_nums=list(range(31,46))+list(range(71,91))
assert sorted(ROWS)==expected_nums
REPORT={'input_file':str(TARGET.relative_to(ROOT)),'checked_on':'2026-11-15','checks':{},'limitations':['源库没有本模块参考答案；这是编辑解答及计算核验，不是官方答案比对。','原PDF与大部分材料原图不在仓库；只能核对现存转写表、源对象与图形选项。','数列采用简洁一致规律；有限数列不可能排除任意插值。','文字检索与证据边界由人工阅读核对，程序中的事实标记不冒称自动语义审题。']}
def serial(v):
 if isinstance(v,F):return {'exact':str(v),'decimal':float(v)}
 if isinstance(v,dict):return {str(k):serial(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [serial(x) for x in v]
 return v

def add(n,answer,method,**detail):
 assert ROWS[n]['answer']==answer,(n,answer,ROWS[n]['answer'])
 REPORT['checks'][str(n)]={'answer':answer,'method':method,**serial(detail)}

def num(x):return F(str(x).replace('−','-').replace('%',''))
def opt(n):return ROWS[n].get('options',ROWS[n]['source_question']['options'])
def mat(n):return ROWS[n].get('materials',[ROWS[n]['source_question']['material']])[0]
def tables(n):return [b for b in mat(n)['blocks'] if b['type']=='table']
def vals(t):return {int(r[0]):[num(x) if x not in ['—',''] else None for x in r[1:]] for r in t['rows']}
def closest(value,choices):return min(choices,key=lambda k:abs(float(value)-choices[k]))
def option_nums(n):
 return {k:float(re.findall(r'-?\d+(?:\.\d+)?',''.join(b.get('text','') for b in blocks))[0]) for k,blocks in opt(n).items()}

# Number series: verify all supplied anchor positions, not only the blank.
assert 3**2+2**2==13 and 8**2+6**2==10**2
add(31,'A','three-term square-sum groups',missing_squared=10**2+3**2)
odd=[28,30,36,54];diff=[b-a for a,b in zip(odd,odd[1:])]
assert diff==[2,6,18] and 17+29==46 and 29+46==75
add(32,'A','separate odd/even position checks',odd_differences=diff,missing=54+18*3,even=[17,29,46,75])
series=[F(3),F(7,3),F(5,3),F(1),F(43,81)]
nums=[v*3**i for i,v in enumerate(series)]
assert nums==[3,7,15,27,43]
assert [b-a for a,b in zip(nums,nums[1:])]==[4,8,12,16]
add(33,'D','rescale fractions by powers of three',unreduced_numerators=nums,missing=F(63,243))
seq=[12,41,59,70,77,81];d=[b-a for a,b in zip(seq,seq[1:])]
assert all(d[i]==d[i-2]-d[i-1] for i in range(2,len(d)))
add(34,'A','difference-sequence recurrence',differences=d,missing=seq[-1]+d[-2]-d[-1])
grid=ROWS[35]['source_question']['stem'][0]['rows']
for row in grid[:-1]:assert num(row[2])*num(row[3])-num(row[1])==num(row[4])
add(35,'B','all three known circles and the unknown use identical positions',missing=num(grid[3][2])*num(grid[3][3])-num(grid[3][1]),reconstruction='Source is a positional table; both PNG/SVG are code drawings of those cells.')

# Integer and mathematical-operation questions; use independent enumeration where useful.
solutions=[]
for t in range(1,500):
 black=F(3,7)*t;blue=F(3,8)*t;red=t-black-blue
 if black.denominator==blue.denominator==red.denominator==1 and 30<red<40:solutions.append((t,black,blue,red))
assert solutions==[(168,72,63,33)]
add(36,'B','enumerate integer total and all three color constraints',solutions=solutions)
nums=[]
for t in range(100,700):
 a,b,c=map(int,str(t))
 if t-(100*b+10*a+c)==270 and t-(100*c+10*b+a)==594:nums.append(t)
assert nums==[630]
buses=[(x,y) for x in range(14) for y in range(17) if 50*x+40*y==630]
assert min(x for x,y in buses)==3
add(37,'C','enumerate possible three-digit populations and bus mixes',population=nums,bus_solutions=buses)
p=F(30,1)/F(1,5);oldprofit=p-120;newprofit=p*F(6,5)-120
salesratio=F(4,5)*oldprofit/newprofit;revenue_ratio=salesratio*F(6,5)
assert revenue_ratio==F(12,25)
add(38,'D','separate price, per-unit profit, volume and revenue',original_price=p,original_profit=oldprofit,new_profit=newprofit,volume_ratio=salesratio,revenue_decline=1-revenue_ratio)
wind=F(12);newwind=wind*F(3,2)
assert (36+wind)/(36-wind)==2
length=F(4)/(F(1,36-newwind)+F(1,36+newwind))
assert length==54
add(39,'D','speed/time reciprocal constraints',first_wind=wind,second_wind=newwind,length=length)
submerged_height=F(7)*F(3,4);drop=7-submerged_height
assert F(3,4)**3==1-F(37,64) and drop==F(7,4)
add(40,'B','similar-cone volume-height power and exposed-volume complement',remaining_volume=1-F(37,64),remaining_height=submerged_height,water_drop=drop)
a=F(1,20);b=F(3,4)/10-a;switch_after=(F(2,5)-5*a)/(a+b);remaining_days=17-5-switch_after;c=F(3,5)/remaining_days-a
assert 5*a+switch_after*(a+b)+remaining_days*(a+c)==1 and b/c==F(5,2)
add(41,'A','reconstruct planned and actual time lines with exact fractions',a_rate=a,b_rate=b,c_rate=c,switch_day=5+switch_after,final_day=17,rate_ratio=b/c)
calendar=[]
for yr in [2023,2024]:
 day=(datetime.date(yr,3,30)-datetime.date(yr,1,1)).days+1
 zhang=(day-1)%12+1;chen=(day-2)%9+1
 calendar.append({'year':yr,'day_number':day,'zhang_phase':zhang,'chen_phase':chen})
assert calendar[0]['zhang_phase']==5 and calendar[1]['zhang_phase']==6 and calendar[1]['chen_phase']==8
add(42,'B','date arithmetic for one common and one leap year',calendar=calendar)
prob=F(0);by_initial=collections.defaultdict(F)
for first in itertools.product([False,True],repeat=4):
 passed=sum(first);pfirst=F(4,5)**passed*F(1,5)**(4-passed)
 if passed<2:continue
 if passed==4:continue
 for retake in itertools.product([False,True],repeat=4-passed):
  k=sum(retake)
  if passed+k==3:
   contribution=pfirst*F(2,5)**k*F(3,5)**(4-passed-k)
   prob+=contribution;by_initial[passed]+=contribution
assert prob==F(4992,15625) and abs(float(prob)-.32)<.001
add(43,'D','enumerate every initial-pass and retake outcome, enforcing gate',probability=prob,contributions_by_initial_pass_count=by_initial)
sets=[]
for dance_only in range(1,50):
 both=F(17,10)*dance_only
 if both.denominator!=1:continue
 instrument_only=both-3;total=dance_only+both+instrument_only+6
 if instrument_only>=0 and 40<total<50:sets.append([dance_only,both,instrument_only,6,total])
assert sets==[[10,17,14,6,47]]
add(44,'D','enumerate disjoint cell populations under integrality',solutions=sets)
allocations=[a for a in itertools.product('ABC',repeat=7) if a.count('A')==3 and a.count('B')>=2 and a.count('C')>=1]
assert len(allocations)==math.comb(7,3)*(math.comb(4,2)+math.comb(4,3))==350
add(45,'B','enumerate all assignments of seven named people to three named parks',count=len(allocations),by_b_count=dict(collections.Counter(a.count('B') for a in allocations)))

# Textual UHD material, with numerical and support-boundary cross-checks.
txt=''.join(b.get('text','') for b in mat(71)['blocks'])
assert '产品端促销、产业链对接、内容制播及AI赋能四大板块' in txt
add(71,'A','manual textual support plus exact phrase existence',support='产品端促销、产业链对接、内容制播及AI赋能')
assert '8K' not in txt and '4K节目量超2.3万小时' in txt
add(72,'C','manual evidence-boundary judgment, not a claim that absent 8K ranking is false',support={'A':'全国唯一的超高清视频产业发展试验区','B':'10803亿元，成为第十个万亿级产业集群','C':'未给出8K数量或排名','D':'国家级制造业创新中心，总投资超4000亿元'})
annual=F(105)/F(1,4)*12
add(73,closest(annual,option_nums(73)),'monthly provincial capacity -> monthly national capacity -> full-load annual production',national_monthly=F(105)/F(1,4),national_annual=annual)
phone_g=F(1044,1000)/F(1094,1000)-1
assert -F(5,100)<phone_g<0
add(74,'D','solve the earlier growth factor from two-year and later-year factors',earlier_growth=phone_g)
television_users=F(2905)/F(89,100);industry_delta=F(10803)*F(5,7)
assert television_users>3000 and industry_delta>7500
add(75,'B','all four alternatives checked separately',A_difference_percentage_points=F('107.9')-F('22.4'),B_total_users_wan=television_users,C='Two national category denominators are different; no volume ordering follows.',D_increment_yi=industry_delta)

# Automotive table. Columns: all firms, losing firms, loss, loss growth, income,
# income growth, profit, profit growth. Missing entries stay None, never zero.
auto=vals(tables(76)[0])
loss_diff=(auto[2022][1]/auto[2022][0]-auto[2016][1]/auto[2016][0])*100
assert 14<loss_diff<15
add(76,'C','difference of the two losing-firm proportions',percentage_point_difference=loss_diff)
ratios={'A':auto[2023][6]/auto[2013][6],'B':auto[2023][2]/auto[2013][2],'C':auto[2023][1]/auto[2013][1],'D':auto[2023][0]/auto[2013][0]}
add(77,max(ratios,key=ratios.get),'same-span CAGR ordering by endpoint/base ratios',ratios=ratios,cagrs={k:float(v)**.1-1 for k,v in ratios.items()})
profit_years=[yr for yr in range(2013,2019) if auto[yr][7]>auto[yr][5]]
assert profit_years==[2013,2014]
add(78,'B','compare profit growth against revenue growth in each listed year',qualifying_years=profit_years,growth_pairs={yr:[auto[yr][7],auto[yr][5]] for yr in range(2013,2019)})
avg22=auto[2022][2]/auto[2022][1]*10000;avg21=auto[2021][2]/auto[2021][1]*10000
assert -112<avg22-avg21<-110
add(79,'D','difference of per-losing-firm loss, converted from 亿元 to 万元',average_2022_wanyuan=avg22,average_2021_wanyuan=avg21,difference_wanyuan=avg22-avg21)
period_losses={yr:auto[yr][2] for yr in range(2016,2021)}
ratio=max(period_losses.values())/min(period_losses.values());profit_delta13=auto[2013][6]*auto[2013][7]/(100+auto[2013][7]);annual_delta=auto[2023][2]-auto[2022][2]
assert ratio>3 and profit_delta13>1000
add(80,'C','check two supported statements and one unsupported monthly inference',item1_max_min_ratio=ratio,item2_profit_increment_yi=profit_delta13,item3_annual_not_december_increment=annual_delta,supported=[True,True,False])

# Air-conditioner cumulative table and manual chart-direction validation.
ac={r[0]:[num(r[1]),num(r[2])] for r in tables(81)[0]['rows']}
prev_june=ac['2023年6月'][0]/(1+ac['2023年6月'][1]/100)
h2=ac['2022年12月'][0]-prev_june
add(81,closest(h2,option_nums(81)),'subtract inferred first-half base from prior-year annual total',inferred_2022_h1=prev_june,computed_2022_h2=h2)
monthly={9:ac['2022年9月'][0]-ac['2022年8月'][0],10:ac['2022年10月'][0]-ac['2022年9月'][0],11:ac['2022年11月'][0]-ac['2022年10月'][0],12:ac['2022年12月'][0]-ac['2022年11月'][0]}
oct_g=monthly[10]/monthly[9]-1
assert -F(18,100)<oct_g<-F(16,100)
add(82,'D','difference adjacent cumulative totals before comparing months',monthly_2022=monthly,october_monthly_growth=oct_g)
cur_june=ac['2023年6月'][0]-ac['2023年5月'][0]
prev_may=ac['2023年5月'][0]/(1+ac['2023年5月'][1]/100)
base_june=prev_june-prev_may;june_g=cur_june/base_june-1
add(83,closest(june_g*100,option_nums(83)),'two cumulative base-period reconstructions then subtraction',current_june=cur_june,base_june=base_june,june_growth=june_g)
# All combinations of source presentation rounding remain nearest 28.3%.
interval=[]
for x6,x5,g6,g5 in itertools.product([F('14059.5'),F('14060.5')],[F('11424.5'),F('11425.5')],[F('16.55'),F('16.65')],[F('14.15'),F('14.25')]):
 value=(x6-x5)/(x6/(1+g6/100)-x5/(1+g5/100))-1;interval.append(value)
assert all(closest(x*100,option_nums(83))=='D' for x in interval)
REPORT['checks']['83']['rounding_sensitivity_growth_bounds']=serial([min(interval),max(interval)])
price_g=F('0.846')/F('1.013')-1
assert -F('0.166')<price_g<-F('0.164')
add(84,'B','ratio-of-growth-factors for unit export price',unit_price_growth=price_g)
mo_increment=[monthly[m]-monthly[m-1] for m in [10,11,12]]
assert mo_increment==[-302,21,309]
line_candidates={}
for key,blocks in opt(85).items():
 path=ROOT/Path(ROWS[85]['source_file']).parent/blocks[0]['path'];im=Image.open(path).convert('L')
 ys=[]
 for x in [13,65,116]:
  dark=[y for y in range(im.height) for xx in range(max(0,x-2),min(im.width,x+3)) if im.getpixel((xx,y))<80]
  ys.append(statistics.median(dark))
 line_candidates[key]={'pixel_y_medians':ys,'strictly_rising':ys[0]>ys[1]>ys[2]}
assert [k for k,v in line_candidates.items() if v['strictly_rising']]==['A']
add(85,'A','two differences of cumulative totals; independently check option-line pixel heights',monthly_output=monthly,month_on_month_increments=mo_increment,graphic_options=line_candidates)

# Energy production/consumption: tables deliberately remain distinct.
energy_prod,energy_cons=map(vals,tables(86))
other_g={yr:energy_prod[yr][4]/energy_prod[yr-1][4]-1 for yr in range(2019,2023)}
assert min(other_g,key=other_g.get)==2022
add(86,'D','compare all four other-energy production growth rates',growth_by_year=other_g)
coal_delta=energy_cons[2021][1]-energy_cons[2020][1];oil_delta=energy_cons[2021][2]-energy_cons[2020][2];delta_ratio=coal_delta/oil_delta
add(87,closest(delta_ratio,option_nums(87)),'two consumption increments and their ratio',coal_increment=coal_delta,oil_increment=oil_delta,ratio=delta_ratio)
shares=[x/energy_cons[2022][0] for x in energy_cons[2022][1:]]
assert sum(shares)==1
# The original pie options were visually inspected. Ray statistics provide an
# independent rough cross-check of gray, checkerboard, white and black areas.
pies={}
for key,blocks in opt(88).items():
 path=ROOT/Path(ROWS[88]['source_file']).parent/blocks[0]['path'];im=Image.open(path).convert('L');cx=cy=105
 sectors=collections.Counter()
 for degrees in range(360):
  theta=math.radians(degrees+.5)
  pixels=[im.getpixel((round(cx+r*math.cos(theta)),round(cy+r*math.sin(theta)))) for r in range(35,91)]
  mean=statistics.mean(pixels);stdev=statistics.pstdev(pixels)
  if stdev<30 and mean>220:kind='white'
  elif stdev<30 and mean<55:kind='black'
  elif stdev<30 and 55<=mean<=170:kind='gray'
  else:kind='checkerboard'
  sectors[kind]+=1
 actual=[sectors[k]/360 for k in ['gray','checkerboard','white','black']]
 distance=sum((a-float(b))**2 for a,b in zip(actual,shares))
 pies[key]={'estimated_sector_proportions':actual,'squared_distance_from_material':distance}
assert min(pies,key=lambda k:pies[k]['squared_distance_from_material'])=='B'
add(88,'B','four numeric proportions, visual identification, and rough radial-pixel check',material_proportions=shares,pie_options=pies)
gas_total=sum(energy_prod[yr][3] for yr in range(2018,2023));gas_mean=gas_total/5
assert 24000<gas_mean<25000
add(89,'C','five-year arithmetic mean (not four growth intervals)',total=gas_total,mean=gas_mean,rounding_mean_bounds=[gas_mean-F(1,2),gas_mean+F(1,2)])
coal_gaps={yr:energy_cons[yr][1]-energy_prod[yr][1] for yr in range(2018,2023)}
above=[yr for yr,x in coal_gaps.items() if abs(x)>10000]
declines=[(yr,k) for yr in range(2019,2023) for k in [1,2,3] if energy_cons[yr][k]<energy_cons[yr-1][k]]
three_share=sum(energy_cons[2021][1:4])/energy_cons[2021][0];totalgrowth=energy_cons[2022][0]/energy_cons[2020][0]-1
assert above==[2018,2022] and declines and three_share>F(4,5) and totalgrowth<F(1,10)
add(90,'C','all alternatives: absolute gaps, declines, combined share, two-year growth',A_signed_gaps=coal_gaps,A_years_abs_gap_above_10000=above,B_declines=declines,C_three_fuel_share=three_share,D_2022_over_2020_growth=totalgrowth)

# Cross-record integrity: all twenty material records are complete, all source
# objects are unchanged, and known textual edits do not alter numeric data.
source_path=ROOT/ROWS[31]['source_file'];bank={q['id']:q for q in map(json.loads,source_path.read_text().splitlines())}
for n,r in ROWS.items():assert r['source_question']==bank[r['source_id']],n
for start in [71,76,81,86]:
 reference=mat(start)
 assert all(mat(n)==reference for n in range(start,start+5))
 original=ROWS[start]['source_question']['material']
 for now,old in zip(reference['blocks'],original['blocks']):
  if now['type']=='table':assert now['headers']==old['headers'] and now['rows']==old['rows']
  elif now['type']=='text':assert re.sub(r'\s','',now['text'])==re.sub(r'\s','',old['text'])
assert len(REPORT['checks'])==35
REPORT['summary']={'question_count':35,'questions_with_numeric_or_rule_computations':33,'manual_support_judgment_components':[71,72,75,80],'source_objects_unchanged':True,'shared_materials_consistent':True,'all_table_cells_preserved':True,'all_answer_keys_match':True,'passed':True}
(HERE/'quant_data_check.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(REPORT['summary'],ensure_ascii=False))
