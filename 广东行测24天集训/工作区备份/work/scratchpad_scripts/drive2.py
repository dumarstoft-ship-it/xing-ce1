import sys
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad')
from drive import run, int_cands, frac_cands, P
from fractions import Fraction as F
which=sys.argv[1:]
if 'G4-20' in which: run('G4-20', cands=[F(i) for i in range(-3000,3001)])
if 'G4-06' in which: run('G4-06', seq_str='7，11，19，35，67，（　）', opts={'A':'99','B':'123','C':'131','D':'135'})
if 'G4-23' in which: run('G4-23')
if 'G4-26' in which: run('G4-26', cands=[F(i) for i in range(0,20001)])
