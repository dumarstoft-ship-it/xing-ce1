"""第76—80题（资料第2组：跨区域人员流动量，累计值表）核算与材料自洽检查。单位：万人次。"""

# (累计到第几月, 跨区域累计值, 跨区域累计同比%, 公路累计值, 公路累计同比%)
Y2024 = [
    (2, 1171807, None, 1086652, 10.3),
    (3, 1671682, 10.2, 1547451, 9.0),
    (4, 2189330, 8.4, 2021233, 7.4),
    (5, 2736268, 8.3, 2523351, 7.4),
    (6, 3241011, 7.4, 2983967, 6.6),
    (7, 3799308, 6.6, 3489943, 5.8),
    (8, 4396867, 6.1, 4029157, 5.4),
    (9, 4909109, 5.4, 4499504, 4.7),
    (10, 5492663, 5.5, 5036908, 4.9),
    (11, 5972154, 5.4, 5478704, 4.8),
    (12, 6459234, 5.4, 5929002, 4.8),
]
Y2025 = [
    (2, 1229386, 4.9, 1139263, 4.8),
    (3, 1738829, 4.0, 1607309, 3.9),
]

CUM = {m: (t, tg, r, rg) for m, t, tg, r, rg in Y2024}


def monthly(idx):
    """由累计值求单月值（1—2月合并为一项）。"""
    out = {}
    prev = 0
    for m, *vals in Y2024:
        v = vals[idx]
        out[m] = v - prev
        prev = v
    return out


TOT_M = monthly(0)   # 跨区域单月（2为1—2月合计）
ROAD_M = monthly(2)  # 公路单月


def check_material():
    print("== 材料自洽检查 ==")
    print("2024年单月值（2=1—2月合计）：")
    for m in TOT_M:
        print(f"  {m:>2}月 跨区域 {TOT_M[m]:>8}  公路 {ROAD_M[m]:>8}  非公路 {TOT_M[m] - ROAD_M[m]:>7}"
              f"  公路占比 {ROAD_M[m] / TOT_M[m] * 100:5.2f}%")
    t25, r25 = Y2025[1][1], Y2025[1][3]
    print(f"2025年1—2月同比：跨区域 {Y2025[0][1] / CUM[2][0] * 100 - 100:.3f}%（表4.9）"
          f" 公路 {Y2025[0][3] / CUM[2][2] * 100 - 100:.3f}%（表4.8）")
    print(f"2025年1—3月同比：跨区域 {t25 / CUM[3][0] * 100 - 100:.3f}%（表4.0）"
          f" 公路 {r25 / CUM[3][2] * 100 - 100:.3f}%（表3.9）")
    # 由同比反推2023年累计值，再求2023单月，检查是否为正、公路是否不超过总量
    print("由同比反推的2023年累计值与单月值：")
    prev_t = prev_r = None
    for m, t, tg, r, rg in Y2024:
        t23 = t / (1 + tg / 100) if tg is not None else None
        r23 = r / (1 + rg / 100)
        mt = (t23 - prev_t) if (t23 is not None and prev_t is not None) else None
        mr = (r23 - prev_r) if prev_r is not None else None
        s = f"  1—{m}月 2023累计：跨区域 {t23:.0f}" if t23 else f"  1—{m}月 2023累计：跨区域 —"
        s += f" 公路 {r23:.0f}"
        if mr is not None:
            s += f" | 2023年{m}月 公路 {mr:.0f}"
            if mt is not None:
                s += f" 跨区域 {mt:.0f}"
        print(s)
        prev_t, prev_r = t23, r23
    print()


def q76():
    print("== 第76题 ==")
    q = {
        "一季度": CUM[3][0],
        "二季度": CUM[6][0] - CUM[3][0],
        "三季度": CUM[9][0] - CUM[6][0],
        "四季度": CUM[12][0] - CUM[9][0],
    }
    for k, v in q.items():
        print(f"  {k}: {v}")
    low = min(q, key=q.get)
    print(f"最低：{low} → D")
    print()


