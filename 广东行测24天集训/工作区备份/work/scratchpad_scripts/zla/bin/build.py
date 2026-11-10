import json, os, re, sys, subprocess, unicodedata, pymupdf
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0, os.path.dirname(__file__))
import qmeta, verify, writemats
W = '/home/user/work'; OUT = f'{W}/out/ZL-A'; S = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zla'
os.makedirs(f'{OUT}/assets/q', exist_ok=True)
parsed = json.load(open(f'{S}/qparsed.json'))

def vkey(k):
    return k if k in verify.R else k.replace('_xc', '')

def claim_key(k):
    tag, q = k.rsplit('-', 1)
    if tag == 'GK2022F_xc': return k
    return tag.replace('_xc', '') + '-' + q

def paper_of(k):
    tag = k.rsplit('-', 1)[0]
    return 'GK2022F' if tag == 'GK2022F_xc' else tag.replace('_xc', '')

# ---------- analysis page finder ----------
ANS_PAGE_FIXED = {'GD2017-96': '15', 'GD2017-97': '15-16', 'GD2017-98': '16', 'GD2018-86': '17', 'GD2018-87': '17', 'GD2019X-96': '16',
                  'GD2019X-97': '16-17', 'GD2020Z-87': '21', 'GD2020Z-88': '21', 'GD2020Z-91': '22', 'GD2020Z-92': '22', 'GK2021F-132': '34',
                  'HB2025_xc-121': '70-71', 'HB2025_xc-123': '71', 'GK2022F_xc-126': None, 'JS2025A_xc-124': None,
                  'GK2023F-116': '36', 'GK2023F-135': '41', 'GK2023F-131': '40', 'ZJ2023A_xc-116': '34', 'GK2023D-119': '36'}
ANS_FILE_FIXED = {
 'GD2017': 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
 'GD2018': 'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
 'GD2019X': 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
 'GD2020Z': 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
 'GK2021F': 'xing-ce1/国考/答案解析/2021年国家公务员考试《行测》真题（副省级）参考答案及解析...pdf',
}
_doc_cache = {}
def find_ans_page(ans_file, qno, anchor_terms):
    if ans_file not in _doc_cache:
        d = pymupdf.open('/home/user/' + ans_file)
        _doc_cache[ans_file] = [unicodedata.normalize('NFKC', p.get_text()) for p in d]
    pages = _doc_cache[ans_file]
    pats = [r'【\s*%d\s*】' % qno, r'第\s*【?%d】?\s*题' % qno, r'题目\s*%d\b' % qno, r'【解析\s*%d' % qno, r'(?:^|\n)\s*%d\s*[、\.．]' % qno]
    cands = []
    for i, t in enumerate(pages):
        for p in pats:
            for m in re.finditer(p, t):
                seg = t[m.start():m.start() + 600]
                score = sum(1 for a in anchor_terms if a in seg) + (1 if re.search(r'答案|选择|解析', seg) else 0)
                cands.append((score, i))
    if not cands: return None
    cands.sort(key=lambda x: (-x[0], -x[1]))
    return str(cands[0][1] + 1)

def render_q(tag, qno):
    out = f'{OUT}/assets/q/{tag}_q{qno}.png'
    d = json.load(open(f'{W}/index/{tag}.json'))
    q = [x for x in d if x['kind'] == 'q' and x['qno'] == qno][0]
    doc = pymupdf.open('/home/user/' + q['file'])
    ims = []
    for (p, y0, y1) in q['segs']:
        page = doc[p]
        clip = pymupdf.Rect(20, max(0, y0 - 2), page.rect.width - 20, min(page.rect.height, y1 + 2))
        pix = page.get_pixmap(clip=clip, dpi=170)
        ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    Wd = max(i.width for i in ims); H = sum(i.height for i in ims)
    c = Image.new('RGB', (Wd, H), 'white'); y = 0
    for i in ims: c.paste(i, (0, y)); y += i.height
    c.save(out)
    return f'assets/q/{tag}_q{qno}.png'

