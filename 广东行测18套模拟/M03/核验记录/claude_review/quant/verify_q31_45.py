#!/usr/bin/env python3
"""M03 第31-45题（数量关系）外审复核脚本 —— Claude 独立复核用。

只读仓库文件：题目.jsonl（考生可见题面/选项）、selection.json（编辑答案、源对象）、
第35题 PNG/SVG。不写仓库。输出写到本脚本所在目录：
  verify_q31_45_report.txt   人读报告
  verify_q31_45_result.json  机读结果

用法：python3 verify_q31_45.py [仓库根目录，默认 /home/user/xing-ce1]

内容：
  1. 数字推理：编辑规律逐锚点复核 + 一组“常见规律族”的替代规律搜索
     （常差、差数列等比、带常数二阶线性递推、三阶线性递推、隔项、分组二元运算、
      第35题小表达式穷举），列出所有拟合全部已知项且命中某选项的规律。
  2. 数学运算：精确分数或穷举复核，逐选项判定是否满足题设；常见错法 -> 干扰项映射。
  3. 第35题：解析 SVG 文本坐标，按象限还原四圆数字，与 source_question 位置表逐格比对；
     测量 PNG 中各负号与竖直直径的间距。
"""
from __future__ import annotations

import collections
import datetime
import itertools
import json
import math
import re
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/user/xing-ce1')
M03 = ROOT / '广东行测18套模拟' / 'M03'
OUT = Path(__file__).resolve().parent

LINES: list[str] = []
RESULT: dict = {'repo_root': str(ROOT), 'questions': {}}


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def fstr(x):
    if isinstance(x, F):
        return str(x) if x.denominator != 1 else str(x.numerator)
    return str(x)


# ---------------------------------------------------------------- load
QS = {}
with open(M03 / '题目.jsonl', encoding='utf-8') as fh:
    for line in fh:
        if line.strip():
            q = json.loads(line)
            if 31 <= q['number'] <= 45:
                QS[q['number']] = q
SEL = {x['number']: x for x in json.loads((M03 / 'selection.json').read_text(encoding='utf-8'))
       if 31 <= x['number'] <= 45}
assert sorted(QS) == list(range(31, 46)) and sorted(SEL) == list(range(31, 46))


def text_of(blocks):
    return ''.join(b.get('text', '') for b in blocks)


def opts(n):
    return {k: text_of(v) for k, v in QS[n]['options'].items()}


