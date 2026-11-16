"""第86—90题（资料第4组：互联网保险保费）核算与材料自洽检查。第90题读图另见 q90_line_fit.py。"""

PREM = {2016: 2299, 2017: 1877, 2018: 1889, 2019: 2696, 2020: 2909,
        2021: 3779, 2022: 4783, 2023: 4949}
SHARE = {2016: 7.4, 2017: 5.1, 2018: 5.0, 2019: 6.3, 2020: 6.4,
         2021: 8.4, 2022: 10.2, 2023: 9.7}
P2013 = 290
CAGR = 32.8
JAN_JUL_2024, JAN_JUL_G = 3663, 15.0


def check_material():
    print("== 材料自洽检查 ==")
    c = ((PREM[2023] / P2013) ** (1 / 10) - 1) * 100
    print(f"2013→2023年均复合增长率 = ({PREM[2023]}/{P2013})^(1/10) - 1 = {c:.2f}%（材料 {CAGR}%）")
    first10 = min(y for y in SHARE if SHARE[y] > 10)
    print(f"占比首次超过10%的年份：{first10}（材料：2022年首次突破10%）")
    print("由占比反推总保费收入（亿元）：")
    for y in PREM:
        print(f"  {y}: {PREM[y]}/{SHARE[y]}% = {PREM[y] / SHARE[y] * 100:.0f}")
    print()


def q86():
    print("== 第86题 ==")
    s = sum(PREM[y] for y in range(2016, 2021))
    print(f"“十三五”2016—2020年合计 = {' + '.join(str(PREM[y]) for y in range(2016, 2021))} = {s} → A")
    print(f"（2017—2021年合计 {sum(PREM[y] for y in range(2017, 2022))}，即D项陷阱）")
    print()


def q87():
    print("== 第87题 ==")
    cnt = 0
    for y in range(2017, 2024):
        g_net = (PREM[y] / PREM[y - 1] - 1) * 100
        tot_now = PREM[y] / SHARE[y] * 100
        tot_prev = PREM[y - 1] / SHARE[y - 1] * 100
        g_tot = (tot_now / tot_prev - 1) * 100
        up = SHARE[y] > SHARE[y - 1]
        cnt += up
        print(f"  {y}: 占比 {SHARE[y - 1]}→{SHARE[y]} {'升' if up else '降'}；互联网保费增速 {g_net:6.2f}% "
              f"vs 总保费增速(反推) {g_tot:6.2f}% → {'超过' if g_net > g_tot else '未超过'}")
    print(f"共 {cnt} 年 → B")
    print()


def q88():
    print("== 第88题 ==")
    inc = PREM[2023] - PREM[2022]
    target = P2013 * 20
    print(f"2023年同比增量 = {PREM[2023]} - {PREM[2022]} = {inc}；目标 = {P2013}×20 = {target}")
    v, y = PREM[2023], 2023
    while v <= target:
        y += 1
        v += inc
        print(f"  {y}: {v}")
    print(f"首次超过 {target} 的年份：{y} → C")
    print(f"（不等式：{PREM[2023]}+{inc}n>{target} → n>{(target - PREM[2023]) / inc:.3f}，n=6）")
    print()


def q89():
    print("== 第89题 ==")
    base = JAN_JUL_2024 / (1 + JAN_JUL_G / 100)
    rest = PREM[2023] - base
    print(f"2023年1—7月 = {JAN_JUL_2024}/(1+{JAN_JUL_G}%) = {base:.2f}")
    print(f"2023年8—12月 = {PREM[2023]} - {base:.2f} = {rest:.2f}；月均 = {rest / 5:.2f} → B（353）")
    print()


def q90_values():
    print("== 第90题（增量序列） ==")
    inc = {y: PREM[y] - PREM[y - 1] for y in range(2017, 2024)}
    print(inc)
    print("读图拟合见 q90_line_fit.py")


if __name__ == "__main__":
    check_material()
    q86()
    q87()
    q88()
    q89()
    q90_values()
