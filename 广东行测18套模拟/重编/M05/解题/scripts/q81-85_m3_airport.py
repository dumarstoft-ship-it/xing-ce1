"""第81—85题（资料第3组：民航运输机场吞吐量）核算与材料自洽检查。第82题的读图另见 q82_pie_measure.py。"""

PAX_2024 = {"东部": (7.57, 18.6), "中部": (1.61, 12.8), "西部": (4.49, 12.6), "东北": (0.93, 15.8)}
PAX_TOTAL_2024, PAX_G = 14.60, 15.9
CARGO_2024 = {"东部": (1376.68, 14.1), "中部": (240.19, 58.5), "西部": (325.27, 21.9), "东北": (64.05, 10.0)}
CARGO_TOTAL_2024, CARGO_G = 2006.19, 19.2

FIG1 = {2020: (8.57, -36.6), 2021: (9.07, 5.8), 2022: (5.20, -42.7), 2023: (12.60, 142.3), 2024: (14.60, 15.9)}
FIG2 = {2020: (1607.49, -6.0), 2021: (1782.80, 10.9), 2022: (1453.05, -18.5), 2023: (1683.31, 15.8), 2024: (2006.19, 19.2)}


def check_material():
    print("== 材料自洽检查 ==")
    s = sum(v for v, _ in PAX_2024.values())
    print(f"旅客：四地区之和 {s:.2f}（全国 {PAX_TOTAL_2024}）")
    base = sum(v / (1 + g / 100) for v, g in PAX_2024.values())
    print(f"  四地区基期之和 {base:.3f}（图1 2023年 {FIG1[2023][0]}）；合成增速 {(s / base - 1) * 100:.2f}%（材料 {PAX_G}%）")
    c = sum(v for v, _ in CARGO_2024.values())
    print(f"货邮：四地区之和 {c:.2f}（全国 {CARGO_TOTAL_2024}）")
    cbase = sum(v / (1 + g / 100) for v, g in CARGO_2024.values())
    print(f"  四地区基期之和 {cbase:.2f}（图2 2023年 {FIG2[2023][0]}）；合成增速 {(c / cbase - 1) * 100:.2f}%（材料 {CARGO_G}%）")
    for name, fig in (("图1", FIG1), ("图2", FIG2)):
        for y in range(2021, 2025):
            calc = (fig[y][0] / fig[y - 1][0] - 1) * 100
            print(f"  {name} {y}: 由数值算增速 {calc:7.2f}%（图中 {fig[y][1]}%）")
    print()


def q81():
    print("== 第81题 ==")
    v2019 = FIG1[2020][0] / (1 + FIG1[2020][1] / 100)
    vals = [v2019] + [FIG1[y][0] for y in range(2020, 2025)]
    avg6 = sum(vals) / 6
    avg5 = sum(vals[1:]) / 5
    print(f"2019年 = {FIG1[2020][0]}/(1{FIG1[2020][1]}%) = {v2019:.3f} 亿人次")
    print(f"2019—2024年合计 = {sum(vals):.3f}，年均 = {avg6:.3f} → A（10.6）")
    print(f"（若漏掉2019年：2020—2024年均 {avg5:.3f}，即B项陷阱）")
    print()


def q83():
    print("== 第83题 ==")
    e = CARGO_2024["东部"][0]
    cw = CARGO_2024["中部"][0] + CARGO_2024["西部"][0]
    r = e / cw
    print(f"东部 {e} / (中部+西部 {cw:.2f}) = {r:.4f}；多 {r - 1:.4f} 倍 → D（1.4）（C项2.4是“是几倍”）")
    print()


def q84():
    print("== 第84题 ==")
    cnt = 0
    for reg in PAX_2024:
        pv, pg = PAX_2024[reg]
        cv, cg = CARGO_2024[reg]
        p_now = pv / PAX_TOTAL_2024
        p_prev = (pv / (1 + pg / 100)) / (PAX_TOTAL_2024 / (1 + PAX_G / 100))
        c_now = cv / CARGO_TOTAL_2024
        c_prev = (cv / (1 + cg / 100)) / (CARGO_TOTAL_2024 / (1 + CARGO_G / 100))
        up_p = pg > PAX_G
        up_c = cg > CARGO_G
        both = up_p and up_c
        cnt += both
        print(f"  {reg}: 旅客增速{pg}% vs {PAX_G}% → 比重{'升' if up_p else '降'}"
              f"（{p_prev * 100:.3f}%→{p_now * 100:.3f}%）；"
              f"货邮增速{cg}% vs {CARGO_G}% → 比重{'升' if up_c else '降'}"
              f"（{c_prev * 100:.3f}%→{c_now * 100:.3f}%）；均升：{both}")
    print(f"两项比重均上升的地区数 = {cnt} → A")
    print()


def q85():
    print("== 第85题 ==")
    cargo = sorted(v for v, _ in FIG2.values())
    print(f"A：货邮吞吐量排序 {cargo}，中位数 {cargo[2]} → 能推出")
    best_p = max(FIG1, key=lambda y: FIG1[y][1])
    best_c = max(FIG2, key=lambda y: FIG2[y][1])
    print(f"B：旅客增速最高 {best_p}年（{FIG1[best_p][1]}%），货邮增速最高 {best_c}年（{FIG2[best_c][1]}%），"
          f"{best_p}年货邮增速 {FIG2[best_p][1]}% → 不能推出")
    v2019 = FIG2[2020][0] / (1 + FIG2[2020][1] / 100)
    g = (FIG2[2021][0] / v2019 - 1) * 100
    g2 = ((1 + FIG2[2020][1] / 100) * (1 + FIG2[2021][1] / 100) - 1) * 100
    print(f"C：2019年货邮 = {FIG2[2020][0]}/(1{FIG2[2020][1]}%) = {v2019:.2f}；2021年较2019年增长 {g:.3f}%"
          f"（间隔增长率公式 {g2:.3f}%）< 5% → 能推出")
    d = FIG1[2022][1] - FIG2[2022][1]
    print(f"D：2022年 {FIG1[2022][1]} - ({FIG2[2022][1]}) = {d:.1f} 个百分点 → 能推出")
    print("答案 B")
    print()


if __name__ == "__main__":
    check_material()
    q81()
    q83()
    q84()
    q85()
