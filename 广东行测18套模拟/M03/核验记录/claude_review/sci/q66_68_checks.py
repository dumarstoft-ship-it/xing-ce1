#!/usr/bin/env python3
"""M03 Q66-Q68 computational checks (reviewer evidence, read-only).

Q66  buoyancy: random sweep over every configuration consistent with the figure
     (identical solid balls; ball floats partly above surface in 甲, is fully
     submerged and suspended in 乙; identical beakers; equal liquid level).
     Checks each option's truth value in every sample.
Q67  projectile: geometry from the vector source s21_p17_i04.svg, plus a sweep
     over all landing points with "A on the wall top left of the corner, B on
     the vertical face below the corner" to show the result is not a drawing
     artefact.
Q68  particle table: atom balance, consumed/produced molecules, option checks,
     oxidation states.
Run: python3 q66_68_checks.py
"""
import random
import re
from pathlib import Path

random.seed(20261115)
g = 9.8

# ---------------- Q66 ----------------
print('== Q66 浮力与液体压强（随机扫描 20000 组满足图示条件的参数）')
truth = {k: set() for k in 'ABCD'}
for _ in range(20000):
    S = random.uniform(20, 200)            # beaker inner base area (cm^2), straight-walled model
    H = random.uniform(8, 20)              # common liquid level (cm)
    V = random.uniform(10, 0.25 * S * H)   # ball volume (cm^3), must fit below the level
    rho_ball = random.uniform(0.3, 3.0)
    rho_yi = rho_ball                      # suspended: equal density
    f = random.uniform(0.05, 0.95)         # submerged fraction in 甲 (figure: partly above surface)
    rho_jia = rho_ball / f                 # floating: rho_ball*V = rho_jia*f*V
    m_ball = rho_ball * V
    disp_jia_w = rho_jia * f * V * g       # weight of displaced liquid
    disp_yi_w = rho_yi * V * g
    p_jia, p_yi = rho_jia * g * H, rho_yi * g * H
    liq_jia = rho_jia * (S * H - f * V)    # liquid mass
    liq_yi = rho_yi * (S * H - V)
    F_jia, F_yi = p_jia * S, p_yi * S
    truth['A'].add(disp_yi_w < disp_jia_w - 1e-9)   # 乙排开液体重力更小
    truth['B'].add(p_yi > p_jia)                    # 乙杯底压强更大
    truth['C'].add(liq_jia < liq_yi)                # 甲液体质量更小
    truth['D'].add(F_jia > F_yi)                    # 甲液体对杯底压力更大
    assert abs(disp_jia_w - m_ball * g) < 1e-6 and abs(disp_yi_w - m_ball * g) < 1e-6
for k in 'ABCD':
    print(f'   选项{k}: 出现过的真值 {sorted(truth[k])}')
print('   结论：只有D在全部样本中恒为真；A、B、C恒为假。（F=pS 与杯形无关，C 的结论只需"杯相同、液面相同"）')

# ---------------- Q67 ----------------
print('\n== Q67 平抛（SVG 图源坐标，单位为 viewBox 单位；y 向下）')
svg = Path('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p17_i04.svg').read_text(encoding='utf-8')
paths = re.findall(r'<path d="M([\d.]+) ([\d.]+) C([\d.]+) ([\d.]+),([\d.]+) ([\d.]+),([\d.]+) ([\d.]+)"', svg)
(oA, cA1, _, eA), (oB, cB1, _, eB) = [((float(p[0]), float(p[1])), (float(p[2]), float(p[3])), None, (float(p[6]), float(p[7]))) for p in paths]
wall = re.search(r'<path d="M(\d+) (\d+) H(\d+) V(\d+)', svg)
top_y, corner_x = float(wall.group(2)), float(wall.group(3))
print(f'   O={oA}  A终点={eA}  B终点={eB}  墙顶 y={top_y}  墙竖直面 x={corner_x}')
hA, hB = eA[1] - oA[1], eB[1] - oB[1]
xA, xB = oA[0] - eA[0], oB[0] - eB[0]
print(f'   h_A={hA}  h_B={hB}  x_A={xA}  x_B={xB}')
print(f'   t_A/t_B = sqrt(h_A/h_B) = {(hA / hB) ** 0.5:.3f}  ; v_A/v_B = (x_A/x_B)*sqrt(h_B/h_A) = {(xA / xB) * (hB / hA) ** 0.5:.3f}')
import math
for name, o, c in (('A', oA, cA1), ('B', oB, cB1)):
    ang = math.degrees(math.atan2(c[1] - o[1], o[0] - c[0]))
    print(f'   轨迹{name}在O点的切线方向：低于水平 {ang:.1f}°（"水平抛出"应为0°；只影响观感，不影响落点比较）')
bad = 0
for _ in range(20000):
    Oy, Ox = 0.0, 0.0
    cx = random.uniform(10, 200)       # horizontal distance from O to the wall's vertical face
    ty = random.uniform(10, 200)       # depth of the wall top below O
    xa = random.uniform(cx + 1e-3, cx + 300)   # A lands on the top face, left of the corner
    yb = random.uniform(ty + 1e-3, ty + 300)   # B hits the vertical face below the corner
    tA, tB = (2 * ty / g) ** 0.5, (2 * yb / g) ** 0.5
    vA, vB = xa / tA, cx / tB
    if not (tA < tB and vA > vB):
        bad += 1
print(f'   拓扑扫描 20000 组（A落墙顶、B落竖直面且低于墙角）：不满足"②③"的组数 = {bad}')

# ---------------- Q68 ----------------
print('\n== Q68 微观粒子表')
before = {'CH4': 1, 'O2': 3}
after = {'CO2': 1, 'O2': 1, 'H2O': 2}
comp = {'CH4': {'C': 1, 'H': 4}, 'O2': {'O': 2}, 'CO2': {'C': 1, 'O': 2}, 'H2O': {'H': 2, 'O': 1}}


def atoms(side):
    tot = {}
    for m, n in side.items():
        for a, k in comp[m].items():
            tot[a] = tot.get(a, 0) + n * k
    return tot


print('   反应前原子', atoms(before), ' 反应后原子', atoms(after))
consumed = {m: before.get(m, 0) - after.get(m, 0) for m in before if before.get(m, 0) > after.get(m, 0)}
produced = {m: after[m] - before.get(m, 0) for m in after if after[m] > before.get(m, 0)}
print('   实际消耗', consumed, ' 生成', produced, ' 剩余', {m: after[m] for m in after if m in before})
print('   A: 分子种类改变 =', set(before) != set(after), '；分子总数', sum(before.values()), '→', sum(after.values()), '→ "种类、数目均不变" 为假')
print('   B: 实际参加反应 CH4:O2 =', f"{consumed['CH4']}:{consumed['O2']}", '→ "1∶3" 为假')
ox = {'CH4': {'C': -4, 'H': +1}, 'O2': {'O': 0}, 'CO2': {'C': +4, 'O': -2}, 'H2O': {'H': +1, 'O': -2}}
print('   C: 化合价 C', ox['CH4']['C'], '→', ox['CO2']['C'], '；O', ox['O2']['O'], '→', ox['CO2']['O'], '→ 有元素化合价升降，属氧化还原反应，为真')
print('   D: 生成物种类数 =', len(produced), '→ "生成了三种不同的分子" 为假')