def parse_opt_value(s):
    """把选项文本转为数值（支持 $\\sqrt{109}$、$\\frac{a}{b}$、百分号、单位、比）。"""
    s = s.strip()
    m = re.fullmatch(r'\$\\sqrt\{(\d+)\}\$', s)
    if m:
        return ('sqrt', int(m.group(1)))
    m = re.fullmatch(r'\$\\frac\{(-?\d+)\}\{(\d+)\}\$', s)
    if m:
        return F(int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(r'(\d+)：(\d+)', s)
    if m:
        return F(int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*(%|米)?', s)
    if m:
        v = F(m.group(1))
        return v / 100 if m.group(2) == '%' else v
    return s


def opt_values(n):
    return {k: parse_opt_value(v) for k, v in opts(n).items()}


def record(n, my_answer, satisfied, notes, **extra):
    key = SEL[n]['answer']
    RESULT['questions'][str(n)] = {
        'editor_answer': key, 'claude_check_answer': my_answer,
        'agree': key == my_answer, 'options_satisfying_conditions': satisfied,
        'source_answer': SEL[n]['source_answer'], 'notes': notes, **extra}
    say(f'  => 复核答案 {my_answer}；编辑答案 {key}；{"一致" if key == my_answer else "不一致！"}；'
        f'满足题设的选项 {satisfied}；源答案 {SEL[n]["source_answer"]}')


def check_stem_matches_selection(n):
    """当前显示题面应等于 stem_override（有则）或源题面。"""
    shown = text_of(QS[n]['stem'])
    sel = SEL[n]
    base = sel.get('stem_override') or sel['source_question']['stem']
    ok = shown == text_of(base)
    so = {k: text_of(v) for k, v in sel['source_question']['options'].items()}
    ok_opts = so == opts(n)
    return ok, ok_opts


# ---------------------------------------------------------------- number-series helpers
def diffs(s):
    return [b - a for a, b in zip(s, s[1:])]


def extend_by_diff_table(s, level, nxt_at_level):
    table = [list(s)]
    for _ in range(level):
        table.append(diffs(table[-1]))
    v = nxt_at_level
    for j in range(level - 1, -1, -1):
        v = table[j][-1] + v
    return v


def family_predictions(s, label=''):
    """对一个序列跑常见规律族；返回 [(规律描述, 预测下一项, 验证次数)]。"""
    out = []
    s = [F(x) for x in s]
    # 1) 某级差为常数（至少3个相同差）
    t = list(s)
    for k in range(1, 4):
        t = diffs(t)
        if len(t) >= 3 and len(set(t)) == 1:
            out.append((f'{label}{k}级差恒为{fstr(t[0])}', extend_by_diff_table(s, k, t[0]), len(t) - 1))
    # 2) 某级差为等比（至少3项，即至少2个比值相同）
    t = list(s)
    for k in range(1, 3):
        t = diffs(t)
        if len(t) >= 3 and all(x != 0 for x in t[:-1]):
            r = [t[i + 1] / t[i] for i in range(len(t) - 1)]
            if len(set(r)) == 1:
                out.append((f'{label}{k}级差公比{fstr(r[0])}', extend_by_diff_table(s, k, t[-1] * r[0]), len(r) - 1))
    # 3) 本身等比
    if len(s) >= 3 and all(x != 0 for x in s[:-1]):
        r = [s[i + 1] / s[i] for i in range(len(s) - 1)]
        if len(set(r)) == 1:
            out.append((f'{label}公比{fstr(r[0])}', s[-1] * r[0], len(r) - 1))
    # 4) a(n)=p a(n-1)+q a(n-2)+r，p,q∈{-3..3,±1/2,±1/3,±2/3}，至少2次额外验证
    coeffs = sorted({F(i) for i in range(-3, 4)} | {F(1, 2), F(-1, 2), F(1, 3), F(-1, 3), F(2, 3), F(-2, 3)})
    if len(s) >= 5:
        for p, q in itertools.product(coeffs, repeat=2):
            if p == 0 and q == 0:
                continue
            r = s[2] - p * s[1] - q * s[0]
            if all(s[i] == p * s[i - 1] + q * s[i - 2] + r for i in range(3, len(s))):
                if len(s) - 3 >= 2:
                    out.append((f'{label}a(n)={fstr(p)}a(n-1)+{fstr(q)}a(n-2)+{fstr(r)}',
                                p * s[-1] + q * s[-2] + r, len(s) - 3))
    # 5) a(n)=p a(n-1)+q a(n-2)+u a(n-3)，整数系数-2..2，至少2个方程成立
    if len(s) >= 5:
        for p, q, u in itertools.product(range(-2, 3), repeat=3):
            if (p, q, u) == (0, 0, 0):
                continue
            if all(s[i] == p * s[i - 1] + q * s[i - 2] + u * s[i - 3] for i in range(3, len(s))):
                if len(s) - 3 >= 2:
                    out.append((f'{label}a(n)={p}a(n-1)+{q}a(n-2)+{u}a(n-3)',
                                p * s[-1] + q * s[-2] + u * s[-3], len(s) - 3))
    return out


def series_battery(seq, include_interleave=True, include_diff_recur=True):
    """序列整体、差数列、隔项子列各跑规律族。返回 [(描述, 预测值)]。"""
    preds = []
    for d, v, c in family_predictions(seq, '整体:'):
        preds.append((d, v, c))
    if include_diff_recur:
        d1 = diffs([F(x) for x in seq])
        for d, v, c in family_predictions(d1, '一级差数列:'):
            preds.append((d, F(seq[-1]) + v, c))
    if include_interleave:
        n_next = len(seq)  # 0-based index of blank
        sub = [F(x) for x in seq[n_next % 2::2]]
        par = '奇数项' if n_next % 2 == 0 else '偶数项'
        for d, v, c in family_predictions(sub, f'{par}子列:'):
            preds.append((d, v, c))
    return preds


def match_option(v, ovals):
    hits = []
    for k, ov in ovals.items():
        if isinstance(ov, F) and isinstance(v, F) and ov == v:
            hits.append(k)
    return hits


# ================================================================ Q31
say('=' * 72)
say('第31题  3，2，√13，8，6，10，10，3，（ ）')
ov = opt_values(31)
groups = [(3, 2, ('sqrt', 13)), (8, 6, 10)]
ops = {
    'a+b': lambda a, b: a + b, 'a-b': lambda a, b: a - b, 'a*b': lambda a, b: a * b,
    'a^2+b^2': lambda a, b: a * a + b * b, 'a^2-b^2': lambda a, b: a * a - b * b,
    'sqrt(a^2+b^2)': lambda a, b: ('sqrt', a * a + b * b), 'sqrt(a^2-b^2)': lambda a, b: ('sqrt', a * a - b * b),
    '(a+b)^2': lambda a, b: (a + b) ** 2, 'a*b+a': lambda a, b: a * b + a, 'a*b+b': lambda a, b: a * b + b,
    '2a+b': lambda a, b: 2 * a + b, 'a+2b': lambda a, b: a + 2 * b, 'a^2+b': lambda a, b: a * a + b,
}


def norm(v):
    if isinstance(v, tuple) and v[0] == 'sqrt':
        r = math.isqrt(v[1]) if v[1] >= 0 else None
        if r is not None and r * r == v[1]:
            return F(r)
        return v
    return F(v)


fits = []
for name, f in ops.items():
    if all(norm(f(a, b)) == norm(c) for a, b, c in groups):
        pv = norm(f(10, 3))
        hit = [k for k, o in ov.items() if (o == pv)]
        fits.append((name, pv, hit))
say('  三项分组：拟合前两组的组内二元运算 ->', fits)
assert [x[0] for x in fits] == ['sqrt(a^2+b^2)'] and fits[0][2] == ['A']
# 其他分组（两项一组无法覆盖9项；四项一组）检查：整体规律族
alt = [(d, fstr(v)) for d, v, c in series_battery([3, 2, 8, 6, 10, 10, 3], include_interleave=False)]
say('  （去掉无理项后整体规律族的拟合，仅作排除参考）:', alt if alt else '无')
say('  干扰项：D=109 漏开方；C=√103 为 10²+3；B=11 无自然规律。')
record(31, 'A', ['A'], '唯一拟合的组内运算为 c=√(a²+b²)')

# ================================================================ Q32
say('=' * 72)
say('第32题  28，17，30，29，36，46，54，75，（ ）')
seq = [28, 17, 30, 29, 36, 46, 54, 75]
ov = opt_values(32)
preds = series_battery(seq)
hits = [(d, fstr(v), c, match_option(v, ov)) for d, v, c in preds]
for h in hits:
    say('   规律:', h[0], '-> 预测', h[1], f'(额外验证{h[2]}次)', '命中选项', h[3])
even = seq[1::2]
assert all(even[i] == even[i - 1] + even[i - 2] for i in range(2, len(even)))
say('  偶数项 17,29,46,75 满足 a(n)=a(n-1)+a(n-2)（隔项印证）')
opt_hit = sorted({k for h in hits for k in h[3]})
say('  所有拟合规律命中的选项:', opt_hit)
record(32, 'A', opt_hit, '奇数项差2,6,18公比3；另奇数项−27=1,3,9,27 同解；无规律指向B/C/D')

# ================================================================ Q33
say('=' * 72)
say('第33题  3，7/3，5/3，1，43/81，（ ）')
seq = [F(3), F(7, 3), F(5, 3), F(1), F(43, 81)]
ov = opt_values(33)
say('  选项值:', {k: fstr(v) for k, v in ov.items()})
nums = [x * 3 ** i for i, x in enumerate(seq)]
say('  ×3^n 还原分子:', [fstr(x) for x in nums], '差', [fstr(x) for x in diffs(nums)])
all_hits = set()
for base in range(2, 7):
    scaled = [x * base ** i for i, x in enumerate(seq)]
    if all(v.denominator == 1 for v in scaled):
        for d, v, c in series_battery(scaled, include_interleave=False):
            pv = v / base ** len(seq)
            h = match_option(pv, ov)
            say(f'   ×{base}^n 后 {d} -> 下一项 {fstr(pv)}（额外验证{c}次） 命中 {h}')
            all_hits |= set(h)
for d, v, c in series_battery(seq, include_interleave=False):
    h = match_option(v, ov)
    say(f'   原值 {d} -> 下一项 {fstr(v)} 命中 {h}')
    all_hits |= set(h)
say('  注意：前四项相邻差均为2/3（3→7/3→5/3→1），第五项43/81破坏该规律——属有意干扰，非竞争解。')
say('  所有拟合规律命中的选项:', sorted(all_hits))
record(33, 'D', sorted(all_hits), '分母统一为3^n，分子3,7,15,27,43二级差为4，下一项63/243=7/27')

# ================================================================ Q34
say('=' * 72)
say('第34题  12，41，59，70，77，81，（ ）')
seq = [12, 41, 59, 70, 77, 81]
ov = opt_values(34)
preds = series_battery(seq, include_interleave=True)
all_hits = set()
for d, v, c in preds:
    h = match_option(v, ov)
    say('   规律:', d, '-> 预测', fstr(v), f'(额外验证{c}次)', '命中', h)
    all_hits |= set(h)
# 差数列 d(n)=d(n-2)-d(n-1)
d = diffs(seq)
assert all(d[i] == d[i - 2] - d[i - 1] for i in range(2, len(d)))
say('  差 29,18,11,7,4：d(n)=d(n-2)-d(n-1) 成立3次 -> 下一差3 -> 84；等价 a(n)=2a(n-2)-a(n-3)')
say('  所有拟合规律命中的选项:', sorted(all_hits))
record(34, 'A', sorted(all_hits), '差数列递推唯一指向84')

# ================================================================ Q35
say('=' * 72)
say('第35题  圆形数阵（左上a、右上b、左下c、右下d）')
src_rows = SEL[35]['source_question']['stem'][0]['rows']


def cell(x):
    return None if x in ('？', '?') else int(x.replace('−', '-'))


circles = [[cell(v) for v in r[1:]] for r in src_rows]
say('  source_question 位置表:', circles)
# --- SVG 解析：按文本坐标归入象限
svg = (M03 / '编辑底稿' / 'quant_data_number_grid.svg').read_text(encoding='utf-8')
centers = [(float(m.group(1)), float(m.group(2))) for m in re.finditer(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)]
texts = [(float(m.group(1)), float(m.group(2)), m.group(3)) for m in
         re.finditer(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]+)</text>', svg)]
svg_circles = []
for cx, cy in centers:
    quad = {}
    for x, y, t in texts:
        if abs(x - cx) < 70 and abs(y - cy) < 70:
            pos = ('上' if y < cy else '下') + ('左' if x < cx else '右')
            quad[pos] = t
    svg_circles.append([quad.get('上左'), quad.get('上右'), quad.get('下左'), quad.get('下右')])
svg_cells = [[cell(v) for v in c] for c in svg_circles]
say('  SVG 按坐标还原（左上,右上,左下,右下）:', svg_circles)
svg_match = svg_cells == circles
say('  SVG 与源位置表逐格一致:', svg_match)
assert svg_match
# --- PNG 与 SVG 尺寸比例、负号间距
try:
    from PIL import Image
    im = Image.open(M03 / '编辑底稿' / 'quant_data_number_grid.png').convert('L')
    W, H = im.size
    sc = W / 720
    say(f'  PNG {W}x{H}，相对 SVG 720x180 比例 {sc}')
    px = im.load()
    gaps = {}
    for (cx, cy), circ in zip(centers, svg_circles):
        # 右下象限文本行：y=118；从竖直直径向右扫描到第一个文字像素
        y = int(118 * sc)
        x0 = int(cx * sc)
        xs = [x for x in range(x0 - 6, int((cx + 70) * sc)) if px[x, y] < 128]
        # 竖线像素是连续的一段，取其后第一段
        runs = []
        for x in xs:
            if runs and x == runs[-1][-1] + 1:
                runs[-1].append(x)
            else:
                runs.append([x])
        if len(runs) >= 2:
            gaps[circ[3]] = runs[1][0] - runs[0][-1] - 1
    say('  右下象限：竖直直径右缘到首个字形像素的间距(px，PNG 2160宽):', gaps)
    RESULT['q35_png_gap_px'] = gaps
except Exception as e:  # pragma: no cover
    say('  PNG 检查跳过:', e)
# --- 小表达式穷举：d = E(a,b,c)，叶子 a,b,c 与常数1,2,3，运算 + − ×，至多2个运算
leaves = {'a': lambda r: r[0], 'b': lambda r: r[1], 'c': lambda r: r[2],
          '1': lambda r: 1, '2': lambda r: 2, '3': lambda r: 3}
binops = {'+': lambda x, y: x + y, '-': lambda x, y: x - y, '*': lambda x, y: x * y}
exprs = dict(leaves)
for (n1, f1), (n2, f2) in itertools.product(list(leaves.items()), repeat=2):
    for on, of in binops.items():
        exprs[f'({n1}{on}{n2})'] = (lambda f1, f2, of: lambda r: of(f1(r), f2(r)))(f1, f2, of)
lvl1 = dict(exprs)
for (n1, f1), (n2, f2) in itertools.product(list(lvl1.items()), list(leaves.items())):
    for on, of in binops.items():
        exprs[f'({n1}{on}{n2})'] = (lambda f1, f2, of: lambda r: of(f1(r), f2(r)))(f1, f2, of)
        exprs[f'({n2}{on}{n1})'] = (lambda f1, f2, of: lambda r: of(f2(r), f1(r)))(f1, f2, of)
fit35 = collections.defaultdict(list)
for name, f in exprs.items():
    if sum(ch in name for ch in 'abc') < 2:
        continue
    if all(f(c[:3]) == c[3] for c in circles[:3]):
        fit35[f(circles[3][:3])].append(name)
ov = opt_values(35)
summary35 = {str(v): (sorted(set(n))[:6], [k for k, o in ov.items() if o == v]) for v, n in fit35.items()}
say('  拟合三圆的小表达式（预测值: 示例表达式, 命中选项）:', summary35)
opt_hit = sorted({k for v in fit35 for k, o in ov.items() if o == v})
say('  命中的选项:', opt_hit)
say('  对称性：a、d 互换或 b、c 互换后规律 a+d=b×c 不变，问号所在格不变 -> 转写若只错在这两对对称位置，答案不受影响。')
record(35, 'B', opt_hit, 'a+d=b×c；重建图与源位置表逐格一致', svg_matches_source_table=svg_match)

# ================================================================ Q36
say('=' * 72)
say('第36题  黑=其余的3/4，蓝=其余的3/5，红30多盒')
sols = []
for T in range(1, 2000):
    for black in range(T + 1):
        if 4 * black != 3 * (T - black):
            continue
        for blue in range(T - black + 1):
            if 5 * blue != 3 * (T - blue):
                continue
            red = T - black - blue
            if 30 < red < 40:
                sols.append((T, black, blue, red))
say('  穷举 T≤1999 的全部整数解:', sols)
ov = opt_values(36)
per_opt = {}
for k, v in ov.items():
    T = int(v)
    black, blue = F(3, 7) * T, F(3, 8) * T
    per_opt[k] = (T, fstr(black), fstr(blue), fstr(T - black - blue))
say('  逐选项（总, 黑, 蓝, 红）:', per_opt, '——四个选项都是56的倍数，只有红=33落在30多')
assert sols == [(168, 72, 63, 33)]
record(36, 'B', [k for k, v in ov.items() if int(v) == 168], '唯一解 168=72+63+33')

# ================================================================ Q37
say('=' * 72)
say('第37题  数位对调 + 50x+40y=总人数')
pops = []
for N in range(1, 700):
    a, b, c = N // 100, N // 10 % 10, N % 10
    if N - (100 * b + 10 * a + c) == 270 and N - (100 * c + 10 * b + a) == 594:
        pops.append(N)
say('  穷举 1≤N≤699（含前导零写法）满足两次对调的 N:', pops)
assert pops == [630]
buses = [(x, y) for x in range(0, 13) for y in range(0, 16) if 50 * x + 40 * y == 630]
say('  50x+40y=630 的非负整数解 (大巴, 小巴):', buses)
ov = opt_values(37)
feas = [k for k, v in ov.items() if any(x == int(v) for x, y in buses)]
say('  选项中可行的大巴数:', feas, '；最少大巴 =', min(x for x, y in buses), '（且小巴≥1，满足“和”）')
say('  注：个位与百位对调得 036=36，需接受首位为0的数值；a−c=6 且 a≤6 迫使 c=0。')
record(37, 'C', feas, '唯一 N=630；x≡3(mod 4)，最少3辆')

# ================================================================ Q38
say('=' * 72)
say('第38题  进价120不变，涨价20%利润增30，总利润为上月80%，求收入降幅')
cost = F(120)
P = F(30) / F(1, 5)
p0, p1 = P - cost, P * F(6, 5) - cost
qratio = F(4, 5) * p0 / p1
rev = qratio * F(6, 5)
say(f'  原售价 {fstr(P)}，原/新单件利润 {fstr(p0)}/{fstr(p1)}，销量比 {fstr(qratio)}，收入比 {fstr(rev)}，降幅 {fstr(1 - rev)}')
ov = opt_values(38)
errs38 = {
    '收入比当降幅(0.48)': F(12, 25),
    '正确降幅 1-0.48': 1 - rev,
    '忽略售价上涨，只看销量降幅 1-0.4': 1 - qratio,
    '把利润降20%直接当收入降幅': F(1, 5),
}
for name, v in errs38.items():
    say(f'   {name}: {fstr(v)} -> 命中 {[k for k, o in ov.items() if o == v]}')
# 若进价可变：售价上涨 0.2P，利润增30 => 新进价 = 120 + 0.2P - 30，P 不定 -> 题目欠定
say('  若删去“进价保持不变”：0.2P−Δ进价=30 有无穷多组 (P,Δ进价)，降幅随之变化（如 Δ进价=6 时 P=180）：')
for dcost in [0, 6, -6]:
    PP = (30 + dcost) / F(1, 5)
    pp0, pp1 = PP - 120, PP * F(6, 5) - (120 + dcost)
    if pp0 > 0 and pp1 > 0:
        rr = F(4, 5) * pp0 / pp1 * F(6, 5)
        say(f'     Δ进价={dcost}: 原价 {fstr(PP)}，收入降幅 {float(1 - rr):.4f}')
record(38, 'D', [k for k, o in ov.items() if o == 1 - rev], '收入为上月48%，降52%；补“进价不变”是必要前提')

# ================================================================ Q39
say('=' * 72)
say('第39题  风场往返')
w = None
for wn in range(1, 36):
    if F(36 + wn, 36 - wn) == 2:
        w = F(wn)
w2 = w * F(3, 2)
L = F(4) / (F(1, 36 - w2) + F(1, 36 + w2))
say(f'  第一次风速 {fstr(w)}，第二次 {fstr(w2)}，L = {fstr(L)}')
ov = opt_values(39)
errs39 = {
    '正确': L,
    '风速未乘1.5（w=12）': F(4) / (F(1, 24) + F(1, 48)),
    '用算术平均速度36': F(4) * 36 / 2,
    '把1.5倍误乘到长度': L * F(3, 2),
}
for name, v in errs39.items():
    say(f'   {name}: L={fstr(v)} -> 命中 {[k for k, o in ov.items() if o == v]}')
record(39, 'D', [k for k, o in ov.items() if o == L], 'w=12，二测18，L=54')

# ================================================================ Q40
say('=' * 72)
say('第40题  倒置圆锥（底面朝上）露出≥37/64')
h_sub = F(7) * F(3, 4)
assert F(3, 4) ** 3 == 1 - F(37, 64)
drop = 7 - h_sub
say(f'  水下小圆锥高 ≤ {fstr(h_sub)}，至少降 {fstr(drop)} 米')
ov = opt_values(40)
errs40 = {
    '正确：7(1-∛(27/64))': 7 * (1 - (27 / 64) ** (1 / 3)),
    '误按尖朝上：露出小圆锥 7∛(37/64)': 7 * (37 / 64) ** (1 / 3),
    '误按线性：7×37/64': 7 * 37 / 64,
    '误按面积比：7(1-√(27/64))': 7 * (1 - (27 / 64) ** 0.5),
    '误算 7(1-∛(37/64))': 7 * (1 - (37 / 64) ** (1 / 3)),
    '7×27/64': 7 * 27 / 64,
}
for name, v in errs40.items():
    say(f'   {name}: {v:.4f} -> 最接近选项 {min(ov, key=lambda k: abs(float(ov[k]) - v))}')
say('  逐选项：水位降x米后露出体积比 = 1-((7-x)/7)^3，与37/64比较（“至少”要求取满足条件的最小x）')
ok40 = []
for k, o in ov.items():
    exposed = 1 - ((7 - o) / 7) ** 3
    sat = exposed >= F(37, 64)
    ok40.append((k, float(o), round(float(exposed), 4), sat))
    say(f'   {k}: 降{float(o)}米 -> 露出{float(exposed):.4f}（37/64={37/64:.4f}） 满足={sat}')
sat_opts = [k for k, o, e, s in ok40 if s]
say('  满足“露出≥37/64”的选项:', sat_opts, '；其中最小降幅选项:', min(sat_opts, key=lambda k: ov[k]),
    '——C、D 也满足但非“至少”，A 不足，故“至少”唯一指向B')
record(40, 'B', [min(sat_opts, key=lambda k: ov[k])], '水下≤27/64 -> 相似比3/4 -> 降1.75；C/D满足但非最小', per_option=ok40)

# ================================================================ Q41
say('=' * 72)
say('第41题  工程换队')
a = F(1, 20)
b = (1 - 15 * a) / 10
t_switch = (F(2, 5) - 5 * a) / (a + b)
c = (1 - F(2, 5)) / (17 - 5 - t_switch) - a
say(f'  乙效率 {fstr(b)}，换队前合作 {fstr(t_switch)} 天（第{fstr(5 + t_switch)}天末），丙效率 {fstr(c)}，乙:丙 = {fstr(b / c)}')
assert 5 * a + t_switch * (a + b) + (17 - 5 - t_switch) * (a + c) == 1
ov = opt_values(41)
# 常见错法：把“完成2/5”当成计划工期的2/5、或忘记前5天甲单干
var = {}
# (i) 误把乙丙接替时刻当作第 5+2/5*10=9 天
ts = F(4)
done = 5 * a + ts * (a + b)
c1 = (1 - done) / (17 - 5 - ts) - a
var['误把换队设在乙合作10天的2/5处(第9天)'] = b / c1
# (ii) 忽略甲开工的前5天（认为甲乙从第1天合作）
b2 = (1 - 15 * a) / 15
t2 = F(2, 5) / (a + b2)
c2 = F(3, 5) / (17 - t2) - a
var['忽略前5天甲单干'] = b2 / c2 if c2 else None
for name, v in var.items():
    say(f'   {name}: 乙:丙={fstr(v)} -> 命中 {[k for k, o in ov.items() if o == v]}')
record(41, 'A', [k for k, o in ov.items() if o == b / c], '乙1/40，丙1/100，5:2')

# ================================================================ Q42
say('=' * 72)
say('第42题  轮班周期与闰年')
rows42 = []
for yr in range(2000, 2101):
    day = (datetime.date(yr, 3, 30) - datetime.date(yr, 1, 1)).days + 1
    zhang = (day - 1) % 12 + 1          # 1..10 上班, 11..12 休息
    chen = (day - 2) % 9 + 1            # 老陈 1月2日为第1天：1..8 上班, 9 休息
    rows42.append((yr, day, zhang, chen))
ok_years = [r for r in rows42 if r[2] == 6]
bad_years = [r for r in rows42 if r[2] != 6]
say('  满足“3月30日为老张休息后第6天”的年份数:', len(ok_years), '，全部为闰年:',
    all((y % 4 == 0 and y % 100 != 0) or y % 400 == 0 for y, *_ in ok_years))
say('  这些年份中老陈所处周期位置集合:', sorted({r[3] for r in ok_years}), '（8=上8休1的第8个工作日=休息前最后一天）')
say('  平年时老张位置集合:', sorted({r[2] for r in bad_years}), '；平年时老陈位置:', sorted({r[3] for r in bad_years}))
say('  干扰项映射：闰年但忘记老陈从1月2日起(用第90天)-> 90≡0(mod9) 休息=A；'
    '误按平年(第88天)-> 第7个工作日=D；')
say('  注意：误按平年且同时忘记1月2日起(用第89天) -> 89≡8 -> 恰得B（两错相消）。')
record(42, 'B', ['B'], '老张条件迫使闰年；老陈第89天≡8(mod 9)')

# ================================================================ Q43
say('=' * 72)
say('第43题  补考门槛概率')


def prob43(gate_rule):
    """gate_rule(first_pass_count) -> True 表示允许补考"""
    total = F(0)
    by = collections.defaultdict(F)
    for first in itertools.product([0, 1], repeat=4):
        k = sum(first)
        pf = F(4, 5) ** k * F(1, 5) ** (4 - k)
        if gate_rule(k):
            for re_ in itertools.product([0, 1], repeat=4 - k):
                m = sum(re_)
                if k + m == 3:
                    v = pf * F(2, 5) ** m * F(3, 5) ** (4 - k - m)
                    total += v
                    by[k] += v
        elif k == 3:
            total += pf
            by[k] += pf
    return total, dict(by)


ov = opt_values(43)
variants = {
    '正确：首次<2人取消补考': lambda k: k >= 2,
    '误读：首次≤2人也取消（“不足一半”含一半）': lambda k: k >= 3,
    '忽略门槛（所有人都可补考）': lambda k: True,
}
res43 = {}
for name, g in variants.items():
    p, by = prob43(g)
    near = min(ov, key=lambda k: abs(float(ov[k]) - float(p)))
    res43[name] = (fstr(p), float(p), near)
    say(f'   {name}: P={fstr(p)}={float(p):.6f} -> 最接近 {near}；按首次合格人数分解 { {k: float(v) for k, v in by.items()} }')
p_ok = prob43(lambda k: k >= 2)[0]
assert p_ok == F(4992, 15625)
forget_c21 = F(4) * F(4, 5) ** 3 * F(1, 5) * F(3, 5) + 6 * F(4, 5) ** 2 * F(1, 5) ** 2 * F(2, 5) * F(3, 5)
say(f'   错法：情形②漏乘C(2,1): {float(forget_c21):.6f} -> 最接近 {min(ov, key=lambda k: abs(float(ov[k]) - float(forget_c21)))}')
say(f'   捷径：每人最终合格率0.88，B(4,0.88)恰3人 = {4 * 0.88 ** 3 * 0.12:.6f}（即忽略门槛）-> 仍最接近D')
say('  门槛只在“把恰好一半也取消”这一误读下改变选项；K=1、K=0 的贡献合计仅约0.0076。')
# 题面原文（无“最终”）若理解为首次恰3人：
say(f'   若把“恰好3名合格”误解为首次恰3人: {float(4 * F(4, 5) ** 3 * F(1, 5)):.4f}（不在选项中）')
record(43, 'D', [k for k in ov if k == min(ov, key=lambda kk: abs(float(ov[kk]) - float(p_ok)))],
       'P=4992/15625=0.319488≈0.32', variants=res43)

# ================================================================ Q44
say('=' * 72)
say('第44题  舞蹈/乐器两集合')
sols44 = []
for both in range(0, 60):
    for dance_only in range(0, 60):
        if 10 * both != 17 * dance_only:
            continue
        for inst_only in range(0, 60):
            if both - inst_only != 3:
                continue
            T = both + dance_only + inst_only + 6
            if 40 < T < 50:
                sols44.append((dance_only, both, inst_only, 6, T))
say('  穷举（只舞, 两者, 只乐, 都不, 总）:', sols44)
assert sols44 == [(10, 17, 14, 6, 47)]
ov = opt_values(44)
say('  干扰项：41=17+10+14 漏加6；44=44k 漏算−3+6；46 无自然错法对应（或少算1人）')
record(44, 'D', [k for k, v in ov.items() if v == 47], '唯一 47')

# ================================================================ Q45
say('=' * 72)
say('第45题  7人分到甲乙丙')
alloc = [x for x in itertools.product('甲乙丙', repeat=7)
         if x.count('甲') == 3 and x.count('乙') >= 2 and x.count('丙') >= 1]
say('  穷举 3^7 种指派中满足条件的方案数:', len(alloc), '；按乙人数分布',
    dict(collections.Counter(x.count('乙') for x in alloc)))
ov = opt_values(45)
say('  干扰项：210=35×6 漏乙3人；700=350×2 重复计序；420=35×12 把乙2丙2按两组再排序')
record(45, 'B', [k for k, v in ov.items() if v == len(alloc)], '35×(6+4)=350')

# ================================================================ 题面一致性
say('=' * 72)
say('题面一致性：题目.jsonl 当前显示题面 vs selection.json（stem_override 或源题面）、选项 vs 源选项')
cons = {}
for n in range(31, 46):
    ok, ok_opts = check_stem_matches_selection(n)
    cons[n] = (ok, ok_opts)
say(' ', cons)
RESULT['display_consistency'] = {str(k): {'stem': v[0], 'options': v[1]} for k, v in cons.items()}
diff_src = {}
for n in range(31, 46):
    s_src = text_of(SEL[n]['source_question']['stem']) if SEL[n]['source_question']['stem'][0]['type'] == 'text' else '[table]'
    s_now = text_of(QS[n]['stem'])
    if s_src != s_now:
        diff_src[n] = {'source': s_src, 'now': s_now}
say('  与源题面不同的题号:', sorted(diff_src))
for n, d in diff_src.items():
    say(f'   第{n}题 源: {d["source"]}')
    say(f'   第{n}题 现: {d["now"]}')
RESULT['stem_changes_vs_source'] = {str(k): v for k, v in diff_src.items()}

say('=' * 72)
agree = all(v['agree'] for v in RESULT['questions'].values())
say('汇总：15题复核答案与编辑答案', '全部一致' if agree else '存在不一致')
(OUT / 'verify_q31_45_report.txt').write_text('\n'.join(LINES) + '\n', encoding='utf-8')
(OUT / 'verify_q31_45_result.json').write_text(json.dumps(RESULT, ensure_ascii=False, indent=1, default=str),
                                               encoding='utf-8')
