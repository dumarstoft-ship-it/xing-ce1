"""M11 第36题：三人平均80，甲乙平均75，乙丙平均80，求甲丙平均。 选项 A70 B75 C80 D85"""
total = 3 * 80
jia_yi, yi_bing = 2 * 75, 2 * 80
bing = total - jia_yi; jia = total - yi_bing; yi = total - jia - bing
print('甲', jia, '乙', yi, '丙', bing)
assert (jia + yi) / 2 == 75 and (yi + bing) / 2 == 80 and (jia + yi + bing) / 3 == 80
avg = (jia + bing) / 2
# 速算：三组两两之和相加=2×总分 → 甲+丙=480−150−160=170
assert 2 * total - jia_yi - yi_bing == jia + bing == 170
print('甲丙平均', avg)
assert avg == 85
# 易错核对：把三个平均数直接再平均或相减：(80+75+80)/3≈78.3、80×2−75=85? 见解析
