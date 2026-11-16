# Extra Q89 (rewrite) and Q90 calculations
# ---- Q89: 2024H1 internet business revenue by region; national 8676 亿元, growth 5.6%
nat_rev, nat_g = 8676.0, 5.6
cen_rev, cen_g = 408.8, nat_g + 6.4
wes_rev, wes_g = 525.4, 4.6
ne_rev,  ne_g  = 20.8, -2.1
eas_g = nat_g - 0.4
eas_rev = nat_rev - cen_rev - wes_rev - ne_rev      # four regions sum to the national total
inc = lambda r,g: r*g/(100+g)
rows=[('东部',eas_rev,eas_g),('中部',cen_rev,cen_g),('西部',wes_rev,wes_g),('东北',ne_rev,ne_g)]
print('Q89 East revenue (residual) = %.1f'%eas_rev)
for n,r,g in rows: print('  %s rev %.1f growth %.1f%% increment %.2f'%(n,r,g,inc(r,g)))
order=[n for n,r,g in sorted(rows,key=lambda x:-inc(x[1],x[2]))]
print('  order:', '、'.join(order))
# consistency: national increment vs sum of regional increments
print('  national increment %.2f, sum of regions %.2f'%(inc(nat_rev,nat_g), sum(inc(r,g) for n,r,g in rows)))
# robustness: even if East revenue were only, say, half of the residual it stays first
print('  East increment if revenue were 1000 only: %.1f'%inc(1000,eas_g))

# ---- Q90
rev={2020:2096.76,2021:2255.38,2022:1930.58,2023:2268.60}
g={2018:15.36,2019:18.03,2020:32.61,2021:7.57,2022:-14.40,2023:17.51}
share={2018:62.47,2019:68.48,2020:75.24,2021:76.06,2022:72.61,2023:74.88}
avg=(rev[2021]+rev[2022]+rev[2023])/3
print('\nQ90 A: avg 2021-23 = %.2f, minus 2020 = %.2f  (<75 ?) %s'%(avg,avg-rev[2020],avg-rev[2020]<75 and avg>rev[2020]))
print('Q90 B: 图2 is revenue share, not quantity/sales volume -> cannot conclude')
yrs=[y for y in range(2019,2024) if (100-share[y])<(100-share[y-1])]
print('Q90 C: years non-mobile share below previous year:',yrs,'count',len(yrs))
dd=(rev[2023]-rev[2020])/3
print('Q90 D: base 2020, avg annual increase 2020->2023 = %.2f (>60 ?) %s'%(dd,dd>60))
# what D would give with other (wrong) bases, to show why the base year matters
r2019=rev[2020]/(1+g[2020]/100)
print('   (if base were 2019: rev2019=%.2f, avg incr over 4 yrs=%.2f)'%(r2019,(rev[2023]-r2019)/4))
# consistency check of table growth rates
for y in (2021,2022,2023): print('   check growth %d: %.2f%% vs table %.2f%%'%(y,(rev[y]/rev[y-1]-1)*100,g[y]))
