# 第36题：甲10天、乙15天、丙20天；甲乙丙合作2天，甲丙合作2天，余下乙单独做。乙共做几天？
from fractions import Fraction as F
a, b, c = F(1, 10), F(1, 15), F(1, 20)
done = (a + b + c) * 2 + (a + c) * 2
rest = 1 - done
b_alone = rest / b
total_b = 2 + b_alone
print("赋总量60：效率 甲%s 乙%s 丙%s" % (a * 60, b * 60, c * 60))
print("前4天完成", done * 60, "剩余", rest * 60, "乙单独", b_alone, "天；乙共", total_b, "天")
assert total_b == 6
print("答案: B（A=4 只算了乙单独做的天数）")
