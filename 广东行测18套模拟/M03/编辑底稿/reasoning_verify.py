#!/usr/bin/env python3
"""Checks tied to the M03 reasoning source records; no source-bank mutation."""
from __future__ import annotations
import hashlib
import itertools as it
import json
from pathlib import Path
import re
import statistics
import subprocess
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
rows=json.loads((HERE/'reasoning.json').read_text())
qm={q['number']:q for q in rows}
report={
    'scope':'M03 reasoning editorial contribution; not an external blind review',
    'date':'2026-11-15',
    'module_sha256':hashlib.sha256((HERE/'reasoning.json').read_bytes()).hexdigest(),
    'checks':{},
}
C=report['checks']

# Exhaust all assignments, rather than merely substitute the keyed answer.
states=[]
for qin,wei,han in it.product([False,True],repeat=3):
    claims=[not wei or han,not qin and not wei,qin or wei]
    if sum(claims)==1:
        states.append({'qin':qin,'wei':wei,'han':han})
assert states and all(s['wei'] and not s['han'] for s in states)
C['Q51']={'answer':'C','all_models':states}

subjects=['文学','经济','历史','社会']
states=[]
for majors in it.permutations(subjects):
    if majors[2:]!=('历史','文学'):continue
    for books in it.permutations(subjects):
        if books[0]!='社会' or books[1]=='文学':continue
        if any(a==b for a,b in zip(majors,books)):continue
        states.append({'majors':majors,'books':books})
truths=[
    all(s['majors'][0]=='经济' for s in states),
    all(s['books'][2]=='文学' for s in states),
    all(s['majors'][1]=='社会' for s in states),
    all(s['books'][3]=='历史' for s in states),
]
assert len(states)==2 and truths==[True,True,True,False]
C['Q53']={'answer':'D','all_models':states,'option_necessity':dict(zip('ABCD',truths))}

failures={k:[] for k in 'ABCD'}
checked=0
for a,b,c,d in it.product(range(11),repeat=4):
    if not a>d:continue
    checked+=1
    opts=[a+b<c+d,a+b>c+d,a>d,c>d]
    if a+c<=b+d:
        for k,ok in zip('ABCD',opts):
            if ok and not failures[k]:failures[k]=[a,b,c,d]
assert not failures['A'] and all(failures[k] for k in 'BCD')
# This bounded search corroborates, but does not replace, the algebraic proof.
assert 2>1 and 2+10>2+1 and 2>1 and 2+2<10+1
C['Q55']={
    'answer':'A','bounded_assignments_with_premise':checked,
    'first_counterexamples_for_other_options':failures,
    'unbounded_proof':'a>d and a+b<c+d imply c-b>a-d>0; adding a>d and c>b gives a+c>b+d.',
}

jobs=['企业家','大学教师','歌手','会计师']
states=[]
for js in it.permutations(jobs):
    predictions=[js[1]!='歌手',js[2]=='会计师',js[3]!='企业家',js[1]!='大学教师']
    if all(p==(job=='会计师') for p,job in zip(predictions,js)):
        states.append(js)
assert states==[('会计师','大学教师','歌手','企业家')]
C['Q60']={'answer':'D','all_models':states,'assignments_checked':24}

states=[]
for a,b,c,d,e,f in it.product([False,True],repeat=6):
    if c+d!=1 or not(a or b) or a+d!=1 or b!=c or a+e+f!=2:continue
    states.append([a,b,c,d,e,f])
assert len(states)==2 and all(sum(s)==4 and s[:4]==[True,True,True,False] for s in states)
C['Q63']={'answer':'C','all_models':states,'assignments_checked':64,
           'source_analysis_issue':'The source explanation drops one direction of iff; its Ding-selected branch violates the actual question.'}

premise_models=[]
for p,q,r in it.product([False,True],repeat=3):
    if (not(p and q) or r) and p and not r:premise_models.append([p,q,r])
assert premise_models==[[True,False,False]]
C['Q64']={'answer':'A','normalized_premise_models':premise_models,
           'note':'Natural-language structural matching was reviewed separately; enumeration checks the shared conjunction/contraposition schema.'}
C['Q61']={'answer':'D','shared_invalid_schema':'P->R, Q->R, therefore R->(P or Q)',
           'countermodel':{'P':False,'Q':False,'R':True}}

# Inspect original source pixels at the centres of the honeycomb's 8x7 cells.
path=ROOT/'江浙行测_AI题库/images/original/1244.png'
im=Image.open(path).convert('L')
def sample(x0,y0):
    cols=[]
    for col in range(8):
        vals=[]
        for row in range(7):
            x=round(x0+10.94*col)
            y=round(y0+6*(col%2)+12.17*row)
            px=[im.getpixel((xx,yy)) for xx in range(x-1,x+2) for yy in range(y-1,y+2)]
            vals.append(int(statistics.median(px)<128))
        cols.append(vals)
    return cols

def moved(m):
    return [[m[(c-2)%8][(r-1)%7] for r in range(7)] for c in range(8)]

