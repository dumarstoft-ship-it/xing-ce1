"""第90题：选出正确的说法。"""
from q86_90_group4_data import rev, mob_share
avg = (rev[2021] + rev[2022] + rev[2023]) / 3
print(f'A：2021-2023年年均 = ({rev[2021]}+{rev[2022]}+{rev[2023]})/3 = {avg:.2f}；较2020年高 {avg-rev[2020]:.2f} < 75 -> 正确')
print(f'   等价算法：三年各自与2020年之差 {rev[2021]-rev[2020]:.2f}、{rev[2022]-rev[2020]:.2f}、{rev[2023]-rev[2020]:.2f}，'
      f'平均 {((rev[2021]-rev[2020])+(rev[2022]-rev[2020])+(rev[2023]-rev[2020]))/3:.2f}')
print('B：图2是“收入占比”，选项说“游戏数量占实际销量的比重”，口径不符 -> 无法推出')
ups = [y for y in range(2019, 2024) if mob_share[y] > mob_share[y-1]]
downs = [y for y in range(2019, 2024) if mob_share[y] < mob_share[y-1]]
print(f'C：非移动占比 = 1-移动占比；非移动占比低于上年 ⇔ 移动占比高于上年：{ups}，共{len(ups)}个，不是1个 -> 错误')
print(f'   易错：数成移动占比下降的年份 {downs}，恰为1个')
inc3 = (rev[2023] - rev[2020]) / 3
print(f'D：2020-2023年年均增长量 = (2268.60-2096.76)/3 = {inc3:.2f} < 60 -> 错误')
r2019 = rev[2020] / 1.3261
print(f'   （若把2020年当年的增长也算进去，以2019年为基期：({rev[2023]}-{r2019:.2f})/4 = {(rev[2023]-r2019)/4:.2f}，'
      f'与常规口径不同，见issues）')
