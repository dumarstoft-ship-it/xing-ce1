import itertools
people=['赵一','王二','张三','李四']
sols=[]
for order in itertools.permutations(people):
    pos={p:i for i,p in enumerate(order)}
    for killer in people+['外人']:
        k=pos.get(killer,None)
        def alive_arr(p): return True if k is None else pos[p]<=k
        def alive_leave(p): return True if k is None else pos[p]<k
        s_zhao=(killer=='外人') and alive_leave('赵一')
        s_wang=(pos['王二']==1) and (not alive_arr('王二'))
        s_zhang=(pos['张三']==2) and alive_leave('张三')
        s_li=(k is not None and k<=pos['李四']) and (not alive_arr('李四'))
        if not any([s_zhao,s_wang,s_zhang,s_li]): sols.append((order,killer))
print(len(sols)); print(set(k for _,k in sols))
