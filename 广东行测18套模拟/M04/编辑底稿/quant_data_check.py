#!/usr/bin/env python3
"""Independent numeric/finite-model checks for the exact M04 module inputs.

Natural-language models were derived by the editor. The fingerprint contract
prevents silently applying these models after the displayed inputs have changed.
The computations below never read the written explanation or use its answer to
derive their result; comparison with the editorial key happens only at the end.
"""
from fractions import Fraction as F
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json
import math
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
rows=json.loads((HERE/'quant_data.json').read_text())
by={r['number']:r for r in rows}
checks=[]

def visible(r):
    s=r['source_question']
    return {'number':r['number'],'source_id':r['source_id'],
            'stem':r.get('stem_override',s['stem']),
            'options':r.get('options',s['options']),
            'materials':r.get('materials',[s['material']] if s['material'] else [])}

def fingerprint(r):
    return hashlib.sha256(json.dumps(visible(r),ensure_ascii=False,sort_keys=True).encode()).hexdigest()

contract=json.loads((HERE/'quant_data_input_contract.json').read_text())['sha256']
assert {str(n):fingerprint(r) for n,r in by.items()}==contract, 'Displayed input changed: re-derive, do not rubber-stamp old checks.'

def plain(n,k):
    return ' '.join(b.get('text','') for b in by[n].get('options',by[n]['source_question']['options'])[k])

def add(n,key,details):
    checks.append({'number':n,'independent_answer':key,'details':details,'input_sha256':fingerprint(by[n])})

def nearest(n,value,values):
    distances=[abs(F(str(value))-F(str(v))) for v in values]
    best=min(distances)
    assert distances.count(best)==1
    return 'ABCD'[distances.index(best)]

# 31-35: verify the same relation on ALL known terms.
s=[14,39,65,94,132,197]
d=[b-a for a,b in zip(s,s[1:])]; dd=[b-a for a,b in zip(d,d[1:])]
assert all(b==a*3 for a,b in zip(dd,dd[1:]))
v=s[-1]+d[-1]+dd[-1]*3
add(31,nearest(31,v,[343,313,278,211]),{'first_differences':d,'second_differences':dd,'next':v})
f=[F(5,12),F(43,96),F(1,2),F(55,96),F(2,3)]
ns=[v*96 for v in f]; ds=[b-a for a,b in zip(ns,ns[1:])]
assert ds==[3,5,7,9]
v=(ns[-1]+11)/96
add(32,nearest(32,v,[F(29,32),F(25,32),F(11,16),F(11,12)]),{'common_denominator':96,'numerators':ns,'next':v})
left=[2,5,11,20]; right=[4,12,36,108]
assert [b-a for a,b in zip(left,left[1:])]==[3,6,9] and all(b==3*a for a,b in zip(right,right[1:]))
v=f'{left[-1]+12}.{right[-1]*3}'
assert plain(33,'A')==v
add(33,'A',{'split_left_next':32,'split_right_next':324,'recombined':v})
s=list(map(F,[26,12,25,31,43.5]))
assert all(s[i]==s[i-1]+s[i-2]/2 for i in range(2,len(s)))
v=s[-1]+s[-2]/2
add(34,nearest(34,v,[53,F('56.5'),59,F('62.5')]),{'recurrence':'x[n]=x[n-1]+x[n-2]/2','next':v})
s=[16,4,36,64,196]; rt=[math.isqrt(x) for x in s]
assert [r*r for r in rt]==s and all(rt[i]==rt[i-1]+rt[i-2] for i in range(2,len(rt)))
v=(rt[-1]+rt[-2])**2
add(35,nearest(35,v,[441,484,576,625]),{'square_roots':rt,'next':v})

