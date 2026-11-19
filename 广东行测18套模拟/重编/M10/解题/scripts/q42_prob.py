"""M10 第42题：10球（黑3白2红1黄2绿1紫1），不放回依次取3个，依次为黑、红、白的概率。
选项 A1/120 B1/240 C1/250 D3/500（原卷选项为公式图，已核对）"""
from fractions import Fraction as F
from itertools import permutations
balls = ['黑'] * 3 + ['白'] * 2 + ['红'] + ['黄'] * 2 + ['绿', '紫']
draws = list(permutations(range(10), 3))
fav = sum(1 for d in draws if [balls[i] for i in d] == ['黑', '红', '白'])
p = F(fav, len(draws))
print('有序取法', len(draws), '符合', fav, '概率', p)
assert p == F(1, 120) == F(3, 10) * F(1, 9) * F(2, 8)
# 若误按放回计算：3/10×1/10×2/10=3/500（D）
print('放回时', F(3, 10) * F(1, 10) * F(2, 10))
