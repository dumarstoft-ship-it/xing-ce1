"""Q61 (结构比较): check validity of each argument form by truth table.
Stem: P->Q, Q |- P (肯定后件, invalid)."""
from itertools import product

imp = lambda a, b: (not a) or b


def valid(premises, concl):
    return all(concl(p, q) for p, q in product([False, True], repeat=2) if all(f(p, q) for f in premises))


forms = {
    '题干 P->Q, Q |- P': ([lambda p, q: imp(p, q), lambda p, q: q], lambda p, q: p),
    'A 到期->重新申请, 非重新申请 |- 非到期': ([lambda p, q: imp(p, q), lambda p, q: not q], lambda p, q: not p),
    'B 不标注->学术不端, 不标注 |- 学术不端': ([lambda p, q: imp(p, q), lambda p, q: p], lambda p, q: q),
    'C 贮存->查验留存(只有…才), 贮存 |- 查验留存': ([lambda p, q: imp(p, q), lambda p, q: p], lambda p, q: q),
    'D 批发->建制度, 建制度 |- 批发': ([lambda p, q: imp(p, q), lambda p, q: q], lambda p, q: p),
}
for k, (prem, concl) in forms.items():
    print(f'{k:42s} {"valid" if valid(prem, concl) else "INVALID (肯定后件)"}')
