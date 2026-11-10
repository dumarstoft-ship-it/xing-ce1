import json, numpy as np, collections
M=np.load('hashM.npy'); K=json.load(open('hashK.json')); keys=K['keys']; ar=np.array(K['ar'])
n=len(keys)
D=(M[:,None,:]!=M[None,:,:]).sum(-1)/M.shape[1]
pairs=[]
for i in range(n):
    for j in range(i+1,n):
        if D[i,j]<0.12 and abs(np.log(ar[i]/ar[j]))<0.25:
            pairs.append((keys[i],keys[j],round(float(D[i,j]),3)))
# union-find
par={k:k for k in keys}
def f(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for a,b,d in pairs: par[f(a)]=f(b)
groups=collections.defaultdict(list)
for k in keys: groups[f(k)].append(k)
G={k:sorted(v) for k,v in groups.items() if len(v)>1}
json.dump({'pairs':pairs,'groups':list(G.values())},open('imgdups.json','w'),ensure_ascii=False)
print(len(pairs), len(G))
# distribution of distances near threshold
near=[(keys[i],keys[j],round(float(D[i,j]),3)) for i in range(n) for j in range(i+1,n) if 0.12<=D[i,j]<0.2 and abs(np.log(ar[i]/ar[j]))<0.25]
print('near',len(near))
for x in near[:60]: print(x)
