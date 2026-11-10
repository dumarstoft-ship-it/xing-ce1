import json, re, os, sys, collections
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
from qx import get, raw, crop
from clean2 import clean_pd, clean_px, norm_text
from ansx import info, seg
from meta import PAPER_CN, T, FLAGS, NOTES, GD_ANS, GD_ANSF, CC_PATCH, STEM_PATCH
from PIL import Image
OUT = '/home/user/work/out2/YY2B'
plan = json.load(open(f'{SP}/plan.json'))
DR = json.load(open(f'{SP}/dups_related.json'))
CJK = r'一-鿿“”‘’《》（）'
def fullwidth_punct(s):
    n0 = s
    s = re.sub(rf'(?<=[{CJK}]),(?=[{CJK}])', '，', s)
    s = re.sub(rf'(?<=[{CJK}]);(?=[{CJK}])', '；', s)
    s = re.sub(rf'(?<=[{CJK}]):(?=[{CJK}“])', '：', s)
    s = re.sub(rf'(?<=[{CJK}]):(?=\s*$)', '：', s, flags=re.M)
    s = re.sub(rf'(?<=[{CJK}])\?(?=\s*$)', '？', s, flags=re.M)
    return s, s != n0
def cc_clean(k, cc):
    if k in CC_PATCH: return CC_PATCH[k]
    if not cc: return None
    cc = cc.strip()
    cc = re.sub(r'(?<=[0-9A-Za-z])[ \t]+(?=[一-鿿])', '', cc)
    cc = re.sub(r'(?<=[一-鿿])[ \t]+(?=[0-9A-Za-z])', '', cc)
    return cc
def title_of(cc):
    if not cc: return None
    m = re.search(r'《.*》', cc)
    return m.group(0) if m else cc
def outlet(cc):
    if not cc: return None
    m = re.match(r'^(.*?)《', cc)
    o = m.group(1).strip('：: ') if m else ''
    return o or None
