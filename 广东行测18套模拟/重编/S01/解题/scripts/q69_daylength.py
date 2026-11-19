"""S01 第69题：2021年9月17日，酒泉（东风着陆场）一带的昼长。用太阳赤纬算昼长。
酒泉市约39.7°N，东风着陆场约41.6°N；秋分在9月23日，此前太阳直射北半球。
气候：酒泉地处河西走廊西端，温带大陆性干旱气候，年降水量不足百毫米（约80—90毫米）。"""
from math import sin, cos, tan, acos, asin, radians, degrees, pi
from datetime import date
def declination(d):
    n = d.timetuple().tm_yday
    g = 2 * pi / 365 * (n - 1)
    return degrees(0.006918 - 0.399912 * cos(g) + 0.070257 * sin(g) - 0.006758 * cos(2 * g)
                   + 0.000907 * sin(2 * g) - 0.002697 * cos(3 * g) + 0.00148 * sin(3 * g))
dec = declination(date(2021, 9, 17))
for lat in (39.7, 41.6):
    H = degrees(acos(-tan(radians(lat)) * tan(radians(dec))))
    print('赤纬%.2f°，纬度%.1f°N：昼长约%.2f小时' % (dec, lat, 2 * H / 15))
    assert 2 * H / 15 > 12
print('太阳直射点在北半球（赤纬>0），北半球昼长夜短 → 干旱少雨、昼长夜短，A。')
