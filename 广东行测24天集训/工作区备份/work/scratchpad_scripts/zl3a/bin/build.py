"""Assemble ZL3A deliverables: out3/ZL3A/questions.jsonl, materials.jsonl, assets/q/*.png; new shared materials in out/zl_materials/.
python3 build.py [--write]"""
import sys, os, json, re, datetime, collections
sys.path.insert(0, os.path.dirname(__file__))
import pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
from render2 import render_material
from sel import SEL, GROUPS
from meta import M
from matspec import SPEC, locate
from mattext import TEXT, TR
from qparse import parse, qrec
from vlib import prec
import v_gk, v_gd, v_wx, v_adapt
from adapt import VAR
from levels import L
R = {}; R.update(v_gk.R); R.update(v_gd.R); R.update(v_wx.R); R.update(v_adapt.R)
W = '/home/user/work'; OUT = f'{W}/out3/ZL3A'; ZM = f'{W}/out/zl_materials'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl3a'
WRITE = '--write' in sys.argv
TODAY = datetime.date.today().isoformat()

# ---------- manual text fixes (garbled text layer, image options, truncations) ----------
FIX_OPT = {
 'SC2021H-96': {'A': '2013年', 'B': '2014年', 'C': '2015年', 'D': '2016年'},
 'SC2021H-99': {'A': '2017年', 'B': '2018年', 'C': '2019年', 'D': '2020年'},
 'SC2023-90': {'D': '2017-2020年'},
 'SD2023-76': {'A': '2019年', 'B': '2020年', 'C': '2021年', 'D': '2022年'},
 'SD2023-77': {'A': '6.1个百分点', 'B': '8.7个百分点', 'C': '18.9个百分点', 'D': '21.5个百分点'},
 'SD2023-78': {'A': '1年', 'B': '2年', 'C': '3年', 'D': '4年'},
 'SD2023-79': {'A': '大型企业', 'B': '中型企业', 'C': '小型企业', 'D': '微型企业'},
 'SD2023-80': {'D': '2020-2022年,大型企业和小型企业发明专利产业化率同比增速差距最大的年份是2022年'},
 'SD2023-86': {'A': '16.8%', 'B': '17.5%', 'C': '18.4%', 'D': '21.6%'},
 'SD2023-87': {'A': '2018年', 'B': '2019年', 'C': '2020年', 'D': '2021年'},
 'SD2023-88': {'A': '10~15个百分点', 'B': '16~21个百分点', 'C': '22~27个百分点', 'D': '28~33个百分点'},
 'SD2023-89': {'A': '0.6个百分点', 'B': '0.7个百分点', 'C': '0.8个百分点', 'D': '0.9个百分点'},
 'SZ20201-95': {'B': '2016—2019年,观影人次同比增长最快的一年,其电影票房及上映电影数均同比增长最快'},
 'ZJ2019A-123': {'D': '6'}, 'ZJ2019A-128': {'D': '4'},
 'ZJ2019A-125': {'A': '仅②', 'B': '仅②③', 'C': '仅①③', 'D': '①②③'},
 'ZJ2019A-129': {'A': '见图', 'B': '见图', 'C': '见图', 'D': '见图'},
}
ORIG_OPT = {'SD2023-88': {'A': '10%~15%', 'B': '16%~21%', 'C': '22%~27%', 'D': '28%~33%'}}
FIX_STEM = {
 'ZJ2019A-125': '能够从上述资料中推出的是:①2016年1~12月柴油内燃机累计完成功率 ②2017年第一季度内燃机累计销量的同比增速 ③2016年园林机械用内燃机累计销量所占比重',
 'SZ20201-100': '根据上表,下列说法正确的有( )个。(1)2011—2018年,中央财政支出占国家财政支出比重逐年降低 (2)2011—2018年,地方财政收入均超过6万亿元 (3)与2011年相比,2018年中央财政收入的增幅小于国家财政收入的增幅',
 'HB2022-114': '2016—2021年我国公共充电桩数量年均增长量约为（以2016年为基期）:',
}
ORIG_STEM = {'HB2022-114': '2016—2021年我国公共充电桩数量年均增长量约为:'}
STEM_SUFFIX = {'GK2024D-113': '（折线图见题图）', 'SZ20201-94': '（折线图见题图）', 'SC2023-90': '（折线图见题图）', 'ZJ2019A-129': '（四个选项均为折线图，见题图）'}
IMG_NEEDED = {'GK2024D-113', 'SZ20201-94', 'SC2023-90', 'ZJ2019A-129'}
QSEG = {'SC2023-90': [[25, 616.8, 760.0], [26, 66.0, 140.0]], 'SZ20201-100': [[12, 781.1, 841.9], [13, 20.0, 80.0]],
        'GD2014Z-95': [[9, 394.6, 443.0]], 'SZ20201-95': [[12, 229.3, 318.0]]}
