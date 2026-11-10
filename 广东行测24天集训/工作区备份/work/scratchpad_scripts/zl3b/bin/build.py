"""Build ZL3B deliverables: zl_materials/<MID>/, out3/ZL3B/{questions.jsonl, materials.jsonl, assets/q/}."""
import json, os, re, sys, unicodedata
import pymupdf
sys.path.insert(0, os.path.dirname(__file__))
from matspec import MATS
from render2 import render_material, JUNK as RJUNK
from qdata_up import Q
pymupdf.TOOLS.mupdf_display_errors(False)

IDX = '/home/user/work/index'
MROOT = '/home/user/work/out/zl_materials'
OUT = '/home/user/work/out3/ZL3B'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl3b'
WRITE = '--write' in sys.argv
CJK = r'㐀-鿿＀-￯'

def clean_text(t):
    t = t.replace('\xa0', ' ')
    out = []
    for line in t.split('\n'):
        if not line.strip():
            continue
        if RJUNK.search(line):
            continue
        line = re.sub(r'(?<=[0-9%.~])[ \t]+(?=[' + CJK + '])', '', line)
        line = re.sub(r'(?<=[' + CJK + '])[ \t]+(?=[0-9])', '', line)
        line = re.sub(r'[ \t]{2,}', ' ', line).strip()
        out.append(line)
    return '\n'.join(out)

def pdf_of(tag):
    return json.load(open(f'{IDX}/{tag}.json'))[0]['file']

# ---------------- materials ----------------
MAT_ROWS = {}
NOTE_EXTRA = {
    'ZLM-GD2016Z-1': '截图从正文第一行起，略去原卷“（一）根据下列资料，回答86~90题：”提示行。原文规划编制段写“第二批示范片的59个行政村和386个自然村”，其余各段第二批为391个自然村，原文如此。',
    'ZLM-GD2015X-2': '同材料亦见GD2015Z（乡镇卷）第91—95题。原文瑕疵：“中国品牌SUV销售55万辆……占SUV市场份额为44.76%”与SUV总销量408万辆不相容（55/408≈13.5%），ZL3B各题均不使用这一句；“日系车占有率下降了0.34%”未写明是百分点还是相对降幅，用到它的GD2015X-95 D项两种读法结论相同。',
    'ZLM-JS2025A-1': '原卷此则材料无“（一）”式标号，是资料分析部分第一则，按出现顺序编为-1。',
    'ZLM-JS2019A-3': '11-09升级时换入（替换原ZLM-JS2024A-1）。原卷资料分析从“（三）”起标号，按卷面标号命名为-3。文中11个百分数在原卷是嵌入图片，文字层缺失；text字段已按截图补全，逐个数值见transcription，以截图为准。“女生3小时35分钟”的“女生”为原卷用字。',
    'ZLM-JS2020A-3': '原卷资料分析部分材料从“（三）”起标号，按卷面标号命名为-3（同卷“（六）”为ZL-A建档的ZLM-JS2020A-6）。',
    'ZLM-GD2014X-1': '',
    'ZLM-GK2013-3': '',
    'ZLM-ZJ2016A-2': '',
}

def build_materials(used_by):
    for mid, s in MATS.items():
        f = pdf_of(s['tag'])
        doc = pymupdf.open('/home/user/' + f)
        im, _ = render_material(f, s['segs'], dpi=200)
        raw = ''
        for (p, y0, y1) in s['segs']:
            raw += doc[p].get_text('text', clip=pymupdf.Rect(0, y0, doc[p].rect.width, y1)) + '\n'
        text = s.get('text_override') or clean_text(raw)
        pages = sorted(set(p + 1 for (p, _, _) in s['segs']))
        users = '；'.join(used_by.get(mid, []))
        note = ('建档：ZL3B（2026-11-09，D08保留块“广东式文字理解、统计口径与轻计算”）。截图由原PDF按页坐标裁切（200dpi），只遮去页眉页脚、页码和店铺水印行，内容像素未改；纯文字材料，无表图。'
                f'卷面标号：{s["label"]}。' + (NOTE_EXTRA.get(mid) or '') + f' ZL3B 使用本材料的题：{users}')
        row = dict(mid=mid,
                   source=dict(paper=s['tag'].replace('_xc', ''), file=f, pages=pages, segs_0based=s['segs'], version_note=''),
                   text=text, assets=[f'zl_materials/{mid}/{mid}.png'], transcription=s.get('transcription'), notes=note)
        MAT_ROWS[mid] = row
        if WRITE:
            d = f'{MROOT}/{mid}'
            os.makedirs(d, exist_ok=True)
            im.save(f'{d}/{mid}.png')
            json.dump(row, open(f'{d}/material.json', 'w'), ensure_ascii=False, indent=1)
        else:
            os.makedirs(f'{SP}/matprev', exist_ok=True)
            im.save(f'{SP}/matprev/{mid}.png')

# ---------------- question images ----------------
DOPT = re.compile(r'(^|[\s　])D\s*[、\.．]')

def qsegs_until_D(tag, qno):
    d = json.load(open(f'{IDX}/{tag}.json'))
    q = [x for x in d if x['kind'] == 'q' and int(x['qno']) == qno][0]
    doc = pymupdf.open('/home/user/' + q['file'])
    segs = [list(s) for s in q['segs']]
    NEWBLK = re.compile(r'^\s*([（(][一二三四五六七八九十][）)]|[（(]材料|材料\s*\d|\d{2,3}\s*[、\.．]|根据以下|根据下列)')
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
            # option D may wrap onto following lines: keep tightly spaced lines that do not start a new block
            for ly0, ly1, t in inseg[hit + 1:]:
                if ly0 - end < 6 and not NEWBLK.search(t) and not RJUNK.search(t):
                    end = max(end, ly1)
                else:
                    nxt = ly0
                    break
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