def main():
    rows = []; uses = {}
    n = 0
    for g in 'ABCD':
        gid, gtitle = qmeta.GROUPS[g]
        for order, k in enumerate(qmeta.ORDER[g], 1):
            n += 1
            qid = f'ZL-A-{n:03d}'
            tag, qno = k.rsplit('-', 1); qno = int(qno)
            pq = parsed[k]
            stem = pq['stem']; opts = qmeta.OPT_OVERRIDE.get(k, pq['options'])
            topic, selv, brief = qmeta.META[k]
            val, opt, note = verify.R[vkey(k)]()
            # source answer
            ajson = f'{W}/answers/{tag}.json'
            src = None; ans_file = None
            if os.path.exists(ajson):
                A = json.load(open(ajson)); ans_file = A['file']
                r = A['answers'].get(str(qno)); src = r.get('ans') if r else None
            if k in qmeta.SRC_ANS: src = qmeta.SRC_ANS[k]
            if tag in qmeta.__dict__.get('X', {}): pass
            if paper_of(k) in ANS_FILE_FIXED and not os.path.exists(ajson): ans_file = ANS_FILE_FIXED[paper_of(k)]
            if k == 'GK2022F_xc-126': ans_file = None
            if k == 'JS2025A_xc-124': ans_file = 'xingce/2025年江苏省公务员录用考试《行测》题（A类）答案及解析（121后暂缺）.pdf'
            if k in ANS_PAGE_FIXED: ans_page = ANS_PAGE_FIXED[k]
            elif ans_file:
                nums = re.findall(r'\d+\.?\d*', stem + ' '.join(opts.values()))[:6]
                ans_page = find_ans_page(ans_file, qno, nums)
            else: ans_page = None
            # flags
            flags = []
            fname = pq['file']
            if '网友回忆' in fname: flags.append('网友回忆版')
            flags += [f for f in qmeta.EXTRA_FLAGS.get(k, []) if f not in flags]
            if src and src != opt: flags.append('原答案冲突')
            status = '已核验' if (src is None or src == opt) else '冲突待复核'
            mid = qmeta.MAT[k]
            uses.setdefault(mid, []).append(f'{qid} {claim_key(k)}')
            q_img = render_q(tag, qno)
            assets = [q_img] if k in qmeta.IMAGE_OPTION_Q else []
            notes = '核算（Python，按材料原数）：' + note
            if src is None: notes += '；无可用解析答案，答案为编者独立求解'
            else: notes += f'；与解析答案{src}一致' if src == opt else f'；与解析答案{src}不一致'
            if k in qmeta.RATE: notes += f'；解析标注全站正确率{qmeta.RATE[k][0]}%、易错项{qmeta.RATE[k][1]}'
            else:
                if os.path.exists(ajson):
                    r = json.load(open(ajson))['answers'].get(str(qno)) or {}
                    if r.get('rate'): notes += f"；解析标注正确率{r['rate']}%、易错项{r.get('yicuo')}"
            if k in qmeta.EXTRA_NOTES: notes += '。' + qmeta.EXTRA_NOTES[k]
            vnote = '网友回忆版' if '网友回忆' in fname else ''
            rows.append(dict(
                id=qid, module='资料', day='ZL01', group=gid, group_title=gtitle, topic=topic, order=order,
                source=dict(paper=paper_of(k), file=fname, page=pq['page'], qno=qno, ans_file=ans_file, ans_page=ans_page, version_note=vnote),
                claim_key=claim_key(k), done_status='已做情况未知', stem=stem, options=opts,
                material_or_article=mid, assets=assets, q_image=q_img,
                source_answer=src, checked_answer=opt, brief_solution=brief, precision_need=qmeta.PRECISION[k], selection_value=selv,
                variant_of=None, check_status=status, flags=flags, notes=notes))
    with open(f'{OUT}/questions.jsonl', 'w') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    mats = writemats.main(write=True, uses=uses)
    with open(f'{OUT}/materials.jsonl', 'w') as f:
        for m in mats:
            if m['mid'] in uses: f.write(json.dumps(m, ensure_ascii=False) + '\n')
    print(len(rows), 'questions;', len([m for m in mats if m['mid'] in uses]), 'materials')
    unused = [m['mid'] for m in mats if m['mid'] not in uses]
    print('materials built but unused:', unused)
    return rows, uses

if __name__ == '__main__':
    main()
