import sys
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *

# SZ2023-38 alternative reading: 相隔3天 = difference 3, 相隔4天 = difference 4
SH=['篮','滑','牛','凉','拖']
for g1,g2 in [(4,5)]:
    M=[]
    for w in product(SH, repeat=7):
        lq=[i for i,x in enumerate(w) if x=='篮']
        if len(lq)!=2 or lq[1]-lq[0]!=g1: continue
        if w.count('牛')!=1 or w.count('滑')!=1: continue
        if abs(w.index('牛')-lq[0])!=1: continue
        if not w.index('滑')<lq[1]: continue
        lj=[i for i,x in enumerate(w) if x=='凉']
        if not lj or any(abs(i-lq[0])!=g2 for i in lj): continue
        if not any(w[i]=='拖' for i in range(lq[0])): continue
        M.append(w)
    print('SZ2023-38 reading',g1,g2,len(M))
    if M:
        judge(f'SZ2023-38[{g1},{g2}]', M, {'A':lambda w:w[0]=='篮','B':lambda w:w[2]=='牛','C':lambda w:w[3]=='拖','D':lambda w:w[4]=='滑'},'must','B')

# SC2025-85 square table: seats N,E,S,W clockwise (seen from above). Left-hand of person facing center.
# Person at seat i faces center; their left-hand neighbour: for a person at S facing N, left is W. Clockwise order N,E,S,W.
# left of seat i = seat (i+1)%4 ? check: S index2 facing north: left = W index3 = (2+1)%4 -> yes. right = (i-1)%4.
names=['高','胡','杨','陈']
M=[]
for seat in permutations(range(4)):
    S=dict(zip(names,seat)); who={v:k for k,v in S.items()}
    for col in permutations(['蓝','黄','粉','红']):
        C=dict(zip(names,col))
        left=lambda n:who[(S[n]+1)%4]; right=lambda n:who[(S[n]-1)%4]; opp=lambda n:who[(S[n]+2)%4]
        if left('杨')!='陈': continue
        if C['陈']=='蓝': continue
        blue=[n for n in names if C[n]=='蓝'][0]
        if right(blue)!='胡': continue
        yel=[n for n in names if C[n]=='黄'][0]
        if opp('杨')!=yel: continue
        if yel=='胡': continue
        M.append((S,C))
print('SC2025-85 models',len(M))
def colr(m,c): return [n for n in names if m[1][n]==c][0]
oppn=lambda m,n:[k for k in names if m[0][k]==(m[0][n]+2)%4][0]
judge('SC2025-85', M, {'A':lambda m: oppn(m,colr(m,'红'))==colr(m,'粉'),'B':lambda m: oppn(m,'陈')==colr(m,'黄'),'C':lambda m: m[1]['胡']=='红','D':lambda m: oppn(m,'高')!='杨'},'must','A')
# mirror convention check
M2=[]
for seat in permutations(range(4)):
    S=dict(zip(names,seat)); who={v:k for k,v in S.items()}
    for col in permutations(['蓝','黄','粉','红']):
        C=dict(zip(names,col))
        left=lambda n:who[(S[n]-1)%4]; right=lambda n:who[(S[n]+1)%4]; opp=lambda n:who[(S[n]+2)%4]
        if left('杨')!='陈' or C['陈']=='蓝': continue
        blue=[n for n in names if C[n]=='蓝'][0]
        if right(blue)!='胡': continue
        yel=[n for n in names if C[n]=='黄'][0]
        if opp('杨')!=yel or yel=='胡': continue
        M2.append((S,C))
print('SC2025-85 mirrored-convention models',len(M2))
if M2: judge('SC2025-85(mirror)', M2, {'A':lambda m: oppn(m,colr(m,'红'))==colr(m,'粉'),'B':lambda m: oppn(m,'陈')==colr(m,'黄'),'C':lambda m: m[1]['胡']=='红','D':lambda m: oppn(m,'高')!='杨'},'must','A')
