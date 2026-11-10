import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import META, SCAN_ANS, GD2021X_FILE
from g1 import G1
from g2 import G2
from g3 import G3
from g4 import G4

OUT = '/home/user/work/out3/PD3B/questions.jsonl'
claims = [json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
mine = {c['key']: c for c in claims if c['owner'] == 'PD3B'}

def version_note(f, extra=None):
    if extra: return extra
    if f.startswith('xingce/'):
        return '网友回忆版' if '网友回忆版' in f else 'xingce 版（文件名未标回忆版）'
    return 'xing-ce1 题本'

VN = {
 'GD2022X-58': 'xing-ce1 题本；xingce 同卷标“网友回忆版（县级卷）”，与本版逐字一致（标点除外）',
 'GD2022X-60': 'xing-ce1 题本；xingce 同卷标“网友回忆版（县级卷）”，与本版逐字一致（标点除外）',
 'GD2022X-66': 'xing-ce1 题本；xingce 同卷标“网友回忆版（县级卷）”，与本版逐字一致（标点除外）',
 'GD2022X-70': 'xing-ce1 题本；xingce 同卷标“网友回忆版（县级卷）”，与本版逐字一致（标点除外）',
 'GD2022X-73': 'xing-ce1 题本；D项“戒骄成躁”按 xingce 网友回忆版（xingce/2022年广东省公务员录用考试《行测》题（县级卷）（网友回忆版）.pdf 第15页）改作“戒骄戒躁”，其余逐字一致',
 'GD2023X-59': 'xing-ce1 题本；xingce 同卷标“网友回忆版（县级卷）”，与本版逐字一致（标点除外）',
 'GD2023X-67': 'xing-ce1 题本；xingce 同卷标“网友回忆版（县级卷）”，与本版逐字一致（标点除外）',
 'GK2021D-101': 'xing-ce1 地市级题本为出处与解析；题干、选项文字按同题 GK2021F-107 的 xingce 副省级网友回忆版（xingce/2021年国家公务员录用考试《行测》题（副省级网友回忆版）.pdf 第21页）录入，xing-ce1 两版“皮表干细胞”“胶原带白”为转录错字',
 'GD2021X-64': '县级卷扫描件（不在索引），对照原页逐字录入',
 'GD2021X-66': '县级卷扫描件（不在索引），对照原页逐字录入',
 'GK2023X-104': 'xing-ce1 题本；题干箭头为图形字符，按原页补回',
 'JS2023A-96': 'xingce 版（文件名未标回忆版）；索引误将97～98题共用题干并入D项，已按原页删去',
}

ORDER = {
 # D09-B1：削弱/加强交替，避免同字母三连
 'GD2017-52': 1, 'GK2025D-103': 2, 'GD2015X-59': 3, 'GK2019F-107': 4, 'SC2020H-82': 5, 'GD2021X-64': 6,
 'GK2017D-101': 7, 'GDXD2019SW-15': 8, 'JS2021A-96': 9, 'HB2024-101': 10, 'GK2020D-105': 11, 'GDXD2020SW-23': 12,
 'GK2023X-104': 13, 'SC2020H-83': 14, 'GK2021D-101': 15,
 # D09-B2：前提/解释交替
 'GD2019X-48': 1, 'GD2023X-67': 2, 'GK2020D-103': 3, 'GD20131-82': 4, 'GD2014X-83': 5, 'JS2023A-96': 6,
 'GDXD2019SW-7': 7, 'GK2015D-107': 8, 'JS2020A-93': 9, 'GD2022X-66': 10, 'HB2022-106': 11, 'SD2024-93': 12,
 'GD2021X-66': 13, 'JS2022A-95': 14, 'GDXD2020SW-35': 15, 'GD2023X-59': 16, 'GK2023D-101': 17, 'SZ2020SW-79': 18,
 'GD2022X-58': 19, 'GD2022X-60': 20,
}
recs = []
for r in G1 + G2 + G3 + G4:
    key = r['key']; pid, q = key.rsplit('-', 1); q = int(q)
    if pid == 'GD2021X':
        f, pages, ans_file = GD2021X_FILE, [8], SCAN_ANS['GD2021X']
        ans_page = r['ans_page']; src_imgs = [f'assets/src/GD2021X_q{q}.png']
    else:
        m = META[key]
        f, pages = m['file'], m['pages']
        src_imgs = []
        if pid in SCAN_ANS:
            ans_file, ans_page = SCAN_ANS[pid], r['ans_page']
        else:
            ans_file = m['ans_file']; ans_page = r.get('ans_page') or m['ans_hits'][0]
    c = mine.get(key)
    same = sorted(set(c['dups']) - {key}) if c else []
    flags = list(r.get('flags', []))
    if '网友回忆版' in version_note(f) and '网友回忆版' not in flags: flags.append('网友回忆版')
    rec = {
        'id': r['id'], 'module': '判断', 'day': 'D09',
        'group': r['group'], 'group_title': r.get('group_title') or ('逻辑·冲突待复核（不计入正式包）' if r['group'].endswith('BX') else '逻辑·备选（已核验，不计入正式包）'),
        'topic': r['topic'], 'order': ORDER.get(key, r['order']) if r['group'] in ('D09-B1','D09-B2') else r['order'],
        'source': {'paper': pid, 'file': f, 'page': pages[0], 'pages': pages, 'qno': q,
                   'ans_file': ans_file, 'ans_page': ans_page, 'version_note': VN.get(key) or version_note(f)},
        'done_status': '已做情况未知',
        'stem': r['stem'], 'options': r['options'], 'material_or_article': None, 'assets': [],
        'source_answer': r['src'], 'checked_answer': r['chk'],
        'brief_solution': r['sol'], 'selection_value': r['val'], 'variant_of': None,
        'check_status': r.get('status', '已核验'), 'flags': flags, 'notes': r['notes'],
        'source_key': key, 'source_rate': r.get('rate'), 'source_yicuo': r.get('yicuo'),
        'difficulty_est': r.get('diff'), 'same_item_in': same, 'replaced_from': None,
    }
    if src_imgs: rec['source_images'] = src_imgs
    if r.get('editor_lean'): rec['editor_lean'] = r['editor_lean']
    recs.append(rec)

grp_rank = {'D09-B1': 0, 'D09-B2': 1, 'D09-B3': 2, 'D09-BX': 3, 'D09-BR': 4}
recs.sort(key=lambda x: (grp_rank[x['group']], x['order']))
n = 0
for rec in recs:
    if rec['group'] in ('D09-B1', 'D09-B2', 'D09-B3'):
        n += 1; rec['id'] = f'PD3B-{n:03d}'
with open(OUT, 'w') as fo:
    for rec in recs:
        fo.write(json.dumps(rec, ensure_ascii=False) + '\n')
print(len(recs), 'records written')
