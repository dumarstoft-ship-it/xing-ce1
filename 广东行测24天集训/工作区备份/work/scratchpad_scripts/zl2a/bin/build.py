"""Assemble ZL2A deliverables: questions.jsonl, materials.jsonl, assets/q/*.png, and new shared materials in zl_materials/."""
import sys, os, json, re, unicodedata, datetime
sys.path.insert(0, os.path.dirname(__file__))
from sel import SEL, GROUPS
from meta import M
from matspec import NEW, REUSE
from mattext import TEXT, TR, IMGPCT, PCT_IMG
from render2 import render_material
W = '/home/user/work'; OUT = f'{W}/out2/ZL2A'; ZM = f'{W}/out/zl_materials'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2a'
WRITE = '--write' in sys.argv
R = json.load(open(f'{SP}/v/verify.json'))
OFF = json.load(open(f'{SP}/v/official.json'))
os.makedirs(f'{OUT}/assets/q', exist_ok=True)

CJK = r'　-〿一-鿿＀-￯“”‘’（）《》【】'
def despace(s):
    s = re.sub(r'(?<=[%s])[ \t]+' % CJK, '', s)
    s = re.sub(r'[ \t]+(?=[%s])' % CJK, '', s)
    s = re.sub(r'(?<=\d)[ \t]+(?=[%s])' % CJK, '', s)
    s = re.sub(r'(?<=[%s])[ \t]+(?=\d)' % CJK, '', s)
    return re.sub(r'\s+', ' ', s).strip()
JUNK = re.compile(r'(·\s*本试卷由粉笔用户.*?生成|\d{4}年[^\n]*?网友回忆版\)|【认准淘宝店铺[^】]*】[^\n]*|淘宝:[^\n]*|TB:Seeyee[^\n]*|获取试卷更新[^\n]*|免费获取更多考公资料[^\n]*|第\s*\d+\s*页\s*,?\s*共\s*\d+\s*页|^\s*-\s*\d+\s*-\s*$)', re.M)
def parse(text, qno):
    t = unicodedata.normalize('NFKC', text)
    t = JUNK.sub('', t)
    t = re.sub(r'^\s*' + str(qno) + r'\s*[\.、．]?\s*', '', t.strip())
    t = re.sub(r'\(单选题\)', '', t)
    m = re.split(r'(?:(?<=\s)|^|(?<=[。?？:：\)）]))([ABCD])\s*[\.、．]\s*', t)
    stem = despace(re.sub(r'\s*\n\s*', '', m[0])); opts = {}
    for i in range(1, len(m) - 1, 2):
        opts[m[i]] = despace(m[i + 1])
    return stem, opts
# manual fixes: trailing next-material text, image options, garbled layouts
FIX_OPT = {
 'SD2021-80': {'D': '2015—2019年间,4G基站数量同比增速和增量最大的年份不是同一个'},
 'SD2020-80': {'D': '电气设备行业销售增量超过3000台'},
 'ZJ2020B-90': {'D': '1—4月,限额以上商品销售额占批发和零售业商品销售总额的比重较上年同期有所提升'},
 'SZ20201-90': {'D': '2018年,该市一般公共预算收入中,非税收收入同比负增长'},
 'GDXD2020ZH-98': {'D': '5.7'},
 'SD2022-87': {'A': '见图', 'B': '见图', 'C': '见图', 'D': '见图'},
 'ZJ2025A-115': {'A': '见图', 'B': '见图', 'C': '见图', 'D': '见图'},
 'GDXD2020ZH-91': {'A': '8.7%', 'B': '19.7%', 'C': '27.3%', 'D': '37.4%'},
 'GK2024F-119': {'A': '不到2%', 'B': '超过9%', 'C': '2%~5%之间', 'D': '5%~9%之间'},
}
FIX_STEM_SUFFIX = {'GK2023F-120': '（折线图见题图）', 'GK2020D-124': '（折线图见题图）', 'GK2024D-130': '（折线图见题图）'}
IMG_NEEDED = {'SD2022-87', 'ZJ2025A-115', 'GK2023F-120', 'GK2020D-124', 'GK2024D-130', 'GDXD2020ZH-91'}
ANS_FILE = {
 'GD2017': 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
 'GD2019X': 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
 'GD2019Z': 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（乡镇级）答案及解析.pdf',
 'SD2021_xc': 'xingce/2021年山东公务员考试《行测》真题参考答案及解析.pdf',
 'SC2022H_xc': 'xingce/2022年四川下半年公务员录用考试《行测》 答案解析_decrypted.pdf',
 'SC2024_xc': 'xingce/2024年四川省公务员录用考试《行测》答案解析.pdf',
 'JS2024A_xc': 'xingce/2024年江苏省公务员录用考试《行测》（A类）答案+解析.pdf',
}
SCAN_PAGE = {'GD2017-86': '14', 'GD2017-89': '14', 'GD2017-90': '14', 'GD2019X-89': '15-16', 'GD2019Z-82': '12',
             'SD2021-76': '22', 'SD2021-79': '22', 'SD2021-80': '22-23', 'SD2021-86': '24'}
