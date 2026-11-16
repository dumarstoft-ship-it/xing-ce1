#!/usr/bin/env python3
"""Exact diagram redraws from stored source grid, net and topology data."""
from pathlib import Path
import json, math, html
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE.parent/'assets';OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
class Canvas:
 def __init__(self,w,h,scale=3):
  self.w=w;self.h=h;self.s=scale;self.im=Image.new('RGB',(w*scale,h*scale),'white');self.d=ImageDraw.Draw(self.im);self.parts=[]
 def points(self,p):return [(round(x*self.s),round(y*self.s))for x,y in p]
 def polygon(self,p,fill='white',stroke='black',width=1.6):
  self.d.polygon(self.points(p),fill=fill)
  if stroke:self.d.line(self.points(p+[p[0]]),fill=stroke,width=max(1,round(width*self.s)),joint='curve')
  self.parts.append(f'<polygon points="'+ ' '.join(f'{x:.3f},{y:.3f}'for x,y in p)+f'" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}" stroke-linejoin="round"/>')
 def rect(self,x,y,w,h,fill='white',stroke='black',width=1.6):self.polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill,stroke,width)
 def line(self,p,width=1.6,fill='black'):
  self.d.line(self.points(p),fill=fill,width=max(1,round(width*self.s)),joint='curve');self.parts.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}'for x,y in p)+f'" fill="none" stroke="{fill}" stroke-width="{width}" stroke-linejoin="round"/>')
 def text(self,x,y,t,size=24):
  f=ImageFont.truetype(FONT,round(size*self.s));bbox=self.d.textbbox((0,0),t,font=f);self.d.text((round(x*self.s)-(bbox[2]+bbox[0])/2,round(y*self.s)-(bbox[3]+bbox[1])/2),t,font=f,fill='black');self.parts.append(f'<text x="{x}" y="{y}" font-family="Noto Sans CJK SC" font-size="{size}" text-anchor="middle" dominant-baseline="central">{html.escape(t)}</text>')
 def circle(self,x,y,r,fill='white',width=1.6):
  self.d.ellipse((round((x-r)*self.s),round((y-r)*self.s),round((x+r)*self.s),round((y+r)*self.s)),fill=fill,outline='black',width=round(width*self.s));self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="black" stroke-width="{width}"/>')
 def save(self,name):
  self.im.save(OUT/(name+'.png'));(OUT/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><rect width="100%" height="100%" fill="white"/>'+''.join(self.parts)+'</svg>')

def sample_grid(path,locations,n,step):
 im=np.array(Image.open(ROOT/path).convert('L'))
 return [[[int(im[round(y+(r+.5)*step),round(x+(col+.5)*step)]<128)for col in range(n)]for r in range(n)]for x,y in locations]
def grids_figure(grids,name):
 n=len(grids[0]);c=Canvas(1200,510);cell=16 if n==9 else 28;side=n*cell
 def panel(x,y,g=None,label=None):
  c.rect(x-9,y-9,side+18,side+18,width=2)
  if g is None:c.text(x+side/2,y+side/2,'?',90)
  else:
   for r in range(n):
    for col in range(n):c.rect(x+col*cell,y+r*cell,cell,cell,fill='black'if g[r][col]else'white',width=.8)
  if label:c.text(x+side/2,y+side+43,label,32)
 for i,g in enumerate(grids[:5]):panel(22+194*i,22,g)
 panel(22+194*5,22)
 for i,g in enumerate(grids[5:]):panel(215+194*i,280,g,'ABCD'[i])
 c.save(name)
g46=sample_grid('模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i00.png',[(13+98*i,15)for i in range(5)]+[(113+98*i,145)for i in range(4)],9,9.55)
g47=sample_grid('模考/2026下半年广东卷_16-33季_AI可读/assets/s25_p11_i00.png',[(16+98*i,18)for i in range(5)]+[(114+98*i,149)for i in range(4)],5,15.2)
assert all(np.array_equal(np.roll(np.array(g46[i]),(-1,-1),(0,1)),g46[i+1])for i in range(4))
assert np.array_equal(np.roll(np.array(g46[4]),(-1,-1),(0,1)),g46[6])
grids_figure(g46,'q46_pixel_shift');grids_figure(g47,'q47_growing_path')
# Cube nets: coordinates are source image cells, markings are local face corners.
nets=[{'cells':[(0,1),(1,1),(2,1),(2,0),(3,1),(3,2)],'black':((2,0),(1,1)),'square':((3,1),(-1,-1)),'tri':((0,1),[(-1,1),(1,1)])},{'cells':[(1,0),(1,1),(0,1),(2,1),(2,2),(3,2)],'black':((0,1),(1,1)),'square':((3,2),(-1,1)),'tri':((1,0),[(-1,-1),(1,-1)])},{'cells':[(1,0),(1,1),(2,1),(3,1),(1,2),(0,2)],'black':((1,1),(-1,1)),'square':((1,0),(-1,-1)),'tri':((3,1),[(-1,-1),(1,-1)])},{'cells':[(0,0),(1,0),(1,1),(2,1),(2,2),(3,2)],'black':((2,1),(1,1)),'square':((2,2),(1,-1)),'tri':((1,1),[(-1,-1),(-1,1)])}]
c=Canvas(1240,310)
def project(x,y,z):return (30+65*x+30*y,215-30*y-65*z)
for x in [0,1]:
 c.polygon([project(x,0,0),project(x+1,0,0),project(x+1,0,1),project(x,0,1)])
 c.polygon([project(x,0,1),project(x+1,0,1),project(x+1,1,1),project(x,1,1)])
c.polygon([project(2,0,0),project(2,1,0),project(2,1,1),project(2,0,1)])
c.polygon([project(0,0,0),project(.5,0,0),project(.5,0,.5),project(0,0,.5)],fill='black')
c.polygon([project(0,0,1),project(.5,0,1),project(.5,.5,1),project(0,.5,1)])
c.polygon([project(1.5,.5,1),project(2,.5,1),project(2,1,1),project(1.5,1,1)],fill='black')
c.line([project(1,0,0),project(1.5,0,.5),project(2,0,0)],width=2)
c.polygon([project(2,.5,.5),project(2,1,.5),project(2,1,1),project(2,.5,1)])
for i,net in enumerate(nets):
 ox=280+i*230;oy=60;a=43
 for x,y in net['cells']:c.rect(ox+a*x,oy+a*y,a,a,width=1.8)
 for kind in ['black','square']:
  (x,y),(sx,sy)=net[kind];xx=ox+a*x+(a/2 if sx==1 else 0);yy=oy+a*y+(a/2 if sy==1 else 0);c.rect(xx,yy,a/2,a/2,fill='black'if kind=='black'else'white',width=1.8)
 (x,y),ends=net['tri'];pts=[(ox+a*x+(sx+1)*a/2,oy+a*y+(sy+1)*a/2)for sx,sy in ends];c.line([pts[0],(ox+a*x+a/2,oy+a*y+a/2),pts[1]],width=1.8)
 c.text(ox+1.5*a,255,'①②③④'[i],28)
c.save('q49_cube_nets')
# Same block sets as verification; draw only outward visible faces, with exact unit seams.
S={(0,0,0),(0,0,1),(0,1,0),(0,1,1),(0,1,2),(1,1,2),(1,1,0),(2,1,0)}
A={(x,1,2)for x in range(3)}|{(0,0,2),(1,0,2),(0,1,1),(0,1,0),(2,1,1)}
B={(x,1,2)for x in range(3)}|{(2,0,2),(2,1,1),(2,1,0),(2,0,1),(1,1,0)}
C={(x,0,2)for x in range(3)}|{(1,1,2),(2,1,2),(0,0,1),(0,0,0),(2,0,1)}
D={(x,1,0)for x in range(3)}|{(1,0,0),(2,0,0),(0,1,1),(2,1,1),(2,1,2)}
c=Canvas(1200,720)
def solid(T,cx,cy,unit=46):
 faces=[]
 for x,y,z in T:
  for delta,corners,fill in [((0,-1,0),[(x,y,z),(x+1,y,z),(x+1,y,z+1),(x,y,z+1)],'white'),((1,0,0),[(x+1,y,z),(x+1,y+1,z),(x+1,y+1,z+1),(x+1,y,z+1)],'#dddddd'),((0,0,1),[(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)],'white')]:
   if (x+delta[0],y+delta[1],z+delta[2])not in T:
    depth=sum(a-2*b+d for a,b,d in corners)/4;faces.append((depth,corners,fill))
 raw=lambda q:(unit*q[0]+unit*.5*q[1],-unit*.5*q[1]-unit*q[2])
 allp=[raw(p)for _,ps,_ in faces for p in ps];mx=(min(x for x,y in allp)+max(x for x,y in allp))/2;my=(min(y for x,y in allp)+max(y for x,y in allp))/2
 for dep,ps,fill in sorted(faces):c.polygon([(cx+raw(p)[0]-mx,cy+raw(p)[1]-my)for p in ps],fill=fill,width=2.2)
solid(S,600,150,65)
for i,T in enumerate([A,B,C,D]):
 c.rect(10+295*i,335,295,315,width=2.4);solid(T,157.5+295*i,493,52);c.text(157.5+295*i,687,'ABCD'[i],32)
c.save('q50_solids')
# Source table reconstructs a 20-cell route. Known colours remain textual in monochrome.
c=Canvas(680,310);positions=[(0,2),(1,2),(1,1),(1,0),(2,0),(3,0),(3,1),(3,2),(3,3),(4,3),(5,3),(5,2),(5,1),(5,0),(6,0),(7,0),(8,0),(9,0),(9,1),(9,2)];fixed={1:'红',5:'橙',6:'黄',10:'红',14:'蓝',16:'黄',18:'橙',20:'绿'}
for i,(x,y)in enumerate(positions,1):
 xx=20+64*x;yy=20+64*y;c.rect(xx,yy,64,64,width=1.6);c.text(xx+32,yy+32,fixed.get(i,str(i)),25)
c.save('q63_snake')
# A below B; horizontal force acts on A.
c=Canvas(960,340);c.line([(60,300),(900,300)],width=2)
for x in range(70,900,30):c.line([(x,300),(x-18,324)],width=1.5)
c.rect(230,150,320,150,width=2);c.rect(310,45,140,105,width=2);c.text(390,225,'A',34);c.text(380,98,'B',34);c.line([(550,210),(800,210)],width=3);c.polygon([(800,210),(780,200),(780,220)],fill='black',width=1);c.text(705,175,'F',30);c.save('q66_blocks')
# Ideal meter topology redraw. V1/V2 are open branches; L1,L2 are series.
c=Canvas(620,700)
def indexed_label(x,y,label,size=24):
 # Draw the index independently: the available CJK font has no subscript glyphs.
 base=label[0];index=label[1:].translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉','0123456789'))
 c.text(x-5,y,base,size);c.text(x+11,y+8,index,size*.62)
def meter(x,y,label):c.circle(x,y,25,width=1.7);indexed_label(x,y,label,24)
def lamp(x,y,label):
 c.circle(x,y,24,width=1.7);c.line([(x-16,y-16),(x+16,y+16)],width=1.6);c.line([(x-16,y+16),(x+16,y-16)],width=1.6);indexed_label(x+43,y-24,label,23)
c.line([(65,210-25),(65,60),(540,60),(540,625)],width=2)
c.line([(65,210+25),(65,625)],width=2)
c.line([(65,150),(275,150),(275,305)],width=2)
c.line([(65,305),(540,305)],width=2)
c.line([(350,305),(350,450),(540,450)],width=2)
c.line([(65,625),(540,625)],width=2)
c.line([(65,545),(200,545)],width=2);c.line([(200,522),(200,568)],width=2.3);c.line([(216,531),(216,559)],width=2.3);c.line([(216,545),(310,545)],width=2);c.circle(310,545,3,fill='black',width=1);c.line([(310,545),(354,519)],width=2.2);c.circle(365,545,3,fill='black',width=1);c.line([(365,545),(540,545)],width=2);c.text(330,503,'S',24)
meter(65,210,'A₁');meter(175,305,'V₁');meter(430,305,'V₂');meter(305,60,'V₃');meter(350,382,'A₂');meter(390,625,'A₃');lamp(275,225,'L₁');lamp(455,450,'L₂');lamp(240,625,'L₃')
for x,y in [(65,150),(65,305),(275,305),(350,305),(540,305),(540,450),(65,545),(540,545)]:c.circle(x,y,2.6,fill='black',width=.5)
c.save('q67_circuit')
meta={'q46_grids':g46,'q47_grids':g47,'q49_nets':nets,'q50_cells':{k:sorted(v)for k,v in zip('SABCD',[S,A,B,C,D])},'q63_positions':positions,'q63_fixed':fixed,'q67_topology':{'series_branch':['A1','L1','A2','L2'],'parallel_branch':['L3','A3'],'voltage_meters':{'V1':'L1 endpoints','V2':'L2 endpoints','V3':'power endpoints'}}}
(HERE/'reasoning_diagram_data.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Wrote seven diagrams as SVG and PNG.')
