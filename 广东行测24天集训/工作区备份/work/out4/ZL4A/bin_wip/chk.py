"""chk.py g2 [g3 ...]: run group modules, list answers, margins, precision-label consistency."""
import sys, importlib
import lib
from lib import Q, ORDER, prec
for mname in [a for a in sys.argv[1:] if not a.startswith("--")]:
    n0 = len(ORDER)
    importlib.import_module(mname)
    for k in ORDER[n0:]:
        q = Q[k]; mg = q['margin']
        flag = '' if (mg is None or prec(mg) == q['precision_need']) else f'  <-- prec label {q["precision_need"]} vs auto {prec(mg)}'
        print(f"{k:<20} {q['kind']:<4} {q['ans']} m={mg:.3f} {q['precision_need']:<6} {q['intensity']:<6} {q['difficulty']}{flag}")
        if '--v' in sys.argv: print('     ', q['calc'])
