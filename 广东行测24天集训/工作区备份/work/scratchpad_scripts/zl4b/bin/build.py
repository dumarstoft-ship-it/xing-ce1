# -*- coding: utf-8 -*-
"""Build ZL4B deliverables:
   /home/user/work/out/zl_materials/<MID>/{<MID>.png, material.json}   (new materials only; reused ones untouched)
   /home/user/work/out4/ZL4B/{questions.jsonl, materials.jsonl, assets/q/*.png}
Run without args for a dry run (previews go to the scratchpad); add --write to write deliverables."""
import json, os, re, sys, unicodedata
import pymupdf
sys.path.insert(0, os.path.dirname(__file__))
from matspec import MATS
from render2 import render_material, JUNK as RJUNK
from mattext import clean as clean_mat
from qdata import Q, ADAPT_NOTE
pymupdf.TOOLS.mupdf_display_errors(False)

IDX = '/home/user/work/index'
MROOT = '/home/user/work/out/zl_materials'
OUT = '/home/user/work/out4/ZL4B'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl4b'
WRITE = '--write' in sys.argv
DAY = 'D11'


def pdf_of(tag):
    return json.load(open(f'{IDX}/{tag}.json'))[0]['file']


# ---------------------------------------------------------------- materials
TEXT_FIX = {
    # 原卷嵌入图片的6个百分数（文字层缺失），按260dpi截图逐个转录后补入
    'ZLM-ZJ2017A-1': [('同比增长约，择优资助', '同比增长约10%，择优资助'),
                      ('比上年增加1709项，占总项数的，直接费用', '比上年增加1709项，占总项数的41%，直接费用'),
                      ('（资助项目占接收申请项目的比重），同比下降2.5个百分点', '（资助项目占接收申请项目的比重）22.9%，同比下降2.5个百分点'),
                      ('重点项目资助625项，同比增长约，直接费用', '重点项目资助625项，同比增长约3.3%，直接费用'),
                      ('比上年减少266项，占总项数的，直接费用', '比上年减少266项，占总项数的40%，直接费用'),
                      ('亿元，平均资助率，同比下降0.7个百分点', '亿元，平均资助率24.6%，同比下降0.7个百分点')],
    # 表、图在文字层没有，按约定加标记行，使题本排版时出图
    'ZLM-ZJ2015A-3': [('兴柜市场周转率为27%。\n', '兴柜市场周转率为27%。\n【表】2012年台湾多层次资本市场一览表（单位：10亿新台币）（见图）\n')],
    'ZLM-ZJ2020B-2': [('（累计装机容量不含报废机器的装机容量）', '（累计装机容量不含报废机器的装机容量）\n【图】2008~2017年全球风电及光伏累计装机容量（单位：GW）（见图）')],
}
TRANSCRIPTION = {
    'ZLM-ZJ2017A-1': '原卷文字层缺失的嵌入图片数字（按260dpi截图逐个转录）：全年接收申请“同比增长约10%”；面上项目“占总项数的41%”“平均资助率22.9%”；重点项目“同比增长约3.3%”；青年科学基金“占总项数的40%”“平均资助率24.6%”。',
    'ZLM-ZJ2015A-3': '表 2012年台湾多层次资本市场一览表（单位：10亿新台币），三列依次为证交所集中市场／上柜市场／兴柜市场：挂牌公司数（家）809／638／285；资本额6384／667／335；总市值21352／1737／538；挂牌公司营收20083／1384／497；总成交值20789／2987／154。',
    'ZLM-ZJ2020B-2': '图 2008~2017年全球风电及光伏累计装机容量（GW）。风电累计装机容量：2008年120.7，2009年159.1，2010年198.0，2011年238.1，2012年282.9，2013年318.7，2014年369.9，2015年432.7，2016年487.3，2017年539.1；光伏累计装机容量：2008年15.8，2009年23.2，2010年40.3，2011年70.5，2012年100.5，2013年138.8，2014年179.0，2015年229.1，2016年306.5，2017年404.5。',
}
NOTE_EXTRA = {
    'ZLM-JS2023A-1': '截图从正文第一行起，略去原卷提示行“一、根据以下资料，回答116~120题。”。本卷是xingce仓库的录入版（非扫描件）：文中“PM2.5年均浓度为30毫克/立方米”的单位照录（ZL4B各题均不使用这一句的单位）。',
    'ZLM-ZJ2015A-3': '文字＋表格材料：表格为原卷图片，数据见transcription，以截图为准。表格单位为“10亿新台币”，正文用“兆新台币”（1兆＝1000个10亿），正文资本额、总市值与表格可互相对上。原文末句无句号，照录。',
    'ZLM-ZJ2017A-1': '文中6个百分数在原卷是嵌入图片，文字层缺失；text字段已按截图补全，逐个数值见transcription，以截图为准。',
    'ZLM-GK2016D-3': '材料在原卷跨页（第14页末至第15页首），截图按两段拼接。同材料亦见国考2016年度副省级卷第四则（第126—130题），登记别名MAT:ZLM-GK2016F-4。原文“教育业0.68万户．同比增长86.17%”的标点及句末无句号，照录。',
    'ZLM-JS2016A-1': '原卷四则材料都只标“(材料)”，本则为第一则，按出现顺序编为-1。',
    'ZLM-JS2018A-3': '材料在原卷跨页（第16页末至第17页首），截图按两段拼接，略去第16页上的“五、资料分析……”说明行。本则在原卷没有标号，下一则标“（四）”；按江苏卷资料分析从“（三）”起标号的惯例（参见ZLM-JS2019A-3、ZLM-JS2020A-3），命名为-3。原文分号为半角，照录。',
    'ZLM-ZJ2020B-2': '文字＋柱状图材料：柱状图为原卷图片，数据见transcription，以截图为准。同材料亦见浙江2020年度A卷（xing-ce1版）第91—95题，登记别名MAT:ZLM-ZJ2020A-2。材料瑕疵：按脚注口径（累计＝上年累计＋新增－报废）倒推，2016年光伏新增约76.8GW（99.1÷1.29）小于当年累计增加量77.4GW（306.5－229.1），报废量为负，数据在2016年不自洽；2017年风电（新增52.5、累计增加51.8）和光伏（新增99.1、累计增加98.0）自洽。ZL4B的改编题只用2017年。',
}
MAT_ROWS = {}


