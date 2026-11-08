"""主旨题存档：python3 -I zz_pack.py <结果.json> <文章目录> <输出.json>
仓库是公开的，不放文章原文。题干材料换成对原文第 from_p 到 to_p 段的删改记录 edits：
["-", 起, 止] 删去原文这几个字，["+", 位置, 文字] 在原文这个位置添上文字（只有几个连接的字）。
建网页时用原文按 edits 还原题干；这里先还原一遍，确认和原来的题干一字不差。"""
import json, sys, os, difflib

def pack(orig, passage):
    ed = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, orig, passage, autojunk=False).get_opcodes():
        if tag in ('delete', 'replace'): ed.append(['-', i1, i2])
        if tag in ('insert', 'replace'): ed.append(['+', i2 if tag == 'replace' else i1, passage[j1:j2]])
    return ed

def unpack(orig, ed):
    out, pos = [], 0
    for e in ed:
        if e[0] == '-':
            out.append(orig[pos:e[1]]); pos = e[2]
        else:
            out.append(orig[pos:e[1]]); pos = e[1]; out.append(e[2])
    out.append(orig[pos:])
    return ''.join(out)

if __name__ == '__main__':
    src, adir, dst = sys.argv[1:4]
    r = json.load(open(src, encoding='utf-8'))
    n = 0
    for art in r['articles']:
        a = json.load(open(os.path.join(adir, art['id'] + '.json'), encoding='utf-8'))
        for q in art['questions']:
            orig = '\n'.join(a['paras'][p - 1] for p in range(q['from_p'], q['to_p'] + 1))
            pas = q.pop('passage').strip()
            q['edits'] = pack(orig, pas)
            assert unpack(orig, q['edits']) == pas, (art['id'], q['from_p'])
            n += 1
    json.dump(r, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{dst}：{n} 题，还原核对无误')
