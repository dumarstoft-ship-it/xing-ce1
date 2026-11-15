"""Q47 rule check: search all torus translations (dr, dq) with dq even (keeps odd-q lattice parity)
that map P1->P2, P2->P3, P3->P4 simultaneously; then apply to P4 and compare with options.
Input: q47_grids.json (from q47_grid.py, transcription verified visually via q47_render.py)."""
import json
import os
D=os.path.dirname(os.path.abspath(__file__))+'/'
G=json.load(open(D+'q47_grids.json'))
NC,NR=8,7
names=['P1','P2','P3','P4','A','B','C','D']
S={n:frozenset((r,q) for r in range(NR) for q in range(NC) if G[n]['grid'][r][q]=='#') for n in names}
def T(s,dr,dq): return frozenset(((r+dr)%NR,(q+dq)%NC) for r,q in s)
hits=[]
for dr in range(NR):
    for dq in range(0,NC,2):
        score=[len(T(S[a],dr,dq)&S[b]) for a,b in (('P1','P2'),('P2','P3'),('P3','P4'))]
        if sum(score)>=30: hits.append((dr,dq,score))
        if score==[16,16,16]:
            nxt=T(S['P4'],dr,dq)
            print(f'translation dr={dr} (rows down), dq={dq} (cols right) maps P1->P2->P3->P4 exactly (16/16 each)')
            for o in 'ABCD':
                print(f'  option {o}: overlap with predicted = {len(nxt&S[o])}/16, extra={sorted(S[o]-nxt)}, missing={sorted(nxt-S[o])}')
print('all translations with >=30/48 overlap:',hits)
# Also show it is 2 steps along the lower-right hex direction
print('Note: in odd-q layout, (dr=1,dq=2) = two steps toward the lower-right neighbour.')
