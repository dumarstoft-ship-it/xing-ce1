"""M11 第46题（GD2018-Q035）：2×2 方格中四段四分之一圆弧。

每段弧以所在小格的一个角为圆心、边长为半径；记圆心所在的角（TL/TR/BL/BR）。
顺时针旋转90°：圆心 TL→TR→BR→BL→TL。
"""
CW = {'TL': 'TR', 'TR': 'BR', 'BR': 'BL', 'BL': 'TL'}
# 各格（左上、右上、左下、右下）弧的圆心，按放大图读出
FIG = {
 1: {'左上': 'BL', '右上': 'BL', '左下': 'TR', '右下': 'TL'},
 2: {'左上': 'BL', '右上': 'TL', '左下': 'TR', '右下': 'TL'},
 3: {'左上': 'BL', '右上': 'TL', '左下': 'TR', '右下': 'TR'},
 4: {'左上': 'BL', '右上': 'TL', '左下': 'BR', '右下': 'TR'},
}
OPT = {
 'A': {'左上': 'BR', '右上': 'TL', '左下': 'BR', '右下': 'TR'},
 'B': {'左上': 'TL', '右上': 'TL', '左下': 'BR', '右下': 'TR'},
 'C': {'左上': 'TL', '右上': 'TL', '左下': 'TR', '右下': 'TR'},
 'D': {'左上': 'TR', '右上': 'TL', '左下': 'BR', '右下': 'TR'},
}
for k in (1, 2, 3):
    diff = [c for c in FIG[k] if FIG[k][c] != FIG[k + 1][c]]
    assert len(diff) == 1 and CW[FIG[k][diff[0]]] == FIG[k + 1][diff[0]], k
    print(f'图{k}→图{k+1}：只有{diff[0]}格变化，{FIG[k][diff[0]]}→{FIG[k+1][diff[0]]}（顺时针90°）')
pred = dict(FIG[4]); pred['左上'] = CW[pred['左上']]
print('依次为右上、右下、左下格，下一步应为左上格顺时针转90°，问号处：', pred)
for k, v in OPT.items():
    print(k, '符合' if v == pred else '不符合', [c for c in v if v[c] != pred[c]])
