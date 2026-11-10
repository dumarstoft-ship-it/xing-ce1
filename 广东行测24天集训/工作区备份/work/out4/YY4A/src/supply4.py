# -*- coding: utf-8 -*-
"""Remaining supply after round 4 (D10-D12), for the handover. Read-only.
  GD 选词 / 语句 of 2017-2023 still unregistered (the list is the round-3 handover list minus this round's 8 items;
  every key is checked against the claim registry here - a key that is no longer FREE is reported);
  HTML articles not yet used, by paper and kind, with the 语句-rich ones listed.
Answers / rates in GD_LEFT were read from the analysis pages during the 110-dpi survey of this round (2022-2023 from
answers/*.json); whoever uses an item must re-read its answer line at 200 dpi, as was done for the 8 delivered items.
Run: python3 supply4.py   (appends to checks.txt unless --no-log)"""
import json, re, subprocess, sys, collections

OUT = '/home/user/work/out4/YY4A'
CL = '/home/user/work/tools/claim.py'
HTML_PATH = '/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'

# key: (segment, kind, other keys of the same item, answer as read, rate, note for scheduling)
GD_LEFT = {
 'GD2017-1':  ('2017-18', '实词', [], 'D 决心 勇气', None, '反腐题材，与 D11 的 GD2020X-4 同题材，不排相邻日'),
 'GD2017-6':  ('2017-18', '实词', [], 'C 坚实 准确', None, '与 GD2019X-3 都含“坚实”，不同日、不相邻；D10 的 GD2019X-6 题干有“坚实基础”'),
 'GD2017-7':  ('2017-18', '实词', [], 'B 持之以恒', None, ''),
 'GD2017-9':  ('2017-18', '实词', [], 'D 可有可无 义不容辞', None, ''),
 'GD2017-10': ('2017-18', '实词', [], 'A 应对 耽误 遏制', None, '“遏制”是 D01 GD2018-4 的答案（同考遏制/遏止），宜放 D20 以后'),
 'GD2018-1':  ('2017-18', '实词', [], 'C 章程 体现', None, 'D12 的 GD2018-5 题干有“体现民情”'),
 'GD2018-2':  ('2017-18', '实词', [], 'A 迸发 日新月异', None, '“迸发”是 D02 GD2014X-16 的答案；与 GD2022X-4 都含“日新月异”'),
 'GD2018-3':  ('2017-18', '实词', [], 'C 推动 增强 实现', None, ''),
 'GD2018-6':  ('2017-18', '实词', [], 'A 因地制宜 扩大 提高', None, '“因地制宜”是 D12 GD2020Z-1 的答案，不排 D13，建议隔5天以上'),
 'GD2019X-3': ('2019-21', '实词', ['GD2019Z-2'], 'A 坚实 坚定', None, '与 GD2019Z-2 同文段（一双空、一单空，dup_group 未合并，两键都要登记）；与 GD2017-6 都含“坚实”'),
 'GD2019X-4': ('2019-21', '实词', [], 'D 如火如荼', None, '与 GD2021X-1 同答案；与 D06 的 GD2019X-8 同出一篇文章'),
 'GD2019X-7': ('2019-21', '实词', [], 'B 战乱 贫困', None, ''),
 'GD2019X-9': ('2019-21', '实词', ['GD2019Z-3'], 'B 整治', None, ''),
 'GD2019X-10': ('2019-21', '实词', ['GD2019Z-4'], 'A 循序渐进 一蹴而就', None, '“一蹴而就”在 D02 的题干里出现过'),
 'GD2020X-1': ('2019-21', '实词', [], 'B 百折不挠', '88%（易错C）', ''),
 'GD2021Z-5': ('2019-21', '实词', ['GD2021X-3'], 'A 一脉相承 诠释', '84%（易错C）', '“诠释”是 D08 GD2020Z-4 的答案；与 D11 GD2020X-4 共用选项词“一脉相承”“相辅相成”；GD2021X 不在 index，GD2021X-3 要手工补登；宜放 D18 以后'),
 'GD2021X-1': ('2019-21', '实词', [], 'B 如火如荼', '88%（易错D）', 'GD2021X 不在 index，按扫描页转录；与 GD2019X-4 同答案'),
 'GD2021X-5': ('2019-21', '实词', [], 'A 前赴后继 殚精竭虑', '87%（易错B）', 'GD2021X 不在 index，按扫描页转录'),
 'GD2022X-4': ('2022-23', '实词', ['GD2022Z-1'], 'A 日新月异 酸甜苦辣', None, '与 GD2018-2 都含“日新月异”'),
 'GD2022Z-2': ('2022-23', '实词', [], 'B 感悟', None, ''),
 'GD2023X-17': ('2022-23', '实词', ['GD2023Z-3'], 'A 融洽 凝聚', None, '“凝聚”是 D06 GD2020Z-3 的答案'),
 'GD2023Z-1': ('2022-23', '实词', [], 'D 乘势而上', None, ''),
 'GD2019X-2': ('关联词', '关联词', ['GD2019Z-1'], 'A 而 也', None, '并列'),
 'GD2020Z-2': ('关联词', '关联词', [], 'A 不仅 更', '93%（易错B）', '与 D07 GD2020X-2 答案相同（不仅 更），放远'),
 'GD2021Z-2': ('关联词', '关联词', [], 'D 不仅 也', '97%（易错C）', '递进，与 2020Z-2、2021X-4 同类，三道错开'),
 'GD2021X-4': ('关联词', '关联词', [], 'D 不仅 而且', '94%（易错C）', '递进；GD2021X 不在 index，按扫描页转录'),
 'GD2022Z-3': ('关联词', '关联词', [], 'D 尽管 但是', None, '转折'),
 'GD2023X-20': ('关联词', '关联词', ['GD2023Z-5'], 'B 既 也 更', None, '递进'),
 'GD2019X-12': ('语句', '语句', [], 'B（葆有坚持不懈的精神，蓄积水滴石穿的韧劲）', None, '题干含“久久为功”“锲而不舍”，答案句含“水滴石穿”，都与 D10 的 GD2023X-16 相关：三道语句里这道最后用（D22/D23），D13/D14 先用另两道'),
 'GD2020X-6': ('语句', '语句', [], 'D（千磨万击还坚劲）', '75%（易错C）', ''),
 'GD2022Z-6': ('语句', '语句', [], 'C（源浚者流长，根深者叶茂）', None, '段中名句；answers/GD2022Z.json'),
}

