"""Paper registry: map source PDFs to stable paper IDs.
Exam year = 考试年度 as written in the file name (e.g. 国考2025 = 2025年度)."""
import os, re, json, hashlib
ROOT = '/home/user'
RAW = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/inventory_raw.json'

PROV = [('广东选调', 'GDXD'), ('广东', 'GD'), ('国家', 'GK'), ('国考', 'GK'), ('浙江', 'ZJ'), ('江苏', 'JS'), ('山东', 'SD'),
        ('四川', 'SC'), ('河北', 'HB'), ('深圳', 'SZ'), ('云南', 'YN'), ('内蒙古', 'NM'), ('湖北', 'HUB'), ('重庆', 'CQ'),
        ('辽宁', 'LN'), ('贵州', 'GZ')]

def classify(path):
    name = os.path.basename(path)
    m = re.search(r'(20\d\d)', name)
    year = int(m.group(1)) if m else None
    prov = None
    if '选调' in name and '广东' in name: prov = 'GDXD'
    elif '选调' in name and '浙江' in name: prov = 'ZJXD'
    else:
        for k, v in PROV:
            if k in name: prov = v; break
    if prov is None and '/国考/' in path: prov = 'GK'
    # paper variant
    var = ''
    if prov == 'GK':
        if '副省' in name or '省级' in name: var = 'F'
        elif '地市' in name or '市地' in name: var = 'D'
        elif '行政执法' in name: var = 'X'
        elif re.search(r'[（(]?A卷|一[）)]', name): var = 'A'
        elif re.search(r'B卷|二[）)]', name): var = 'B'
    elif prov == 'GD':
        if '乡镇' in name and '县级' in name: var = ''  # 统一卷
        elif '乡镇' in name: var = 'Z'
        elif '县级' in name: var = 'X'
        elif '一卷' in name: var = '1'
        elif '三卷' in name: var = '3'
        elif '上半年' in name: var = 'S'
        elif '下半年' in name: var = 'H'
    elif prov == 'GDXD':
        if '思维' in name: var = 'SW'
        elif '综合行政' in name: var = 'ZH'
        else: var = 'XC'
    elif prov == 'SZ':
        if '思维' in name: var = 'SW'
        elif '行测1' in name: var = '1'
        elif '行测2' in name: var = '2'
    elif prov == 'SC':
        if '0327' in name or '上半年' in name or '0326' in name: var = 'S'
        elif '下半年' in name or '1206' in name: var = 'H'
        elif '0725' in name: var = 'S'
    elif prov in ('ZJ',):
        if 'B卷' in name: var = 'B'
        else: var = 'A'
    elif prov == 'JS':
        var = 'A'
    kind = 'ans' if any(k in name for k in ['解析', '答案']) else 'q'
    if '数量关系答案' in name or '资料分析答案' in name or '政治理论答案' in name: kind = 'ans_part'
    recall = '网友回忆' in name
    pid = f"{prov}{year}{var}" if prov and year else None
    return dict(pid=pid, prov=prov, year=year, var=var, kind=kind, recall=recall, name=name)

def registry():
    rows = json.load(open(RAW))
    out = []
    for r in rows:
        if not r['path'].lower().endswith(('.pdf', '.docx')): continue
        c = classify(r['path'])
        c.update(path=r['path'], md5=r['md5'], pages=r.get('pages'), text=r.get('text_chars_all', 0))
        out.append(c)
    return out

if __name__ == '__main__':
    reg = registry()
    import collections
    by = collections.defaultdict(list)
    for r in reg: by[(r['pid'], r['kind'])].append(r)
    for k in sorted(by, key=lambda x: (str(x[0]), x[1])):
        v = by[k]
        print(k, len(v), [ (x['path'].split('/')[0], x['md5'][:6], x['text']) for x in v])
