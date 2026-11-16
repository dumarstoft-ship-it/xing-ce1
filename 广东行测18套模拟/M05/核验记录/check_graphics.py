#!/usr/bin/env python3
"""Reproducible checks for region counts, symbol repetition and cube edges.
Figure-to-model transcription is explicit and still requires human review.
"""
import json,hashlib,itertools
from pathlib import Path
from collections import deque
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parents[1];R=D.parents[1];M=R/'模考/2026下半年广东卷_16-33季_AI可读'
Q={q['number']:q for q in json.loads((D/'selection.json').read_text())}
# Count bounded white components, ignoring the frame and external background.
im=Image.open(M/'assets/s27_p12_i00.png').convert('L').resize((800,938),Image.Resampling.NEAREST)
def regions(box):
 a=np.asarray(im.crop(box));white=a>150;H,W=white.shape;seen=np.zeros_like(white);sizes=[]
 for y in range(H):
  for x in range(W):
   if not white[y,x] or seen[y,x]:continue
   seen[y,x]=True;q=deque([(y,x)]);size=0;touch=False
   while q:
    yy,xx=q.popleft();size+=1;touch|=yy==0 or yy==H-1 or xx==0 or xx==W-1
    for Y,X in [(yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)]:
     if 0<=Y<H and 0<=X<W and white[Y,X] and not seen[Y,X]:seen[Y,X]=True;q.append((Y,X))
   if not touch and size>60:sizes.append(size)
 return len(sizes)
stem=[regions((108+c*198,18+r*196,294+c*198,197+r*196)) for r in range(3) for c in range(3) if (r,c)!=(2,2)]
options=[regions((18+c*194,665,201+c*194,850)) for c in range(4)]
assert stem==[2,3,4,3,4,2,5,7],stem
assert options==[6,7,7,5],options
assert Q[47]['answer']=='ABCD'[options.index(stem[2]+stem[5])]
# Original glyphs, including orientation, are transcribed as equivalence classes.
pattern=[0,1,2,0,3,1,2,0]
patterns={'A':[0,1,2,0,1,3,2,0],'B':[0,1,0,2,3,4,2,5],'C':[0,1,2,0,3,4,2,5],'D':pattern}
assert [k for k,v in patterns.items() if v==pattern]==[Q[48]['answer']]
# Cube-net geometry. Image y points down, so displayed face has v=(0,-1,0).
cells={(0,0):0,(1,0):1,(1,1):0,(2,1):1,(2,2):0,(3,2):1}
basis={(0,0):(np.array([1,0,0]),np.array([0,-1,0]),np.array([0,0,1]))};stack=[(0,0)]
while stack:
 a=stack.pop();u,v,n=basis[a]
 for delta,b in [((1,0),(-n,v,u)),((-1,0),(n,v,-u)),((0,1),(u,-n,v)),((0,-1),(u,n,-v))]:
  c=(a[0]+delta[0],a[1]+delta[1])
  if c in cells and c not in basis:basis[c]=b;stack.append(c)
def edge(c,side):
 u,v,n=basis[c]
 return (n+u-v,n+u+v) if side=='r' else (n-v-u,n-v+u)
E={8:edge((0,0),'r'),5:edge((1,1),'r'),6:edge((2,2),'r'),7:edge((2,1),'t')}
V={1:[[-1,1,1],[1,1,1]],2:[[1,-1,1],[1,1,1]],3:[[1,-1,-1],[1,1,-1]],4:[[-1,-1,-1],[-1,-1,1]]}
canon=lambda ps:tuple(sorted(tuple(int(x) for x in p) for p in ps));visible={(0,0,1),(0,-1,0),(1,0,0)}
opts={'A':{1:7,2:5,3:6,4:8},'B':{1:6,2:5,3:8,4:7},'C':{1:5,2:7,3:8,4:6},'D':{1:5,2:7,3:6,4:8}}
records=[];rotations=0
for perm in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  mat=np.eye(3,dtype=int)[:,perm]@np.diag(signs)
  if round(np.linalg.det(mat))!=1:continue
  rotations+=1
  if {tuple(mat@basis[c][2]) for c in cells if cells[c]}!=visible:continue
  transformed={k:canon([mat@a for a in ends]) for k,ends in E.items()}
  pairs={k:next((j for j,e in transformed.items() if e==canon(ends)),None) for k,ends in V.items()}
  records.append({'rotation':mat.tolist(),'pairs':pairs,'matching_options':[x for x,q in opts.items() if q==pairs]})
assert rotations==24 and {a for r in records for a in r['matching_options']}=={Q[49]['answer']}
assets={}
for n in [46,47,48,49,50,66,67,70,90]:
 s=Q[n]['source_question'];blocks=s['stem']+sum(s['options'].values(),[])
 for b in blocks:
  if b.get('type')=='figure':assets[b['path']]=hashlib.sha256((M/b['path']).read_bytes()).hexdigest()
report={'status':'PASS','version':'0.1.0','q47':{'bounded_regions_stem':stem,'options':dict(zip('ABCD',options)),'threshold':150,'minimum_area_doubled_pixels':60},
'q48':{'stem_pattern':pattern,'option_patterns':patterns,'same_glyph_rule':'完整朝向不变的同一图符'},
'q49':{'rotations_examined':rotations,'compatible_rotations':records},'source_asset_sha256':assets,
'manual_checks':{'46':'逐元素追踪后合并；原图已查看。','50':'截面高低边界、遮挡和右端小块由原图判断；不声称程序已证明原图三维实体模型。','66':'原F-t图已查看，不将F曲线等同于摩擦力曲线。','67':'原图接线已查看；等效电路的代数检查在数学逻辑报告。','70':'原图线型和标高已查看。','90':'四个原选项实际查看，数值二次差分另算。'},
'limits':['像素连通域只辅助面计数，不替代读题。','符号和折叠模型的图像转写由同一编辑完成，不是独立盲审。','未重绘任何源图。']}
(D/'核验记录/图形核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'PASS','region_counts':options,'cube_answer':Q[49]['answer']},ensure_ascii=False))
