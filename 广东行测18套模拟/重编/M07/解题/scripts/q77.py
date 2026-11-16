"""第77题：2023年下半年（7-12月）中，当月同比增速高于当月累计同比增速的月份数。
累计增速R_m是“前m-1月累计增速R_{m-1}”与“当月增速g_m”的加权平均（权重为各自基期量，均为正），
所以R_m必介于R_{m-1}与g_m之间：R_m > R_{m-1} ⇔ g_m > R_m；R_m < R_{m-1} ⇔ g_m < R_m。"""
from q76_80_group2_data import rev_g23
cnt = 0
for m in range(7, 13):
    prev, cur = rev_g23[m-1], rev_g23[m]
    up = cur > prev
    cnt += up
    print(f'1-{m-1}月 {prev:>4} -> 1-{m}月 {cur:>4}：{"上升，当月增速高于累计" if up else "下降，当月增速低于累计"}')
print('满足的月份数 =', cnt, '-> D')
# 取整影响：变化最小的为±0.2个百分点，大于两端各±0.05的取整误差，判断不受影响
print('最小变动幅度:', min(abs(rev_g23[m]-rev_g23[m-1]) for m in range(7, 13)))

# 数值演示：任取一组满足这些累计增速的基期月度值，验证结论（结论与基期取值无关）
import random
random.seed(1)
for trial in range(3):
    base = [random.uniform(800, 1500) for _ in range(12)]  # 2022年1-12月当月值（任意正数）
    cumb = [sum(base[:i+1]) for i in range(12)]
    cumc = {m: cumb[m-1]*(1+rev_g23[m]/100) for m in range(2, 13)}
    ok = 0
    for m in range(7, 13):
        g = (cumc[m]-cumc[m-1])/base[m-1]*100 - 100
        ok += g > rev_g23[m]
    print('随机基期验证，满足月份数 =', ok)
# 易错核对
print('只在1-7月至1-12月之间比较（漏掉7月与1-6月的比较）：', sum(rev_g23[m] > rev_g23[m-1] for m in range(8, 13)), '-> C')
print('规则用反（累计增速下降的月份）：', sum(rev_g23[m] < rev_g23[m-1] for m in range(7, 13)), '-> A')
