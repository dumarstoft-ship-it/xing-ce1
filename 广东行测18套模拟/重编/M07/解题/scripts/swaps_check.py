"""M07换入题复算：第37题（ZJ2023-A类-056，最不利构造）。"""
# 20种礼品各4张券；求最少人数n，使任意抽法都至少有3人领到同一种礼品
kinds, per = 20, 4
worst = kinds * min(2, per)           # 每种至多2人时最多能有的人数
n = worst + 1
print("最不利：每种2人，共", worst, "人；最少", n, "人 → A")
assert n == 41
print("误按每种3人：", kinds * 3 + 1, "→ C")

# 第57题（ZJ2020-B卷-063，翻译推理）：P=采取大刀阔斧的举措，S=经济稳健增长，D=公共债务不断攀升
import itertools
models = [(P, S, D) for P, S, D in itertools.product([True, False], repeat=3)
          if (P or not S) and (S or D)]          # 非P→非S；非S→D
opts = {"A": lambda P, S, D: (not D) or (not P),   # D→非P
        "B": lambda P, S, D: (not D) or (not P),   # 只有非P，才D：D→非P
        "C": lambda P, S, D: (not P) or (not D),   # P→非D
        "D": lambda P, S, D: D or P}               # 非D→P
valid = [k for k, f in opts.items() if all(f(*m) for m in models)]
print("第57题：满足题干的情形", len(models), "种；必然成立：", valid)
assert valid == ["D"]
