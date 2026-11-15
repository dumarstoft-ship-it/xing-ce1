#!/usr/bin/env python3
"""Reproducible source, constraint and geometric checks for M04 Q46–70.

Run from any directory. This checks the editor module, not the printed PDF.
The manually encoded figure interpretation is disclosed; it is not OCR proof.
"""
from pathlib import Path
from collections import Counter, deque
from itertools import combinations, permutations, product
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROJECT = HERE.parents[1]
MODULE = HERE.parent / '编辑底稿/reasoning_science.json'
DATA = HERE.parent / '编辑底稿/reasoning_diagram_data.json'
questions = json.loads(MODULE.read_text())
Q = {q['number']: q for q in questions}
data = json.loads(DATA.read_text())
checks = []

def check(name, actual, expected=True, detail=None):
    ok = actual == expected
    row = {'name': name, 'pass': bool(ok), 'actual': actual, 'expected': expected}
    if detail is not None:
        row['detail'] = detail
    checks.append(row)
    assert ok, row

def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

check('question_numbers', sorted(Q), list(range(46, 71)))
check('source_ids_unique', len({q['source_id'] for q in questions}), 25)
banks = {}
for q in questions:
    if q['source_file'] not in banks:
        banks[q['source_file']] = {r.get('id', r.get('question_id')): r for r in rows(ROOT / q['source_file'])}
check('original_source_objects_unchanged', all(q['source_question'] == banks[q['source_file']][q['source_id']] for q in questions))
source_key_rows = [q for q in questions if q.get('source_answer') is not None]
check('provided_source_answer_count', len(source_key_rows), 11)
check('provided_source_answers_agree', all(q['source_answer'] == q['answer'] for q in source_key_rows))
check('mock_answers_marked_editorial', all(q['source_answer'] is None for q in questions if q['source_bank'] == 'guangdong_mock'))

# Current/retired source exclusion; old graphic booklet references are not user completion evidence.
excluded = {r['source_id'] for r in rows(PROJECT / '用题登记.jsonl') if r.get('paper_id') != 'M04'}
for paper in ['M01', 'M02', 'M03']:
    excluded.update(q['source_id'] for q in json.loads((PROJECT / paper / 'selection.json').read_text()))
exclusion_file = HERE.parent / '编辑底稿/excluded_source_ids.json'
if exclusion_file.exists():
    excluded.update(json.loads(exclusion_file.read_text()))
check('prior_paper_and_retired_id_overlap', sorted({q['source_id'] for q in questions} & excluded), [])
old_graphics = json.loads((PROJECT / 'M01/核验记录/old_graphic_source_ids.json').read_text())
old_graphic_ids = set(old_graphics['recognized_jz_source_ids'])
check('old_graphic_booklet_id_overlap', sorted({Q[n]['source_id'] for n in range(46, 51)} & old_graphic_ids), [])

# Q46: all four visible transitions share one cyclic two-dimensional translation.
g46 = [np.array(g) for g in data['q46_grids']]
shifts = [(r, c) for r in range(9) for c in range(9)
          if all(np.array_equal(np.roll(g46[i], (r, c), (0, 1)), g46[i + 1]) for i in range(4))]
check('q46_unique_cyclic_shift_mod_9', shifts, [(8, 8)])
q46_matches = [k for k, g in zip('ABCD', g46[5:]) if np.array_equal(np.roll(g46[4], (-1, -1), (0, 1)), g)]
check('q46_matching_option', q46_matches, [Q[46]['answer']])
check('q46_all_grids_have_14_black_cells', [int(g.sum()) for g in g46], [14] * 9)

# Q47: model the continuous route; each next frame removes one tail cell and adds two head cells.
route = [(0,0),(1,0),(2,0),(3,0),(4,0),(4,1),(4,2),(3,2),(2,2),
         (1,2),(0,2),(0,3),(0,4),(1,4),(2,4),(3,4),(4,4)]
g47 = [np.array(g) for g in data['q47_grids']]
def path_grid(k):
    out = np.zeros((5, 5), dtype=int)
    for r, c in route[k:5 + 2*k]:
        out[r, c] = 1
    return out
check('q47_all_five_frames_match_growth_rule', all(np.array_equal(path_grid(k), g47[k]) for k in range(5)))
q47_matches = [k for k, g in zip('ABCD', g47[5:]) if np.array_equal(path_grid(5), g)]
check('q47_matching_option', q47_matches, [Q[47]['answer']])