# ---------- original answers: text-layer analyses (snippets saved by getans.py) and scanned GD analyses ----------
SCAN = {  # key: (file, page, answer, rate, yicuo)
 'GD2015X-96': ('xing-ce1/答案解析/2015年广东公务员考试《行测》真题县级卷答案及解析.pdf', '14', 'B', None, None),
 'GD2015X-97': ('xing-ce1/答案解析/2015年广东公务员考试《行测》真题县级卷答案及解析.pdf', '14', 'B', None, None),
 'GD2015X-98': ('xing-ce1/答案解析/2015年广东公务员考试《行测》真题县级卷答案及解析.pdf', '14', 'D', None, None),
 'GD2015X-99': ('xing-ce1/答案解析/2015年广东公务员考试《行测》真题县级卷答案及解析.pdf', '14', 'C', None, None),
 'GD2015X-100': ('xing-ce1/答案解析/2015年广东公务员考试《行测》真题县级卷答案及解析.pdf', '14', 'C', None, None),
 'GD2016Z-91': ('xing-ce1/答案解析/2016年广东公务员考试《行测》真题（乡镇卷）答案及解析.pdf', '14', 'A', None, None),
 'GD2016Z-92': ('xing-ce1/答案解析/2016年广东公务员考试《行测》真题（乡镇卷）答案及解析.pdf', '14-15', 'B', None, None),
 'GD2016Z-93': ('xing-ce1/答案解析/2016年广东公务员考试《行测》真题（乡镇卷）答案及解析.pdf', '15', 'B', None, None),
 'GD2016Z-95': ('xing-ce1/答案解析/2016年广东公务员考试《行测》真题（乡镇卷）答案及解析.pdf', '15', 'A', None, None),
 'GD2014Z-93': ('xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf', '19', 'B', '75%', 'C'),
 'GD2014Z-94': ('xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf', '19', 'A', '87%', 'B'),
 'GD2014Z-95': ('xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf', '19-20', 'D', '26%', 'C'),
 'GD2014Z-97': ('xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf', '20', 'B', '86%', 'C'),
 'GD2014Z-98': ('xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf', '20', 'C', '83%', 'B'),
 'GD2014Z-99': ('xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf', '20', 'B', '70%', 'C'),
 'GD2014Z-100': ('xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf', '20', 'D', '56%', 'C'),
}
def official(tag, q, key):
    if key in SCAN:
        f, pg, a, rate, yc = SCAN[key]
        return f, pg, a, (dict(正确率=rate, 易错项=yc) if rate else None), '扫描件，渲染第%s页图像读出' % pg
    fn = f'{SP}/v/ans/{tag}_{q}.txt'
    t = open(fn).read()
    f, pgl, seg = t.split('\n', 2)
    pg = pgl.replace('page ', '')
    a = re.findall(r'(?:正确答案|答案)\s*(?:为|是|:|：)?\s*[【\[]?\s*([A-D])|故(?:本题)?选\s*([A-D])|选择\s*([A-D])\s*选项', seg)
    a = [x for tt in a for x in tt if x]
    assert a and len(set(a)) == 1, (key, a)
    rate = re.search(r'正确率\s*[:：]?\s*(\d+)\s*%', seg); yc = re.search(r'易错项\s*[:：]?\s*([A-D])', seg)
    st = dict(正确率=rate.group(1) + '%', 易错项=yc.group(1) if yc else None) if rate else None
    return f, pg, a[0], st, '文字层'

def qimage_segs(key, x):
    return QSEG.get(key, x['segs'])

