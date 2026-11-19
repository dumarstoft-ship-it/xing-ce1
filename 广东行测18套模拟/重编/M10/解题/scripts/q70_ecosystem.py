"""M10 第70题：柱状图只给五个物种的个体数量 A>B>C>D>E，问哪项“必然正确”。
用一个与柱状图相容的反例检验A、B、C：林地里一棵（少量）大树是生产者，昆虫个体最多（数量金字塔倒置）。"""
counts = {'A': 5000, 'B': 300, 'C': 40, 'D': 8, 'E': 2}     # 与图的大小顺序一致
assert list(counts) == sorted(counts, key=counts.get, reverse=True)
# 反例：E=乔木（生产者），A=蚜虫（以E为食），B=瓢虫（以A为食），C=小鸟（以B为食），D=蛇（以C为食）
eats = {'A': ['E'], 'B': ['A'], 'C': ['B'], 'D': ['C'], 'E': []}
producers = [k for k, v in eats.items() if not v]
primary = [k for k, v in eats.items() if v and all(x in producers for x in v)]
print('反例中：生产者', producers, '初级消费者', primary, '能量流向 E→A→B→C→D')
assert 'A' not in producers          # A项“物种A是生产者”不必然
assert 'B' not in primary            # B项“物种B是初级消费者”不必然
energy_from_A_to_E = False           # C项：能量从生产者E流出，不是从A到E
# D项：地表生态系统的生产者靠光合作用固定太阳能，最终能量来源都是太阳能（与各物种数量无关）
print('A、B、C都有与图相容的反例；只有D与数量无关、必然成立。')
