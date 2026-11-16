# 第51题（翻译推理）与第61题（推理形式）真值表核验
from itertools import product


def entails(premises, conclusion, n):
    """premises/conclusion: functions of a tuple of n booleans"""
    for v in product([False, True], repeat=n):
        if all(p(v) for p in premises) and not conclusion(v):
            return False
    return True


imp = lambda a, b: (not a) or b

# ---------- 第51题 ----------
# T=将人文底蕴转化为城市发展优势  M=满足美好生活需要  J=加快人民城市建设、推动高质量发展
# F=发挥四个作用
# "T是M的关键" -> M→T；"T是J的必由之路" -> J→T；"如果不F就不T" -> ¬F→¬T 即 T→F
T, M, J, F = range(4)
prem51 = [lambda v: imp(v[M], v[T]), lambda v: imp(v[J], v[T]), lambda v: imp(not v[F], not v[T])]
opts51 = {
    'A 只有J才M（M→J）': lambda v: imp(v[M], v[J]),
    'B F才能J（J→F）': lambda v: imp(v[J], v[F]),
    'C 如果F就T（F→T）': lambda v: imp(v[F], v[T]),
    'D 不J就不T（T→J）': lambda v: imp(not v[J], not v[T]),
}
print('第51题：')
for k, c in opts51.items():
    print('  ', k, '可推出' if entails(prem51, c, 4) else '推不出')

# ---------- 第61题 ----------
# 用"对任意个体"的命题形式检验各项推理是否有效：P(x)=前件，Q(x)=后件
# 题干：所有P都Q，a是Q，所以a是P（肯定后件）
P, Q = range(2)
forms = {
    '题干 所有P都Q, a是Q ⇒ a是P': ([lambda v: imp(v[P], v[Q]), lambda v: v[Q]], lambda v: v[P]),
    'A 只有在保质期内(Q)才能正常销售(P), 火腿肠P ⇒ Q': ([lambda v: imp(v[P], v[Q]), lambda v: v[P]], lambda v: v[Q]),
    'B 浇营养液(P)都延长花期(Q), 没延长 ⇒ 没浇': ([lambda v: imp(v[P], v[Q]), lambda v: not v[Q]], lambda v: not v[P]),
    'C 正宗蜂蜜(P)都有花香(Q), 槐花蜜Q ⇒ P': ([lambda v: imp(v[P], v[Q]), lambda v: v[Q]], lambda v: v[P]),
}
print('第61题（有效=True 表示推理正确；题干与C均为无效的“肯定后件”）：')
for k, (ps, c) in forms.items():
    print('  ', k, '有效' if entails(ps, c, 2) else '无效（肯定后件式错误）')
print('   D 项为“很多(有的)喜欢书法的老人心态平和”推出“书法家都心态平和”，错在由“有的”推“所有”，与题干错误类型不同')
