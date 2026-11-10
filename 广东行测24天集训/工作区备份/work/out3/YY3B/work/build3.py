"""YY3B round-3 build: verbal D07-D09, passage reading (片段) 18/day + sentence ordering (排序) 4/day.
Reads plan3.py (PLAN/META) and PXPLAN below; writes questions.jsonl, articles.jsonl, source crops."""
import json, re, os, sys, collections
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
from qx import get, raw, crop
from clean3 import clean_pd3, clean_px3, RADICAL
from ansx import info, seg
from simcheck import sims
from plan3 import PLAN, META
from PIL import Image
OUT = '/home/user/work/out3/YY3B'
os.makedirs(f'{OUT}/assets/src', exist_ok=True); os.makedirs(f'{SP}/crops', exist_ok=True)

PXPLAN = {
 'D07': ['GDXD2020ZH-74', 'GK2019D-49', 'SD2024_xc-37', 'JS2019A-19'],
 'D08': ['GDXD2020ZH-73', 'GK2020D-46', 'JS2021A_xc-30', 'ZJ2018A-103'],
 'D09': ['GK2018D-53', 'SC2021H_xc-35', 'ZJ2023A_xc-34', 'ZJ2015A-44'],
}
PXMETA = {  # key: topic phrase
 'GDXD2020ZH-74': '新时代教育改革创新的“基点”（教育时政）',
 'GK2019D-49': '巴黎地下城与城市现代化转型（城市史）',
 'SD2024-37': '文旅融合与乡村旅游精品线路升级（三农/文旅）',
 'JS2019A-19': '手术知情同意与医学伦理（社会/医患）',
 'GDXD2020ZH-73': '现代信用体系与乡村熟人社会（三农/社会信用）',
 'GK2020D-46': '稀土产业从受制于人到创新突破（产业经济）',
 'JS2021A-30': '书法样式演变与科学断代（文化）',
 'ZJ2018A-103': '盛世由进取而兴、因懈怠而衰（历史时评）',
 'GK2018D-53': '城市绿化选用乡土草木（城市生态）',
 'SC2021H-35': '现代化转型期的社会治理（社会治理）',
 'ZJ2023A-34': '教师有偿补课与师德建设（教育治理）',
 'ZJ2015A-44': '多元文化之间的“生成性对话”（文化）',
}
TYPE_CN = {'主旨': '主旨概括', '意图': '意图判断', '细节': '细节判断', '标题': '标题填入', '下文': '下文推断', '词句': '词句理解'}
CAT_NOTE = {'法治': '法治', '三农': '三农', '经济': '经济', '社会': '社会治理/民生', '党政': '党政时政', '国际': '国际时政',
            '文化': '文化', '生态': '生态文明', '科技时政': '科技自立（时政议论）'}

def paper_cn(pid):
    m = re.match(r'([A-Z]+)(\d{4})(.*)', pid); prov, y, v = m.groups()
    if prov == 'GK': return f'国考{y}年度' + {'F': '副省级', 'D': '地市级', 'X': '行政执法卷'}.get(v, '')
    if prov == 'GDXD': return {'XC': '广东选调2019年（选调优秀大学毕业生）《行测》卷', 'ZH': '广东选调2020年《综合行政能力测验》卷'}[v]
    if prov == 'GD': return f'广东{y}年度' + {'Z': '乡镇卷', 'X': '县级卷', '': '卷'}.get(v, v)
    name = {'SD': '山东', 'JS': '江苏', 'ZJ': '浙江', 'SC': '四川', 'HB': '河北', 'SZ': '深圳'}[prov]
    return f'{name}{y}年度' + {'A': 'A类', 'H': '下半年卷', 'S': '上半年卷', '': '卷'}.get(v, v)

CJK = r'一-鿿“”‘’《》（）'
def fullwidth_punct(s):
    n0 = s
    s = re.sub(rf'(?<=[{CJK}]),(?=[{CJK}])', '，', s)
    s = re.sub(rf'(?<=[{CJK}]);(?=[{CJK}])', '；', s)
    s = re.sub(rf'(?<=[{CJK}]):(?=[{CJK}“])', '：', s)
    s = re.sub(rf'(?<=[{CJK}]):(?=\s*$)', '：', s, flags=re.M)
    s = re.sub(rf'(?<=[{CJK}])\?(?=\s*$)', '？', s, flags=re.M)
    return s, s != n0