# Q48: positions of equal symbols, manually transcribed after actually viewing the source PNG.
q48_pattern = [0, 1, 1, 2, 3, 0, 2, 4]
q48_options = {'A':[0,1,1,2,3,0,2,3], 'B':[0,1,1,2,3,0,2,4],
               'C':[0,1,2,3,4,0,3,5], 'D':[0,1,1,2,3,1,2,4]}
check('q48_matching_equality_pattern', [k for k,v in q48_options.items() if v == q48_pattern], [Q[48]['answer']])

# The 24 orientation-preserving symmetries of the coordinate cube. Reflections are excluded.
eye = np.eye(3, dtype=int)
rotations = []
for perm in permutations(range(3)):
    for signs in product([-1, 1], repeat=3):
        matrix = eye[:, perm] * np.array(signs)
        if round(np.linalg.det(matrix)) == 1:
            rotations.append(matrix)
check('cube_proper_rotation_count', len(rotations), 24)

def fold_net(net):
    cells = {tuple(c) for c in net['cells']}
    start = tuple(net['cells'][0])
    # u points page-right, v page-down; the exterior normal is -cross(u,v).
    frames = {start:(np.array([1,0,0]), np.array([0,-1,0]), np.array([0,0,1]))}
    queue = deque([start])
    while queue:
        x,y = queue.popleft()
        u,v,n = frames[x,y]
        for (dx,dy), new in [((1,0),(-n,v,u)),((-1,0),(n,v,-u)),((0,1),(u,-n,v)),((0,-1),(u,n,-v))]:
            pos = (x+dx,y+dy)
            if pos in cells and pos not in frames:
                frames[pos] = new
                queue.append(pos)
    assert len(frames) == 6
    assert len({tuple(f[2]) for f in frames.values()}) == 6
    def point(cell, xy):
        u,v,n = frames[tuple(cell)]
        return n + xy[0]*u + xy[1]*v
    out = {}
    for kind in ['black','square']:
        cell,xy = net[kind]
        out[kind] = {'normal':frames[tuple(cell)][2], 'point':point(cell,xy)}
    cell,ends = net['tri']
    out['tri'] = {'normal':frames[tuple(cell)][2], 'points':[point(cell,xy) for xy in ends]}
    return out

left = {'black':{'normal':np.array([0,-1,0]),'point':np.array([-1,-1,-1])},
        'square':{'normal':np.array([0,0,1]),'point':np.array([-1,-1,1])}}
right = {'black':{'normal':np.array([0,0,1]),'point':np.array([1,1,1])},
         'square':{'normal':np.array([1,0,0]),'point':np.array([1,1,1])},
         'tri':{'normal':np.array([0,-1,0]),'points':[np.array([-1,-1,-1]),np.array([1,-1,-1])]}}
def matches(src, target, rotation):
    for kind,obj in target.items():
        for field,value in obj.items():
            if field == 'points':
                if sorted(tuple(rotation@p) for p in src[kind][field]) != sorted(tuple(p) for p in value):
                    return False
            elif not np.array_equal(rotation@src[kind][field], value):
                return False
    return True
net_matches = {side:[i for i,net in enumerate(data['q49_nets'],1)
                    if any(matches(fold_net(net),target,r) for r in rotations)]
               for side,target in [('left',left),('right',right)]}
check('q49_cube_net_matches', net_matches, {'left':[2], 'right':[4]})
check('q49_answer', Q[49]['answer'], 'A')

def normalise(cells):
    array = np.array(list(cells))
    array = array - array.min(axis=0)
    return tuple(sorted(map(tuple,array)))
solids = {k:{tuple(p) for p in v} for k,v in data['q50_cells'].items()}
solid_matches = {k:any(normalise([r@np.array(p) for p in solids['S']]) == normalise(v) for r in rotations)
                 for k,v in solids.items() if k != 'S'}
