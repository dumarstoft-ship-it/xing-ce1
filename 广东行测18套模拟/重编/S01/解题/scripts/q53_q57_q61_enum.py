"""S01 第53、57、61题：枚举检验。"""
import itertools

# ---- 第53题：性别（2男1女）、项目、年龄（互不相同）全部枚举 ----
P = ['甲', '乙', '丙']
sols = []
for sex in set(itertools.permutations(['男', '男', '女'])):
    for sport in itertools.permutations(['羽毛球', '排球', '长跑']):
        for age in itertools.permutations([1, 2, 3]):   # 数字越大越年长
            s = dict(zip(P, sex)); sp = dict(zip(P, sport)); ag = dict(zip(P, age))
            who = {v: k for k, v in sp.items()}
            run, bad = who['长跑'], who['羽毛球']
            if s['甲'] == '女' or ag['甲'] == ag[run] or run == '甲': continue      # ①
            if not ag[bad] > ag['丙']: continue                                   # ②
            if not ag['乙'] < ag[run]: continue                                   # ③
            sols.append((s, sp, ag))
print('第53题 情形数', len(sols))
def avg(s, ag, g):
    xs = [ag[p] for p in P if s[p] == g]; return sum(xs) / len(xs)
checks = {
 'A 排球运动员最小': lambda s, sp, ag: ag[{v: k for k, v in sp.items()}['排球']] == 1,
 'B 甲不是羽毛球': lambda s, sp, ag: sp['甲'] != '羽毛球',
 'C 长跑运动员不是女性': lambda s, sp, ag: s[{v: k for k, v in sp.items()}['长跑']] != '女',
 'D 男性平均年龄大于女性': lambda s, sp, ag: avg(s, ag, '男') > avg(s, ag, '女'),
}
for k, f in checks.items():
    print(f'  {k}: {sum(f(*x) for x in sols)}/{len(sols)}')

# ---- 第57题：U 建立统一规划，S 各方面都有系统性，R 有序推进城市更新，G 经济增速超出预期，E 推动经济发展 ----
imp = lambda a, b: (not a) or b
res = {k: True for k in 'ABCD'}
for U, S, R, G, E in itertools.product([0, 1], repeat=5):
    if not (imp(not U, not S) and imp(U, R) and imp(G, U)):
        continue
    res['A'] &= imp(not U, not E)          # 缺乏统一规划 → 无法推动经济发展
    res['B'] &= imp(U, S)                  # 建立统一规划 → 各方面有系统性
    res['C'] &= imp(not G, not U)          # 除非增速超预期，否则没建立统一规划
    res['D'] &= imp(not R, not G)          # 城市更新未有序推进 → 增速不可能超预期
print('第57题 各项是否必然为真', res)

# ---- 第61题：2位七年级＋1位八年级，科目互不相同 ----
grade = {'甲': 7, '乙': 7, '丙': 7, '丁': 8, '戊': 8, '己': 8}
subj = {'甲': '语文', '乙': '数学', '丙': '英语', '丁': '数学', '戊': '历史', '己': '语文'}
for k, g in {'A': '甲己戊', 'B': '甲乙己', 'C': '乙丙戊', 'D': '乙丙丁'}.items():
    ok = [grade[x] for x in g].count(7) == 2 and len({subj[x] for x in g}) == 3
    print('第61题', k, g, '符合' if ok else '不符合')
