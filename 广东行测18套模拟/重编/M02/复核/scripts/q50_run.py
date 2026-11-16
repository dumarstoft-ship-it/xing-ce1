import sys
sys.path.insert(0, '.')
from q50_fit import refine
res = {}
for name, (X0, YB, off) in {'A': (33, 209.5, (25, 140)), 'B': (156, 209.5, (148, 140)),
                            'C': (268, 209.0, (262, 140)), 'D': (395, 209.5, (387, 140))}.items():
    res[name] = refine(name, X0, YB, off)