# ---------------- questions ----------------
VKEY_ADAPT = {1: 'ZL3B-A1', 2: 'U002', 3: 'U003', 7: 'U007', 10: 'U010', 12: 'U012', 13: 'U013', 21: 'ZL3B-A4', 28: 'ZL3B-A3', 31: 'U031', 35: 'U035', 36: 'U036'}
def main():
    ver = json.load(open(f'{SP}/verify_results.json'))
    vkey = {}
    for k, v in ver.items():
        vkey[k.split(' ')[0].split('(')[0]] = v['ans']
    ids = {}
    order_in_group = {}
    rows = []
    # first pass: ids
    for i, q in enumerate(Q, 1):
        q['id'] = f'ZL3B-{i:03d}'
        if q['kind'] == 'orig':
            ids[f"{q['src']['paper']}-{q['qno']}"] = q['id']
    used_by = {}
    for q in Q:
        mid = q['src']['mid']
        lab = f"{q['id']}（{q['src']['paper']}-{q['qno']}）" if q['kind'] == 'orig' else f"{q['id']}（改编，variant_of {q['src']['paper']}-{q['qno']}）"
        used_by.setdefault(mid, []).append(lab)
    build_materials(used_by)
    for q in Q:
        g, gt = q['group']
        order_in_group[g] = order_in_group.get(g, 0) + 1
        s = q['src']
        notes = re.sub(r'\{REF:([^}]+)\}', lambda m: ids[m.group(1)], q['notes'])
        if q['kind'] == 'orig':
            key = f"{s['paper']}-{q['qno']}"
            vk = vkey.get(key)
            assert vk == q['answer'], (key, vk, q['answer'])
            assert q['src_answer'] == q['answer'], key
            rel, segs = make_qimg(s['tag'], q['qno'])
            source = dict(paper=s['paper'], file=s['file'], page=s['page'], qno=q['qno'], ans_file=s['ans_file'],
                          ans_page=q['ans_page'], version_note=s['version_note'])
            flags = list(q.get('extra_flags', []))
            row = dict(id=q['id'], module='资料', day='D08', group=g, group_title=gt, topic=q['topic'], order=order_in_group[g],
                       source=source, claim_key=key, done_status='已做情况未知', stem=q['stem'], options=q['options'],
                       material_or_article=s['mid'], assets=[rel] if q.get('need_qimg') else [], q_image=rel,
                       source_answer=q['src_answer'], checked_answer=q['answer'], brief_solution=q['brief'],
                       selection_value=q['value'], variant_of=None, check_status='已核验', flags=flags, notes=notes)
            if q.get('original_stem'):
                row['original_stem'] = q['original_stem']
        else:
            pos = int(q['id'][-3:])
            pref = VKEY_ADAPT[pos]
            vk = [v['ans'] for k, v in ver.items() if k.startswith(pref + ' ')]
            assert len(vk) == 1 and vk[0] == q['answer'], (q['id'], pref, vk, q['answer'])
            source = dict(paper=s['paper'], file=s['file'], page=s['page'], qno=q['qno'], ans_file=None, ans_page=None,
                          version_note='ZL3B改编：沿用母题材料，设问与四个选项均为ZL3B新拟')
            row = dict(id=q['id'], module='资料', day='D08', group=g, group_title=gt, topic=q['topic'], order=order_in_group[g],
                       source=source, claim_key=None, done_status='已做情况未知', stem=q['stem'], options=q['options'],
                       material_or_article=s['mid'], assets=[], q_image=None,
                       source_answer=None, checked_answer=q['answer'], brief_solution=q['brief'],
                       selection_value=q['value'], variant_of=f"{s['paper']}-{q['qno']}", check_status='已核验-改编',
                       flags=['改编'], notes=notes)
        for extra in ('replaced_from', 'replace_reason', 'revision_note'):
            if q.get(extra):
                row[extra] = re.sub(r'\{REF:([^}]+)\}', lambda m: ids[m.group(1)], q[extra])
        rows.append(row)
    if WRITE:
        os.makedirs(OUT, exist_ok=True)
        with open(f'{OUT}/questions.jsonl', 'w') as fo:
            for r in rows:
                fo.write(json.dumps(r, ensure_ascii=False) + '\n')
        with open(f'{OUT}/materials.jsonl', 'w') as fo:
            for mid in MATS:
                fo.write(json.dumps(MAT_ROWS[mid], ensure_ascii=False) + '\n')
        used = set(r['q_image'] for r in rows if r.get('q_image')) | set(a for r in rows for a in r['assets'])
        for fn in sorted(os.listdir(f'{OUT}/assets/q')):
            if f'assets/q/{fn}' not in used:
                os.remove(f'{OUT}/assets/q/{fn}'); print('removed unreferenced', fn)
    print(len(rows), 'questions;', len(MAT_ROWS), 'materials; write =', WRITE)
    for r in rows:
        print(r['id'], r['group'], r['order'], r['material_or_article'], r['source']['paper'], r['source']['qno'], r['checked_answer'], r['check_status'], r['variant_of'])

if __name__ == '__main__':
    main()