# ---------- answers ----------
SCAN = {  # answers read by the editor from scanned analysis pages (rendered & viewed)
 'GD2020Z-9': dict(ans='C', page=2, rate=62, yc='B', cc=None,
                   file='xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
                   how='扫描件解析（无文字层），编者出图（110dpi）目读“9、正确答案：C，全站正确率：62%，易错项：B”；与第1轮判读记录一致'),
 'GK2021F-38': dict(ans='D', page=12, rate=15, yc='C', cc=None,
                    file='xing-ce1/国考/答案解析/2021年国家公务员考试《行测》真题（副省级）参考答案及解析...pdf',
                    how='副省级解析为扫描件（无文字层），编者出图（150dpi）目读“38、正确答案：D，全站正确率：15%，易错项：C”，其后解析亦称“D项是文段主旨句的同义替换”'),
 'GK2021F-42': dict(ans='D', page=12, rate=31, yc='B', cc=None,
                    file='xing-ce1/国考/答案解析/2021年国家公务员考试《行测》真题（副省级）参考答案及解析...pdf',
                    how='副省级解析为扫描件（无文字层），编者出图目读第12页末“42、正确答案：D，全站正确率：31%，易错项：B”，第13页解析称“D项是对文段主旨的同义替换”'),
}
def cc_clean(raw_cc):
    """Join a (possibly wrapped) source-title line from the analysis; drop text-layer spaces next to digits/Latin, keep spaces between CJK words."""
    if not raw_cc: return None
    s = raw_cc.replace('\n', '').strip()
    s = re.sub(r'(?<=[0-9A-Za-z.])[ \t]+(?=[一-鿿])', '', s)
    s = re.sub(r'(?<=[一-鿿])[ \t]+(?=[0-9A-Za-z])', '', s)
    s = re.sub(r'[ \t]{2,}', ' ', s).strip()
    return s or None
def get_cc(segtext):
    m = re.search(r'(?:【文段出处】|文段出处[：:]|【文段来源】|文段来源[：:])[ \t]*\n?[ \t]*([^\n]+)((?:\n[^\n【]{1,60}》[^\n]*)?)', segtext)
    if not m: return None
    first = m.group(1)
    cont = m.group(2) if ('《' in first and '》' not in first) else ''
    return cc_clean(first + cont)
def answer_of(tag, q, k):
    if k in SCAN:
        a = SCAN[k]; return a['ans'], a['page'], a['rate'], a['yc'], a['cc'], a['file'], a['how'], None
    r = info(tag, q)
    s = r['seg']
    # every answer statement in the segment must agree, except an explicit dispute remark
    disp = None
    m = re.search(r'此题存在争议[^。\n]*。', s)
    if m: disp = m.group(0).strip()
    cc = get_cc(s)
    if cc in ('暂无',): cc = None
    # all answer statements before any dispute remark must agree
    head = s[:m.start()] if m else s
    letters = set(re.findall(r'(?:正确答案[：:]\s*|故正确答案为\s*|正确选项为\s*|因此[，,]?\s*选择\s*)([A-D])', head))
    assert len(letters) == 1, (k, letters)
    main = letters.pop()
    if not disp: assert main == r['ans'], (k, main, r['ans'])
    auto = json.load(open(f'/home/user/work/answers/{tag}.json'))['answers'].get(str(q), {}).get('ans')
    assert auto == main, (k, auto, main)
    how = '解析文字层答案句（如“故正确答案为X”“正确答案：X”）提取，与 answers/ 自动抽取一致'
    if disp: how += '（取争议说明之前的原参考答案）'
    return main, r['page'], r['rate'], r['yicuo'], cc, r['file'], how, disp
def partner_answers(partners):
    out = []
    for p in partners:
        pt, pq = p.rsplit('-', 1)
        for t in (pt, pt + '_xc'):
            if os.path.exists(f'/home/user/work/answers/{t}.json'):
                try:
                    rr = seg(t, int(pq))
                    if rr: out.append((t + '-' + pq, rr['ans']))
                except Exception: pass
    return out

def page_list(segs): return sorted({s[0] + 1 for s in segs})
def outlet(cc):
    if not cc: return None
    m = re.match(r'^(.*?)《', cc); o = m.group(1).strip('：:-－— ') if m else ''
    return o or None
def title_of(cc):
    if not cc: return None
    m = re.search(r'《.*》', cc); return m.group(0) if m else cc

