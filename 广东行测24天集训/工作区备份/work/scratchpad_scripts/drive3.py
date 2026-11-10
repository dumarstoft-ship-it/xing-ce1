import sys
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad')
from drive import run, int_cands, frac_cands, P
from fractions import Fraction as F
for b in sys.argv[1:]:
    if b in ('G4-05','G4-10'):
        seq_vals=None
        # halves allowed
        cands=sorted({F(p,q) for q in (1,2,4) for p in range(-3000*q//q*q, 3000*q+1)}, key=lambda x:(x.denominator,abs(x)))
        run(b, cands=cands)
    else:
        run(b, cands=frac_cands([F(3)], maxden=30, mult=6) if b!='G4-18' else frac_cands([F(25)], maxden=12, mult=2))
