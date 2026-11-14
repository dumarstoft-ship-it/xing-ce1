"""Independent, finite-model checks for the five M01 science selections."""
from itertools import permutations, combinations_with_replacement, product
import json
from pathlib import Path

# 66. Rightward is positive. A is in uniform motion, B is stationary.
f_ab = 5
f_ground_on_b = -(10 - f_ab)
force_check = {'A_net_horizontal_N':-5+f_ab,'B_net_horizontal_N':10-f_ab+f_ground_on_b,'friction_A_on_B_N':-f_ab,'friction_ground_on_B_N':f_ground_on_b,'option_truth':{'A':True,'B':True,'C':abs(f_ground_on_b)<10,'D':abs(f_ab)<5}}
assert [k for k,v in force_check['option_truth'].items() if not v]==['D']

# 67. Three parallel paths: R1+R2, R3, R4. V=U; A1=I_total; A2=I3+I4.
def readings(u, r1, r2, r3, r4):
    return (u, u/(r1+r2)+u/r3+u/r4, u/r3+u/r4)
examples=[]
for u,r1,r2,r3,r4 in product((1,7),(1,9),(2,8),(2,11),(3,12)):
    v,i1,i2=readings(u,r1,r2,r3,r4)
    cool=readings(u,r1,r2/2,r3,r4)
    bright=readings(u,r1,r2,r3/2,r4)
    dark=readings(u,r1,r2,r3*2,r4)
    assert cool[0]==v and cool[1]>i1 and cool[2]==i2
    assert bright[1]>i1 and bright[2]>i2
    assert dark[1]<i1 and dark[2]<i2
    examples.append(1)
circuit={'analytic_formulas':{'V':'U','A1':'U/(R1+R2)+U/R3+U/R4','A2':'U/R3+U/R4'},'positive_parameter_cases':len(examples),'option_truth':{'A':False,'B':True,'C':False,'D':False},'note':'Numerical checks supplement, not replace, the monotonic symbolic proof.'}

# 68. The observations give order relations, rather than assume the known order.
orders=list(permutations(('Fe','Cu','Ag','H')))
def matches(order, experiments):
    rank={x:i for i,x in enumerate(order)}
    above=lambda x,y:rank[x]<rank[y]
    tests={1:above('Fe','Cu'),2:above('Cu','Ag'),3:above('Cu','Ag'),4:above('Fe','H') and above('H','Cu')}
    return all(tests[i] for i in experiments)
experiment_pairs={'A':[1,3],'B':[1,4],'C':[2,4],'D':[3,4]}
chem={k:sorted({'>'.join(x for x in order if x!='H') for order in orders if matches(order,pair)}) for k,pair in experiment_pairs.items()}
assert {k:len(v) for k,v in chem.items()}=={'A':1,'B':3,'C':1,'D':1}

# 69. The ordinary three-allele ABO model, explicitly not rare clinical variants.
genotypes=list(combinations_with_replacement(('A','B','O'),2))
def phenotype(g):
    s=set(g)-{'O'}
    return 'AB' if s=={'A','B'} else next(iter(s)) if s else 'O'
def offspring(g,h):
    return {phenotype((a,b)) for a in g for b in h}
by_parent={}
for p,q in product(('A','B','AB','O'),repeat=2):
    by_parent[p+' x '+q]=sorted(set().union(*(offspring(g,h) for g,h in product(genotypes,repeat=2) if phenotype(g)==p and phenotype(h)==q)))
abo_truth={
'A':all(offspring(g,h)<={'A','B'} for g,h in product(genotypes,repeat=2) if phenotype(g)=='A' and phenotype(h)=='B'),
'B':all('O' in (phenotype(g),phenotype(h)) for g,h in product(genotypes,repeat=2) if 'O' in offspring(g,h)),
'C':all('O' not in offspring(g,h) for g,h in product(genotypes,repeat=2) if phenotype(g)=='AB' and phenotype(h)=='O'),
'D':all({phenotype(g),phenotype(h)}=={'A','B'} for g,h in product(genotypes,repeat=2) if 'AB' in offspring(g,h))}
assert abo_truth=={'A':False,'B':False,'C':True,'D':False}

# 70. Coordinates transcribed by viewing the actual pole-centred map.
coords={'A':(-50,-90),'B':(-60,-45),'C':(-70,45),'D':(-70,135)}
western=lambda lon:lon < -20 or lon > 160
geo_truth=[all(lat<0 for lat,lon in coords.values()),all(30<=abs(lat)<=60 for lat,lon in coords.values()),all(23.5<abs(lat)<66.5 for lat,lon in coords.values()),coords['A']==(-50,-90) and coords['D']==(-70,135),coords['B']==(-60,45) and coords['C']==(-70,-45),all(western(coords[n][1]) for n in ['A','B']) and all(not western(coords[n][1]) for n in ['C','D'])]
assert geo_truth==[True,False,False,True,False,True]
answer_checks={66:'D',67:'B',68:'B',69:'C',70:'D'}
report={'status':'PASS','answers':answer_checks,'Q66':force_check,'Q67':circuit,'Q68':{'compatible_metal_orders_by_option':chem},'Q69':{'model':'ordinary three-allele Mendelian ABO; rare variants excluded','parental_genotype_pairs_checked':36,'option_truth':abo_truth,'possible_child_phenotypes_by_parent_phenotype':by_parent},'Q70':{'coordinates_lat_lon_degrees':coords,'statements_1_to_6':geo_truth},'limits':['These checks verify models and option logic, not source-PDF transcription.','Images were inspected separately; coordinates and circuit topology are manual inputs.','Not a second model or Claude review.']}
out=Path(__file__).parent/'science_model_checks.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'PASS','answers':answer_checks,'chemistry_possible_orders':chem,'circuit_cases':len(examples),'abo_pairs':36},ensure_ascii=False))
