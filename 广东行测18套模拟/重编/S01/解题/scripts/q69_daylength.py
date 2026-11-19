"""S01 第69题：2021年9月17日，酒泉（东风着陆场）一带的昼长。用低精度太阳位置公式算赤纬，再算昼长。
酒泉市约39.7°N，东风着陆场约41.6°N；2021年秋分在9月23日（北京时间），此前太阳直射北半球。
气候：酒泉地处河西走廊西端，温带大陆性干旱气候，年降水量不足百毫米（约80—90毫米）。"""
from math import sin, cos, asin, acos, radians, degrees
from datetime import datetime, timezone

def declination(dt):
    # 天文年历低精度太阳位置公式（误差约0.01°）
    jd = dt.timestamp() / 86400 + 2440587.5
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = radians((357.528 + 0.9856003 * n) % 360)
    lam = radians(L + 1.915 * sin(g) + 0.020 * sin(2 * g))
    eps = radians(23.439 - 0.0000004 * n)
    return degrees(asin(sin(eps) * sin(lam)))

def day_length(lat, dec, h0=-0.833):          # h0：日出日落时太阳中心高度（计大气折射与视半径）
    c = (sin(radians(h0)) - sin(radians(lat)) * sin(radians(dec))) / (cos(radians(lat)) * cos(radians(dec)))
    return 2 * degrees(acos(c)) / 15

landing = datetime(2021, 9, 17, 4, 0, tzinfo=timezone.utc)      # 北京时间12时前后
dec = declination(landing)
print('2021-09-17 太阳赤纬 %.2f°' % dec)
assert dec > 0
for lat in (39.7, 41.6):
    L1, L0 = day_length(lat, dec), day_length(lat, dec, h0=0.0)
    print('纬度%.1f°N：昼长约%.2f小时（不计折射%.2f小时）' % (lat, L1, L0))
    assert L0 > 12
for d in (datetime(2021, 9, 23, 4, tzinfo=timezone.utc), datetime(2021, 10, 1, 4, tzinfo=timezone.utc)):
    de = declination(d)
    print(d.date(), '赤纬%.2f°，酒泉昼长（不计折射）约%.2f小时' % (de, day_length(39.7, de, h0=0.0)))
print('9月17日太阳直射点在北半球，北半球昼长夜短 → 干旱少雨、昼长夜短，A。')
