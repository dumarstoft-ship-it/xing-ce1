"""第83题：2026年一季度三次产业增加值同比增长量排序。增长量 = 现期 × r/(1+r)。"""
from q81_85_group3_data import ind
inc = {k: v*g/100/(1+g/100) for k, (v, g) in ind.items()}
for k, x in inc.items():
    print(f'{k}：{ind[k][0]} × {ind[k][1]}%/(1+{ind[k][1]}%) = {x:.2f}')
order = sorted(inc, key=inc.get)
print('由小到大：', '、'.join(order), '-> B')
# 估算：第三产业现期约为第二产业的1.74倍，增速4.5%与4.7%之比约0.96，增长量约为1.67倍
print(f'三产/二产：现期比 {21597.72/12410.95:.3f}，增长量比 {inc["第三产业"]/inc["第二产业"]:.3f}')
print('易错：按增速排序 3.9% < 4.5% < 4.7% -> 第一、第三、第二 = A')