# 南方日报 non-常识 articles: result of this round's read-through (answerable from the blank's paragraph / one context paragraph)
NF_STATUS = {
 'nf20260311_10164827': '可用；q4 建议加第6段（“尽力而为、量力而行”），该段无他题答案',
 'nf20260414_10167858': '可用，不需上下文',
 'nf20260508_10169767': '可用，不需上下文；q1 答案“连续性”与 D11 岭南文化篇 q4 相同，不排 D11 相邻日，隔开几天；源段有零宽字符 U+200C',
 'nf20260331_10166714': '可用，不需上下文；0 语句（当天另两篇要凑足 6 道语句）',
 'nf20260824_10179433': '可用，不需上下文',
 'nf20260914_10181250': '可用，不需上下文',
 'nf20260914_10181304': '可用，不需上下文',
 'nf20251201_10155013': '可用；q3 加第11段（无他题答案）',
 'nf20260518_10170615': '可用；q2 加第7段（无他题答案）',
 'nf20260914_10181306': '可用；q5 加第9段（“高层互访已实现常态化”，无他题答案）',
 'nf20251203_10155311': '可用；q3 加第28段（无他题答案）',
 'nf20260129_10161789': '可用；q1 加第2段（“第一”清单，无他题答案）',
 'nf20251202_10155140': '可用；q2 所在段只有引语一句，加第10段（无他题答案）',
 'nf20260225_10163813': '不合条件：q2 的依据在第38段，而该段含答案“主干”；且 0 语句、76 段',
}

# 人民日报 non-常识 articles with 3+ 语句 (the scarce kind: after this round the 南方日报 articles left carry at most one
# 语句 each, so a day without a GD 语句 item needs one of these): result of this round's read-through.
RM3_STATUS = {
 '20260817_30175302': '可用，五题都只看本段（本轮选过又撤下，登记已释放）；q5 答案 大局/准头/定力：当天前面的题干（含片段）不能有“定力”“大局”；q2 的干扰项“一把钥匙开一把锁”与 D10 基层减负篇 q3 相同',
 '20260826_30177077': '可用，不需上下文；q3 答案“防火墙”见于《“管得好”的治理智慧》（20260112_30131269）第2段题干，两篇不同日',
 '20260921_30182219': '可用，不需上下文；q1 答案“犯其难方能图其远”，YY4B 排在 D12 的 GD2016X-30 文段首句是“犯其至难方能图其至远”，远离 D12',
 '20260821_30176330': '可用，不需上下文；0选4语，可配南方日报 nf20260331_10166714（4选0语）',
 '20260205_30138627': '可用，不需上下文；5选3语共8题，q3、q4 同段互相遮蔽',
 '20260728_30171397': '可用，不需上下文；1选3语',
 '20260805_30173157': '可用；q1（一股清流）的依据（团播的低俗问题）在第7、9段，单看本段偏难，第9段是 q5 所在段，不宜作上下文',
 '20260410_30150275': '可用；q6 加第12段（q5 所在段，q5 空缺以“另题”遮蔽）；q1 的依据在下一段，但下一段有“重返线下”，加了等于给答案，只用本段',
 '20260518_30157380': '可用；q4 加第11段',
 '20251215_30120393': '可用；q1 加第3段（南京办赛的三条做法；该段无他题答案）',
 '20251216_30122646': '勉强可用：q1 所在段只有空缺一句（设问），加第4段（紧跟的回答之一，无他题答案）后可答；第5段是 q2 所在段，不加',
}


