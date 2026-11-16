"""第71—75题（资料第1组：2025年广东省人口）核算与材料自洽检查。"""

# ---- 材料数据（万人） ----
POP_2025 = 12859
POP_INC = 79
BIRTH, BIRTH_RATE = 100.3, 7.82      # 万人，‰
DEATH, DEATH_RATE = 71.3, 5.56
NAT_RATE = 2.26
URBAN, RURAL = 9847, 3012
URB_RATE, URB_PP = 76.58, 0.67       # %，较上年提高百分点
AGE_0_15, AGE_16_59, AGE_60P, AGE_65P = 2339, 8527, 1993, 1324
WORK_SHARE = 66.31
GRAD_2025, GRAD_INC = 87, 3

POP_2024 = POP_2025 - POP_INC


def check_material():
    print("== 材料自洽检查 ==")
    print(f"城镇+乡村 = {URBAN + RURAL}（常住人口 {POP_2025}）")
    print(f"城镇化率 = {URBAN / POP_2025 * 100:.3f}%（材料 {URB_RATE}%）")
    print(f"三个年龄段之和 = {AGE_0_15 + AGE_16_59 + AGE_60P}（常住人口 {POP_2025}）")
    print(f"16—59岁占比 = {AGE_16_59 / POP_2025 * 100:.3f}%（材料 {WORK_SHARE}%）")
    avg = (POP_2024 + POP_2025) / 2
    print(f"年平均人口 = ({POP_2024}+{POP_2025})/2 = {avg}")
    print(f"出生率 = {BIRTH / avg * 1000:.3f}‰（材料 {BIRTH_RATE}‰）；"
          f"死亡率 = {DEATH / avg * 1000:.3f}‰（材料 {DEATH_RATE}‰）")
    print(f"自然增长率 = {BIRTH_RATE} - {DEATH_RATE} = {BIRTH_RATE - DEATH_RATE:.2f}‰（材料 {NAT_RATE}‰）；"
          f"按人数 {(BIRTH - DEATH) / avg * 1000:.3f}‰")
    print(f"净迁入（总增量−自然增长）≈ {POP_INC} - {BIRTH - DEATH:.1f} = {POP_INC - (BIRTH - DEATH):.1f} 万人")
    print()


def q71():
    print("== 第71题 ==")
    print("材料列举的人口发展新常态：少子化、老龄化、区域人口增加分化；未提“人口负增长”→ C")
    print()


def q72():
    print("== 第72题 ==")
    print("A、B、C 均为材料原句的复述；材料称广东“吸引普通劳动力”“集聚大量高端人才”，"
          f"且常住人口增量{POP_INC}万中自然增长仅{BIRTH - DEATH:.1f}万 → D“主要依靠自给自足”与材料不符")
    print()


def q73():
    print("== 第73题 ==")
    r24 = URB_RATE - URB_PP
    urban24 = POP_2024 * r24 / 100
    inc = URBAN - urban24
    print(f"2024年城镇化率 = {URB_RATE} - {URB_PP} = {r24:.2f}%")
    print(f"2024年常住人口 = {POP_2025} - {POP_INC} = {POP_2024}")
    print(f"2024年城镇人口 = {POP_2024} × {r24:.2f}% = {urban24:.2f} 万人")
    print(f"城镇人口增量 = {URBAN} - {urban24:.2f} = {inc:.2f} 万人 → 超过100万 → A")
    # 另一种拆分：增量 = 现期率×人口增量 + 百分点变化×上年人口
    alt = URB_RATE / 100 * POP_INC + URB_PP / 100 * POP_2024
    print(f"拆分验算：{URB_RATE}%×{POP_INC} + {URB_PP}%×{POP_2024} = {alt:.2f} 万人")
    exact_r25 = URBAN / POP_2025
    inc_exact = URBAN - POP_2024 * (exact_r25 - URB_PP / 100)
    print(f"用精确城镇化率{exact_r25 * 100:.4f}%推上年：增量 = {inc_exact:.2f} 万人（同样>100万）")
    print()
    return inc


def q74():
    print("== 第74题 ==")
    v = AGE_65P / AGE_60P * 100
    print(f"{AGE_65P} / {AGE_60P} = {v:.3f}% → 约66% → B")
    print()


def q75():
    print("== 第75题 ==")
    nat = BIRTH - DEATH
    print(f"A：自然增长人口 = {BIRTH} - {DEATH} = {nat:.1f} 万人 → 正确")
    non_work = AGE_0_15 + AGE_60P
    print(f"B：劳动年龄 {AGE_16_59} / 非劳动年龄({AGE_0_15}+{AGE_60P}={non_work}) = {AGE_16_59 / non_work:.4f} 倍 → 不到2倍，错误")
    print(f"   （用比重：{WORK_SHARE}/(100-{WORK_SHARE}) = {WORK_SHARE / (100 - WORK_SHARE):.4f}）")
    print(f"C：材料只说“每12名毕业生有1名来广东工作”，来广东工作的人数未给出，推不出全国总数不到1000万；"
          f"若误把广东毕业生{GRAD_2025}万×12 = {GRAD_2025 * 12}万，反而超过1000万 → 不能选")
    r24 = URB_RATE - URB_PP
    urban24 = POP_2024 * r24 / 100
    rural24 = POP_2024 - urban24
    print(f"D：城镇增量 {URBAN - urban24:.2f} 万；乡村 2024年 {rural24:.2f} → 2025年 {RURAL}，增量 {RURAL - rural24:.2f} 万（减少）→ 错误")
    print("答案 A")
    print()


if __name__ == "__main__":
    check_material()
    q71()
    q72()
    q73()
    q74()
    q75()
