"""第82题：选出不正确的说法。A、D为材料原句；B需计算；C由“降幅收窄”反推。"""
from q81_85_group3_data import gdp, ind, house_area_g, house_narrow
share1 = ind['第一产业'][0] / gdp
print(f'B：941.66/34950.34 = {100*share1:.3f}% < 3% -> 正确（估算：34950×3%≈1049 > 941.66）')
prev = house_area_g - house_narrow
print(f'C：本期 {house_area_g}%，降幅收窄1.5个百分点 -> 比较期降幅 {-prev:.1f}%，不是14.1% -> 不正确')
print(f'   易错：15.6-1.5 = {15.6-1.5:.1f}（把“收窄”算反） -> 正好是C中的14.1%')
