"""ZL4A shared registry: every question (original or adaptation) is registered here together with its
independent Python re-solution, so verification and editorial metadata stay in one place.
Q[key] = record. Keys: '<paper>-<qno>' for originals, '<paper>-<qno>V' / 'V2' for adaptations (mother = paper-qno)."""
import itertools, random, math
from vlib import gr, inc, base, f, nearest, interval, rank_margin, prec, INF

Q = {}
ORDER = []
I1, I2, IM = '一步', '两步', '多步或多口径'

def one(opts_true):
    """letter -> bool; returns the single true letter (asserts uniqueness)."""
    t = [k for k, v in opts_true.items() if v]
    assert len(t) == 1, opts_true
    return t[0]

def robust(fn, inputs, steps, expect, n=3000, seed=7):
    """Perturbation test for rounded data. fn(**inputs)->letter. steps: name->half-width of rounding
    (e.g. 0.05 for a number printed to one decimal). Checks all corners (if <=12 perturbed inputs) plus random
    samples; returns True when the answer letter never changes."""
    names = [k for k in steps if steps[k]]
    rnd = random.Random(seed)
    cases = []
    if len(names) <= 12:
        for signs in itertools.product((-1, 1), repeat=len(names)):
            cases.append({k: inputs[k] + s * steps[k] for k, s in zip(names, signs)})
    for _ in range(n):
        cases.append({k: inputs[k] + rnd.uniform(-1, 1) * steps[k] for k in names})
    for c in cases:
        d = dict(inputs); d.update(c)
        if fn(**d) != expect:
            return False
    return True

def O(key, ref, ans, calc, margin, topic, tags, precision, brief, value, inten, diff, flags=None, note=None,
      stem=None, options=None, orig_stem=None, orig_options=None, stem_suffix=None, need_img=False, stats=None, noref=False):
    """Register an original question. ref = answer in the original analysis (None when no analysis exists)."""
    assert key not in Q, key
    assert ans in ('A', 'B', 'C', 'D'), (key, ans)
    if not noref:
        assert ref == ans, ('MISMATCH with reference answer', key, ref, ans)
    Q[key] = dict(kind='orig', key=key, ref=ref, ans=ans, calc=calc, margin=margin, topic=topic, skill_tags=tags,
                  precision_need=precision, brief_solution=brief, selection_value=value, intensity=inten, difficulty=diff,
                  flags=list(flags or []), note=note, stem=stem, options=options, original_stem=orig_stem,
                  original_options=orig_options, stem_suffix=stem_suffix, need_img=need_img, stats=stats, noref=noref)
    ORDER.append(key)

def V(key, mother, stem, options, ans, calc, margin, topic, tags, precision, brief, value, why, mock, inten, diff,
      flags=None, robust_note=None, note=None):
    """Register an adaptation built on a real-exam material. ans must come from one()/nearest()/interval()."""
    assert key not in Q, key
    assert ans in ('A', 'B', 'C', 'D'), (key, ans)
    assert sorted(options) == ['A', 'B', 'C', 'D']
    Q[key] = dict(kind='var', key=key, mother=mother, stem=stem, options=options, ans=ans, calc=calc, margin=margin,
                  topic=topic, skill_tags=tags, precision_need=precision, brief_solution=brief, selection_value=value,
                  why=why, mock=mock, intensity=inten, difficulty=diff, flags=list(flags or []) + ['改编'],
                  robust_note=robust_note, note=note)
    ORDER.append(key)

# ---- 粉笔模考卷：只借设问方式（不收模考题与模考材料）----
def M(season, level='行政执法类'):
    return f'粉笔《2027年国考第{season}季行测模考大赛（{level}）》'
