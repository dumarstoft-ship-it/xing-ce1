import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan4 import PLAN, PXPLAN
from mkcrop import stitch
from preview import show
day, i = sys.argv[1], int(sys.argv[2])
n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
keys = (PLAN[day] + PXPLAN[day])[i:i+n]
os.makedirs('vb', exist_ok=True)
print(stitch(f'vb/{day}_{i:02d}.png', keys))
show(keys)
