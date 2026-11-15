#!/usr/bin/env python3
"""Q50: explicit visual transcription and exhaustive proper-rotation packing.

This verifies the stated voxel transcription, not image interpretation itself.
No original source, selection, or module report is modified.
"""
from itertools import permutations, product
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IMAGE = ROOT / '江浙行测_AI题库/images/original/352.png'

# Coordinates: x right, y back, z up. A/B/C/D are transcribed upright.
PIECES = {
    '1': {(x,y,0) for x in range(4) for y in range(2)}
         | {(1,1,1),(3,1,1),(3,1,2)},
    '2': {(0,0,0),(1,0,0),(1,0,1)},
    'A': {(x,1,z) for x in range(2) for z in range(4)
          if (x,z)!=(0,0)} | {(0,0,1),(0,0,2),(1,0,0)},
    'B': {(x,1,z) for x in range(2) for z in range(4)}
         | {(1,0,z) for z in range(4)} | {(0,0,0)},
    'C': {(x,0,z) for x in range(2) for z in range(4)}
         | {(1,1,3),(1,2,3)},
    'D': {(x,1,z) for x in range(2) for z in range(4)
          if (x,z)!=(1,3)} | {(0,0,0),(0,0,1),(1,0,0)},
}

ROTATIONS=[]
for perm in permutations(range(3)):
    parity=(-1)**sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3))
    for signs in product((-1,1),repeat=3):
        if parity*signs[0]*signs[1]*signs[2]==1:
            ROTATIONS.append((perm,signs))
assert len(ROTATIONS)==24

def normal(shape):
    mins=[min(p[a] for p in shape) for a in range(3)]
    return frozenset(tuple(p[a]-mins[a] for a in range(3)) for p in shape)

def dims(shape):
    return tuple(max(p[a] for p in shape)-min(p[a] for p in shape)+1 for a in range(3))

def orientations(shape):
    return {normal({tuple(signs[a]*p[perm[a]] for a in range(3)) for p in shape})
            for perm,signs in ROTATIONS}

def placements(shape,box):
    out=set()
    for oriented in orientations(shape):
        d=dims(oriented)
        for off in product(*(range(box[a]-d[a]+1) for a in range(3))):
            out.add(frozenset(tuple(p[a]+off[a] for a in range(3)) for p in oriented))
    return sorted(out,key=lambda s:sorted(s))

def factor_boxes(volume):
    return [(a,b,volume//(a*b)) for a in range(1,volume+1)
            for b in range(a,volume//a+1)
            if volume%(a*b)==0 and volume//(a*b)>=b]

def encoded(shape):
    return sorted(shape)

report={
    'scope':'Internal supplementary spatial verification, not Claude external review',
    'source_id':'ZJ2021-A类-085', 'M03_number':50,
    'image_sha256':hashlib.sha256(IMAGE.read_bytes()).hexdigest(),
    'image_was_visually_inspected':True,
    'image_interpretation_limit':
      'Standard pictured polycube convention: the shaded faces bound the depicted solid, '
      'with no unshown appendages or internal cavities. Enumeration proves this explicit '
      'transcription; it is not automatic recovery of hidden geometry from pixels. '
      'A has two occluded cells (0,1,1),(0,1,2); removing either only lowers the '
      'combined volume below the 24-cell minimum box containing piece 1.',
    'rotation_count':len(ROTATIONS),
    'rotations':[{'permutation':p,'signs':s,'determinant':1} for p,s in ROTATIONS],
    'transcription':{k:{'cells':encoded(v),'volume':len(v),
                        'bounding_dimensions':dims(v)} for k,v in PIECES.items()},
    'options':{},
}

for key in 'ABCD':
    volume=len(PIECES['1'])+len(PIECES['2'])+len(PIECES[key])
    candidates=factor_boxes(volume)
    admissible=[b for b in candidates if placements(PIECES['1'],b)]
    result={'total_volume':volume,'all_factor_boxes':candidates,
            'boxes_containing_piece1':admissible,'boxes':[],'solution_count':0}
    for boxdims in admissible:
        box=frozenset(product(*(range(n) for n in boxdims)))
        p1s=placements(PIECES['1'],boxdims)
        p2s=set(placements(PIECES['2'],boxdims))
        ops=placements(PIECES[key],boxdims)
        disjoint=[];solutions=[]
        for p1 in p1s:
            for op in ops:
                if p1&op:continue
                remainder=box-p1-op
                disjoint.append((p1,op))
                if remainder in p2s:
                    solutions.append({'piece1':encoded(p1),'piece2':encoded(remainder),
                                      'option':encoded(op)})
        result['boxes'].append({'dimensions':boxdims,'piece1_placements':len(p1s),
            'piece2_placements':len(p2s),'option_placements':len(ops),
            'piece1_option_disjoint_pairs':len(disjoint),
            'solution_count':len(solutions),'witnesses':solutions})
        result['solution_count']+=len(solutions)
    report['options'][key]=result

# A transparent fixed-frame elimination. Full base forbids A at z=0.
boxdims=(4,2,3)
fixed=PIECES['1']
tall={(3,1,1),(3,1,2)}
short={(1,1,1)}
upper_As=[a for a in placements(PIECES['A'],boxdims)
          if min(c[2] for c in a)==1]
avoid_tall=[a for a in upper_As if not a&tall]
assert len(upper_As)==8 and len(avoid_tall)==2
assert all(a&short for a in avoid_tall)
report['A_layer_elimination']={
    'fixed_piece1':encoded(fixed),'A_placements_above_full_base':len(upper_As),
    'placements_avoiding_tall_pillar':len(avoid_tall),
    'remaining_placements':[{'cells':encoded(a),
        'z1':sorted((x,y) for x,y,z in a if z==1),
        'z2':sorted((x,y) for x,y,z in a if z==2),
        'collision_with_short_pillar':encoded(a&short)} for a in avoid_tall],
    'all_eight_placements':[{'cells':encoded(a),'collision_with_piece1':encoded(a&fixed)}
                            for a in upper_As],
}
assert [report['options'][k]['solution_count'] for k in 'ABCD']==[0,0,0,4]
report['conclusion']='D is unique for the explicitly transcribed standard polycubes.'
(HERE/'q50_spatial_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:{'volume':v['total_volume'],'boxes':v['boxes_containing_piece1'],
                    'solutions':v['solution_count']} for k,v in report['options'].items()},ensure_ascii=False))
print(json.dumps(report['A_layer_elimination']['remaining_placements'],ensure_ascii=False))
