"""M09 第69题：房屋北面夏天能被阳光照射、冬天南面能被照射，最可能在哪个城市？ 选项 A海口 B武汉 C上海 D北京
核验：计算夏至、冬至正午太阳的方位与高度（太阳赤纬δ=±23.44°），并顺带算夏至日出方位，
说明“北面被照射”应理解为正午前后太阳在北方天空（只在北回归线以南才会出现）。"""
from math import degrees, radians, sin, cos, acos
cities = {'海口': 20.03, '武汉': 30.59, '上海': 31.23, '北京': 39.90}
for name, phi in cities.items():
    out = []
    for season, dec in (('夏至', 23.44), ('冬至', -23.44)):
        h = 90 - abs(phi - dec)
        side = '北' if dec > phi else '南'
        out.append(f'{season}正午太阳在{side}方，高度{h:.1f}°')
    A_rise = degrees(acos(sin(radians(23.44)) / cos(radians(phi))))   # 自正北起算的日出方位
    print(f'{name}(北纬{phi}°)：', '；'.join(out), f'；夏至日出方位：北偏东{A_rise:.1f}°')
noon_north = [n for n, phi in cities.items() if 23.44 > phi]
print('夏季正午太阳可位于北方（纬度低于北回归线23.44°N）的城市：', noon_north)
assert noon_north == ['海口']
# 说明：四城夏至日出方位都在东偏北，清晨、傍晚太阳都在北半边天空，北墙都能短时受晒；
# 题目“最有可能”指正午前后北面受晒，只有北回归线以南的海口符合。
