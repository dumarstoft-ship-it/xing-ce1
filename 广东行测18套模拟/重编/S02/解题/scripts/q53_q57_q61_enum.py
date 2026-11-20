"""S02 第53、57、61题：枚举检验。"""
import itertools
# ---- 第53题：每天(上午, 下午)∈{鱼,蟹}²，上午鱼→下午蟹；3个上午鱼、3个下午鱼、4个下午蟹 ----
days = []
for n in range(1, 15):
    for combo in itertools.combinations_with_replacement([('鱼', '蟹'), ('蟹', '鱼'), ('蟹', '蟹')], n):
        am_fish = sum(a == '鱼' for a, b in combo); pm_fish = sum(b == '鱼' for a, b in combo)
        pm_crab = sum(b == '蟹' for a, b in combo)
        if am_fish == 3 and pm_fish == 3 and pm_crab == 4:
            days.append(n)
print('第53题 可能的天数：', sorted(set(days)))
# ---- 第57题：只有下雨，客车才不准时（不准时→下雨） ----
imp = lambda a, b: (not a) or b
must = {'一定': True, '可能': True, '不可能': True}
for rain, late in itertools.product([0, 1], repeat=2):
    if imp(late, rain) and late:
        must['一定'] &= bool(rain); must['不可能'] &= not rain
print('第57题 客车没准时时，“遇到下雨天”：', '一定' if must['一定'] else ('不可能' if must['不可能'] else '可能'))
# ---- 第61题：赵钱孙李排名，按①～⑤枚举 ----
know = {frozenset('孙李'), frozenset('钱李')}            # ①⑤：经常一起打球、骑车，彼此认识
ball = {'孙', '李'}; bike = {'钱', '李'}
sols = []
for perm in itertools.permutations('赵钱孙李'):
    rank = {p: i + 1 for i, p in enumerate(perm)}
    first, second, third = perm[0], perm[1], perm[2]
    if frozenset((first, third)) in know: continue           # ②第一、三名刚认识
    if second in ball or second in bike: continue             # ③第二名不骑车不打球
    if not rank['赵'] < rank['钱']: continue                 # ④
    sols.append(perm)
print('第61题 名次（一到四）：', sols)