SCAN_STATS = {'SD2021-76': ('69%', 'B'), 'SD2021-79': ('57%', 'B'), 'SD2021-80': ('75%', 'C'), 'SD2021-86': ('74%', 'A')}
SCAN_ANS = {'GD2017-86': 'B', 'GD2017-89': 'A', 'GD2017-90': 'B', 'GD2019X-89': 'A', 'GD2019Z-82': 'B',
            'SD2021-76': 'A', 'SD2021-79': 'A', 'SD2021-80': 'D', 'SD2021-86': 'B'}

def index(tag):
    return json.load(open(f'{W}/index/{tag}.json'))
def ans_snip(tag, q):
    fn = f'{SP}/v/ans/{tag}_{q}.txt'
    if not os.path.exists(fn): return None, None
    t = open(fn).read(); f = t.split('\n', 1)[0]
    m = re.search(r'hit at page (\d+)', t)
    return f, (m.group(1) if m else None)

rows = []; uses = {}; n = 0
for g, mats in SEL.items():
    order = 0
    for mid, tag, qs in mats:
        d = index(tag); paper = tag.replace('_xc', '')
        for q in qs:
            n += 1; order += 1
            variant = isinstance(q, str) and q.endswith('V')
            qno = int(str(q).rstrip('V'))
            key = f'{paper}-{q}'
            x = next(y for y in d if y['kind'] == 'q' and y['qno'] == qno)
            stem, opts = parse(x['text'], qno)
            if variant:
                stem = '2016年,该省小微服务业样本企业的营业收入比2014年大约多多少亿元?'
                opts = {'A': '10.7', 'B': '19.1', 'C': '20.3', 'D': '21.7'}
            for kk, vv in FIX_OPT.get(key, {}).items(): opts[kk] = vv
            stem += FIX_STEM_SUFFIX.get(key, '')
            assert sorted(opts) == ['A', 'B', 'C', 'D'] and all(opts.values()), (key, opts)
            # official answer & analysis location
            of = None
            for kk, vv in OFF.items():
                if kk.replace('_xc', '') == key: of = vv
            src_ans = SCAN_ANS.get(key) or (of or {}).get('letter')
            af, ap = ans_snip(tag, qno)
            if tag in ANS_FILE: af = ANS_FILE[tag]
            if key in SCAN_PAGE: ap = SCAN_PAGE[key]
            if tag == 'ZJ2026A_xc': af, ap = None, None
            if key == 'JS2025A-122':
                af = 'xingce/2025年江苏省公务员录用考试《行测》题（A类）答案及解析（121后暂缺）.pdf'; ap = None; src_ans = None
            if af and af.startswith('/home/user/'): af = af[len('/home/user/'):]
            if variant: src_ans = None; af = None; ap = None
            stats = None
            if key in SCAN_STATS: stats = dict(正确率=SCAN_STATS[key][0], 易错项=SCAN_STATS[key][1])
            elif of and (of.get('rate') or of.get('yicuo')): stats = dict(正确率=of.get('rate'), 易错项=of.get('yicuo'))
            v = R[key]; mm = M[key]
            chk = v['ans']
            assert chk in 'ABCD'
            if src_ans and not variant: assert src_ans == chk, (key, src_ans, chk)
            # images
            qimg = None
            if not variant:
                qimg = f'assets/q/{tag}_q{qno}.png'
                if WRITE:
                    im, _ = render_material(x['file'], x['segs'], dpi=200)
                    im.save(f'{OUT}/{qimg}')
            vnote = '网友回忆版' if '网友回忆' in x['file'] else ''
            flags = list(mm['flags'])
            if vnote: flags.append('网友回忆版')
            if variant: flags.append('改编')
            if key in ('JS2025A-122', 'ZJ2026A-112'): flags.append('无原解析')
            notes = '核算（Python，按材料原数）：' + v['calc'].rstrip('。')
            if variant:
                notes = ('改编说明：母题GD2017-86问“2016年比2015年多多少”（一年增量）；本题只把比较期改为2014年，材料不动。'
                         '改动的目的：用户点名的“隔年”增长量在未用真题里没有干净的原题（GDXD2020ZH-94已在第1轮使用），而本材料恰好给出“增速比上年回落0.6个百分点”，'
                         '可以自然地推出2015年增速，形成“读出上年增速→隔年增长率（含交叉项）→增量”的新思考点；选项按四种真实错误路径设计。'
                         '独立重解与唯一性：' + v['calc'])
            elif src_ans:
                notes += f'；与原解析答案{src_ans}一致（解析第{ap}页）。'
            else:
                notes += '；无可用原解析，答案由编者独立求解，四个选项逐一验算，答案唯一。'
            if key == 'GD2017-89':
                notes += ' 口径提示：答案册宜注明“变化量的大小”按变化幅度（绝对值）比较；若题干是“增长量/增加值”则按带符号比较（见D05-ZA3组GD2023X-89、GK2022D-112）。'
            rec = dict(
                id=f'ZL2A-{n:03d}', module='资料', day='D05', group=g, group_title=GROUPS[g], topic=mm['topic'], order=order,
                source=dict(paper=paper, file=x['file'], page=x['segs'][0][0] + 1, qno=qno, ans_file=af, ans_page=ap, version_note=vnote),
                claim_key=None if variant else f'{paper}-{qno}', done_status='已做情况未知', stem=stem, options=opts,
                material_or_article=mid, assets=[qimg] if (key in IMG_NEEDED and qimg) else [], q_image=qimg,
                source_answer=src_ans, checked_answer=chk, brief_solution=mm['brief_solution'], precision_need=mm['precision_need'],
                selection_value=mm['selection_value'], variant_of='GD2017-86' if variant else None,
                check_status='已核验-改编' if variant else '已核验', flags=flags, notes=notes,
                skill_tags=mm['skill_tags'], answer_stats=stats)
            rows.append(rec)
            uses.setdefault(mid, []).append(f"{rec['id']} {key}")

