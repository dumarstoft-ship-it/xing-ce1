"""第3组（第81—85题）共用数据与自洽检查：2026年一季度广东经济运行（文字材料）。"""
gdp, gdp_g = 34950.34, 4.6
ind = {'第一产业': (941.66, 3.9), '第二产业': (12410.95, 4.7), '第三产业': (21597.72, 4.5)}
# 规上工业及分门类：一季度增速、比上年全年提高的百分点
ind_detail = {'规上工业': (5.4, 2.4), '采矿业': (18.8, 15.8), '制造业': (5.0, 1.8), '电力热力燃气水': (5.2, 4.9)}
fai_g, fai_ex_re_g = 0.2, 5.8
house_area_g, house_narrow = -15.6, 1.5
cpi, cpi_expand = 0.5, 0.7
ppi, ppi_narrow = -1.2, 0.3
ipi, ipi_narrow = -0.1, 2.7

if __name__ == '__main__':
    s = sum(v for v, g in ind.values())
    print(f'三次产业合计 {s:.2f} vs GDP {gdp}（差 {gdp-s:.2f}，取整误差）')
    bases = {k: v/(1+g/100) for k, (v, g) in ind.items()}
    print('上年同期：', {k: round(v, 2) for k, v in bases.items()}, '合计', round(sum(bases.values()), 2),
          '；GDP上年同期', round(gdp/(1+gdp_g/100), 2))
    print(f'由三次产业推出的GDP增速 = {100*(gdp/sum(bases.values())-1):.3f}%（材料4.6%，取整后一致；实际增速按不变价，只作粗核）')
    print('服务业增速4.5% 与 第三产业增速4.5% 一致')
    print('2025年全年增速（一季度增速-提高幅度）：', {k: round(a-b, 1) for k, (a, b) in ind_detail.items()})
    print(f'CPI 2025年全年 {cpi-cpi_expand:+.1f}%；PPI 2025年全年 {ppi-ppi_narrow:+.1f}%；IPI 2025年全年 {ipi-ipi_narrow:+.1f}%')
    print(f'新建商品房销售面积：本期 {house_area_g}%，降幅收窄1.5个百分点 -> 比较期为 {house_area_g-house_narrow}%（比较期未写明）')
