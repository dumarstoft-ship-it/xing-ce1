"""资料减量版两遍题本：资料减量版 + 言语（不变），每天一份 HTML，再由 topdf.js 出 PDF。"""
import os, sys, html as H
sys.path.insert(0, '/home/user/work/books')
import build_print_r3 as B
OUT = '/home/user/work/reduce/out'; os.makedirs(OUT, exist_ok=True)
DAYS = {
 'D05': {'title': 'D05 · 资料减量版 87 问 ＋ 言语 40 题',
         'parts': [('/home/user/work/reduce/md/D05_资料减量版.md', '资料 87 问（含 D02 余下 18 问）'), ('/home/user/work/books/r2_md/D05_言语.md', '言语 40 题')],
         'note': '资料从 135 问减到 87 问：开头 18 问是 D02 你没做的部分里挑出来的（D02 做到材料 60 即算完成），其余删去的题不用补。材料按本册重新编号。言语 40 题与原题本相同。'},
 'D08': {'title': 'D08 · 资料减量版 91 问 ＋ 言语 40 题',
         'parts': [('/home/user/work/reduce/md/D08_资料减量版.md', '资料 91 问'), ('/home/user/work/books/r3_md/D08_言语.md', '言语 40 题')],
         'note': '资料从 135 问减到 91 问，删去的 44 问不用补。材料按本册重新编号。言语 40 题与原题本相同。'},
}
VERSION = '资料减量版，2026-11-11（按用户反馈与 GPT 资料减量建议）；题号、题目、选项、答案都没改，只删题并重排材料编号'
def build(day, cfg, pass_label):
    parts = []
    for i, (p, title) in enumerate(cfg['parts']):
        parts.append(f'<h1 class="part{" first" if i == 0 else ""}">{H.escape(title)}</h1>' + B.md_to_html(p))
    cover = (f'<div class="cover"><div class="big">{H.escape(cfg["title"])}</div><div class="pass">题本 · {pass_label}</div>'
             f'<div class="meta">{VERSION}<br>只含题目，不含答案；答案见打包目录 README<br>'
             f'{"第一遍做完后，第二遍在后面的“第二遍”题本上作答，两遍都做完再核对答案" if pass_label == "第一遍" else "第二遍在本册作答；两遍都做完再核对答案"}</div>'
             f'<div class="note">{H.escape(cfg["note"])}</div></div>')
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{day} 资料减量版 {pass_label}</title><style>{B.CSS}</style></head><body>{cover}{"".join(parts)}</body></html>'
if __name__ == '__main__':
    for day, cfg in DAYS.items():
        for k, label in (('1', '第一遍'), ('2', '第二遍')):
            open(f'{OUT}/{day}_{k}.html', 'w', encoding='utf-8').write(build(day, cfg, label))
        print(day, 'html ok')
