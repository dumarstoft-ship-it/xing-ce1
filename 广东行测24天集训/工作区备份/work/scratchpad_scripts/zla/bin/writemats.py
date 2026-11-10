import json, os, re, sys, shutil, unicodedata, datetime
sys.path.insert(0, os.path.dirname(__file__))
from matspec import MATS, SHARED
from mattext import FIG, MANUAL, MANUAL_NOTE
from render2 import render_material
IDX = '/home/user/work/index'
OUT = '/home/user/work/out'
ZM = f'{OUT}/zl_materials'
JUNK = re.compile(r'(本试卷由粉笔|认准淘宝|通关达人|免费获取更多考公|添加微信|TB:Seeyee|^\s*-\s*\d+\s*-\s*$|^\s*\d+\s*/\s*\d+\s*$|^\s*第\s*\d+\s*[页⻚]|公务员录用考试《行测》题|公务员考试《行测》真题|^第五部分\s*资料分析$|^\d{1,2}$)')
HEAD = re.compile(r'^[（(]\s*(?:[一二三四五六七八九十]|材料\s*\d?)\s*[)）]|^材料$|^[（(]三[)）]根据以下资料')

CJK = r'\u3000-\u303f\u4e00-\u9fff\uff00-\uffef“”‘’（）《》【】'
def despace(s):
    s = re.sub(r'(?<=[%s]) +' % CJK, '', s)
    s = re.sub(r' +(?=[%s])' % CJK, '', s)
    return s

def reflow(t):
    t = t.replace('(', '（').replace(')', '）')
    lines = [l.strip() for l in t.split('\n')]
    lines = [l for l in lines if l and not JUNK.search(unicodedata.normalize('NFKC', l))]
    paras = []; cur = ''
    for l in lines:
        if HEAD.match(unicodedata.normalize('NFKC', l)):
            if cur: paras.append(cur); cur = ''
            paras.append(l); continue
        cur += l
        if re.search(r'[。：:]$', l):
            paras.append(cur); cur = ''
    if cur: paras.append(cur)
    out = '\n'.join(paras)
    out = re.sub(r'(\d) (?=[年月日万亿个家件元%％余起名次])', r'\1', out)   # "2016 年" -> "2016年"
    out = re.sub(r'(?<=[，。；、：,;])[ \t]+', '', out)
    out = despace(out)
    return out

def build_text(mid, raw):
    if mid in MANUAL:
        return MANUAL[mid]
    txt = reflow(raw)
    f = FIG.get(mid, {})
    for pre in f.get('drop', []):
        txt = '\n'.join(l for l in txt.split('\n') if not l.startswith(pre))
    if f.get('head'):
        lines = txt.split('\n')
        if lines and HEAD.match(unicodedata.normalize('NFKC', lines[0])):
            txt = lines[0] + '\n' + f['head'] + ('\n' + '\n'.join(lines[1:]) if len(lines) > 1 else '')
        else:
            txt = f['head'] + ('\n' + txt if txt else '')
    if f.get('insert_after') and f.get('fig'):
        k = f['insert_after']
        assert k in txt, (mid, k)
        txt = txt.replace(k, k + '\n' + f['fig'] + '\n', 1)
    if f.get('mid_after') and f.get('mid'):
        k = f['mid_after']; assert k in txt, (mid, k)
        txt = txt.replace(k, k + '\n' + f['mid'] + '\n', 1)
    if f.get('tail'):
        if f.get('tail_after'):
            k = f['tail_after']; assert k in txt, (mid, k)
            txt = txt.replace(k, k + '\n' + f['tail'] + '\n', 1)
        else:
            txt = txt + '\n' + f['tail']
    txt = re.sub(r'\n{2,}', '\n', txt)
    return txt.strip()

def main(write=True, uses=None):
    uses = uses or {}
    rows = []
    for m in MATS:
        mid = m['mid']; tag = m['tag']
        d = json.load(open(f'{IDX}/{tag}.json')); f = d[0]['file']
        im, raw = render_material(f, m['segs'])
        text = build_text(mid, raw)
        paper = tag.replace('_xc', '') if not mid.startswith('ZLM-GK2022F_xc') else 'GK2022F'
        vnote = m.get('version_note', '') or ('网友回忆版' if '网友回忆' in f else '')
        notes = []
        if mid in MANUAL: notes.append(MANUAL_NOTE)
        if tag == 'GK2022F_xc':
            notes.append('xingce网友回忆版第(三)则（电池制造业）；xing-ce1“副省级”文件中无此材料，两份GK2022F解析均不含本材料，答案由编者独立求解。')
        notes.append(f"建档：ZL-A（{datetime.date.today()}）。图片按原页坐标截取（200dpi），只遮去页码、页眉考试名、店铺/水印广告行并压缩大段空白，不改动内容像素。原卷材料标号：{m['label']}。")
        if uses.get(mid): notes.append('ZL-A 使用本材料的题：' + '；'.join(uses[mid]))
        rec = dict(mid=mid,
                   source=dict(paper=paper, file=f, pages=sorted({s[0] + 1 for s in m['segs']}),
                               segs_0based=[[s[0], round(s[1], 1), round(s[2], 1)] for s in m['segs']], version_note=vnote),
                   text=text,
                   assets=[f'zl_materials/{mid}/{mid}.png'],
                   transcription=FIG.get(mid, {}).get('tr'),
                   notes=' '.join(notes))
        if write:
            os.makedirs(f'{ZM}/{mid}', exist_ok=True)
            if os.path.exists(f'{ZM}/{mid}/material.json'):
                old = json.load(open(f'{ZM}/{mid}/material.json'))
                if 'ZL-A' not in old.get('notes', ''):
                    print('SKIP existing (other editor):', mid); rows.append(old); continue
            im.save(f'{ZM}/{mid}/{mid}.png')
            json.dump(rec, open(f'{ZM}/{mid}/material.json', 'w'), ensure_ascii=False, indent=1)
        rows.append(rec)
    # shared materials built by ZL-B: reuse as-is (read only), add ZL-A usage note in ZL-A's own jsonl only
    for mid in SHARED:
        rec = json.load(open(f'{ZM}/{mid}/material.json'))
        rec = dict(rec)
        rec['notes'] = rec.get('notes', '') + ' ｜ZL-A复用（未改动ZL-B文件）' + ('；ZL-A 使用本材料的题：' + '；'.join(uses.get(mid, [])) if uses.get(mid) else '')
        rows.append(rec)
    return rows

if __name__ == '__main__':
    rows = main(write='--dry' not in sys.argv)
    for r in rows:
        print(r['mid'], len(r['text']), r['text'][:60].replace('\n', ' | '))
