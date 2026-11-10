import itertools
people=['赵一','王二','张三','李四']
sols=[]
for order in itertools.permutations(people):
    pos={p:i for i,p in enumerate(order)}
    for killer in people:
        k=pos[killer]
        alive_arr=lambda p: pos[p]<=k   # alive when p arrives
        alive_leave=lambda p: pos[p]<k  # alive when p leaves
        # all clauses false
        c=[]
        c.append(not(False))            # zhao: 'none of us killed' is false (killer among 4) -> always true here
        c.append(not alive_leave('赵一'))
        c.append(not(pos['王二']==1))
        c.append(not(not alive_arr('王二')))
        c.append(not(pos['张三']==2))
        c.append(not alive_leave('张三'))
        c.append(not(pos[killer]<=pos['李四']))  # '凶手进他家不比我晚' false
        c.append(not(not alive_arr('李四')))
        if all(c): sols.append((order,killer))
for s in sols: print(s)
print('killers:',set(k for _,k in sols))