# 36: integer population constraints.
solutions=[]
for total in range(1,101):
    if total%7 or total%8 or (total//8)%7: continue
    girls=total//7; outside=total//8
    outside_m=outside*4//7; outside_f=outside*3//7
    if outside_m<=total-girls and outside_f<=girls:
        solutions.append((total,girls-outside_f-outside_m))
assert solutions==[(56,1)]
add(36,'A',{'feasible_total_and_difference':solutions})

# 37: exact base changes; threshold is 5 percentage points.
old_cost=F(100); old_price=old_cost*F(5,4)
cost=old_cost*F(115,100); price=old_price*F(3,2)*F(4,5)
rate=(price-cost)/cost; delta=(rate-F(1,4))*100
assert delta>5
add(37,'A',{'new_profit_rate':rate,'increase_percentage_points':delta})

# 38: enumerate integer side lengths after point/interval conversion.
spacing=F(24,9-1); perimeter=spacing*40
triangles=[(24,x,y) for x in range(1,120) for y in range(1,120)
           if 24+x+y==perimeter and 24**2+x*x==y*y]
assert triangles==[(24,45,51)]
add(38,'D',{'spacing':spacing,'perimeter':perimeter,'triangles':triangles})

# 39: relative-distance identity plus the final destination timeline.
v=(5*60-4*60)/(F(4)-F(1)-F('1.5')*F('1.2'))
distance=4*(v+60); time=F(1)+F('2.5')+(distance-v)/(F('1.2')*v)
assert v==50 and distance==440 and time==10
add(39,'D',{'original_speed':v,'distance':distance,'arrival_hours':time})

# 40: exact order size; enumerate all integer nail allocations to two shops.
n=F(20)/(F(1,30)-F(1,40)); assert n==2400
def schedules(T):
    out=[]
    for a_nails in range(2401):
        b_nails=2400-a_nails
        ta=F(T)-F(a_nails,40); tb=F(T)-F(b_nails,30)
        if ta<0 or tb<0: continue
        a_caps=math.floor(ta*50); b_caps=math.floor(tb*60)
        if a_caps+b_caps>=2400: out.append((a_nails,b_nails,a_caps,b_caps))
    return out
assert not schedules(51)
valid=schedules(52); assert valid
lower=F(2400)+F(2400,2); lower/=70
add(40,'B',{'quantity_each':2400,'continuous_lower_bound_hours':lower,
            'integer_hour_51_feasible':False,'integer_hour_52_feasible':True,
            'example_at_52':{'A_nails':2080,'B_nails':320,'B_caps':2400,
                            'A_time':52,'B_time':F(320,30)+F(2400,60)}})

# 41: prove the upper bound, then give a compatible witness.
discounted=[20,20,35,35,35,35]; days=[1,1,2,3,4,5]
assert sum(x<25 for x in discounted)==2 and len(set(days))==5
paid=sum(discounted)-4*3-5*4; original=F(sum(discounted),1)/F('0.6')
assert paid==148 and original==300
add(41,'D',{'max_coupon_count':5,'max_threshold_discount':12,
            'discounted_values_witness':discounted,'days_witness':days,
            'paid':paid,'original_total':original})

# 42: construct disjoint dissatisfaction sets, not only a formal bound.
sizes=[20,160,24,32]; start=0; sets=[]
for size in sizes:
    sets.append(set(range(start,start+size))); start+=size
union=set().union(*sets); all_happy=400-len(union)
assert all_happy==164 and len(union)==sum(sizes)
add(42,'A',{'dissatisfied_counts':sizes,'union_max':len(union),'all_satisfied_min':all_happy,
            'attainability':'The four dissatisfaction sets are disjoint subsets of 400 households.'})

# 43: unlabelled committee enumeration. Couples are (M0,F0),(M1,F1).
sample=[(m,f) for m in combinations(range(5),2) for f in combinations(range(4),2)]
good=[(m,f) for m,f in sample if sum(i in m and i in f for i in [0,1])==1]
p=F(len(good),len(sample)); assert p==F(11,30)
option_fractions={}
for key in 'ABCD':
    m=re.search(r'\\frac\{(\d+)\}\{(\d+)\}',plain(43,key))
    assert m, (key,plain(43,key))
    option_fractions[key]=F(int(m[1]),int(m[2]))
assert all(0<=v<=1 for v in option_fractions.values())
assert len(set(option_fractions.values()))==4
assert [k for k,v in option_fractions.items() if v==p]==['D']
assert option_fractions['B']==F(2*12,60)
add(43,'D',{'sample_space':len(sample),'favourable_committees':len(good),'probability':p,
            'current_option_values':option_fractions,
            'B_distractor_error':'Forgetting the subtraction of the second complete couple.'})

# 44: labelled left/right bins; remove only coincident interior right bins.
left=set(range(0,1486,15)); right=set(range(0,1486,33)); shared=(left&right)-{0,1485}
count=len(left)+len(right)-len(shared); assert count==138
add(44,'B',{'left_count':len(left),'right_before_merge':len(right),
            'interior_right_positions_removed':sorted(shared),'final':count})

# 45: exhaust all eight-person permutations. 0=A,1=B,2=C,3=D.
count=0
for arrangement in permutations(range(8)):
    at={person:i for i,person in enumerate(arrangement)}
    if at[0] in [0,7] or at[1] in [0,7] or abs(at[0]-at[1])!=1: continue
    if any(abs(at[x]-at[y])==1 for x in [0,1] for y in [2,3]):continue
    count+=1
assert count==2880
add(45,'C',{'full_permutations':math.factorial(8),'valid_permutations':count})

# 71-75: four textual decisions and two numerical computations.
add(71,'D',{'material_list':['岭南特色植物园体系建设工程','珠三角大美湿地体系建设工程','粤港澳大湾区内湾绿带工程','国有林场样板带动工程'],
            'reason':'D is absent from the four named projects.'})
add(72,'C',{'provided_period':'十四五','unsupported_option_period':'十三五','epistemic_scope':'unsupported, not proven factually false'})
ratio=F(2682,4931+2682)*100
add(73,nearest(73,ratio,['35.2','40.1','45.8','51.3']),{'repair_share_percent':ratio})
avg=F('7.39')/5
add(74,nearest(74,avg,['1.28','1.48','1.65','1.92']),{'annual_average_10000_events':avg})
add(75,'B',{'A_percentage_points':60-54,'B_scope_error':'first batch does not establish whole-period total','C_cities':3,'D_target_minimum_percent':5})

# 76-80: read table cells from the actual shared material.
table=by[76]['source_question']['material']['blocks'][0]
val=[F(r[2]) for r in table['rows']]
gr=[F(r[3].replace('−','-'))/100 for r in table['rows']]
old=[a/(1+b) for a,b in zip(val,gr)]
pp=(val[1]/val[0]-old[1]/old[0])*100
assert pp<0
add(76,'A',{'current_share':val[1]/val[0],'base_share':old[1]/old[0],'change_percentage_points':pp})
area=old[2]-old[3]
add(77,nearest(77,area,['4691.4','4907.8','5145.2','10938.1']),{'base_nonresidential_construction_area':area})
component_growth=[]
for i in range(0,10,2):
    other=(val[i]-val[i+1])/(old[i]-old[i+1])-1
    component_growth.append({'row_pair':i//2+1,'residential':gr[i+1],'nonresidential':other,'residential_faster':gr[i+1]>other})
count=sum(v['residential_faster'] for v in component_growth)
assert count==2
add(78,'B',{'individual_component_checks':component_growth,'count':count})
delta=(val[8]-val[9])-(old[8]-old[9])
add(79,nearest(79,delta,[59,-60,30,225]),{'nonresidential_sales_growth_100m_yuan':delta})
add(80,'C',{'inferable':[True,True,False],'item_3_missing_year':2021,
            'item_1_share':(old[6]-old[7])/old[6],
            'item_2_yuan_per_square_metre':old[8]/old[6]*10000})

# 81-85: display-module export table and source paragraph values.
table=by[81]['source_question']['material']['blocks'][1]
qty=[F(r[1]) for r in table['rows']]; qg=[F(r[2].replace('−','-'))/100 for r in table['rows']]
amt=[F(r[3]) for r in table['rows']]; ag=[F(r[4].replace('−','-'))/100 for r in table['rows']]
avg=sum(qty[:6])/6
add(81,nearest(81,avg,['345.8','362.4','386.1','406.5']),{'first_half_total':sum(qty[:6]),'monthly_average':avg})
change=(F('3.95')/F('6.869')-1)*100
add(82,nearest(82,change,['73.9','42.5','-73.9','-42.5']),{'unit_price_change_percent':change})
change=(sum(amt[3:6])/sum(amt[:3])-1)*100
add(83,nearest(83,change,['80.1','83.8','85.5','88.2']),{'q1':sum(amt[:3]),'q2':sum(amt[3:6]),'qoq_percent':change})
prices=[a/q*10000 for a,q in zip(amt[:6],qty[:6])]; months=[i+1 for i,p in enumerate(prices) if p<=150]
add(84,'C',{'unit_prices_yuan':prices,'months_at_or_below_150':months,
            'rounding_scope':'Uses displayed values, explicitly stated in the edited stem.',
            'April_interval_if_underlying_values_rounded':[F('6.05')/F('409.45')*10000,F('6.15')/F('409.35')*10000]})
A=amt[4]/(1+ag[4])+amt[5]/(1+ag[5]); jan=qty[0]/(1+qg[0]); feb=qty[1]/(1+qg[1])
C=(F('596.7')/F('10.109'))/(F('65.2')/F('2.636'))
assert A<10 and feb>jan and C<3
assert qty[:6].index(max(qty[:6]))==amt[:6].index(max(amt[:6]))==5
add(85,'D',{'A_base_May_June_amount':A,'B_base_January':jan,'B_base_February':feb,
            'C_base_export_ratio':C,'D_both_maximum_month':6})

# 86-90: railway statistics; amounts are read from the source table.
monthly=F(13050-6847,12)
add(86,nearest(86,monthly,[253,412,517,661]),{'monthly_difference_10000_tonnes':monthly})
national=F('0.999')/F('1.002')-1; others=F('1.166')/F('1.039')-1
assert national<0 and others>0
add(87,'B',{'national_mean_distance_growth':national,'other_mean_distance_growth':others})
share=(F('32638.50')/F('0.999'))/(F('36460.39')-F('514.70'))*100
add(88,nearest(88,share,[77,89,91,95]),{'2022_national_turnover_share_percent':share})
table=by[89]['source_question']['material']['blocks'][1]
vol={int(r[0]):F(r[1]) for r in table['rows']}
average=(vol[2023]-vol[2020])/3/10000
add(89,nearest(89,average,['2.2','2.0','1.8','1.6']),{'annual_average_increase_100m_tonnes':average,'interval_count':3})
growth=[vol[y]/vol[y-1]-1 for y in range(2019,2023)]
pattern=['up' if b>a else 'down' for a,b in zip(growth,growth[1:])]
assert pattern==['down','up','down']
figures={}
for key,blocks in by[90]['source_question']['options'].items():
    p=ROOT/'模考/2026下半年广东卷_16-33季_AI可读'/blocks[0]['path']
    assert p.is_file()
    figures[key]={'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
add(90,'A',{'growth_rates':growth,'trend':pattern,
            'visually_observed_option_trends':{'A':['down','up','down'],'B':['up','down','down'],'C':['down','down','up'],'D':['down','up','up']},
            'original_option_images_viewed':figures})

assert len(checks)==35
for c in checks:
    c['editorial_answer']=by[c['number']]['answer']
    c['agrees']=c['independent_answer']==c['editorial_answer']
assert all(c['agrees'] for c in checks)

# Verify immutable source objects and complete, consistent materials.
source={q['id']:q for q in map(json.loads,(ROOT/'模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl').read_text().splitlines())}
assert all(r['source_question']==source[r['source_id']] for r in rows)
materials={}; group_members={}
for r in rows:
    if r['number']<71:continue
    m=r.get('materials',[r['source_question']['material']])[0]; mid=m['id']
    if mid in materials: assert materials[mid]==m
    materials[mid]=m; group_members.setdefault(mid,[]).append(r['number'])
assert len(materials)==4 and all(len(v)==5 for v in group_members.values())

report={'status':'pass','question_count':35,'answer_agreement_count':35,
        'source_objects_identical_to_bank':True,'material_groups':group_members,
        'scope':'Exact displayed-input fingerprints checked before calculation. Natural-language models were derived by the editor; program checks do not replace another reader or external review.',
        'source_pdf_rechecked':False,'source_answers_available':False,
        'checks':checks}

def encode(obj):
    if isinstance(obj,F):return {'exact':str(obj),'decimal':float(obj)}
    raise TypeError(type(obj).__name__)

(HERE/'quant_data_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=encode)+'\n')
print(json.dumps({'status':'pass','questions':35,'all_keys_agree':True,'complete_data_groups':4},ensure_ascii=False))
