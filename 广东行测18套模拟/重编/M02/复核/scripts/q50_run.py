"""Automatic render-fit of the four Q50 options.  NOTE: for option B the greedy fit drops (0,2,1)
by a tiny loss margin; the zoomed comparison shows the top layer's left edge is one unbroken
diagonal, so (0,2,1) is present.  Final readings used for the verdict are in q50_robust.py."""
import sys
sys.path.insert(0, '.')
from q50_fit import refine
res = {}
for name, (X0, YB, off) in {'A': (33, 209.5, (25, 140)), 'B': (156, 209.5, (148, 140)),
                            'C': (268, 209.0, (262, 140)), 'D': (395, 209.5, (387, 140))}.items():
    res[name] = refine(name, X0, YB, off)
