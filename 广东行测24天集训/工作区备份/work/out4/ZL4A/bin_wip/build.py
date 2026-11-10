"""Assemble ZL4A deliverables: out4/ZL4A/questions.jsonl, materials.jsonl, assets/q/*.png; new shared materials in out/zl_materials/.
python3 build.py [--write] [--sizes]"""
import sys, os, json, re, datetime, collections, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
from render2 import render_material
from sel import SEL, GROUPS
from matspec import SPEC, locate
from mattext import TEXT, TR
from qparse import parse, qrec
import lib
from lib import Q, MOCK, prec
for g_ in ('g1', 'g2', 'g3', 'g4', 'g5'): importlib.import_module(g_)

W = '/home/user/work'; OUT = f'{W}/out4/ZL4A'; ZM = f'{W}/out/zl_materials'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl4a'
WRITE = '--write' in sys.argv
TODAY = '2026-11-09'

# ---------- text-layer repairs (garbled options, circled numbers lost in normalisation, stray spaces). Not wording changes. ----------
FIX_OPT = {
 'GK2024F-126': {'A': '30%', 'B': '35%', 'C': '40%', 'D': '45%'},
 'GK2024F-128': {'A': '4', 'B': '6', 'C': '8', 'D': '10'},
 'GK2024F-129': {'A': '仅①', 'B': '仅④', 'C': '①②', 'D': '③④'},
 'GK2021F-120': {'D': '通过生活类排口排放的总氮量占所有排口总氮排放量的比重,高于通过生活类排口排的总磷量占所有排口总磷排放量的比重'},
}
FIX_STEM = {
 'GK2024F-129': '在①磷酸铁锂电池、②三元锂电池、③铅酸/铅碳电池和④液流电池四类应用不同技术的电化学储能电站中,2022年末累计投运电站总能量占各类电化学储能电站总能量比重高于2021年末水平的是:',
}
# question screenshots whose indexed region runs into the next material / page furniture: explicit (page0, y0, y1)
QSEG = {}
QSEG_FILE = f'{SP}/bin/qseg.json'
if os.path.exists(QSEG_FILE): QSEG = json.load(open(QSEG_FILE))

# ---------- original answers: text-layer analyses (snippets saved by getans.py) and scanned analyses read from page renders ----------
SCANF = {'GK2021F': 'xing-ce1/国考/答案解析/2021年国家公务员考试《行测》真题（副省级）参考答案及解析...pdf',
         'GD2017': 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
         'SZ2023': 'xingce/2023年深圳市考公务员录用考试《行测》真题（解析）.pdf'}
SCAN = {  # key: (page, answer)
 'GK2021F-116': ('30', 'C'), 'GK2021F-119': ('31', 'D'), 'GK2021F-120': ('31', 'C'),
 'GD2017-92': ('14-15', 'B'), 'GD2017-93': ('15', 'B'), 'GD2017-95': ('15', 'A'),
 'SZ2023-93': ('24', 'B'), 'SZ2023-95': ('24-25', 'A'),
}
def official(tag, q, key):
    paper = key.rsplit('-', 1)[0]
    if key in SCAN:
        pg, a = SCAN[key]
        return SCANF[paper], pg, a, None, '扫描件，渲染第%s页图像读出' % pg
    fn = f'{SP}/v/ans/{tag}_{q}.txt'
    t = open(fn).read()
    f, pgl, seg = t.split('\n', 2)
    pg = pgl.replace('page ', '')
    a = re.findall(r'(?:正确答案|答案)\s*(?:为|是|:|：)?\s*[【\[]?\s*([A-D])|故(?:本题)?选\s*([A-D])|选择\s*([A-D])\s*选项|解析\d+—正确答案([A-D])', seg)
    a = [x for tt in a for x in tt if x]
    assert a and len(set(a)) == 1, (key, a)
    rate = re.search(r'正确率\s*[:：]?\s*(\d+)\s*%', seg); yc = re.search(r'易错项\s*[:：]?\s*([A-D])', seg)
    st = dict(正确率=rate.group(1) + '%', 易错项=yc.group(1) if yc else None) if rate else None
    return f, pg, a[0], st, '文字层'

