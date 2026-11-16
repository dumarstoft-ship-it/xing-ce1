# Extra Q57 truth table.  P = 采取大刀阔斧的举措, G = 经济稳健增长, D = 公共债务不断攀升
# premise1 "除非P，否则不G": not P -> not G ;  premise2 "没有G，D": not G -> D
import itertools
imp=lambda a,b: (not a) or b
models=[(P,G,D) for P,G,D in itertools.product([True,False],repeat=3)
        if imp(not P, not G) and imp(not G, D)]
print('models (P,G,D):',models)
opts={
 'A: D -> not P':            lambda P,G,D: imp(D, not P),
 'B: 只有非P才D = D -> not P': lambda P,G,D: imp(D, not P),
 'C: P -> not D':            lambda P,G,D: imp(P, not D),
 'D: not D -> P':            lambda P,G,D: imp(not D, P),
}
for k,f in opts.items():
    bad=[m for m in models if not f(*m)]
    print(k,'VALID' if not bad else 'not valid, counterexample %s'%(bad[0],))