def build_materials(used_by):
    for mid, s in MATS.items():
        users = '；'.join(used_by.get(mid, []))
        if s.get('reuse'):
            row = json.load(open(f'{MROOT}/{mid}/material.json'))
            row = dict(row)
            row['notes'] = (row.get('notes') or '') + f' ‖ ZL4B（2026-11-09，D11保留块）复用本材料，未改动材料文件；ZL4B 使用本材料的题：{users}'
            MAT_ROWS[mid] = row
            continue
        f = pdf_of(s['tag'])
        im, raw = render_material(f, s['segs'], dpi=200)
        text = clean_mat(raw, mid)
        for a, b in TEXT_FIX.get(mid, []):
            assert a in text, (mid, a)
            text = text.replace(a, b)
        pages = sorted(set(p + 1 for (p, _, _) in s['segs']))
        kind = '文字＋图表材料' if mid in ('ZLM-ZJ2015A-3', 'ZLM-ZJ2020B-2') else '纯文字材料，无表图'
        note = ('建档：ZL4B（2026-11-09，D11保留块“广东式文字理解、统计口径与轻计算”）。截图由原PDF按页坐标裁切（200dpi），只遮去页眉页脚、页码和店铺水印行，内容像素未改；'
                f'{kind}。text字段取自原PDF文字层，只合并版面换行、去掉排版空格，已与截图逐句对过。卷面标号：{s["label"]}。'
                + (NOTE_EXTRA.get(mid) or '') + f' ZL4B 使用本材料的题：{users}')
        row = dict(mid=mid,
                   source=dict(paper=s['tag'].replace('_xc', ''), file=f, pages=pages, segs_0based=s['segs'], version_note=''),
                   text=text, assets=[f'zl_materials/{mid}/{mid}.png'], transcription=TRANSCRIPTION.get(mid), notes=note)
        MAT_ROWS[mid] = row
        if WRITE:
            d = f'{MROOT}/{mid}'
            os.makedirs(d, exist_ok=True)
            im.save(f'{d}/{mid}.png')
            json.dump(row, open(f'{d}/material.json', 'w'), ensure_ascii=False, indent=1)
        else:
            os.makedirs(f'{SP}/matprev', exist_ok=True)
            im.save(f'{SP}/matprev/{mid}.png')


# ---------------------------------------------------------------- question images
DOPT = re.compile(r'(^|[\s　])D\s*[、\.．]')
NEWBLK = re.compile(r'^\s*([（(][一二三四五六七八九十][）)]|[（(]材料|材料\s*\d|\d{2,3}\s*[、\.．]|[一二三四五六]、根据|根据以下|根据下列)')


