#!/usr/bin/env python3
"""Check units, part/whole bounds and displayed rounding in four M04 materials."""
from fractions import Fraction as F
from pathlib import Path
import json
import hashlib

HERE=Path(__file__).resolve().parent
MODULE=HERE.parent/'编辑底稿/quant_data.json'
rows=json.loads(MODULE.read_text());by={r['number']:r for r in rows}
groups=[]

# 71-75: no manufactured additive identity between different kinds of trees.
groups.append({'numbers':[71,72,73,74,75],'source_material_id':'gd-mock-2026h2-s26-m1',
  'units':{'forest_stock':'亿立方米','mixed_arbor_forest_share':'%','tree_planting':'株/万株/亿株','mangrove_area':'公顷','tree_planting_events':'万场','participation':'万人次'},
  'checks':{'mangrove_activity_area_sum_hectares':4931+2682,'repair_share_percent':F(2682,4931+2682)*100,'fourteenth_five_year_period_years':5,'events_annual_average_10000':F('7.39')/5,'forest_mix_target_change_percentage_points':60-54},
  'scope':'Different tree-planting and participation categories are not assumed mutually exclusive. No common total is asserted for those categories in the material.',
  'material_internal_contradiction_found':False})

# 76-80: each total and residential part has its own rate; units stay paired.
m=by[76]['source_question']['material'];t=m['blocks'][0];pairs=[]
for i in range(0,len(t['rows']),2):
    total,part=t['rows'][i:i+2]
    assert total[1]==part[1]
    tv,pv=F(total[2]),F(part[2]);tr,pr=[F(x.replace('−','-'))/100 for x in [total[3],part[3]]]
    t0,p0=tv/(1+tr),pv/(1+pr)
    assert 0<pv<tv and 0<p0<t0
    pairs.append({'total':total[0],'part':part[0],'unit':total[1],
                  'current_other_component':tv-pv,'base_other_component':t0-p0,
                  'current_and_base_part_within_total':True})
groups.append({'numbers':[76,77,78,79,80],'source_material_id':m['id'],'part_whole_pairs':pairs,
  'unit_conversion':'亿元 / 万平方米 × 10000 = 元/平方米',
  'material_internal_contradiction_found':False})

# 81-85: months are flows; October export destinations are subsets of its total.
m=by[81]['source_question']['material'];t=m['blocks'][1]
q=[F(r[1]) for r in t['rows']];a=[F(r[3]) for r in t['rows']]
assert len(q)==9 and all(x>0 for x in q+a)
oct_total=F('693.3');vn=F('596.7');hk=F('65.2')
oct_old=oct_total/F('6.869');vn_old=vn/F('10.109');hk_old=hk/F('2.636')
assert vn+hk<oct_total and vn_old+hk_old<oct_old
april_interval=[F('6.05')/F('409.45')*10000,F('6.15')/F('409.35')*10000]
groups.append({'numbers':[81,82,83,84,85],'source_material_id':m['id'],
  'units':{'export_quantity':'万个','export_amount':'亿元','growth':'%','unit_price':'元/个'},
  'unit_conversion':'亿元 / 万个 × 10000 = 元/个',
  'time_scope':'Table is monthly January-September flows; paragraph is October. No monthly value is a cumulative figure.',
  'checks':{'october_other_destinations_current':oct_total-vn-hk,'october_other_destinations_base':oct_old-vn_old-hk_old,
            'april_unit_price_from_displayed_values':a[3]/q[3]*10000,
            'april_possible_range_if_cells_rounded_before_display':april_interval},
  'rounding_resolution':'Question84 explicitly asks to calculate from displayed values. Without that scope, the underlying unrounded April price could cross 150 yuan.',
  'material_internal_contradiction_found':False})

# 86-90: reconcile rounded body totals with table precision and rate displays.
m=by[86]['source_question']['material'];t=m['blocks'][1]
vol={int(r[0]):F(r[1]) for r in t['rows']}
current=vol[2023]/10000;base=vol[2022]/10000
assert abs(current-F('50.35'))<=F('0.005')
assert abs(current-base-F('0.51'))<=F('0.005')
total_growth=(current/base-1)*100
assert F('0.95')<=total_growth<F('1.05')
commodity_sum=sum(map(F,[278101,90986,13050,6847]))/10000
assert commodity_sum<current
assert F('32638.50')+F('3821.89')==F('36460.39')

# Existence witnesses: displayed component growth rates need not add exactly
# when treated as infinitely precise; show a consistent pre-rounding assignment.
national_qty_current=F('39.11');other_qty_current=current-national_qty_current
other_qty_base=other_qty_current/F('1.039')
national_qty_base=base-other_qty_base
national_qty_growth=(national_qty_current/national_qty_base-1)*100
assert F('0.15')<=national_qty_growth<F('0.25')
total_turnover_base=F('36460.39')-F('514.70')
other_turnover_base=F('3821.89')/F('1.166')
national_turnover_base=total_turnover_base-other_turnover_base
national_turnover_growth=(F('32638.50')/national_turnover_base-1)*100
assert F('-0.15')<=national_turnover_growth<F('-0.05')
groups.append({'numbers':[86,87,88,89,90],'source_material_id':m['id'],
  'units':{'body_total_quantity':'亿吨','table_and_commodity_quantity':'万吨','turnover':'亿吨公里','average_distance':'公里'},
  'unit_conversions':['10000万吨 = 1亿吨','亿吨公里 / 亿吨 = 公里'],
  'checks':{'table_2023_quantity_in_100m_tonnes':current,'body_quantity':F('50.35'),
            'table_annual_growth_in_100m_tonnes':current-base,'body_growth_amount':F('0.51'),
            'table_total_growth_percent':total_growth,'listed_four_commodities_100m_tonnes':commodity_sum,
            'turnover_components_exactly_sum_to_total':True},
  'rounding_feasibility_witnesses':{
      'sending_quantity':{'national_current':national_qty_current,'other_current':other_qty_current,
                          'national_base':national_qty_base,'other_base':other_qty_base,
                          'national_growth_percent':national_qty_growth,'national_displayed_growth_percent':'0.2',
                          'other_growth_percent':'3.9'},
      'turnover':{'total_base':total_turnover_base,'national_base':national_turnover_base,
                   'other_base':other_turnover_base,'national_growth_percent':national_turnover_growth,
                   'national_displayed_growth_percent':'-0.1','other_growth_percent':'16.6'}},
  'material_internal_contradiction_found':False})

report={'scope':'Internal consistency of the current supplied material; not external verification of actual official statistics or original PDF transcription.',
        'quant_data_module_sha256':hashlib.sha256(MODULE.read_bytes()).hexdigest(),
        'groups':groups,'material_internal_contradiction_found':False,
        'rejected_candidate_not_in_paper':{'source_material_id':'gd-mock-2026h2-s32-m2','claimed_total':F('5271.86'),'sum_of_three_types':F('3458.84')+F('206.92')+F('87.49'),'unexplained_gap':F('5271.86')-F('3458.84')-F('206.92')-F('87.49'),'reason':'Difference is far too large to be explained by stated rounding.'}}
def encode(x):
    if isinstance(x,F):return {'exact':str(x),'decimal':float(x)}
    raise TypeError(type(x).__name__)
(HERE/'data_material_consistency.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=encode)+'\n')
print(json.dumps({'groups':4,'internal_contradiction_found':False,'displayed_rounding_scope_explicit_for_q84':True},ensure_ascii=False))
