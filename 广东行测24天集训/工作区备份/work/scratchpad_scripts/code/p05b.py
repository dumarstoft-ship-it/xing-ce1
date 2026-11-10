exec(open('p05.py').read().split("for mirror in (False,True):")[0])
import itertools
hidden=[(1,1,0)]
base=set(solid)
for drop in [(1,1,0)]:
    solid=base-{drop}
    print('drop',drop,'size',len(solid))
    for k,v in opts.items():
        if len(P1)+len(P2)+len(P3)+len(v)!=len(solid): print(k,'size mismatch'); continue
        pl=[placements(P,True) for P in (P1,P2,P3,v)]
        n=0
        for a in pl[0]:
            for b in pl[1]:
                if a&b: continue
                for c in pl[2]:
                    if (a|b)&c: continue
                    for d in pl[3]:
                        if (a|b|c)&d: continue
                        if len(a|b|c|d)==len(solid): n+=1
        print(k,'solutions',n)