def qsegs_until_D(tag, qno):
    d = json.load(open(f'{IDX}/{tag}.json'))
    q = [x for x in d if x['kind'] == 'q' and int(x['qno']) == qno][0]
    doc = pymupdf.open('/home/user/' + q['file'])
    segs = [list(s) for s in q['segs']]
    for i, (p, y0, y1) in enumerate(segs):
        lines = []
        for b in doc[p].get_text('dict')['blocks']:
            if b.get('type') != 0:
                continue
            for l in b['lines']:
                t = ''.join(sp['text'] for sp in l['spans'])
                if t.strip():
                    lines.append((l['bbox'][1], l['bbox'][3], unicodedata.normalize('NFKC', t)))
        lines.sort()
        inseg = [x for x in lines if x[0] >= y0 - 1 and x[1] <= y1 + 1]
        hit = None
        for k, (ly0, ly1, t) in enumerate(inseg):
            if DOPT.search(t):
                hit = k
        if hit is not None:
            end = inseg[hit][1]
            nxt = None
            for ly0, ly1, t in inseg[hit + 1:]:
                if ly0 - end < 6 and not NEWBLK.search(t) and not RJUNK.search(t):
                    end = max(end, ly1)
                else:
                    nxt = ly0
                    break
            # option images (formula / percent pictures) on the option line may be taller than the text line
            for info in doc[p].get_image_info():
                bb = info['bbox']
                if bb[1] < end + 2 and bb[3] > inseg[hit][0] - 2 and (bb[3] - bb[1]) < 60 and bb[1] >= y0 - 2:
                    end = max(end, bb[3])
            pad = 4 if nxt is None else max(0.3, min(4, nxt - end - 3))
            return q['file'], segs[:i] + [[p, y0, min(end + pad, y1)]]
    return q['file'], segs


def make_qimg(tag, qno):
    f, segs = qsegs_until_D(tag, qno)
    im, _ = render_material(f, segs, dpi=170)
    rel = f'assets/q/{tag}_q{qno}.png'
    if WRITE:
        os.makedirs(f'{OUT}/assets/q', exist_ok=True)
        im.save(f'{OUT}/{rel}')
    else:
        os.makedirs(f'{SP}/qprev', exist_ok=True)
        im.save(f'{SP}/qprev/{tag}_q{qno}.png')
    return rel, segs


# ---------------------------------------------------------------- questions
def mother_info(tag, qno):
    """母题的原题干与原参考答案（供复核对照；取自索引文字层和解析抽取结果，母题本身不单独收录）"""
    d = json.load(open(f'{IDX}/{tag}.json'))
    x = [y for y in d if y['kind'] == 'q' and int(y['qno']) == qno][0]
    t = unicodedata.normalize('NFKC', x['text'])
    t = re.split(r'\n\s*A\s*[、\.．]', t)[0]
    t = re.sub(r'^\s*\d{2,3}\s*[、\.．]\s*(\(单选题\))?', '', t).replace('\n', '')
    t = re.sub(r'(?<=[0-9%~])\s+(?=[\u4e00-\u9fff])|(?<=[\u4e00-\u9fff,，、])\s+(?=[0-9])|(?<=[0-9])\s+(?=[0-9~—])', '', t).replace(',', '，').replace('?', '？').replace(':', '：')
    t = t.replace('GW 以上', 'GW以上')
    if tag == 'GK2022X' and qno == 130:
        t = '以下信息中，能够从上述资料中推出的有几项？①2020年1—5月，全国抓获电信网络诈骗犯罪嫌疑人10万名以上 ②2021年1—5月，全国公安机关破获被骗百万元以上案件比去年同期多500件以上 ③2020年10月—2021年5月，每打掉1个“两卡”违法犯罪团伙，平均缴获的电话卡和银行卡总量就在300张以上'
    a = json.load(open(f'/home/user/work/answers/{tag}.json'))['answers'].get(str(qno), {})
    return dict(key=f"{tag.replace('_xc', '')}-{qno}", stem=t.strip(), source_answer=a.get('ans'))


