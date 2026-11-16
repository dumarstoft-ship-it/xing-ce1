"""Q48: 5行x10列黑底白块, 问号占第3-5行、第4-6列(3x3). 读出已知格, 检验"白块排成左上-右下方向的斜线, 每隔两条出现一条"
(等价于: 每一行都是上一行整体右移一格, 每行白块间隔3格), 推出问号处并与选项比对."""
from PIL import Image
import numpy as np
IMG='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s22_p12_i01.png'
im=np.array(Image.open(IMG).convert('L')).astype(float)
x0,x1,y0,y1=65.5,428,5,187.5; cw=(x1-x0)/10; ch=(y1-y0)/5
def cell(r,c):
    cx=x0+(c+0.5)*cw; cy=y0+(r+0.5)*ch
    return '.' if im[int(cy)-6:int(cy)+7,int(cx)-6:int(cx)+7].mean()>200 else '#'
G=[[('?' if (r>=2 and 3<=c<=5) else cell(r,c)) for c in range(10)] for r in range(5)]
print('\n'.join(''.join(row) for row in G))
known=[(r,c) for r in range(5) for c in range(10) if G[r][c]!='?']
rule=lambda r,c:'.' if (c-r)%3==2 else '#'
print('规律对全部已知格成立:',all(G[r][c]==rule(r,c) for r,c in known))
pred=[''.join(rule(r,c) for c in range(3,6)) for r in range(2,5)]
print('问号处应为:',pred)
opts={'A':(13,120),'B':(134,241),'C':(256,363),'D':(378,485)}
for k,(a,b) in opts.items():
    w=(b-a)/3; h=(319-212)/3
    g=[''.join('.' if im[int(212+(r+.5)*h)-6:int(212+(r+.5)*h)+7,int(a+(c+.5)*w)-6:int(a+(c+.5)*w)+7].mean()>200 else '#' for c in range(3)) for r in range(3)]
    print('选项'+k,g,'<- 符合' if g==pred else '')
