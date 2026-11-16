# 第41题：9页中3页有错别字，且这3页中恰有2页页码连续；求第3、6、9页都没有错别字的概率
from itertools import combinations
from fractions import Fraction as F

def n_adjacent_pairs(s):
    s = sorted(s)
    return sum(1 for i in range(len(s)) for j in range(i + 1, len(s)) if s[j] - s[i] == 1)

def exactly_two_consecutive(s):
    # 恰有2页连续：恰好一对相邻，第三页与这两页都不相邻（排除三页连续）
    return n_adjacent_pairs(s) == 1

allc = list(combinations(range(1, 10), 3))
S = [s for s in allc if exactly_two_consecutive(s)]
good = [s for s in S if all(p % 3 != 0 for p in s)]
print('C(9,3) =', len(allc), '；恰有2页连续的组合数 =', len(S))
print('其中不含3、6、9的组合：', good, '共', len(good))
print('概率 =', F(len(good), len(S)))
# 对照：若理解为“至少2页连续”（含三页连续）
S2 = [s for s in allc if n_adjacent_pairs(s) >= 1]
good2 = [s for s in S2 if all(p % 3 != 0 for p in s)]
print('对照（至少2页连续）：', len(good2), '/', len(S2), '=', F(len(good2), len(S2)))
# 对照：不加连续条件
good3 = [s for s in allc if all(p % 3 != 0 for p in s)]
print('对照（无连续条件）：', len(good3), '/', len(allc), '=', F(len(good3), len(allc)))