def main():
    ver = json.load(open(f'{SP}/verify_results.json'))

    def vfind(prefix):
        hits = [(k, v) for k, v in ver.items() if k == prefix or k.startswith(prefix + ' ') or k.startswith(prefix + '(')]
        assert len(hits) == 1, (prefix, [k for k, _ in hits])
        return hits[0][1]

    ids = {}
    for i, q in enumerate(Q, 1):
        q['id'] = f'ZL4B-{i:03d}'
        if q['kind'] == 'orig':
            ids[f"{q['src']['paper']}-{q['qno']}"] = q['id']
    used_by = {}
    for q in Q:
        mid = q['src']['mid']
        lab = f"{q['id']}（{q['src']['paper']}-{q['qno']}）" if q['kind'] == 'orig' else f"{q['id']}（改编，variant_of {q['src']['paper']}-{q['qno']}）"
        used_by.setdefault(mid, []).append(lab)
    build_materials(used_by)

    rows = []
    order_in_group = {}
    seen_mid_order = []
    for q in Q:
        g, gt = q['group']
        order_in_group[g] = order_in_group.get(g, 0) + 1
        s = q['src']
        if s['mid'] not in seen_mid_order:
            seen_mid_order.append(s['mid'])
        v = vfind(q['vkey'])
        assert v['ans'] == q['answer'], (q['id'], q['vkey'], v['ans'], q['answer'])
        vnote = ' 【复算记录】' + v['detail'] + ('；扰动检验：' + v['pert'] if v.get('pert') else '')
        notes = q['notes'] + vnote
        common = dict(module='资料', day=DAY, group=g, group_title=gt, topic=q['topic'], order=order_in_group[g])
        if q['kind'] == 'orig':
            key = f"{s['paper']}-{q['qno']}"
            assert q['src_answer'] == q['answer'] == v['src'], (key, q['src_answer'], q['answer'], v['src'])
            rel, segs = make_qimg(s['tag'], q['qno'])
            page = json.load(open(f"{IDX}/{s['tag']}.json"))
            page = [x for x in page if x['kind'] == 'q' and int(x['qno']) == q['qno']][0]['segs'][0][0] + 1
            source = dict(paper=s['paper'], file=s['file'], page=page, qno=q['qno'], ans_file=s['ans_file'],
                          ans_page=q['ans_page'], version_note=s['version_note'])
            flags = list(q.get('extra_flags', []))
            reworded = bool(q.get('reworded'))
            row = dict(id=q['id'], **common, source=source, claim_key=key, done_status='已做情况未知',
                       stem=q['stem'], options=q['options'], material_or_article=s['mid'],
                       assets=[rel] if (q.get('need_qimg') and not reworded) else [],
                       q_image=None if reworded else rel,
                       source_answer=q['src_answer'], checked_answer=q['answer'], brief_solution=q['brief'],
                       selection_value=q['value'], variant_of=None, check_status='已核验', flags=flags, notes=notes,
                       intensity=q['intensity'], difficulty=q['difficulty'], calibers=q['calibers'],
                       source_kind='原题整理' if reworded else '真题选编')
            if reworded:
                row['source_image'] = rel
            if q.get('original_options'):
                row['original_options'] = q['original_options']
            if q.get('original_stem'):
                row['original_stem'] = q['original_stem']
        else:
            mrel, _ = make_qimg(s['tag'], q['qno'])          # 母题截图，仅供复核追溯，不进assets
            source = dict(paper=s['paper'], file=s['file'], page=s['page'], qno=q['qno'], ans_file=None, ans_page=None,
                          version_note=ADAPT_NOTE)
            row = dict(id=q['id'], **common, source=source, claim_key=None, done_status='已做情况未知',
                       stem=q['stem'], options=q['options'], material_or_article=s['mid'], assets=[], q_image=None,
                       source_answer=None, checked_answer=q['answer'], brief_solution=q['brief'],
                       selection_value=q['value'], variant_of=f"{s['paper']}-{q['qno']}", check_status='已核验-改编',
                       flags=['改编'], notes=notes, intensity=q['intensity'], difficulty=q['difficulty'], calibers=q['calibers'],
                       source_kind='改编', mother_image=mrel, mother=mother_info(s['tag'], q['qno']))
        rows.append(row)

    if WRITE:
        os.makedirs(OUT, exist_ok=True)
        with open(f'{OUT}/questions.jsonl', 'w') as fo:
            for r in rows:
                fo.write(json.dumps(r, ensure_ascii=False) + '\n')
        with open(f'{OUT}/materials.jsonl', 'w') as fo:
            for mid in seen_mid_order:
                fo.write(json.dumps(MAT_ROWS[mid], ensure_ascii=False) + '\n')
        used = set()
        for r in rows:
            for k in ('q_image', 'source_image', 'mother_image'):
                if r.get(k):
                    used.add(r[k])
            used.update(r['assets'])
        for fn in sorted(os.listdir(f'{OUT}/assets/q')):
            if f'assets/q/{fn}' not in used:
                os.remove(f'{OUT}/assets/q/{fn}'); print('removed unreferenced', fn)
    print(len(rows), 'questions;', len(MAT_ROWS), 'materials; write =', WRITE)
    for r in rows:
        print(r['id'], r['group'], r['order'], r['material_or_article'], r['source']['paper'], r['source']['qno'], r['checked_answer'],
              r['check_status'], r['intensity'], r['difficulty'], r['variant_of'] or '')
    return rows


if __name__ == '__main__':
    main()
