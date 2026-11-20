# -*- coding: utf-8 -*-
"""S02 第76—80题（GD2014-XZ-M1，社区卫生服务中心与乡镇卫生院，纯文字材料）核算与本组自洽检查。
文字与原卷第9页文字层一致；第79题题干原卷作“卫生技术人数数量之和”（应为“人员数量”）。"""

comm = dict(n=7861, staff=328676, tech=276252, nat_share=0.045, city_share=0.088)
town = dict(n=37295, staff=1165996, tech=981227, nat_share=0.158, rural_share=0.321)
city_per_k, rural_per_k = 7.97, 3.18

print('== 本组自洽检查 ==')
n1, n2 = comm['tech'] / comm['nat_share'], town['tech'] / town['nat_share']
print('由4.5%%、15.8%%反推全国卫生技术人员 %.0f、%.0f（相差%.1f%%，4.5%%是四舍五入：276252/620万≈%.2f%%）'
      % (n1, n2, (n2 / n1 - 1) * 100, comm['tech'] / 6.2e6 * 100))
city, rural = comm['tech'] / comm['city_share'], town['tech'] / town['rural_share']
print('城市卫生技术人员 %.0f + 农村 %.0f = %.0f，与上面约620万吻合' % (city, rural, city + rural))
print('城市人口 %.2f 亿、农村人口 %.2f 亿，合计 %.2f 亿（合理）' % (city / city_per_k / 1e5, rural / rural_per_k / 1e5, (city / city_per_k + rural / rural_per_k) / 1e5))
print('未发现矛盾。')

print('\n== 第76题 ==')
print('社区卫生服务中心 %d 家 < 乡镇卫生院 %d 家 -> B' % (comm['n'], town['n']))
print('\n== 第77题 ==')
print('1165996/328676 = %.3f -> C 3.5' % (town['staff'] / comm['staff']))
print('\n== 第78题 ==')
print('328676−276252 = %d -> B' % (comm['staff'] - comm['tech']))
print('\n== 第79题 ==')
print('4.5%%+15.8%% = %.1f%% -> D；按620万总数核算 %.2f%%' % ((comm['nat_share'] + town['nat_share']) * 100, (comm['tech'] + town['tech']) / 6.2e6 * 100))
print('\n== 第80题 ==')
print('7.97−3.18 = %.2f，城市多 -> A' % (city_per_k - rural_per_k))
