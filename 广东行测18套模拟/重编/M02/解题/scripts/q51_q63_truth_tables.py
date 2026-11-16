"""第51题、第63题核验：真值表枚举。

第51题  S=形成科学的饮食结构，D=免疫系统功能衰退，B=均衡的营养配比，R=规律的喂食频率
  条件：¬S→D；“除非B且R，否则¬S”即 ¬(B∧R)→¬S
  检验各选项是否在所有满足条件的情形下都成立（“可以推出”）。

第63题  P=周密的应急预案，S=成功举办，C=承载能力足够，E=主办方经验丰富，O=安全有序
  条件：P→S；S→C；O→(E∧C)
  “最不可能发生”= 与条件矛盾、在任何满足条件的情形下都不会出现。
"""
from itertools import product

imp = lambda a, b: (not a) or b

print("== 第51题 ==")
worlds = [w for w in product([False, True], repeat=4)
          if imp(not w[0], w[1]) and imp(not (w[2] and w[3]), not w[0])]
opts51 = {
    "A 只要B且R，D不会发生": lambda S, D, B, R: imp(B and R, not D),
    "B 如果B且R，那么S": lambda S, D, B, R: imp(B and R, S),
    "C 如果D，那么¬S": lambda S, D, B, R: imp(D, not S),
    "D 除非R，否则D（¬R→D）": lambda S, D, B, R: imp(not R, D),
}
for k, f in opts51.items():
    print(k, "一定成立" if all(f(*w) for w in worlds) else "不一定成立")

print("== 第63题 ==")
worlds = [w for w in product([False, True], repeat=5)
          if imp(w[0], w[1]) and imp(w[1], w[2]) and imp(w[4], w[3] and w[2])]
opts63 = {
    "A ¬P 且 C": lambda P, S, C, E, O: (not P) and C,
    "B E且C 但 ¬O": lambda P, S, C, E, O: E and C and not O,
    "C C 且 ¬E 且 O": lambda P, S, C, E, O: C and (not E) and O,
    "D S（与条件无关的附加信息）": lambda P, S, C, E, O: S,
}
for k, f in opts63.items():
    print(k, "可能发生" if any(f(*w) for w in worlds) else "不可能发生")
