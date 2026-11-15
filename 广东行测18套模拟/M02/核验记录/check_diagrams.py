import itertools,json
import numpy as np
from pathlib import Path
from PIL import Image
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'模考/2026下半年广东卷_16-33季_AI可读/assets/s29_p11_i00.png'
im=np.array(Image.open(p).convert('L'))
boxes=[(14,12,94,98),(106,12,193,98),(205,12,293,98),(307,12,394,98),(407,12,494,98),(112,140,197,224),(208,140,294,224),(308,140,393,224),(405,140,487,224)]
cs=[]
for b in boxes:
 a=im[b[1]:b[3],b[0]:b[2]]>160;labs,num=ndimage.label(a)
 border=set(np.concatenate([labs[0],labs[-1],labs[:,0],labs[:,-1]]))
 regs=[int((labs==i).sum()) for i in range(1,num+1) if i not in border and (labs==i).sum()>10]
 cs.append(regs)
# Face pattern types: full diamond F; blank O; grid G; centered line M; offset line L; offset narrow diamond D.
nets={
 'A':{(0,0):('F',None),(1,0):('O',None),(2,0):('L','left'),(3,0):('G',None),(0,-1):('M','vertical'),(1,1):('D','left')},
 'B':{(0,0):('F',None),(1,0):('D','left'),(2,0):('L','down'),(3,0):('M','horizontal'),(1,-1):('G',None),(2,1):('O',None)},
 'C':{(0,0):('G',None),(1,0):('M','vertical'),(1,1):('F',None),(2,1):('O',None),(3,1):('L','left'),(2,2):('D','left')},
 'D':{(0,0):('F',None),(1,0):('D','left'),(2,0):('L','up'),(1,-1):('O',None),(2,1):('G',None),(3,1):('M','vertical')}
}
def fold(net):
 start=next(iter(net));f={start:(np.array([1,0,0]),np.array([0,1,0]),np.array([0,0,1]))};todo=[start]
 while todo:
  x,y=todo.pop();u,v,n=f[(x,y)]
  for dx,dy,ori in [(1,0,(-n,v,u)),(-1,0,(n,v,-u)),(0,1,(u,-n,v)),(0,-1,(u,n,-v))]:
   p=(x+dx,y+dy)
   if p in net and p not in f:f[p]=ori;todo.append(p)
 out={}
 for p,(typ,direction) in net.items():
  u,v,n=f[p];line=None;off=None
  if typ=='M':line=v if direction=='vertical' else u
  if typ in ('L','D'):
   off={'left':-u,'right':u,'up':-v,'down':v}[direction]
   line=v if direction in ('left','right') else u
  out[typ]={'normal':n,'line':line,'offset':off}
 assert len({tuple(x['normal']) for x in out.values()})==6
 return out
rot=[]
for perm in itertools.permutations(range(3)):
 for sgn in itertools.product([-1,1],repeat=3):
  m=np.eye(3,dtype=int)[:,perm]*np.array(sgn)
  if round(np.linalg.det(m))==1:rot.append(m)
assert len(rot)==24
def match(a,b):
 for m in rot:
  ok=True
  for typ in a:
   for k in ['normal','line','offset']:
    va=a[typ][k];vb=b[typ][k]
    if va is None:continue
    x=m@va
    if not (np.array_equal(x,vb) or k=='line' and np.array_equal(x,-vb)):ok=False
  if ok:return m.tolist()
 return None
fs={k:fold(v) for k,v in nets.items()}
assert match(fs['A'],fs['B']) is None and all(match(fs['A'],fs[k]) is not None for k in ['A','C','D'])
assert [len(x) for x in cs]==[5,4,5,4,5,5,4,4,5]
out={'Q48_enclosed_regions':[len(x) for x in cs],'Q50_net_transcription':{k:[{'xy':list(xy),'pattern':v[0],'orientation':v[1]} for xy,v in net.items()] for k,net in nets.items()},'Q50_A_to_each_proper_rotation':{k:match(fs['A'],f) for k,f in fs.items()},'Q50_boundary':'网格坐标与图案朝向人工目视转录；程序核验折叠和24种正旋转，不等同于自动图像识别。'}
(Path(__file__).parent/'diagram_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','Q48_regions':out['Q48_enclosed_regions'],'Q50_A_matches':[k for k,v in out['Q50_A_to_each_proper_rotation'].items() if v is not None]},ensure_ascii=False))
