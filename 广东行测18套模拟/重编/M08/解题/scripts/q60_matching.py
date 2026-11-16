"""Q60 (分析推理): years 2023-2026 <-> companies 甲乙丙丁 <-> businesses.
"乙、丙企业的引进时间间隔1年" is tested under both readings:
  'gap'      : one year lies between them (years differ by 2)  -- the intended reading
  'adjacent' : consecutive years (differ by 1)
"""
from itertools import permutations

years = [2023, 2024, 2025, 2026]
firms = ['甲', '乙', '丙', '丁']
biz = ['电子科技', '机械设备', '装饰材料', '生物制药']
opts = {
    'A 甲最早': lambda Y, B: Y['甲'] == min(Y.values()),
    'B 丁是2023年': lambda Y, B: Y['丁'] == 2023,
    'C 甲主营装饰材料': lambda Y, B: B['甲'] == '装饰材料',
    'D 2024年的企业主营机械设备': lambda Y, B: B[[f for f in firms if Y[f] == 2024][0]] == '机械设备',
}
for reading, diff in [('gap', 2), ('adjacent', 1)]:
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
            if abs(Y['乙'] - Y['丙']) != diff:
                continue
            sols.append((Y, B))
    print(f'reading "{reading}": {len(sols)} solutions')
    for Y, B in sols:
        print('   ', {f: (Y[f], B[f]) for f in firms})
    for k, f in opts.items():
        print('   ', k, '-> must be true' if sols and all(f(Y, B) for Y, B in sols) else '-> not necessarily')