os.makedirs(f'{OUT}/assets/q', exist_ok=True); os.makedirs(f'{OUT}/assets/src', exist_ok=True)
rows = []; uses = collections.defaultdict(list); n = 0; sizes = []
for g, mats in SEL.items():
    order = 0
    for mid, tag, qs in mats:
        paper = tag.replace('_xc', '')
        for q in qs:
            n += 1; order += 1
            key = f'{paper}-{q}'
            rec_q = Q[key]
            variant = rec_q['kind'] == 'var'
            qno = int(re.match(r'\d+', q).group())
            x = qrec(tag, qno)
            if variant:
                stem, opts = rec_q['stem'], dict(rec_q['options'])
            else:
                stem, opts = parse(x['text'], qno)
                if key in FIX_STEM: stem = FIX_STEM[key]
                for kk, vv in FIX_OPT.get(key, {}).items(): opts[kk] = vv
                if rec_q['stem']: stem = rec_q['stem']
                if rec_q['options']: opts = dict(rec_q['options'])
                stem = re.sub(r'\(\s*\)', '( )', stem)
                stem += rec_q.get('stem_suffix') or ''
            assert sorted(opts) == ['A', 'B', 'C', 'D'] and all(opts.values()), (key, opts)
            chk = rec_q['ans']
            modified = bool(rec_q.get('original_stem') or rec_q.get('original_options'))
            qimg = srcimg = None
            if variant:
                af = ap = src = stats = how = None
            else:
                if rec_q['noref']:
                    af = ap = src = how = None; stats = None
                else:
                    af, ap, src, stats, how = official(tag, qno, key)
                    assert src == chk == rec_q['ref'], (key, src, chk, rec_q['ref'])
                stats = rec_q.get('stats') or stats
                path = f'assets/src/{tag}_q{qno}.png' if modified else f'assets/q/{tag}_q{qno}.png'
                if modified: srcimg = path
                else: qimg = path
                if WRITE or '--sizes' in sys.argv:
                    im, _ = render_material(x['file'], QSEG.get(key, x['segs']), dpi=200)
                    sizes.append((key, im.size, x['segs']))
                    if WRITE: im.save(f'{OUT}/{path}')
            if af and af.startswith('/home/user/'): af = af[len('/home/user/'):]
            vnote = '网友回忆版' if '网友回忆' in x['file'] else ''
            flags = list(rec_q['flags'])
            if key in SCAN: flags.append('解析为扫描件')
            if variant:
                notes = ('改编说明：' + rec_q['why']
                         + (' 设问方式借鉴' + MOCK[rec_q['mock']] + '，只借设问方式，材料与数据全部来自原真题。' if rec_q['mock'] else ' 设问为编者自拟，材料与数据全部来自原真题。')
                         + ' 独立重解与唯一性（Python，按材料原数逐项验算）：' + rec_q['calc'])
            else:
                notes = '核算（Python，按材料原数）：' + rec_q['calc'].rstrip('。') + '。'
                if rec_q['noref']: notes += '本卷无原解析，无原参考答案可核对。'
                else: notes += f'与原解析答案{src}一致（解析第{ap}页，{how}）。'
            if rec_q.get('note'): notes += ' ' + rec_q['note']
            rec = dict(
                id=f'ZL4A-{n:03d}', module='资料', day='D11', group=g, group_title=GROUPS[g], topic=rec_q['topic'], order=order,
                source=dict(paper=paper, file=x['file'], page=x['segs'][0][0] + 1, qno=qno, ans_file=af, ans_page=ap, version_note=vnote),
                claim_key=None if variant else key, done_status='已做情况未知', stem=stem, options=opts,
                material_or_article=mid, assets=[qimg] if (rec_q.get('need_img') and qimg) else [], q_image=qimg,
                source_answer=src, checked_answer=chk, brief_solution=rec_q['brief_solution'], precision_need=rec_q['precision_need'],
                selection_value=rec_q['selection_value'], variant_of=rec_q['mother'] if variant else None,
                check_status='已核验-改编' if variant else '已核验', flags=flags, notes=notes,
                skill_tags=rec_q['skill_tags'], answer_stats=stats, intensity=rec_q['intensity'], difficulty=rec_q['difficulty'])
            if rec_q.get('original_stem'): rec['original_stem'] = rec_q['original_stem']
            if rec_q.get('original_options'): rec['original_options'] = rec_q['original_options']
            if srcimg: rec['source_image'] = srcimg
            assert prec(rec_q['margin']) == rec_q['precision_need'], (key, rec_q['margin'])
            rows.append(rec)
            uses[mid].append(f"{rec['id']} {key}")

