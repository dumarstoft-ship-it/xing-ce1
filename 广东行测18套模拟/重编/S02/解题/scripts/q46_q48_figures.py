"""S02 第46、47、48题图形核验（格子与线段由放大图读出）。"""
# ---- 第46题：按列看，黑块要么在该列最下面，要么正好在中间（上下白块一样多） ----
# 每列从上到下记 'W'/'B'（只记该列实有的格子）
F46 = {
 '图1': ['WB', 'WWWB', 'WBW'],
 '图2': ['WB', 'WBW'],
 '图3': ['WWWB', 'WB', 'WWWB', 'WB', 'WWBWW'],
 '图4': ['WWWB', 'WWBWW', 'WBW'],
 '图5': ['WWWB', 'WB', 'WWWB'],
 'A': ['WBWWW', 'WBW'],
 'B': ['WBW', 'WWWB', 'WBW'],
 'C': ['BW', 'BW', 'WBW', 'BW'],
 'D': ['BW', 'BWW'],
}
def col_ok(c):
    if c.count('B') != 1: return False
    i = c.index('B'); above, below = i, len(c) - 1 - i
    return below == 0 or above == below
for k, cols in F46.items():
    res = [col_ok(c) for c in cols]
    print('第46题', k, '符合' if all(res) else '不符合', ['底' if c.endswith('B') else ('中' if col_ok(c) else '×') for c in cols])

# ---- 第47题：笔画（奇点数），度数按图读出 ----
def strokes(name, degs, comps=1):
    odd = sum(d % 2 for d in degs)
    print('第47题', name, f'奇点{odd}', '一笔画' if comps == 1 and odd in (0, 2) else '不能一笔画')
strokes('图1 椭圆+三角(顶点相切)+曲线', [4, 3, 1, 2, 2])
strokes('图2 长方形+五角星+竖线', [5, 1, 4] + [2] * 14)
strokes('图3 圆+弯带+菱形', [4, 4, 4, 4, 4] + [2] * 6)
strokes('图4 两竖线+两个V', [1, 1, 4, 2, 2, 2, 2, 2])
strokes('A 圆角长方形+两小方块+同心圆', [3, 3, 3, 3] + [2] * 8, comps=3)
strokes('B 外框+内长方形', [2] * 8, comps=2)
strokes('C 方形+圆+扇形', [5, 5, 4, 2, 2])
strokes('D 外形+三角+圆内十字', [3, 3] + [2] * 6, comps=6)

# ---- 第48题：同位置叠加，相同→白，不同→灰 ----
def overlay(a, b):
    return ['白' if x == y else '灰' for x, y in zip(a, b)]
g1 = (['白', '灰', '条', '白'], ['条', '灰', '灰', '白'], ['灰', '白', '灰', '白'])   # 圆：左上、右上、左下、右下
assert overlay(g1[0], g1[1]) == g1[2]
pos = ['上', '右上', '右下', '下', '左下', '左上']
f4 = ['白', '白', '白', '灰', '白', '条']; f5 = ['灰', '条', '白', '灰', '白', '条']
pred = overlay(f4, f5)
print('第48题 第一组验证通过；问号处灰格：', [p for p, c in zip(pos, pred) if c == '灰'])
opts = {'A': ['上', '下'], 'B': ['上', '下'], 'C': ['上', '右上'], 'D': ['上', '右上']}
extra = {'B': '另有右上条纹', 'C': '另有左上条纹'}
for k, v in opts.items():
    ok = set(v) == {p for p, c in zip(pos, pred) if c == '灰'} and k not in extra
    print('   ', k, '灰格', v, extra.get(k, ''), '→ 符合' if ok else '→ 不符合')