def main():
    log = []
    by = collections.defaultdict(list)
    notfree = []
    for key, (seg, kind, others, ans, rate, note) in GD_LEFT.items():
        for k in [key] + others:
            r = subprocess.run([sys.executable, CL, 'check', k], capture_output=True, text=True).stdout.strip()
            if r != 'FREE':
                notfree.append((k, r))
        by[seg].append(key)
    log.append('[supply] GD 2017-2023 still unregistered after round 4 (every key and its twin checked FREE in the claim registry'
               + ('' if not notfree else f'; NOT FREE: {notfree}') + '):')
    for seg in ('2017-18', '2019-21', '2022-23', '关联词', '语句'):
        log.append(f'   {seg}: {len(by[seg])}  ' + '、'.join(by[seg]))
        for key in by[seg]:
            _, _, others, ans, rate, note = GD_LEFT[key]
            log.append(f"      {key}" + (f"（＝{'、'.join(others)}）" if others else '') + f"：{ans or '答案待读'}" + (f"，正确率{rate}" if rate else '') + (f"；{note}" if note else ''))
    n_x = sum(len(by[s]) for s in ('2017-18', '2019-21', '2022-23', '关联词'))
    log.append(f'   选词 {n_x}（D13-D24 共12天，平均每天 {n_x / 12:.2f} 道）；语句 {len(by["语句"])}')
    # ---- HTML
    raw = open(HTML_PATH, encoding='utf-8').read()
    D = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S).group(1))
    used = set()
    for l in open('/home/user/work/out/claims.jsonl'):
        if l.strip():
            c = json.loads(l)
            if c['key'].startswith('HTML:'):
                used.add(c['key'].split(':')[1])
    left = [a for a in D if a['id'] not in used]
    log.append(f'[supply] HTML articles: {len(D)} in the file, {len(used)} used or registered, {len(left)} left')
    for src in ('人民日报', '南方日报'):
        for cs in (False, True):
            aa = [a for a in left if a['src'] == src and (a['kind'] == 'cs') == cs]
            kc = collections.Counter(q['kind'] for a in aa for q in a['q'])
            log.append(f"   {src} {'常识类' if cs else '非常识类'}: {len(aa)} 篇；选词 {kc['选词填空']}、语句 {kc['语句填空']}")
    rich = [a for a in left if a['kind'] != 'cs' and a['src'] == '人民日报' and sum(1 for q in a['q'] if q['kind'] == '语句填空') >= 3]
    log.append(f'   人民日报非常识类中语句≥3的还有 {len(rich)} 篇（D13-D24 不放广东语句的9天，每天要1篇）:')
    for a in rich:
        kc = collections.Counter(q['kind'] for q in a['q'])
        log.append(f"      {a['id']} {a['col']} {a['date']} {kc['选词填空']}选{kc['语句填空']}语：{RM3_STATUS.get(a['id'], '未通读')}")
    assert set(RM3_STATUS) == {a['id'] for a in rich}, (set(RM3_STATUS) ^ {a['id'] for a in rich})
    nf = [a for a in left if a['src'] == '南方日报' and a['kind'] != 'cs']
    log.append(f'   南方日报非常识类 {len(nf)} 篇（D13-D24 每天1篇，需12篇）:')
    for a in nf:
        kc = collections.Counter(q['kind'] for q in a['q'])
        log.append(f"      {a['id']} {a['col']} {a['date']} {kc['选词填空']}选{kc['语句填空']}语：{NF_STATUS.get(a['id'], '未通读')}")
    assert set(NF_STATUS) == {a['id'] for a in nf}, (set(NF_STATUS) ^ {a['id'] for a in nf})
    print('\n'.join(log))
    if '--no-log' not in sys.argv:
        open(f'{OUT}/checks.txt', 'a').write('\n'.join(log) + '\n')


if __name__ == '__main__':
    main()