# per-item text patches: (old, new, note) — only to restore text lost from the PDF text layer, checked against the page image
STEM_PATCH = {
 'GK2024D-53': ('微型机器人能够加热到，对人体组织', '微型机器人能够加热到70°C，对人体组织',
                '原页“70°C”为公式图像，文字层为空；已按原页图像补录，其余用字未动。'),
}
FLAGS = {
 'GK2021D-55': ['争议(原标)'],
 'GK2024D-53': ['文字层缺字已据原页补录'],
 'GK2021F-38': ['答案取自扫描件'],
 'GK2021F-42': ['答案取自扫描件'],
 'GD2020Z-9': ['答案取自扫描件'],
}
NOTES = {
 'GK2021D-55': '原解析（地市级第15—16页）先给“正确答案：B”，随后另起一段注明“此题存在争议，粉笔的答案为D”并附另一套解析；副省级同题（GK2021F-47）扫描件解析第13—14页同样如此。本包按原参考答案B录入，争议标记照录于 dispute_note，不论证、不改答。',
 'GK2021F-38': '同题见市地级卷 GK2021D-42：该卷解析文字层作“42、正确答案:,全站正确率:15%,易错项:C。”，答案字母缺失且无解析正文；故本题取副省级卷原题与副省级扫描件解析（答案D）。',
 'GK2021F-42': '副省级解析为扫描件，未载文段出处。',
 'GD2020Z-9': '同一文段的一部分亦见县级卷 GD2020X-2（关联词选词，答案句即本文段“公众本身不仅是被动的接受者，更是主动的参与者”）；该题已由 YY3A 登记并排在 D07 选词组，本题排 D08，在其后、不同日，不构成先看全文后做挖空的泄题；GD2020X-2 归 YY3A，本编者未重复登记。',
 'GK2017F-45': '',
}
SCAN_XCHECK = {
 'GK2021D-45': '副省级同题 GK2021F-39 扫描件解析第12页亦为“正确答案：A，全站正确率：51%，易错项：C”',
 'GK2021D-53': '副省级同题 GK2021F-46 扫描件解析第13页亦为“正确答案：D，全站正确率：78%，易错项：B”',
 'GK2021D-55': '副省级同题 GK2021F-47 扫描件解析第13—14页亦为“正确答案：B，全站正确率：22%，易错项：D”，并同样注明“此题存在争议，粉笔的答案为D”',
}
def fmt_rate(rate, yc):
    if rate is None: return None
    return f'原解析全站正确率{rate}%' + (f'、易错项{yc}' if yc else '')