# ---------------- materials ----------------
mats = []
today = datetime.date.today().isoformat()
for m in NEW:
    mid = m['mid']; tag = m['tag']
    f = index(tag)[0]['file']
    paper = tag.replace('_xc', '')
    vnote = m.get('version_note', '') or ('网友回忆版' if '网友回忆' in f else '')
    notes = []
    if mid in PCT_IMG: notes.append(IMGPCT)
    notes.append(f'建档：ZL2A（{today}）。图片按原页坐标截取（200dpi），只遮去页码、页眉考试名、店铺/公众号/水印广告行并压缩大段空白，不改动内容像素。原卷材料标号：{m["label"]}。')
    notes.append('ZL2A 使用本材料的题：' + '；'.join(uses.get(mid, [])))
    rec = dict(mid=mid, source=dict(paper=paper, file=f, pages=sorted({s[0] + 1 for s in m['segs']}),
                                    segs_0based=[[s[0], round(s[1], 1), round(s[2], 1)] for s in m['segs']], version_note=vnote),
               text=TEXT[mid], assets=[f'zl_materials/{mid}/{mid}.png'], transcription=TR.get(mid), notes=' '.join(notes))
    if WRITE:
        os.makedirs(f'{ZM}/{mid}', exist_ok=True)
        mj = f'{ZM}/{mid}/material.json'
        if os.path.exists(mj) and 'ZL2A' not in json.load(open(mj)).get('notes', ''):
            print('SKIP existing (other editor):', mid); mats.append(json.load(open(mj))); continue
        im, _ = render_material(f, m['segs'], dpi=200)
        im.save(f'{ZM}/{mid}/{mid}.png')
        json.dump(rec, open(mj, 'w'), ensure_ascii=False, indent=1)
    mats.append(rec)
for mid in REUSE:
    rec = dict(json.load(open(f'{ZM}/{mid}/material.json')))
    rec['notes'] = rec.get('notes', '') + ' ｜ZL2A复用（未改动原文件）；ZL2A 使用本材料的题：' + '；'.join(uses.get(mid, []))
    mats.append(rec)
used_mids = {r['material_or_article'] for r in rows}
assert used_mids == {m['mid'] for m in mats}, used_mids ^ {m['mid'] for m in mats}
if WRITE:
    with open(f'{OUT}/questions.jsonl', 'w') as fo:
        for r in rows: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(f'{OUT}/materials.jsonl', 'w') as fo:
        for r in mats: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
print('questions', len(rows), 'materials', len(mats))
import collections
print(collections.Counter(r['checked_answer'] for r in rows))
for g in GROUPS:
    rr = [r for r in rows if r['group'] == g]
    print(g, len(rr), ''.join(r['checked_answer'] for r in rr), collections.Counter(r['precision_need'] for r in rr))