def q77():
    print("== 第77题 ==")
    t, tg, r, rg = CUM[3]
    t23 = t / (1 + tg / 100)
    r23 = r / (1 + rg / 100)
    share = (t23 - r23) / t23 * 100
    print(f"2023年一季度 跨区域 = {t}/(1+{tg}%) = {t23:.1f}；公路 = {r}/(1+{rg}%) = {r23:.1f}")
    print(f"非公路占比 = 1 - {r23:.1f}/{t23:.1f} = {share:.3f}% → A（6.4%）")
    print(f"对照：2024年一季度非公路占比 = {(t - r) / t * 100:.3f}%（B项7.4%是误用现期）")
    # 公式：1 - (r/t)×(1+tg)/(1+rg)
    print(f"公式验算：1 - {r / t:.5f}×{1 + tg / 100}/{1 + rg / 100} = {(1 - r / t * (1 + tg / 100) / (1 + rg / 100)) * 100:.3f}%")
    print()


def q78():
    print("== 第78题 ==")
    r25 = Y2025[1][3]
    r24, rg24 = CUM[3][2], CUM[3][3]
    r23 = r24 / (1 + rg24 / 100)
    g = (r25 / r23 - 1) * 100
    print(f"2023年一季度公路 = {r24}/(1+{rg24}%) = {r23:.1f}")
    print(f"增长率 = {r25}/{r23:.1f} - 1 = {g:.3f}%")
    g_round = ((1 + 3.9 / 100) * (1 + 9.0 / 100) - 1) * 100
    print(f"间隔增长率公式（用表中3.9%、9.0%）：3.9%+9.0%+3.9%×9.0% = {g_round:.3f}%")
    print("两种算法都约13.2%—13.3%，与B（13.3%）最接近，与C（12.9%）相差0.3个百分点以上 → B")
    print()


def q79():
    print("== 第79题 ==")
    h2 = {m: CUM[m][1] for m in range(7, 13)}
    print("下半年累计同比：", h2)
    best = max(h2, key=h2.get)
    print(f"最高为1—{best}月 → {best}月")
    cur, prev = ROAD_M[best], ROAD_M[best - 1]
    print(f"{best}月公路 = {CUM[best][2]} - {CUM[best - 1][2]} = {cur}；"
          f"{best - 1}月公路 = {CUM[best - 1][2]} - {CUM[best - 2][2]} = {prev}")
    print(f"环比 = {cur}/{prev} - 1 = {(cur / prev - 1) * 100:.3f}% → C（9.8%）")
    for m in range(4, 13):
        print(f"  （参考）{m}月公路环比 {(ROAD_M[m] / ROAD_M[m - 1] - 1) * 100:7.2f}%")
    print()


def q80():
    print("== 第80题 ==")
    r, rg = CUM[12][2], CUM[12][3]
    inc = r - r / (1 + rg / 100)
    print(f"A：2024年公路同比增量 = {r} - {r}/(1+{rg}%) = {inc:.0f} 万人次 = {inc / 10000:.2f} 亿人次 < 30亿 → 错")
    # B：逐月同比需由累计同比反推2023单月；1、2月只有合计，无法分月；并按四舍五入区间检验9月
    lo9 = CUM[9][2] / (1 + 4.75 / 100)
    hi9 = CUM[9][2] / (1 + 4.65 / 100)
    lo8 = CUM[8][2] / (1 + 5.45 / 100)
    hi8 = CUM[8][2] / (1 + 5.35 / 100)
    sep23_min, sep23_max = lo9 - hi8, hi9 - lo8
    print(f"B：1月、2月只有合计数，无法判断单月；另按同比四舍五入区间反推2023年9月公路量∈[{sep23_min:.0f}, {sep23_max:.0f}]，"
          f"2024年9月 = {ROAD_M[9]}，低于区间下限 → 9月同比下降，B错")
    for m in range(3, 13):
        r23_now = CUM[m][2] / (1 + CUM[m][3] / 100)
        r23_prev = CUM[m - 1][2] / (1 + CUM[m - 1][3] / 100)
        m23 = r23_now - r23_prev
        print(f"   {m}月公路同比（点估计）{(ROAD_M[m] / m23 - 1) * 100:6.2f}%")
    t6, r6 = CUM[6][0], CUM[6][2]
    print(f"C：2024年上半年非公路占比 = ({t6}-{r6})/{t6} = {(t6 - r6) / t6 * 100:.3f}% < 10% → 对")
    q1 = Y2025[1][1]
    year = q1 / 3 * 12
    print(f"D：{q1}/3×12 = {year:.0f} 万人次 = {year / 10000:.2f} 亿人次 < 700亿 → 错")
    print("答案 C")
    print()


if __name__ == "__main__":
    check_material()
    q76()
    q77()
    q78()
    q79()
    q80()
