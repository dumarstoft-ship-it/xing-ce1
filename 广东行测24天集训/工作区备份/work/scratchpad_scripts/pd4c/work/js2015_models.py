from itertools import product
B=(0,1); ppl='WZL'; name={'W':'王刚','Z':'赵虎','L':'李亮'}; tn={'d':'单身','p':'乒乓','n':'北方','s':'硕士'}
def imp(a,b): return (not a) or b
M=[]
for bits in product(B, repeat=12):
    X={(p,t):bits[i*4+j] for i,p in enumerate(ppl) for j,t in enumerate('dpns')}
    if any(sum(X[(p,t)] for p in ppl)!=2 for t in 'dpns'): continue
    if any(sum(X[(p,t)] for t in 'dpns')>3 for p in ppl): continue
    if not imp(X[('W','s')] and X[('L','s')], X[('W','n')] and X[('L','n')]): continue
    if not imp(X[('Z','p')] and X[('L','p')], X[('Z','d')] and X[('L','d')]): continue
    M.append(X)
def show(X): return '；'.join(name[p]+'：'+'、'.join(tn[t] for t in 'dpns' if X[(p,t)]) for p in ppl)
M69=[X for X in M if imp(X[('W','n')],X[('W','d')])]
M70=[X for X in M if imp(X[('Z','d')],X[('W','d')])]
print('69 models',len(M69))
for X in M69: print('  ',show(X))
print('70 models',len(M70))
for X in M70: print('  ',show(X))
