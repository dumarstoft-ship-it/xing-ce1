"""M05 第66题："潜浮小车"从漂浮（空腔缓慢注水）到恰好悬浮。
用一组具体数值模拟注水过程，检验四个选项：
  F浮 = ρ水 g V排；漂浮、悬浮时 F浮 = G总（G总含空腔内的水）；p = ρ水 g h。
"""
from fractions import Fraction as F

rho = 1000            # kg/m^3
g = F(98, 10)         # N/kg
V = F(1, 1000)        # 小车外部总体积 1 L
H = F(1, 10)          # 小车高 0.1 m
m0 = F(6, 10)         # 空车质量 0.6 kg（<ρV=1 kg，起初漂浮）
cavity = F(6, 1000)   # 空腔容积 0.6 L，足够注水 0.4 kg

states = []
for dm_g in range(0, 401, 50):                 # 注水 0~400 g
    m = m0 + F(dm_g, 1000)
    assert F(dm_g, 1000) / rho <= cavity
    G = m * g
    if m < rho * V:                             # 漂浮：F浮=G，V排=m/ρ
        V_sub = m / rho
        state = "漂浮"
    else:                                       # m=ρV：完全浸没且恰好悬浮
        V_sub = V
        state = "悬浮"
    Fb = rho * g * V_sub
    states.append((dm_g, state, float(V_sub / V), float(G), float(Fb)))
    print(f"注水{dm_g:3d}g  {state}  浸入比例{float(V_sub / V):.2f}  G总={float(G):.2f}N  F浮={float(Fb):.2f}N")

Gs = [s[3] for s in states]
Fbs = [s[4] for s in states]
assert all(b > a for a, b in zip(Fbs, Fbs[1:])), "浮力应逐渐增大"      # A 错
assert all(b > a for a, b in zip(Gs, Gs[1:])), "重力应逐渐增大"        # B 对
assert states[-1][1] == "悬浮" and states[-1][3] == states[-1][4]     # C 错：悬浮时 F浮=G

# 悬浮时设顶部在水下 0.2 m，底部在 0.2+H
top_depth = F(2, 10)
p_top = rho * g * top_depth
p_bottom = rho * g * (top_depth + H)
print("悬浮时 顶部压强", float(p_top), "Pa，底部压强", float(p_bottom), "Pa")
assert p_bottom > p_top                                              # D 错
print("A错(浮力增大) B对(重力增大) C错(悬浮时浮力=重力) D错(底部压强更大)")
print("答案: B")
