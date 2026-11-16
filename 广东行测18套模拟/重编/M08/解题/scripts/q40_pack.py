"""M08 第40题：机器:工人=2:3，机器40秒/份，工人90秒/份，每天10小时，共9000份，求机器比人工多包装多少份。枚举k。"""
T = 10*3600
per_m, per_w = T//40, T//90
print('每台机器/天', per_m, '每名工人/天', per_w)
sols = [(2*k, 3*k) for k in range(1, 100) if 2*k*per_m + 3*k*per_w == 9000]
print('(机器数, 工人数):', sols)
assert sols == [(6, 9)]
m, w = sols[0]
diff = m*per_m - w*per_w
print('机器', m*per_m, '人工', w*per_w, '差', diff)
assert diff == 1800
print('若误按效率比2:3分配 9000:', 9000*2//5, 9000*3//5)