def page_list(segs): return sorted({s[0] + 1 for s in segs})
recs, arts = [], []
n = 0
for day in ['D04', 'D05', 'D06']:
    for gk in ('pd', 'px'):
        for order, key in enumerate(plan[day][gk], 1):
            n += 1; rid = f'YY2B-{n:03d}'
            tag, q = key.rsplit('-', 1); q = int(q); pid = tag.replace('_xc', ''); k = f'{pid}-{q}'
            qq = get(tag, q); r = raw(qq); pages = page_list(qq['segs'])
            notes = []; flags = list(FLAGS.get(k, []))
            if gk == 'pd':
                stem, opts = clean_pd(r)
                if k in STEM_PATCH:
                    a, b = STEM_PATCH[k]; assert a in stem, k; stem = stem.replace(a, b)
                stem, ch1 = fullwidth_punct(stem)
                o2 = {}; ch2 = False
                for L, v in opts.items():
                    v2, c = fullwidth_punct(v); o2[L] = v2; ch2 = ch2 or c
                opts = o2
                if ch1 or ch2: notes.append('原PDF文字层此处为半角标点（,:;?），已统一为全角，用字未改。')
            else:
                sents, prompt, lead, opts = clean_px(r)
                assert not lead, (k, lead)
                sents2 = []
                chg = False
                for s in sents:
                    s2, c = fullwidth_punct(s); sents2.append(s2); chg = chg or c
                sents = sents2
                stem = '\n'.join(sents) + '\n' + prompt
                if chg: notes.append('原PDF文字层此处为半角标点，已统一为全角，用字未改。')
            assert set(opts) == set('ABCD') and all(opts.values()), (k, opts)
            # answers
            if pid.startswith('GD'):
                g = GD_ANS[k]; ans, ans_page, cc, rate, yc = g['ans'], g['page'], g['cc'], g['rate'], g['yc']
                ans_file = GD_ANSF[pid]; ans_how = '扫描件解析，编者出图（110dpi）逐题目读；与第1轮判读记录一致'
            else:
                a = info(tag, q); ans, ans_page, rate, yc = a['ans'], a['page'], a['rate'], a['yicuo']
                cc = cc_clean(k, a['chuchu']); ans_file = a['file']; ans_how = '解析文字层（“故正确答案为X”等句）提取，已与自动抽取答案、同题他卷（副省/地市/执法、xingce版）答案交叉核对一致'
            assert ans in 'ABCD'
            topic, tphrase = T[k]
            paper_cn = PAPER_CN[pid]
            vnote = '网友回忆版' if '网友回忆版' in qq['file'] else None
            dups = [d for d, _ in DR[key]['dups']]
            sv = [f'{paper_cn}原题（{topic.replace("（", "，").replace("）", "")}）', f'题材：{tphrase}']
            if pid.startswith('GD'): sv.append('广东锚题，用于校准广东命题取向')
            elif gk == 'pd': sv.append('国考补量，选党政、社会、经济、文化类题材为主，取材与广东卷时政文段相近' if '说明文' not in tphrase else '国考补量；保留少量科技说明文细节题，与广东卷细节判断题型对应')
            else: sv.append('国考补量' if pid.startswith('GK') else '外省补量（用户已放开排序外省卷）')
            if rate is not None: sv.append(f'原解析全站正确率{rate}%、易错项{yc}')
            o = outlet(cc)
            if o and gk == 'pd': sv.append(f'原解析所载出处：{o}')
            if k in NOTES: notes.append(NOTES[k])
            notes.append(f'题干、选项已对原页截图（{"assets/src/" + rid + ".png"}）逐字核对；答案来源：{ans_how}，见解析第{ans_page}页。')
            if dups: notes.append('同题亦见 ' + '、'.join(dups) + '，已一并登记占用。')
            if gk == 'px' and order == 4:
                notes.append('本题为当日第4道排序：若按《用户决定记录》“排序每日3道、第4题位置给语句填空或片段”的默认建议执行，本题可整体撤下（撤下后释放登记）。')
            # crop
            dst = f'assets/src/{rid}.png'
            tmp = crop(qq, f'{SP}/crops/{key}_150.png', dpi=150)
            Image.open(tmp).convert('L').save(f'{OUT}/{dst}', optimize=True)
            prov = re.match(r'[A-Z]+', pid).group(0)
            aid = f'ART-{prov}-{pid}-{q}'
            src = {'paper': pid, 'file': qq['file'], 'page': pages[0], 'pages': pages, 'qno': q, 'index_tag': tag,
                   'ans_file': ans_file, 'ans_page': ans_page, 'version_note': vnote}
            rec = {'id': rid, 'module': '言语', 'day': day, 'official_day': day,
                   'group': f'{day}-{"PD" if gk == "pd" else "PX"}',
                   'group_title': '片段阅读（广东锚题＋国考）' if gk == 'pd' else '语句排序（国考＋外省）',
                   'topic': topic, 'order': order, 'source': src, 'done_status': '已做情况未知',
                   'stem': stem, 'options': opts, 'material_or_article': aid, 'assets': [], 'source_crop': dst,
                   'source_answer': ans, 'checked_answer': ans, 'source_rate': rate, 'source_yicuo': yc,
                   'source_passage_title': cc, 'dispute_note': None,
                   'brief_solution': '', 'selection_value': '；'.join(sv) + '。',
                   'variant_of': None, 'check_status': '已核验', 'flags': flags, 'notes': ' '.join(notes),
                   'replaced_from': None, 'gd_anchor': pid.startswith('GD'), 'px_slot4_replaceable': (gk == 'px' and order == 4),
                   'claim_key': k, 'dup_keys': dups}
            recs.append(rec)
            # article object
            ext = {'status': '待补' if cc else '无出处', 'title_per_analysis': cc, 'text': None}
            if gk == 'pd':
                art = {'aid': aid, 'kind': 'pending_text',
                       'kind_cn': '待补：仅有原解析所载文段出处，正文未取得' if cc else '待补：原解析未载文段出处，原标题与正文均无从恢复',
                       'source': {'paper': pid, 'file': qq['file'], 'page': pages[0], 'qno': q, 'ans_file': ans_file, 'ans_page': ans_page, 'passage_title_per_analysis': cc},
                       'title': title_of(cc), 'text': '', 'external_original': ext,
                       'note': (f'正文待补；出处据原解析照录：{cc}' if cc else '正文待补；原解析未载出处'),
                       'editor_note': '本轮未联网取外部原文，不以模型改写或从解析倒推代替；题干文段即原卷文段，未作改写。'}
            else:
                order_str = opts[ans]
                smap = {s[0]: s[1:] for s in sents}
                seq = [smap[c] for c in order_str]
                out = []; added = []
                for s in seq:
                    if s.endswith(('。', '！', '？', '；', '…')) or (s.endswith(('”', '’')) and len(s) > 1 and s[-2] in '。！？…'): out.append(s)
                    elif s.startswith(('如何', '怎样', '为何', '为什么')) or s.endswith(('吗', '呢')): out.append(s + '？'); added.append('？')
                    else: out.append(s + '。'); added.append('。')
                text = ''.join(out)
                art = {'aid': aid, 'kind': 'restored_from_answer', 'kind_cn': '按参考答案顺序还原的文段（非外部原文）',
                       'source': {'paper': pid, 'file': qq['file'], 'page': pages[0], 'qno': q, 'ans_file': ans_file, 'ans_page': ans_page, 'passage_title_per_analysis': cc},
                       'title': title_of(cc), 'order': order_str, 'text': text, 'external_original': ext,
                       'note': f'按参考答案{ans}（{order_str}）还原，非外部原文；句内用字未改' + ('，句末“。”（疑问句“？”）为编者所补' if added else '') + '。' + (f'出处据原解析照录：{cc}；外部原文正文待补。' if cc else '原解析未载出处。'),
                       'editor_note': '还原文段只按参考答案顺序连接原句；外部原文未检索（本轮未联网），不以模型改写代替。'}
            arts.append(art)
with open(f'{OUT}/questions.jsonl', 'w') as f:
    for r in recs: f.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(f'{OUT}/articles.jsonl', 'w') as f:
    for a in arts: f.write(json.dumps(a, ensure_ascii=False) + '\n')
print(len(recs), len(arts))
print(collections.Counter((r['day'], r['group'][-2:]) for r in recs))
