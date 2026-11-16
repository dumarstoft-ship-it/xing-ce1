"""Q46: 读出5个题图和4个选项的4x4黑白格, 检验"黑格按从左到右、从上到下的顺序整体后移一格(末格移回首格)"."""
from PIL import Image
import numpy as np
IMG='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s22_p11_i07.png'
im=np.array(Image.open(IMG).convert('L')).astype(float)
def centers(lines):
    g=[];cur=[lines[0]]
    for v in lines[1:]:
        if v==cur[-1]+1: cur.append(v)
        else: g.append(cur); cur=[v]
    g.append(cur); return [(c[0]+c[-1])/2 for c in g]
def read(rowl,coll):
    cells=set()
    for i in range(4):
        for j in range(4):
            m=im[int(rowl[i])+3:int(rowl[i+1])-2,int(coll[j])+3:int(coll[j+1])-2].mean()
            assert m<100 or m>180
            if m<100: cells.add(i*4+j)
    return cells
top=centers([24,25,26,40,41,42,55,56,57,71,72,73,86,87,88])
bot=centers([149,150,151,165,166,167,180,181,182,196,197,198,211,212,213])
tops=[[24,25,26,40,41,55,56,57,70,71,72,86,87,88],[122,123,124,138,139,153,154,155,169,170,171,184,185,186],
      [219,220,221,235,236,250,251,252,266,267,268,281,282,283],[316,317,318,331,332,333,347,348,349,363,364,378,379,380],
      [414,415,416,430,431,445,446,447,461,462,463,476,477,478]]
bots=[[121,122,123,136,137,138,152,153,167,168,169,183,184,185],[218,219,220,234,235,236,249,250,251,265,266,280,281,282],
      [317,318,319,332,333,334,348,349,363,364,365,379,380,381],[414,415,416,430,431,445,446,447,461,462,463,476,477,478]]
P=[read(top,centers(c)) for c in tops]
O={k:read(bot,centers(c)) for k,c in zip('ABCD',bots)}
show=lambda s:'\n'.join(''.join('#' if 4*r+c in s else '.' for c in range(4)) for r in range(4))
for i,s in enumerate(P): print('图%d 黑格序号(按行读)'%(i+1),sorted(s))
for k,s in O.items(): print('选项'+k,sorted(s))
shift=lambda s:{(x+1)%16 for x in s}
print('每步+1成立:',all(shift(P[i])==P[i+1] for i in range(4)))
nxt=shift(P[4]); print('推得问号处:',sorted(nxt)); print(show(nxt))
print('符合的选项:',[k for k,s in O.items() if s==nxt])