os.makedirs(f'{OUT}/assets/q', exist_ok=True)
rows = []; uses = collections.defaultdict(list); n = 0
for g, mats in SEL.items():
    order = 0
    for mid, tag, qs in mats:
        paper = tag.replace('_xc', '')
        for q in qs:
            n += 1; order += 1
            variant = isinstance(q, str) and q.endswith('V')
            qno = int(str(q).rstrip('V'))
            key = f'{paper}-{q}'
            x = qrec(tag, qno)
            stem, opts = parse(x['text'], qno)
            if variant:
                stem, opts = VAR[key]['stem'], dict(VAR[key]['options'])
            if key in FIX_STEM: stem = FIX_STEM[key]
            for kk, vv in FIX_OPT.get(key, {}).items(): opts[kk] = vv
            stem += STEM_SUFFIX.get(key, '')
            assert sorted(opts) == ['A', 'B', 'C', 'D'] and all(opts.values()), (key, opts)
            v = R[key]; mm = VAR[key] if variant else M[key]
            chk = v['ans']; assert chk in ('A', 'B', 'C', 'D'), (key, chk)
            if variant:
                af, ap, src, stats, how = None, None, None, None, None
            else:
                af, ap, src, stats, how = official(tag, qno, key)
                assert src == chk, (key, src, chk)
            if af and af.startswith('/home/user/'): af = af[len('/home/user/'):]
            qimg = None
            if not variant:
                qimg = f'assets/q/{tag}_q{qno}.png'
                if WRITE:
                    im, _ = render_material(x['file'], qimage_segs(key, x), dpi=200)
                    im.save(f'{OUT}/{qimg}')
            vnote = '网友回忆版' if '网友回忆' in x['file'] else ''
            flags = list(mm['flags'])
            if key in SCAN: flags.append('解析为扫描件')
            notes = '核算（Python，按材料原数）：' + v['calc'].rstrip('。') + '。'
            if variant:
                notes = ('改编说明：' + VAR[key]['why'] + (' 设问方式借鉴' + VAR[key]['mock'] + '，只借设问方式，材料与数据全部来自原真题。' if VAR[key]['mock'] else '')
                         + ' 独立重解与唯一性（Python，按材料原数逐项验算）：' + v['calc'])
            else:
                notes += f'与原解析答案{src}一致（解析第{ap}页，{how}）。'
            extra = {
             'SD2023-88': '原题选项写作“10%~15%”等，所求是两个比重之差，单位应为百分点，按审核要求改为“个百分点”，原选项存original_options；答案D不变。',
             'HB2022-114': '原题“2016—2021年……年均增长量”未写基期，按2015年为基期得18.17（恰为C），按2016年为基期得19.94（D，原解析读法）；按审核要求在题干明示“以2016年为基期”，原题干存original_stem。本题原属第7个主轴（跨期年均）候选，因整篇材料连做收入本日。',
             'SD2023-76': '“产业化率同比增幅”按增长率或按百分点差理解，答案都是2020年，无需改题。',
             'SD2023-78': '本题“同比增速”只能按产业化率本身的增长率理解（按百分点差则没有一年超过2.7，无对应选项），答案唯一。',
             'JS2022A-135': '原解析A项理由用了2020年7月日均53.1万吨作比较（表中无2021年7月日均），理由有误；按2021年7月产量1686万吨与3月、5月月产量比较，A项仍不成立，答案C不变。',
             'GD2016Z-91': '表中年份为2014→2010倒序排列，题面照录。',
             'GK2015D-130': '原题干作“能够给从上述资料中推出的是”，照录。',
             'GK2015D-118': '材料“机械行业实现主营业务收入3886元”原卷漏“亿”，照录，不影响本题。',
             'JS2021A-131': '本材料卷面误标“(材料3)”（与上一则重号），材料ID按资料部分顺序记为第4则。',
            }.get(key)
            if extra: notes += ' ' + extra
            rec = dict(
                id=f'ZL3A-{n:03d}', module='资料', day='D08', group=g, group_title=GROUPS[g], topic=mm['topic'], order=order,
                source=dict(paper=paper, file=x['file'], page=x['segs'][0][0] + 1, qno=qno, ans_file=af, ans_page=ap, version_note=vnote),
                claim_key=None if variant else key, done_status='已做情况未知', stem=stem, options=opts,
                material_or_article=mid, assets=[qimg] if (key in IMG_NEEDED and qimg) else [], q_image=qimg,
                source_answer=src, checked_answer=chk, brief_solution=mm['brief_solution'], precision_need=mm['precision_need'],
                selection_value=mm['selection_value'], variant_of=VAR[key]['mother'] if variant else None,
                check_status='已核验-改编' if variant else '已核验', flags=flags, notes=notes,
                skill_tags=mm['skill_tags'], answer_stats=stats, intensity=L[key][0], difficulty=L[key][1])
            if key in ORIG_STEM: rec['original_stem'] = ORIG_STEM[key]
            if key in ORIG_OPT: rec['original_options'] = ORIG_OPT[key]
            rows.append(rec)
            uses[mid].append(f"{rec['id']} {key}")