# ---------- materials ----------
mats = []
for g, ms in SEL.items():
    for mid, tag, qs in ms:
        paper = tag.replace('_xc', '')
        f = qrec(tag, int(re.match(r'\d+', qs[0]).group()))['file']
        mj = f'{ZM}/{mid}/material.json'
        if mid in SPEC:
            s = SPEC[mid]; segs = locate(mid)
            vnote = '网友回忆版' if '网友回忆' in f else ''
            notes = [f'建档：ZL4A（{TODAY}）。图片按原页坐标截取（200dpi），只遮去页码、页眉考试名、店铺/公众号/水印广告行并压缩大段空白，不改动内容像素。原卷材料标号：{s["label"]}。',
                     'ZL4A 使用本材料的题：' + '；'.join(uses[mid])]
            extra = {
             'ZLM-GK2013-4': '第一张表标题“主要行为分布”原卷如此（应为“行业”），照录。',
             'ZLM-GK2026F-4': '2026年度国考副省级卷为网友回忆版，题库中没有原解析。第三段“钢材、铝矿、锡矿……”回忆版如此，按上下文疑为“铜材”，照录并在正文中标注；ZL4A所用各题的答案不依赖这一处。',
             'ZLM-ZJ2018A-2': '文字材料中的“50.8%”在原PDF中为嵌入图片（文字层缺失），按渲染图转录，并与49.86÷(49.86−16.79)−1=50.8%核对一致。',
             'ZLM-GK2016F-5': '同一材料亦见于GK2016D（地市级卷第126—130题）。',
             'ZLM-GK2018D-1': '同一材料亦见于GK2018F（副省级卷第116—120题）。',
             'ZLM-GK2019D-3': '同一材料亦见于GK2019F（副省级卷第126—130题）。',
             'ZLM-GK2024F-3': '同一材料亦见于GK2024X（行政执法卷第121—125题）。',
             'ZLM-GK2025D-1': '同一材料亦见于GK2025X（行政执法卷第121—125题）。',
             'ZLM-GK2023D-4': '同一材料亦见于GK2023X（行政执法卷第121—125题）。',
            }.get(mid)
            if extra: notes.append(extra)
            rec = dict(mid=mid, source=dict(paper=paper, file=f, pages=sorted({sg[0] + 1 for sg in segs}),
                                            segs_0based=[[sg[0], round(sg[1], 1), round(sg[2], 1)] for sg in segs], version_note=vnote),
                       text=TEXT[mid], assets=[f'zl_materials/{mid}/{mid}.png'], transcription=TR.get(mid), notes=' '.join(notes))
            if WRITE:
                os.makedirs(f'{ZM}/{mid}', exist_ok=True)
                if os.path.exists(mj) and 'ZL4A' not in json.load(open(mj)).get('notes', ''):
                    raise SystemExit('existing material by another editor: ' + mid)
                im, _ = render_material(f, segs, dpi=200)
                im.save(f'{ZM}/{mid}/{mid}.png')
                json.dump(rec, open(mj, 'w'), ensure_ascii=False, indent=1)
        else:
            rec = json.load(open(mj))      # reuse a material built by an earlier editor; the shared file is left untouched
            assert rec['mid'] == mid and os.path.exists(f"{W}/out/{rec['assets'][0]}"), mid
            rec = dict(rec)
            rec['notes'] = (rec.get('notes') or '') + f' 【ZL4A（{TODAY}，D11）复用本材料，未改动共享文件】ZL4A 使用本材料的题：' + '；'.join(uses[mid])
        mats.append(rec)
used = [r['material_or_article'] for r in rows]
assert set(used) == {m['mid'] for m in mats} and len(mats) == 21
if WRITE:
    with open(f'{OUT}/questions.jsonl', 'w') as fo:
        for r in rows: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(f'{OUT}/materials.jsonl', 'w') as fo:
        for r in mats: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
print('questions', len(rows), 'materials', len(mats), 'WRITE' if WRITE else 'dry-run')
print('answers', sorted(collections.Counter(r['checked_answer'] for r in rows).items()))
print('intensity', dict(collections.Counter(r['intensity'] for r in rows)))
print('difficulty', dict(collections.Counter(r['difficulty'] for r in rows)))
print('kind', dict(collections.Counter(r['check_status'] for r in rows)))
for g in GROUPS:
    rr = [r for r in rows if r['group'] == g]
    print(g, len(rr), ''.join(r['checked_answer'] for r in rr), dict(collections.Counter(r['intensity'] for r in rr)))
if sizes:
    for k_, sz, sg in sizes:
        if sz[1] > 700 or len(sg) > 1: print('  qimg', k_, sz, [[s[0], round(s[1]), round(s[2])] for s in sg])