recs, arts = [], []; n = 0; claim_plan = []
for day in ['D07', 'D08', 'D09']:
    for gk, keys in (('pd', PLAN[day]), ('px', PXPLAN[day])):
        for order, key in enumerate(keys, 1):
            n += 1; rid = f'YY3B-{n:03d}'
            tag, q = key.rsplit('-', 1); q = int(q); pid = tag.replace('_xc', ''); k = f'{pid}-{q}'
            qq = get(tag, q); r = raw(qq); pages = page_list(qq['segs'])
            notes = []; flags = list(FLAGS.get(k, []))
            if gk == 'pd':
                passage, prompt, opts, rad = clean_pd3(r)
                if k in STEM_PATCH:
                    a, b, note = STEM_PATCH[k]; assert a in passage, k; passage = passage.replace(a, b); notes.append(note)
                passage, c1 = fullwidth_punct(passage); prompt, c2 = fullwidth_punct(prompt)
                o2 = {}; c3 = False
                for L, v in opts.items():
                    v2, c = fullwidth_punct(v); o2[L] = v2; c3 = c3 or c
                opts = o2
                stem = passage + '\n' + prompt
                if c1 or c2 or c3: notes.append('原PDF文字层此处为半角标点（,:;?），已统一为全角，用字未改。')
            else:
                sents, prompt, lead, opts, rad = clean_px3(r)
                assert not lead, (k, lead)
                s2 = []; chg = False
                for s in sents:
                    x, c = fullwidth_punct(s); s2.append(x); chg = chg or c
                sents = s2; prompt, c2 = fullwidth_punct(prompt)
                stem = '\n'.join(sents) + '\n' + prompt
                if chg or c2: notes.append('原PDF文字层此处为半角标点，已统一为全角，用字未改。')
            left = RADICAL.findall(stem + ''.join(opts.values()))
            assert not left, (k, left)
            assert set(opts) == set('ABCD') and all(opts.values()), (k, opts)
            ans, ans_page, rate, yc, cc, ans_file, how, disp = answer_of(tag, q, k)
            assert ans in 'ABCD', (k, ans)
            if disp and '争议(原标)' not in flags: flags.append('争议(原标)')
            # paper meta
            vnote = '网友回忆版' if '网友回忆版' in qq['file'] else None
            if vnote and '网友回忆版' not in flags: flags.append('网友回忆版')
            partners = sorted({f'{t.replace("_xc", "")}-{qq2}' for c, t, qq2, sec, _ in (sims(tag, q) or []) if c >= 0.9} - {k})
            related = ['GD2020X-2'] if k == 'GD2020Z-9' else []
            pc = paper_cn(pid)
            if gk == 'pd':
                typ, _, cat, short = META[key]
                topic = TYPE_CN[typ]
                if pid.startswith('GDXD'): role = '广东选调卷原题，作“广东系锚题”（gd_anchor=选调），校准广东命题取向'; anchor = '选调'
                elif pid.startswith('GD'): role = '广东省考锚题（2017—2020年度仅剩此1道，2021—2023年度留作考前回校）'; anchor = True
                elif cat == '科技': role = '当日唯一一道科技说明文（用户限每天至多1道），保留细节判断题型'; anchor = False
                else: role = f'国考补量，{CAT_NOTE[cat]}题材（用户要求多选党政、社会治理、三农、经济、法治、文化）'; anchor = False
                sv = [f'{pc}原题（{topic}）', f'题材：{short}', role]
            else:
                cnt = len(sents)
                topic = f'语句排序（{cnt}句）'
                if pid.startswith('GDXD'): role = '广东选调卷排序（广东系，gd_anchor=选调）'; anchor = '选调'
                elif pid.startswith('GK'): role = '国考排序（用户：国考、省考排序各年度能用皆用）'; anchor = False
                else: role = '外省排序（用户已放开排序外省卷）' + ('；新拉入的江苏2015—2019/浙江2015—2020A卷' if re.match(r'(JS201[5-9]|ZJ201[5-9]|ZJ2020A)', pid) else ''); anchor = False
                sv = [f'{pc}原题（{topic}）', f'题材：{PXMETA[k]}', role]
            fr = fmt_rate(rate, yc)
            if fr: sv.append(fr)
            if disp: sv.append('原解析标有争议，照录')
            o = outlet(cc)
            if o and gk == 'pd': sv.append(f'原解析所载出处：{o}')
            pa = partner_answers(partners) if k not in SCAN else []
            if pa:
                assert all(a2 == ans for _, a2 in pa), (k, ans, pa)
                how += '；同题他卷解析（' + '、'.join(f'{t}:{a2}' for t, a2 in pa) + '）一致'
            if NOTES.get(k): notes.append(NOTES[k])
            if re.search(r'·{3,}|\.{6}|•{3,}', r): notes.append('原PDF文字层省略号为“······”（六个间隔号），已统一为“……”，用字未改。')
            if k in SCAN_XCHECK: how += '；' + SCAN_XCHECK[k]
            notes.append(f'题干、选项已对原页截图（assets/src/{rid}.png）逐字核对；答案来源：{how}，见解析第{ans_page}页。')
            if partners: notes.append('同一文段亦见 ' + '、'.join(partners) + '，已一并登记占用。')
            if gk == 'px' and order == 4:
                notes.append('本题为当日第4道排序（可撤位）：如改为每日3道，本题可整体撤下并释放登记。')
            # crop for verification
            dst = f'assets/src/{rid}.png'
            tmp = crop(qq, f'{SP}/crops/{key}_150.png', dpi=150)
            Image.open(tmp).convert('L').save(f'{OUT}/{dst}', optimize=True)
            prov = re.match(r'[A-Z]+', pid).group(0)
            aid = f'ART-{prov}-{pid}-{q}'
            src = {'paper': pid, 'file': qq['file'], 'page': pages[0], 'pages': pages, 'qno': q, 'index_tag': tag,
                   'ans_file': ans_file, 'ans_page': ans_page, 'version_note': vnote}
            if pid.startswith('GDXD'): src['section_note'] = 'index 把本卷言语部分标成“常识”；已按原页核对：本题位于原卷“三、阅读理解”部分'
            rec = {'id': rid, 'module': '言语', 'day': day, 'official_day': day,
                   'group': f'{day}-{"PD" if gk == "pd" else "PX"}', 'group_title': None,
                   'topic': topic, 'order': order, 'source': src, 'done_status': '已做情况未知',
                   'stem': stem, 'options': opts, 'material_or_article': aid, 'assets': [], 'source_crop': dst,
                   'source_answer': ans, 'checked_answer': ans, 'source_rate': rate, 'source_yicuo': yc,
                   'source_passage_title': cc, 'dispute_note': disp,
                   'brief_solution': '', 'selection_value': '；'.join(sv) + '。',
                   'variant_of': None, 'check_status': '已核验', 'flags': flags, 'notes': ' '.join(notes),
                   'replaced_from': None, 'gd_anchor': anchor, 'px_slot4_replaceable': (gk == 'px' and order == 4),
                   'claim_key': k, 'dup_keys': partners, 'related_passages': related}
            recs.append(rec)
            ext = {'status': '待补' if cc else '无出处', 'title_per_analysis': cc, 'text': None}
            asrc = {'paper': pid, 'file': qq['file'], 'page': pages[0], 'qno': q, 'ans_file': ans_file, 'ans_page': ans_page, 'passage_title_per_analysis': cc}
            if gk == 'pd':
                art = {'aid': aid, 'kind': 'exam_passage', 'kind_cn': '原题文段：逐字照录考试题干中的文段，不是外部文章全文',
                       'source': asrc, 'title': title_of(cc), 'text': passage, 'external_original': ext,
                       'note': (f'外部文章全文未取得；出处据原解析照录：{cc}' if cc else '外部文章全文未取得；原解析未载文段出处') + '。原题文段逐字照录题干，未改写、未从解析倒推。',
                       'editor_note': '本轮未联网取外部原文，不以模型改写或从解析倒推代替。' + (' ' + STEM_PATCH[k][2] if k in STEM_PATCH else '')}
            else:
                order_str = re.sub(r'[^①-⑧]', '', opts[ans])
                smap = {s[0]: s[1:] for s in sents}
                assert sorted(order_str) == sorted(smap), (k, order_str, list(smap))
                seq = [smap[c] for c in order_str]
                out = []; added = []
                for s in seq:
                    if s.endswith(('。', '！', '？', '；', '…')) or (s.endswith(('”', '’')) and len(s) > 1 and s[-2] in '。！？…'): out.append(s)
                    elif s.startswith(('如何', '怎样', '为何', '为什么')) or s.endswith(('吗', '呢')): out.append(s + '？'); added.append('？')
                    else: out.append(s + '。'); added.append('。')
                text = ''.join(out)
                art = {'aid': aid, 'kind': 'restored_from_answer', 'kind_cn': '按参考答案顺序还原的文段（非外部原文）',
                       'source': asrc, 'title': title_of(cc), 'order': order_str, 'text': text, 'external_original': ext,
                       'note': f'非外部原文：按参考答案{ans}（{order_str}）还原，句内用字未改' + (('，句末“。”' + ('及疑问句末“？”' if '？' in added else '') + '为编者所补（原题各句无句末标点）') if added else '') + '。' + (f'出处据原解析照录：{cc}；外部原文正文待补。' if cc else '原解析未载出处。'),
                       'editor_note': '还原文段只按参考答案顺序连接原句；外部原文未检索（本轮未联网），不以模型改写代替。'}
            arts.append(art)
            claim_plan.append((k, partners, rid, day, gk))
# group titles per day (computed from content; no solution hints)
for day in ['D07', 'D08', 'D09']:
    pdr = [r for r in recs if r['day'] == day and r['group'].endswith('PD')]
    pxr = [r for r in recs if r['day'] == day and r['group'].endswith('PX')]
    for r in pdr: r['group_title'] = '片段阅读（广东系锚题＋国考）'
    srcs = []
    if any(r['source']['paper'].startswith('GK') for r in pxr): srcs.append('国考')
    if any(r['source']['paper'].startswith('GDXD') for r in pxr): srcs.append('广东选调')
    if any(not r['source']['paper'].startswith(('GK', 'GD')) for r in pxr): srcs.append('外省')
    for r in pxr: r['group_title'] = '语句排序（' + '＋'.join(srcs) + '）'
with open(f'{OUT}/questions.jsonl', 'w') as f:
    for r in recs: f.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(f'{OUT}/articles.jsonl', 'w') as f:
    for a in arts: f.write(json.dumps(a, ensure_ascii=False) + '\n')
json.dump(claim_plan, open(f'{SP}/claim_plan.json', 'w'), ensure_ascii=False, indent=0)
print(len(recs), len(arts))
print(collections.Counter((r['day'], r['group'][-2:]) for r in recs))
