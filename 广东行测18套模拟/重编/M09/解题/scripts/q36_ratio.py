"""M09 第36题：四月比三月多1/3，五月比四月多1/3，三月比五月少几分之几？ 选项 A1/6 B2/3 C7/9 D7/16
核验：特值三月=9，四月=12，五月=16；“三月比五月少”以五月为基准：(16−9)/16=7/16。"""
from fractions import Fraction as F
mar = F(9)
apr = mar * (1 + F(1, 3))
may = apr * (1 + F(1, 3))
print('三月、四月、五月 =', mar, apr, may)
ans = (may - mar) / may
print('三月比五月少（以五月为基准）=', ans)
opts = {'A': F(1, 6), 'B': F(2, 3), 'C': F(7, 9), 'D': F(7, 16)}
ok = [k for k, v in opts.items() if v == ans]
assert ok == ['D']
# 易错路径
wrong_base = (may - mar) / mar          # 以三月为基准 = “五月比三月多”
add_rates = F(1, 3) + F(1, 3)            # 把两个1/3直接相加
print('以三月为基准：', wrong_base, '→', [k for k, v in opts.items() if v == wrong_base])
print('两次增长直接相加：', add_rates, '→', [k for k, v in opts.items() if v == add_rates])
# 通用性：与三月取值无关
for m in (1, 3, 100, F(7, 2)):
    m = F(m); y = m * F(16, 9)
    assert (y - m) / y == F(7, 16)
print('答案 D = 7/16（与三月营业额取值无关）')
