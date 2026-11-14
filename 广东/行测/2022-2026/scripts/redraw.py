# -*- coding: utf-8 -*-
"""Redraw low-resolution source diagrams with explicit geometry. No generated content."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).parent;O=W/'redrawn';O.mkdir(exist_ok=True);manifest={};S=3
FONT='/System/Library/Fonts/Supplemental/Songti.ttc';LATIN='/System/Library/Fonts/Supplemental/Times New Roman.ttf'
class Canvas:
 def __init__(self,w,h):self.im=Image.new('RGB',(w*S,h*S),'white');self.d=ImageDraw.Draw(self.im)
 def line(self,pts,width=2,fill='black'):self.d.line([(round(x*S),round(y*S)) for x,y in pts],fill=fill,width=round(width*S),joint='curve')
 def poly(self,pts,fill='white',width=2):self.d.polygon([(round(x*S),round(y*S)) for x,y in pts],fill=fill);self.line(pts+[pts[0]],width)
 def ellipse(self,box,fill='white',width=2):self.d.ellipse(tuple(round(v*S) for v in box),fill=fill,outline='black',width=round(width*S))
 def text(self,xy,s,size=27,anchor='mm',latin=False):self.d.text((xy[0]*S,xy[1]*S),s,font=ImageFont.truetype(LATIN if latin else FONT,size*S),fill='black',anchor=anchor)
 def dash(self,a,b,step=12,width=2):
  x,y=a;dx,dy=b[0]-x,b[1]-y;L=math.hypot(dx,dy)
  for t in range(0,int(L),step*2):u=min(t+step,L);self.line([(x+dx*t/L,y+dy*t/L),(x+dx*u/L,y+dy*u/L)],width)
 def arrow(self,a,b,width=2,head=12):
  self.line([a,b],width);dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy);ux,uy=dx/L,dy/L
  self.poly([b,(b[0]-head*ux+head*.35*uy,b[1]-head*uy-head*.35*ux),(b[0]-head*ux-head*.35*uy,b[1]-head*uy+head*.35*ux)],fill='black',width=1)
 def save(self,ids,description):
  for iid in ids.split():self.im.save(O/(iid+'.png'));manifest[iid]={'script':'redraw.py','description':description,'verification':'人工对照原图核对线段、连接关系、标签和相对位置'}
# Source GD2022-XZ p13 i02: same origin, same distance, different arrival times.
c=Canvas(620,470);c.arrow((80,410),(570,410),3);c.arrow((80,410),(80,35),3);c.dash((80,105),(520,105),7,2)
c.line([(80,410),(350,105)],3);c.line([(80,410),(500,105)],3);c.text((52,47),'s',32,latin=True);c.text((585,417),'t',32,latin=True);c.text((237,185),'甲',34);c.text((390,262),'乙',34)
c.save('GD2022-XZ-p13-i02','按原图重绘s-t图；共同原点、共同终点高度及两条直线斜率顺序保持一致。')
# Cube with a low horizontal slice. Hidden back edge remains dotted.
c=Canvas(350,370)
c.poly([(40,285),(115,225),(315,225),(240,285)],'#b1b1b1')
c.poly([(40,285),(240,285),(240,340),(40,340)],'#b1b1b1')
c.poly([(240,285),(315,225),(315,280),(240,340)],'#b1b1b1')
c.line([(40,100),(115,40),(315,40),(240,100),(40,100),(40,340)],3)
c.line([(240,100),(240,340)],3);c.line([(315,40),(315,280),(240,340)],3);c.dash((115,40),(115,225),2,2)
c.text((166,260),'切面',35)
c.save('GD2023-XZ-p09-i01 GD2023-XJ-p08-i01','按原图重绘正方体水平切面，保留底部灰色区域及背面虚线。')
# Block on an incline: preserve triangle, block orientation and force direction.
c=Canvas(640,360);c.poly([(30,310),(600,310),(600,115)],'white',3)
a=math.atan2(-195,570);u=(math.cos(a),math.sin(a));v=(u[1],-u[0]);P=(360,310-(360-30)*195/570);L=95
pts=[P,(P[0]+L*u[0],P[1]+L*u[1]),(P[0]+L*(u[0]+v[0]),P[1]+L*(u[1]+v[1])),(P[0]+L*v[0],P[1]+L*v[1])];c.poly(pts,'white',3)
c.text((P[0]+L*(u[0]+v[0])/2,P[1]+L*(u[1]+v[1])/2),'M',45,latin=True)
c.arrow((210,225),(315,189),3,16);c.text((245,168),'F',46,latin=True)
c.save('GD2023-XZ-p18-i01','按原图重绘斜面、M物体及沿斜面向上的F箭头。')
# Velocity-time plot, two source copies.
c=Canvas(620,520);c.arrow((90,470),(90,35),3);c.arrow((90,310),(570,310),3)
c.line([(90,310),(210,110),(435,440),(545,310)],3)
c.dash((90,110),(210,110),10,3);c.dash((210,110),(210,310),10,3);c.dash((90,440),(435,440),10,3);c.dash((435,310),(435,440),10,3)
c.text((60,48),'v',32,latin=True);c.text((584,314),'t',32,latin=True);c.text((65,327),'0',27,latin=True)
for x,y,base,sub in [(55,110,'v','1'),(55,440,'v','2'),(210,335,'t','1'),(346,336,'t','2'),(435,286,'t','3'),(545,286,'t','4')]:
 c.text((x-5,y),base,29,latin=True);c.text((x+8,y+8),sub,20,latin=True)
c.save('GD2023-XZ-p21-i01 GD2023-XJ-p22-i01','按原图重绘v-t折线及t₁—t₄、v₁/v₂标记；零点交叉、虚线和正负区域保持一致。')
# Cold plate above a candle. Rebuild only the printed outline and labels.
c=Canvas(440,450)
c.ellipse((40,30,400,95),fill='#e6e6e6',width=2)
# Bowl front: shallow curved sides, flattened lower edge.
points=[]
for t in range(181):
 theta=math.radians(t);points.append((220+180*math.cos(theta),min(134,62+90*math.sin(theta))))
c.line(points,3)
# Candle and flame remain under the plate, with matching contact direction.
c.poly([(195,185),(250,185),(250,425),(195,425)],'#e8e8e8',2)
for shift in [-24,-12,0,12,24]:
 pts=[(222,185)]
 for i in range(1,40):
  t=i/39;pts.append((222+shift*math.sin(t*math.pi/2),185-48*t))
 c.line(pts,1.5)
c.text((220,110),'冷碟子',29);c.text((222,278),'蜡',31);c.text((222,319),'烛',31)
c.save('GD2024-p11-i01','按原图重绘冷碟子与蜡烛示意图；保留相对位置和原文字标签。')
(W/'redraw_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('redrawn',len(manifest))