check('q50_rotational_equivalence', solid_matches, {'A':True,'B':True,'C':False,'D':True})
check('q50_answer', [k for k,v in solid_matches.items() if not v], [Q[50]['answer']])
def branches_outside_square(cells):
    squares = []
    for p in cells:
        for i,j in combinations(range(3),2):
            square = {p, tuple(np.array(p)+eye[i]), tuple(np.array(p)+eye[j]), tuple(np.array(p)+eye[i]+eye[j])}
            if square <= cells:
                squares.append(square)
    assert len(squares) == 1
    remaining = cells - squares[0]
    sizes = []
    while remaining:
        queue = [remaining.pop()]
        size = 0
        while queue:
            p = queue.pop()
            size += 1
            neighbours = {q for q in remaining if sum(abs(a-b) for a,b in zip(p,q)) == 1}
            remaining -= neighbours
            queue.extend(neighbours)
        sizes.append(size)
    return sorted(sizes)
check('q50_four_cube_square_branch_invariant', {k:branches_outside_square(v) for k,v in solids.items()},
      {'S':[2,2],'A':[2,2],'B':[2,2],'C':[1,3],'D':[2,2]})

# Q56: all three feature counts, biconditional, negative conjunction, and existence of the group leader.
people = range(4)
q56_solutions = []
for males in combinations(people,2):
    for party in combinations(people,3):
        for professor in people:
            if (0 in males) != (1 in males):
                continue
            if (1 in party) != (2 in party) or (2 in party and 3 in party):
                continue
            if not all(p in males or p in party or p == professor for p in people):
                continue
            leaders = [p for p in people if p in males and p in party and p == professor]
            if leaders:
                q56_solutions.append({'males':list(males),'party':list(party),'professor':professor,'leader':leaders[0]})
check('q56_unique_model', q56_solutions, [{'males':[2,3],'party':[0,1,2],'professor':2,'leader':2}])
check('q56_answer', Q[56]['answer'], 'ABCD'[q56_solutions[0]['leader']])

# Q60: a false compound statement is the negation of the whole conjunction.
q60_solutions = []
for heights in permutations([165,168,170,172]):
    for slim in combinations(people,2):
        truths = [heights[0] < 170, heights[2] == 172 and 2 in slim,
                  heights[3] == 168 and 3 not in slim, heights[1] == 165 and 1 in slim]
        if truths == [p in slim for p in people]:
            q60_solutions.append({'heights_cm':list(heights),'slim':list(slim)})
check('q60_unique_model', q60_solutions, [{'heights_cm':[165,172,170,168],'slim':[0,2]}])
check('q60_answer', Q[60]['answer'], 'D')

# Q63: any two cells within three steps on the route have different colours.
colours = ['红','橙','黄','绿','蓝']
known = {int(k):v for k,v in data['q63_fixed'].items()}
q63_solutions = []
def colour_search(prefix):
    i = len(prefix)+1
    if i == 21:
        q63_solutions.append(prefix)
        return
    for colour in ([known[i]] if i in known else colours):
        if colour not in prefix[-3:]:
            colour_search(prefix+[colour])
colour_search([])
check('q63_unique_model_count', len(q63_solutions), 1)
sequence = q63_solutions[0]
q63_options = {'A':sequence[1]=='绿','B':sequence[8]=='蓝','C':sequence[11]=='黄','D':sequence[18]=='红'}
check('q63_matching_option', [k for k,v in q63_options.items() if v], [Q[63]['answer']])
check('q63_route_is_20_connected_cells', len(set(map(tuple,data['q63_positions']))), 20)
check('q63_route_step_adjacency', all(sum(abs(a-b) for a,b in zip(p,q)) == 1
                                     for p,q in zip(data['q63_positions'], data['q63_positions'][1:])))

# Q67: solve the middle-node KCL for three equal resistance lamps, with ideal meters.
voltage, resistance = 12.0, 12.0
mid_voltage = float(np.linalg.solve([[2/resistance]], [voltage/resistance])[0])
meters = {'V1':voltage-mid_voltage, 'V2':mid_voltage, 'V3':voltage,
          'A1':(voltage-mid_voltage)/resistance, 'A2':mid_voltage/resistance, 'A3':voltage/resistance}
q67_options = {'A':meters['V3'] < min(meters['V1'],meters['V2']),
               'B':meters['A3'] > max(meters['A1'],meters['A2']),
               'C':meters['A1'] == meters['A2'], 'D':meters['V1'] == meters['V2']}
check('q67_only_false_option', [k for k,v in q67_options.items() if not v], [Q[67]['answer']])

