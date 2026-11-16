# -*- coding: utf-8 -*-
"""第71—75题（资料第1组，S市保险保费）核算脚本。数据从输入 data.json 读取。"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', '..', '输入', 'data.json'), encoding='utf-8'))
m1 = [m for m in d['materials'] if m['id'].endswith('-m1')][0]
tab = [b for b in m1['blocks'] if b['type'] == 'table'][0]
life = {int(r[0].rstrip('月')): float(r[1]) for r in tab['rows']}   # 2023年各月寿险保费收入（亿元）

TOTAL_DEC = 139.56      # 2023年12月保险保费收入（亿元）
G_DEC = 9.66            # 同比增速 %
SH_PROP, SH_HEALTH = 29.16, 22.71   # 财产险、健康险占比 %
PER_CAPITA, PER_CAPITA_UP = 790.18, 95.06   # 12月人均保费（元）、比上月多

print('寿险各月:', life)


def nearest(val, opts):
    return min(opts.items(), key=lambda kv: abs(kv[1] - val))


# ---------------- 数据自洽检查 ----------------
print('\n[自洽检查]')
sh_life = life[12] / TOTAL_DEC * 100
sh_acc = 100 - sh_life - SH_PROP - SH_HEALTH
print(f'12月寿险占比={sh_life:.3f}%  意外险占比={sh_acc:.3f}%  （寿险最高、意外险最低：'
      f'{sh_life > SH_PROP > SH_HEALTH > sh_acc}）')
print(f'寿险+财产+健康={sh_life + SH_PROP + SH_HEALTH:.3f}% (<100% 才能有意外险)')
pop = TOTAL_DEC * 1e8 / PER_CAPITA
print(f'由人均反推人数={pop / 1e4:.1f}万人；11月人均={PER_CAPITA - PER_CAPITA_UP:.2f}元；'
      f'若人数不变，11月保费≈{(PER_CAPITA - PER_CAPITA_UP) * pop / 1e8:.2f}亿元，'
      f'其中寿险53亿元占{53 / ((PER_CAPITA - PER_CAPITA_UP) * pop / 1e8) * 100:.1f}%')
print('全年寿险合计=', sum(life.values()))

# ---------------- 第71题 ----------------
print('\n[71] 2022年12月同比增速')
opts71 = {'A': 14.2, 'B': 13.1, 'C': 12.5, 'D': 11.3}
r = (1 + 0.22) / (1 + G_DEC / 100) - 1
print(f'正确：1.22/1.0966-1 = {r * 100:.4f}% → {nearest(r * 100, opts71)}')
wrong = {
    '增速直接相减 22%-9.66%': 22 - G_DEC,
    '22%-9.66%-22%×9.66%': 22 - G_DEC - 22 * G_DEC / 100,
    '(22-9.66)×1.0966': (22 - G_DEC) * 1.0966,
    '(22-9.66)/(1-9.66%)': (22 - G_DEC) / (1 - G_DEC / 100),
    '2022=139.56×(1-9.66%)，2021=139.56/1.22': (TOTAL_DEC * (1 - G_DEC / 100)) / (TOTAL_DEC / 1.22) * 100 - 100,
    '2022=139.56/1.0966，2021=139.56×(1-22%)': (TOTAL_DEC / 1.0966) / (TOTAL_DEC * 0.78) * 100 - 100,
    '两者都用乘(1-r)': (TOTAL_DEC * (1 - G_DEC / 100)) / (TOTAL_DEC * 0.78) * 100 - 100,
    '1.22×(1-9.66%)-1': (1.22 * (1 - G_DEC / 100) - 1) * 100,
}
for k, v in wrong.items():
    print(f'  错误思路 {k}: {v:.3f}% → 最近选项 {nearest(v, opts71)}')

# ---------------- 第72题 ----------------
print('\n[72] 寿险比重比意外险高几个百分点')
opts72 = {'A': 38.8, 'B': 40.7, 'C': 43.6, 'D': 45.1}
diff = sh_life - sh_acc
print(f'正确：寿险{sh_life:.4f}% - 意外险{sh_acc:.4f}% = {diff:.4f} → {nearest(diff, opts72)}')
print(f'  简算：2×{sh_life:.3f} - (100-29.16-22.71) = {2 * sh_life - (100 - SH_PROP - SH_HEALTH):.4f}')
wrong = {
    '只算寿险占比': sh_life,
    '寿险占比-意外险当成(财产-健康)': sh_life - (SH_PROP - SH_HEALTH),
    '用11月寿险53算': 53 / TOTAL_DEC * 100 * 2 - (100 - SH_PROP - SH_HEALTH),
    '用全年月均寿险': (sum(life.values()) / 12) / TOTAL_DEC * 200 - (100 - SH_PROP - SH_HEALTH),
    '寿险当成100-29.16-22.71(忽略意外险)再减意外险0': 100 - SH_PROP - SH_HEALTH,
    '寿险占比-健康险': sh_life - SH_HEALTH,
    '寿险占比-财产险': sh_life - SH_PROP,
    '寿险=64/(139.56×1.0966)': life[12] / (TOTAL_DEC * 1.0966) * 200 - (100 - SH_PROP - SH_HEALTH),
    '寿险=64/(139.56/1.0966)': life[12] / (TOTAL_DEC / 1.0966) * 200 - (100 - SH_PROP - SH_HEALTH),
}
for k, v in wrong.items():
    print(f'  {k}: {v:.3f} → 最近 {nearest(v, opts72)}')

# ---------------- 第73题 ----------------
print('\n[73] 下半年环比增长量最高月份的环比增长率')
opts73 = {'A': 43, 'B': 48, 'C': 36, 'D': 31}
for mth in range(2, 13):
    inc = life[mth] - life[mth - 1]
    print(f'  {mth:>2}月: 环比增长量={inc:+.0f}  环比增速={inc / life[mth - 1] * 100:+.2f}%  (增量/现期={inc / life[mth] * 100:+.2f}%)')
h2 = {m: life[m] - life[m - 1] for m in range(7, 13)}
best = max(h2, key=h2.get)
rate = h2[best] / life[best - 1] * 100
print(f'下半年环比增长量最高：{best}月 +{h2[best]:.0f}，增速 {rate:.3f}% → {nearest(rate, opts73)}')
allm = {m: life[m] - life[m - 1] for m in range(2, 13)}
bm = max(allm, key=allm.get)
print(f'  全年环比增量最高：{bm}月 +{allm[bm]:.0f}，增速 {allm[bm] / life[bm - 1] * 100:.3f}% → {nearest(allm[bm] / life[bm - 1] * 100, opts73)}')
print(f'  11月增量÷11月现期 = {h2[best] / life[best] * 100:.3f}% → {nearest(h2[best] / life[best] * 100, opts73)}')
best_rate = max(range(7, 13), key=lambda m: (life[m] - life[m - 1]) / life[m - 1])
print(f'  下半年环比增速最高的月份 = {best_rate}月')

# ---------------- 第74题 ----------------
print('\n[74] 上半年月均比下半年月均高多少亿元')
opts74 = {'A': 45.2, 'B': 34.3, 'C': 22.5, 'D': 13.3}
H1 = sum(life[m] for m in range(1, 7))
H2 = sum(life[m] for m in range(7, 13))
v = H1 / 6 - H2 / 6
print(f'上半年合计={H1:.0f} 月均={H1 / 6:.4f}；下半年合计={H2:.0f} 月均={H2 / 6:.4f}；差={v:.4f} → {nearest(v, opts74)}')
wrong = {
    '差额/12': (H1 - H2) / 12,
    '上半年去掉1月(5个月)': (H1 - life[1]) / 5 - H2 / 6,
    '上半年月均-全年月均': H1 / 6 - sum(life.values()) / 12,
    '全年月均-下半年月均': sum(life.values()) / 12 - H2 / 6,
    'Q1月均-Q2月均': (life[1] + life[2] + life[3]) / 3 - (life[4] + life[5] + life[6]) / 3,
    '1月-6月平均差/...': (life[1] - life[12]) / 6,
    '上半年月均-12月': H1 / 6 - life[12],
    '6月-下半年月均': life[6] - H2 / 6,
    '中位数之差': sorted([life[m] for m in range(1, 7)])[2] - sorted([life[m] for m in range(7, 13)])[2],
}
for k, val in wrong.items():
    print(f'  {k}: {val:.3f} → 最近 {nearest(val, opts74)}')

# ---------------- 第75题 ----------------
print('\n[75] 逐项')
print(f'A: 12月人数=139.56亿÷790.18元={pop / 1e4:.2f}万人（>1700万，且“人均”是按人口不是按参保人数）')
q2 = life[4] + life[5] + life[6]
print(f'B: 第二季度寿险=63+62+92={q2:.0f}亿元（≠227）；Q1={life[1] + life[2] + life[3]:.0f}, Q3={life[7] + life[8] + life[9]:.0f}, Q4={life[10] + life[11] + life[12]:.0f}')
print('C: 材料没有2022年各月寿险数据，同比增长量无法计算（环比增长量最高的才是6月）')
base22 = TOTAL_DEC / (1 + G_DEC / 100)
print(f'D: 2022年12月=139.56/1.0966={base22:.3f}亿元 > 123 → 正确；若误用139.56×(1-9.66%)={TOTAL_DEC * (1 - G_DEC / 100):.3f}，仍>123')
