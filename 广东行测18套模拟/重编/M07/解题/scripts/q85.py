"""第85题：选出正确的说法。"""
from q81_85_group3_data import ind_detail, fai_g, fai_ex_re_g, ppi, ppi_narrow, ipi, ipi_narrow
y25 = {k: round(a-b, 1) for k, (a, b) in ind_detail.items()}
print('2025年全年增速：', y25)
d = y25['制造业'] - y25['电力热力燃气水']
print(f'A：2025年 制造业 {y25["制造业"]}% 与 电力等 {y25["电力热力燃气水"]}% 相差 {d:.1f} 个百分点，不是0.2 -> 错误；'
      f'易错：拿一季度 5.2-5.0 = {5.2-5.0:.1f}')
print(f'B：2025年 采矿业增速 {y25["采矿业"]}% = 规上工业增速 {y25["规上工业"]}% -> 比重 ×(1+3.0%)/(1+3.0%) 不变，与上年持平 -> 正确')
print(f'C：全部投资增速 {fai_g}% 是“房地产开发投资”与“其余投资({fai_ex_re_g}%)”的加权平均，'
      f'其余部分高于{fai_g}%，房地产开发投资增速必低于{fai_g}%（实为负） -> 错误')
# 数值示意：设房地产占比 w，r_re = (0.2 - (1-w)*5.8)/w
for w in (0.2, 0.3, 0.4):
    print(f'   若房地产开发投资占上年投资的{int(w*100)}%，其增速 = {(fai_g-(1-w)*fai_ex_re_g)/w:.1f}%')
print(f'D：材料只给“比上年全年”：2025年全年 PPI {ppi-ppi_narrow:+.1f}%，IPI {ipi-ipi_narrow:+.1f}%；'
      f'选项问的是2025年一季度，材料无数据 -> 无法推出')
