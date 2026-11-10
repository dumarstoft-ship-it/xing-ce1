import pool, os, re, json, sys, collections
SCOPE = []
for f in sorted(os.listdir('/home/user/work/index')):
    t = f[:-5]; pid = t.replace('_xc', '')
    m = re.match(r'([A-Z]+?)(20\d\d)', pid); prov, yr = m.group(1), int(m.group(2))
    ok = False
    if prov == 'GD' and yr <= 2023: ok = True
    if prov == 'GDXD': ok = True
    if prov == 'GK' and yr <= 2025: ok = True
    if prov in ('HB','SC','SD','SZ','ZJ','JS') and yr >= 2015: ok = True
    if prov == 'ZJXD': ok = True
    if ok: SCOPE.append(t)
# prefer xing-ce1 version when both exist; keep _xc tags only if no plain tag
plain = {t for t in SCOPE if not t.endswith('_xc')}
SCOPE = [t for t in SCOPE if not (t.endswith('_xc') and t[:-3] in plain)]
ARG = re.compile(r'削弱|加强|支持|质疑|反驳|前提|假设|解释|评价|论证方式|论证结构|相似|最为类似|最类似|类似|不能成为|理由|论点|结论成立|有助于|反对|上述论证|上述推理的漏洞|漏洞|缺陷|错误相同')
FORMAL = re.compile(r'只有|除非|如果|若|才|那么|则|否则|所有|有的|都|真话|假话|为真|为假|说对|说错|猜对|猜测|一定|必然|可能|不可能|或者|要么|并非|并且|每')
ANAL = re.compile(r'甲|乙|丙|丁|戊|分别|各|名次|排序|顺序|座位|相邻|左|右|值班|周[一二三四五六日]|星期|安排|分配|匹配|编号|号|位置|组|职业|来自')
def kind(text):
    t = text
    if '根据上述定义' in t or '定义的是' in t or '符合上述定义' in t or '属于' in t and '定义' in t: return 'def'
    if re.search(r'[：:]\S{1,8}\s*\n?\s*A[、\.．]', t[:120]) and len(t) < 200: return 'analogy'
    if ARG.search(t): return 'arg'
    return 'other'
def main():
    out = []
    for t in SCOPE:
        pid = t.replace('_xc', '')
        d = pool.idx(t)
        for q in d:
            if q.get('kind') != 'q': continue
            sec = q.get('section')
            if sec not in ('判断', None): continue
            txt = q['text']
            if q.get('images') and len(txt) < 150: continue
            k = kind(txt)
            if k in ('def', 'analogy'): continue
            if len(txt) < 120: continue
            key = f"{pid}-{q['qno']}"
            tk = pool.taken(key)
            out.append(dict(key=key, tag=t, kind=k, taken=tk, text=txt))
    json.dump(out, open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd4c/logic_all.json', 'w'), ensure_ascii=False)
    c = collections.Counter((x['kind'], bool(x['taken'])) for x in out)
    print(c)
main()
