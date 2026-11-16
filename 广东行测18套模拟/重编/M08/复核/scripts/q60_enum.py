"""第60题 分析推理：甲乙丙丁四家企业与2023-2026四年、四种业务全排列枚举。
条件(4)“乙、丙引进时间间隔1年”有两种读法：相差1年（相邻）/中间隔一年（相差2年），两种都算。"""
from itertools import permutations
firms = ['甲', '乙', '丙', '丁']
years = [2023, 2024, 2025, 2026]
biz = ['电子科技', '机械设备', '装饰材料', '生物制药']
def solve(gap):
    sols = []
    for yp in permutations(years):
        Y = dict(zip(firms, yp))
        for bp in permutations(biz):
            B = dict(zip(firms, bp))
            byyear = {Y[f]: B[f] for f in firms}
            if byyear[2025] != '生物制药' or byyear[2026] != '装饰材料':
                continue
            if B['丁'] not in ('电子科技', '机械设备'):
                continue
            if Y['甲'] == 2025 or Y['乙'] == 2025:
                continue
            if abs(Y['乙'] - Y['丙']) != gap:
                continue
            sols.append((Y, B, byyear))
    return sols
opts = {
 'A 甲最早': lambda Y, B, by: Y['甲'] == 2023,
 'B 丁是2023': lambda Y, B, by: Y['丁'] == 2023,
 'C 甲是装饰材料': lambda Y, B, by: B['甲'] == '装饰材料',
 'D 2024是机械设备': lambda Y, B, by: by[2024] == '机械设备',
}
for gap, name in [(1, '相差1年(相邻)'), (2, '中间隔一年(相差2年)')]:
    sols = solve(gap)
    print(f'== 读法：{name}，解的个数 {len(sols)}')
    for Y, B, by in sols:
        print('  ', {f: (Y[f], B[f]) for f in firms})
    for k, f in opts.items():
        vals = [f(*s) for s in sols]
        print('  ', k, '必然成立' if all(vals) else ('必然不成立' if not any(vals) else '可能'))