# ---------- materials ----------
mats = []
for mid, s in SPEC.items():
    tag = s['tag']; paper = tag.replace('_xc', '')
    f = None
    for g, ms in SEL.items():
        for m_, t_, qs_ in ms:
            if m_ == mid: f = qrec(t_, int(str(qs_[0]).rstrip('V')))['file']
    segs = locate(mid)
    vnote = '网友回忆版' if '网友回忆' in f else ''
    notes = [f'建档：ZL3A（{TODAY}）。图片按原页坐标截取（200dpi），只遮去页码、页眉考试名、店铺/公众号/水印广告行并压缩大段空白，不改动内容像素。原卷材料标号：{s["label"]}。',
             'ZL3A 使用本材料的题：' + '；'.join(uses[mid])]
    if mid == 'ZLM-GK2015D-2': notes.append('原卷“机械行业实现主营业务收入3886元”漏“亿”字，照录。')
    if mid == 'ZLM-JS2021A-4': notes.append('卷面把本则与上一则（ZLM-JS2021A-3）都标作“(材料3)”，ID按资料部分顺序记为第4则。')
    if mid == 'ZLM-GK2014-4': notes.append('表2中2008年清洁能源上网电量4146与水电、核电、新能源之和4161不符，原卷如此，不影响所选各题。')
    rec = dict(mid=mid, source=dict(paper=paper, file=f, pages=sorted({sg[0] + 1 for sg in segs}),
                                    segs_0based=[[sg[0], round(sg[1], 1), round(sg[2], 1)] for sg in segs], version_note=vnote),
               text=TEXT[mid], assets=[f'zl_materials/{mid}/{mid}.png'], transcription=TR.get(mid), notes=' '.join(notes))
    if WRITE:
        os.makedirs(f'{ZM}/{mid}', exist_ok=True)
        mj = f'{ZM}/{mid}/material.json'
        if os.path.exists(mj) and 'ZL3A' not in json.load(open(mj)).get('notes', ''):
            raise SystemExit('existing material by another editor: ' + mid)
        im, _ = render_material(f, segs, dpi=200)
        im.save(f'{ZM}/{mid}/{mid}.png')
        json.dump(rec, open(mj, 'w'), ensure_ascii=False, indent=1)
    mats.append(rec)
used = {r['material_or_article'] for r in rows}
assert used == {m['mid'] for m in mats}, used ^ {m['mid'] for m in mats}
if WRITE:
    with open(f'{OUT}/questions.jsonl', 'w') as fo:
        for r in rows: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(f'{OUT}/materials.jsonl', 'w') as fo:
        for r in mats: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
print('questions', len(rows), 'materials', len(mats))
print('answers', collections.Counter(r['checked_answer'] for r in rows))
for g in GROUPS:
    rr = [r for r in rows if r['group'] == g]
    print(g, len(rr), ''.join(r['checked_answer'] for r in rr), dict(collections.Counter(r['precision_need'] for r in rr)))
print('precision', collections.Counter(r['precision_need'] for r in rows))
# consistency of precision labels with margins
for r in rows:
    k_ = r['claim_key'] or (r['variant_of'] + 'V')
    mg = R[k_]['margin'] if k_ in R else None
    if mg is not None and mg >= 0 and prec(mg) != r['precision_need']:
        print('  prec-check', r['id'], r['claim_key'] or r['variant_of'], 'label', r['precision_need'], 'margin', mg, '->', prec(mg))
