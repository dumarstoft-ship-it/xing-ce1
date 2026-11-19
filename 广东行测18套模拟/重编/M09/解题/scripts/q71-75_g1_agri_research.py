# -*- coding: utf-8 -*-
"""M09 第71—75题（G省农业科研和科技开发机构）核算、易错路径与本组自洽检查。
数据按原卷裁图逐格核对，与转写一致。"""

years = [2015, 2016, 2017, 2018, 2019]
inst = [76, 76, 76, 73, 68]            # 机构数（个）
staff = [4983, 4781, 4760, 4289, 4633]  # 职工人数（人）
sci = [3502, 3611, 3651, 3432, 3995]    # 从事科技活动人员（人）
topics = [1688, 1813, 1918, 1631, 2286]  # 科技活动课题数（个）
fund = [50350, 56237, 56224, 42623, 68810]  # 课题投入经费（万元）
papers = [1519, 1680, 1891, 1383, 1862]  # 科学论文合计（篇）
foreign = [339, 365, 393, 308, 605]      # 其中：国外发表（篇）
books = [41, 49, 44, 43, 32]             # 科技论著合计（种）
senior, middle = 1254, 1148              # 文字：2019年高级、中级职称人数
demo_base, demo_street, demo_comm = 554, 145, 1341  # 文字：科普示范基地、街道（乡镇）、社区（村）


def nearest(x, opts):
    return min(opts, key=lambda k: abs(opts[k] - x))


print('== 自洽检查 ==')
print('文字2019年机构68个、职工4633人，与表格2019年列一致：', inst[-1] == 68 and staff[-1] == 4633)
print('高级＋中级＝%d ≤ 职工4633：%s' % (senior + middle, senior + middle <= staff[-1]))
print('各年 从事科技活动人员 ≤ 职工：', all(s <= t for s, t in zip(sci, staff)))
print('各年 国外发表 ≤ 论文合计：', all(f <= p for f, p in zip(foreign, papers)))

print('\n== 第71题 ==')
o71 = {'A': 18.5, 'B': 20.5, 'C': 22.5, 'D': 24.5}
v = senior / inst[-1]
print('1254÷68＝%.3f → %s' % (v, nearest(v, o71)))
print('误用中级职称1148÷68＝%.2f（不在选项中）；职工4633÷68＝%.1f' % (middle / 68, staff[-1] / 68))

print('\n== 第72题 ==')
o72 = {'A': 60, 'B': 70, 'C': 80, 'D': 90}
v = sci[3] / staff[3] * 100
print('2018年 3432÷4289＝%.2f%% → %s；4289×80%%＝%.1f' % (v, nearest(v, o72), staff[3] * 0.8))
w = sci[4] / staff[4] * 100
print('误用2019年 3995÷4633＝%.2f%% → %s（易错）' % (w, nearest(w, o72)))

print('\n== 第73题 ==')
o73 = {'A': 3152, 'B': 4615, 'C': 5517, 'D': 7890}
d = fund[-1] - fund[0]
print('(68810−50350)÷4＝%d÷4＝%.1f → %s' % (d, d / 4, nearest(d / 4, o73)))
print('误除以5：%.1f（不在选项中）' % (d / 5))

print('\n== 第74题 ==')
print('科学论文合计最多：%d年（%d篇）' % (years[papers.index(max(papers))], max(papers)))
print('误看“国外发表”一行最多：%d年（%d篇）→ D' % (years[foreign.index(max(foreign))], max(foreign)))

print('\n== 第75题 ==')
print('A 1341÷145＝%.2f，145×10＝%d＞1341 → 不到十倍，错' % (demo_comm / demo_street, demo_street * 10))
print('B 课题数', topics, '2018年下降：', topics[3] < topics[2], '→ 错')
print('C 605−339＝%d → 对' % (foreign[-1] - foreign[0]))
print('D 论著', books, '2019年32＜40 → 错；只看2015—2018年均＞40：', all(b > 40 for b in books[:4]))
