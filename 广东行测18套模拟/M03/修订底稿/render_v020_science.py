#!/usr/bin/env python3
"""Create exact, source-traceable science diagrams for the 0.2.0 revision.

Q67 retains the stored diagram's launch point, landing points and wall. Q68
reconstructs the recorded particle inventory, not the unavailable original PDF.
Uses Inkscape only to rasterize the SVG; neither figure is generative artwork.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[1]
ASSETS = PAPER / 'assets'
OUT = PAPER / '核验记录'
ASSETS.mkdir(exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def render(name, svg):
    path = ASSETS / (name + '.svg')
    path.write_text(svg, encoding='utf-8')
    png = path.with_suffix('.png')
    subprocess.run(['inkscape', str(path), '--export-type=png',
                    '--export-filename=' + str(png)], check=True,
                   capture_output=True, text=True)
    return {'svg': str(path.relative_to(ROOT)), 'png': str(png.relative_to(ROOT)),
            'svg_sha256': sha(path), 'png_sha256': sha(png)}

# Quadratic Bézier paths: x is linear in t and downward displacement is in t².
# Thus both paths start horizontally and have constant downward acceleration.
q67_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 216 170" width="1296" height="1020">
<title>M03 第67题：平抛轨迹示意图（0.2.0）</title>
<desc>依据已存图保留起点 O、两落点和墙角坐标；两条虚线按水平初速度、竖直匀加速的二次曲线绘制，不添加数值或比较结论。</desc>
<rect width="216" height="170" fill="white"/>
<path d="M11 69 H137 V165 H129 V78 H11 Z" fill="black"/>
<g fill="none" stroke="black" stroke-width="1.1" stroke-dasharray="3.2 1.8">
<path id="trajectory-A" d="M195 13 Q156 13 117 69"/>
<path id="trajectory-B" d="M195 13 Q166 13 137 84"/>
</g>
<circle cx="195" cy="13" r="2.1" fill="black"/>
<g fill="black" font-family="Arial, sans-serif" font-size="9.5">
<text x="201" y="17">O</text><text x="147" y="26">A</text><text x="154" y="64">B</text>
</g></svg>
'''
q67 = render('q67_projectile_v020', q67_svg)
q67.update({'basis': '保留源库 SVG 的 O=(195,13)、A=(117,69)、B=(137,84) 及墙角=(137,69)，仅修正轨迹曲线并移开标签。',
            'source_svg': '模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p17_i04.svg',
            'source_svg_sha256': sha(ROOT / '模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p17_i04.svg'),
            'paths': {'A': {'origin': [195,13], 'control': [156,13], 'end': [117,69]},
                      'B': {'origin': [195,13], 'control': [166,13], 'end': [137,84]}},
            'answer': 'B', 'comparisons': {'fall_A_lt_B': 56 < 71, 'horizontal_A_gt_B': 78 > 58}})

# A molecule is a cluster of touching atom circles. Neither formula names nor
# reaction coefficients are printed; students must interpret the legend.
inventory = [
    ('before', 'CH4', 150, 135), ('before', 'O2', 355, 135),
    ('before', 'O2', 150, 265), ('before', 'O2', 355, 265),
    ('after', 'CO2', 830, 135), ('after', 'H2O', 1055, 135),
    ('after', 'H2O', 830, 265), ('after', 'O2', 1055, 265),
]
compositions = {'CH4': [('C',0,0),('H',0,-34),('H',34,0),('H',0,34),('H',-34,0)],
                'O2': [('O',-22,0),('O',22,0)],
                'CO2': [('O',-44,0),('C',0,0),('O',44,0)],
                'H2O': [('O',0,0),('H',-24,24),('H',24,24)]}
parts = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 430" width="2400" height="860">
<title>M03 第68题：反应前后微观粒子示意图（0.2.0）</title>
<desc>依源库完整粒子表重绘，布局为编辑重排，不是原图复原。反应前后各四个分子，保留反应后未消耗的氧气。分子式仅存于核验清单，不印在题图上。</desc>
<defs><pattern id="oxygen-hatch" width="8" height="8" patternUnits="userSpaceOnUse">
<rect width="8" height="8" fill="white"/><path d="M-2 2 L2 -2 M0 8 L8 0 M6 10 L10 6" stroke="black" stroke-width="1.5"/>
</pattern></defs>
<rect width="1200" height="430" fill="white"/>
<g fill="none" stroke="black" stroke-width="2.5"><rect x="20" y="55" width="475" height="280"/><rect x="705" y="55" width="475" height="280"/></g>
<g font-family="Noto Sans CJK SC, sans-serif" font-size="26" fill="black" text-anchor="middle">
<text x="257.5" y="35">反应前</text><text x="942.5" y="35">反应后</text><text x="600" y="175">点燃</text>
</g><path d="M535 200 H665 M651 191 L665 200 L651 209" fill="none" stroke="black" stroke-width="3"/>
''']
def atom(element, x, y, extra=''):
    radius = 12 if element == 'H' else 22
    fill = 'url(#oxygen-hatch)' if element == 'O' else 'white'
    return f'<circle {extra} data-element="{element}" cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="black" stroke-width="2.5"/>'

molecules = []
for i, (stage, formula, x, y) in enumerate(inventory, 1):
    atoms = [{'element': e, 'cx': x+dx, 'cy': y+dy} for e, dx, dy in compositions[formula]]
    molecules.append({'id': i, 'stage': stage, 'formula_for_audit_only': formula, 'atoms': atoms})
    parts.append(f'<g id="molecule-{i}" data-stage="{stage}">')
    parts.extend(atom(a['element'], a['cx'], a['cy']) for a in atoms)
    parts.append('</g>')
parts.append('<g id="legend">')
for element, x, label in [('C',300,'碳原子'),('O',550,'氧原子'),('H',800,'氢原子')]:
    parts.append(atom(element, x, 389))
    parts.append(f'<text x="{x+38}" y="399" font-family="Noto Sans CJK SC, sans-serif" font-size="26" fill="black">{label}</text>')
parts.append('</g></svg>\n')
q68 = render('q68_particles_v020', '\n'.join(parts))
q68.update({'basis': 'gd-mock-2026h2-s26-q68 的 source_question.stem 粒子表及完整图例；原PDF/原粒子位图不可用。',
            'source_asset_id': 's26_p19_i00', 'molecules': molecules,
            'printed_formula_labels': False, 'original_image_restoration': False})

# Check the generated SVG itself, not merely the input list used to draw it.
tree = ET.fromstring('\n'.join(parts)); ns = {'s':'http://www.w3.org/2000/svg'}
actual = {'before': Counter(), 'after': Counter()}
actual_atoms = {'before': Counter(), 'after': Counter()}
for g in tree.findall('s:g', ns):
    stage = g.attrib.get('data-stage')
    if stage:
        composition = Counter(c.attrib['data-element'] for c in g.findall('s:circle', ns))
        signature = tuple(sorted(composition.items()))
        actual[stage][signature] += 1
        actual_atoms[stage].update(composition)
selection = json.loads((PAPER/'selection.json').read_text())
source_table = next(b for b in selection[67]['source_question']['stem'] if b['type']=='table')
expected_rows = [['反应前','1 个碳原子、4 个氢原子','1'], ['反应前','2 个氧原子','3'],
                 ['反应后','1 个碳原子、2 个氧原子','1'], ['反应后','2 个氧原子','1'],
                 ['反应后','1 个氧原子、2 个氢原子','2']]
assert source_table['rows'] == expected_rows, 'Source inventory changed; reassess reconstruction.'
assert actual['before'] == Counter({(('C',1),('H',4)):1, (('O',2),):3})
assert actual['after'] == Counter({(('C',1),('O',2)):1, (('O',2),):1, (('H',2),('O',1)):2})
assert actual_atoms['before'] == actual_atoms['after'] == Counter(C=1,H=4,O=6)
q68['checks'] = {'source_rows_match': True, 'svg_molecules_each_stage': {s:sum(v.values()) for s,v in actual.items()},
                 'svg_atoms_each_stage': {s:dict(v) for s,v in actual_atoms.items()},
                 'actual_consumed_ratio_CH4_to_O2': '1:2', 'product_species': ['CO2','H2O'],
                 'remaining_O2': 1, 'answer': 'C'}
record = {'paper_id':'M03','version':'0.2.0','rendering':'SVG → Inkscape PNG',
          'question_67':q67,'question_68':q68,'result':'PASS',
          'limits':['Q67几何只表达水平距离、下落高度和接触表面；不以图量取具体速度。',
                    'Q68依据源库转写重建，无法证明不可用原PDF的粒子布局或转写本身完全无误。']}
(OUT/'v020_science_diagrams.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'result':'PASS','Q67':q67['png'],'Q68':q68['png'],'Q68_atoms':q68['checks']['svg_atoms_each_stage']},ensure_ascii=False))