MOCK = {
 'gx1':  M('一') + '资料题“2022年，全国煤货运量对铁路主要货物运输量的增长贡献率约为”（增量占整体增量的比重）',
 'gx6':  M('六') + '资料题“2023年全国快递业务量前10位的城市，其快递业务量对全国快递业务量的增长贡献率约为”（多个部分合计的增长贡献率）',
 'gx34': M('三十四') + '资料题“若2024年云南糖料产量同比增速为6.3%，则2024年云南糖料产量对我国糖料总产量的增长贡献率约为”（假设条件下的贡献率）',
 'ld28': M('二十八') + '资料题“2024年，200家重点联系企业完成出口交货值拉动全国通用机械行业规模以上企业完成出口交货值增长约”（拉动增长几个百分点）',
 'js31': M('三十一') + '资料题“表中所列五类水果中，2022年、2023年其产量占H省水果总产量的比重均同比上升的有几类”（比重升降的多对象计数）',
 'js28': M('二十八') + '资料题“……占全国的比重均高于上年的地区有多少个”（两个指标的比重同时比较并计数）',
 'js7':  M('七') + '资料题“我国电动汽车市场锂电装机总量中各细分市场的占比同比、环比均上升的有几类”（双条件比重升降计数）',
 'lj37': M('三十七', '地市级') + '资料题“2023年，全国政府卫生支出占GDP的比重约为”（比重的链式换算：部分占部分）',
 'lj36': M('三十六', '副省级') + '资料题“2023年末，J省规上国有控股文化企业全年实现营业收入占全部文化产业的比重约为”（比重的链式换算）',
 'zl22': M('二十二') + '资料题“最能准确反映2024年前三季度……第一产业、第二产业、第三产业增加值同比增量占比情况的是”（增量的构成）',
 'zl14': M('十四') + '资料题“以下饼图最能准确反映2024年全国谷物中……产量的同比增量占比关系的是”（增量的构成）',
 'dy22': M('二十二') + '资料题“2024年9月，……固定资产投资额占全市固定资产投资额的比重高于2024年前三季度的是”（当期比重与累计比重比较）',
 'dy18': M('十八') + '资料题“2023年12月出口额占该产品全年出口额的比重高于上年同期水平的有几种”（当月占全年比重的两期比较）',
 'wt17': M('十七') + '资料题“假设……线上渠道、线下渠道市场规模均保持2021年同比增长量不变，则到哪一年……线下渠道市场规模所占比重降到50%以下”（假设外推下的比重）',
 'cz17': M('十七') + '资料题“……线下渠道市场规模占比比线上渠道高20个百分点以上的年份有几个”（两个比重之差逐年判断计数）',
 'rc13': M('十三') + '资料题“截至2023年底，中国共产党党员中大专及以上学历的男党员人数占比至少约为”（比重的容斥极值）',
 'bb10': M('十') + '资料题“2021年末，南昌市60岁及以上人口中，65岁及以上人口的占比在以下哪项范围内”（部分占部分）',
 'gn4':  M('四') + '资料题“2022年G省实现地区生产总值中，第二产业增加值所占比重较2020年约”（隔年比重变化）',
 'bc38': M('三十八') + '资料题“2022年，我国秋粮产量占粮食产量的比重比夏粮约”（两个部分的比重之差）',
 'bc40': M('四十') + '资料题“2024年1月，我国羔羊肉进口量中冻整头及半头的占比较绵羊肉进口量中冻整头及半头的占比约高”（两个不同整体下的比重之差）',
 'pj36': M('三十六', '副省级') + '资料题“……平均每个规模以上工业企业利润总额较上年约”（平均数的两期变化）',
 'jd37': M('三十七', '地市级') + '资料题“若……均价同比下降9.0%，则同期……销售额同比下降约”（假设条件下的增速叠加）',
 'zn2':  M('二') + '资料题“……日均供水量最高的年份，其日均供水量占全国的比重比上年约提高了”（先定位对象再求两期比重差）',
 'dy13': M('十三') + '资料题“2024年1-5月全国同城及异地快递业务量中，5月当月业务量占比约为”（当月占累计的比重）',
}
