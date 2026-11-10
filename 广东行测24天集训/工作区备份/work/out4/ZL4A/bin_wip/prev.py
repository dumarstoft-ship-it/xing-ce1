"""prev.py <tag> <q0> <q1>: print parsed stem/options for original questions (qparse), to spot garbling."""
import sys
from qparse import parse, qrec
tag, q0, q1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
for q in range(q0, q1 + 1):
    x = qrec(tag, q)
    stem, opts = parse(x['text'], q)
    print(f'[{tag}-{q}] p{x["segs"][0][0]+1} segs={[[s[0], round(s[1]), round(s[2])] for s in x["segs"]]} imgs={len(x["images"])}')
    print('   S:', stem)
    print('   O:', opts)