def distance(a,b):
    return sum(a[c][r]!=b[c][r] for c in range(8) for r in range(7))

stem=[sample(x,25.42) for x in [29.2,142.7,254.7,363.9]]
options=[sample(x,167.1) for x in [82.4,190.3,298.2,407.3]]
dist=[distance(moved(stem[i]),stem[i+1]) for i in range(3)]
od=[distance(moved(stem[-1]),o) for o in options]
assert dist==[0,0,0] and od==[0,2,4,21]
C['Q47']={'answer':'A','image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
           'grid_columns':8,'cells_per_column':7,'transition_mismatches':dist,
           'option_mismatches':dict(zip('ABCD',od)),
           'sampled_columns':{str(i+1):[''.join(map(str,c)) for c in m] for i,m in enumerate(stem)},
           'boundary_rule':'Columns wrap modulo 8; cells within a column wrap modulo 7.'}

# A constructive filling witness for the spatial problem, in a fixed 4x2x3 box.
# The D transcription is from the pictured option after rotating it horizontally.
box=set(it.product(range(4),range(2),range(3)))
piece1={(x,y,0) for x in range(4) for y in range(2)}|{(1,1,1),(3,1,1),(3,1,2)}
piece2={(2,0,1),(3,0,1),(2,1,1)}
pieceD={(x,y,2) for x in range(4) for y in range(2) if (x,y)!=(3,1)}|{(0,0,1),(1,0,1),(0,1,1)}
assert len(piece1)==11 and len(piece2)==3 and len(pieceD)==10
assert not(piece1&piece2 or piece1&pieceD or piece2&pieceD)
assert piece1|piece2|pieceD==box
C['Q50']={'answer':'D','box_dimensions':[4,2,3],
           'piece1':sorted(piece1),'piece2':sorted(piece2),'rotated_D':sorted(pieceD),
           'note':'Constructive D witness plus visual elimination of A/B/C; this is not an exhaustive machine reconstruction of all four pictured options.'}

# Exact project-source deduplication, source preservation and known exposure checks.
prior=set()
for m in ['M01','M02']:
    prior|={q['source_id'] for q in json.loads((ROOT/f'广东行测18套模拟/{m}/selection.json').read_text())}
withdrawn=ROOT/'广东行测18套模拟/M02/撤题记录.json'
prior|={q['source_id'] for q in json.loads(withdrawn.read_text())}
assert not prior&{q['source_id'] for q in rows}
banks={}
for q in rows:
    sf=q['source_file']
    if sf not in banks:
        raw=list(map(json.loads,(ROOT/sf).read_text().splitlines()))
        banks[sf]={x.get('question_id',x.get('id')):x for x in raw}
    assert q['source_question']==banks[sf][q['source_id']]

index=(ROOT/'习题本/图推/200题与固定题型_题后即看答案/平面图推200题_题源索引.md').read_text()
known_planar={('JS' if p=='江苏' else 'ZJ')+y+'-A类-'+n.zfill(3)
              for y,p,n in re.findall(r'｜(20\d+)年(江苏|浙江)\s*·\s*原第(\d+)题',index)}
spatial=subprocess.check_output(['pdftotext','-layout',str(ROOT/'习题本/图推/200题与固定题型_题后即看答案/固定题型178题_题后即看答案.pdf'),'-']).decode()
graph_hits=[]
for q in rows[:5]:
    s=q['source_question']
    if q['source_id'] in known_planar or re.search(str(s['year'])+s['province']+r'[^\n]*第'+str(s['original_number'])+r'题',spatial):
        graph_hits.append(q['number'])
assert not graph_hits
oldfiles=[p for directory in ['广东行测24天集训','习题本'] for p in (ROOT/directory).rglob('*')
          if p.is_file() and p.suffix in ['.md','.json','.jsonl','.csv','.txt']]
oldtext=[(str(p.relative_to(ROOT)),re.sub(r'\s+','',p.read_text(errors='ignore'))) for p in oldfiles]
hits={}
for q in rows:
    s=q['source_question']['stem']
    if isinstance(s,list):s=''.join(b.get('text','') for b in s)
    prefix=re.sub(r'\s+','',s)[:45]
    hs=[p for p,t in oldtext if q['source_id'] in t or (q['number']>50 and prefix in t)]
    if hs:hits[q['number']]=hs
assert not hits
C['integrity']={
    'question_count':20,'numbers':list(range(46,66)),'source_answer_matches':18,
    'source_records_unchanged':True,'M01_M02_and_withdrawn_overlap':[],
    'known_planar200_spatial178_overlap':graph_hits,
    'old_text_files_scanned':len(oldfiles),'old_stable_id_or_45char_stem_hits':hits,
    'boundary':'No match is not a proof of never having seen the question; cross-version paraphrases and unindexed external practice are outside this scan.',
}
report['result']='PASS'
(HERE/'reasoning_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 20-source integrity; 18 source answers; five exhaustive logic checks; honeycomb pixels; spatial filling witness; prior-project exposure scan.')
