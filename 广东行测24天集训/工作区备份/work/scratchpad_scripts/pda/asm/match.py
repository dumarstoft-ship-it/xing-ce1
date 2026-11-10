import json, itertools, numpy as np
exec(open('asm.py').read().split('FULL=')[0])
res=json.load(open('comps.json'))
comps=[ [tuple(x) for x in c] for c in res["((0, 1, 0), (0, 2, 0))"]]
Cvis=[(0,2,2),(1,2,2),(1,1,2),(1,0,1),(2,0,1),(2,1,1),(2,0,0),(2,1,0)]
for i,R in enumerate(comps):
    print('complement',i,sorted(R))
    for o in orientations(R):
        a=set(o)
        # try translations aligning Cvis inside
        for t in itertools.product(range(-2,3),repeat=3):
            sh={(c[0]+t[0],c[1]+t[1],c[2]+t[2]) for c in Cvis}
            if sh<=a:
                extra=sorted(a-sh)
                print('   matches C-visible with translation',t,'extra cubes',extra)