# Q69: independent allele enumeration; the scenario assumes Mendelian dominant/recessive inheritance.
offspring = Counter(''.join(sorted((a,b))) for a in 'Aa' for b in 'Aa')
check('q69_genotype_frequencies', dict(offspring), {'AA':1,'Aa':2,'aa':1})
check('q69_long_wing_probability', (offspring['AA']+offspring['Aa'])/4, .75)
check('q69_answer', Q[69]['answer'], 'C')

asset_files = sorted((HERE.parent/'assets').glob('q*.png')) + sorted((HERE.parent/'assets').glob('q*.svg'))
owned_assets = [p for p in asset_files if int(p.name[1:3]) in [63]]
check('active_reconstructed_asset_count', len(owned_assets), 2)
assets = [{'path':str(p.relative_to(ROOT)), 'sha256':digest(p)} for p in owned_assets]
source_figures = ['s21_p11_i00.png','s25_p11_i00.png','s23_p12_i02.png','s22_p13_i01.png',
                  's26_p13_i00.png','s33_p18_i00.png','s17_p18_i00.png']
source_root = ROOT/'模考/2026下半年广东卷_16-33季_AI可读/assets'
source_images = [{'path':str((source_root/f).relative_to(ROOT)), 'sha256':digest(source_root/f)}
                 for f in source_figures if (source_root/f).exists()]

report = {
    'scope':'M04 Q46–70: 5 graphic, 15 logical, 5 scientific reasoning questions',
    'status':'v020_editor_rechecked_pending_incremental_claude',
    'method':'Editor read and solved before comparing available source keys. This is not an isolated blind review or Claude review.',
    'module_sha256':digest(MODULE), 'diagram_data_sha256':digest(DATA),
    'source_banks':[{'path':p,'sha256':digest(ROOT/p)} for p in banks],
    'checks':checks,
    'independent_text_review':{
        'path':'核验记录/reasoning_science_independent_review.json',
        'scope':'Historical v0.1.0 review only; replaced Q57 and revised explanations are not covered by that old agreement.',
        'followups_closed':'Current layout is verified separately; Q67 now uses the original figure.',
        'not_claimed':'This is internal GPT cross-review, not external Claude review.'
    },
    'q48_manual_symbol_patterns':{'stem':q48_pattern, 'options':q48_options},
    'q49_result':net_matches,
    'q50_rotation_result':solid_matches,
    'q56_solutions':q56_solutions, 'q60_solutions':q60_solutions,
    'q63_unique_sequence':sequence, 'q67_example_meter_values':meters,
    'q66_manual_derivation':{
        'static_phase':'B has zero horizontal friction; ground static friction on A balances F.',
        'moving_phase':'A and B remain relatively at rest; f_B=m_B*a, a=(F-f_ground)/(m_A+m_B).',
        'derivative':'df_B/dF=m_B/(m_A+m_B)>0 with positive masses and constant sliding ground friction.',
        'explicit_edit':'F continues increasing throughout the moving phase; ideal Coulomb sliding model.'
    },
    'visual_review':{
        'date':'2026-11-15',
        'historical_v010_source_images_viewed':[46,47,48,49,50,66,67],
        'current_revision_image_read_again':[48],
        'source_table_actually_read':[63],
        'historical_v010_redrawn_pngs_viewed':[46,47,49,50,63,66,67],
        'currently_active_reconstruction':[63],
        'q67_font_issue_fixed':'Replaced unsupported Unicode subscript glyphs with separately drawn small digits; final PNG reviewed.',
        'pdf_layout_review':'Out of scope for this module; the full-paper builder must inspect final rendered pages.'
    },
    'original_image_hashes':source_images, 'redraw_assets':assets,
    'limitations':[
        'The original PDFs were not downloaded and compared word-for-word in this session.',
        'Graphic grids/nets/solids were interpreted from source images; code proves consequences of that interpretation, not unseen original image content.',
        'Eleven Jiangzhe items have repository reference keys; fourteen mock items have editorial keys only. No claim of official answer provenance.',
        'Old-booklet source-ID screening does not establish full visual deduplication or user completion status.',
        'The current q57 is JS2023-A类-104 (answer A); previous candidates and the v0.1 complaint-rate question are retired and do not supply its proof.',
        'Textual argument questions require human reading; deterministic constraint checks do not certify their semantics.'
    ]
}
out = HERE/'reasoning_science_verification.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks_passed':len(checks),'provided_keys':len(source_key_rows),
                  'editorial_only_keys':25-len(source_key_rows),'report':str(out.relative_to(ROOT))}, ensure_ascii=False))
