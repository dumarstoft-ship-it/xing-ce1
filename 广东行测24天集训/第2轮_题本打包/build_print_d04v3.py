"""第2轮 D04 重新打包：数量用 GPT main 上的 D04-减量73题-v3，言语 40 题不变。"""
import os, sys, html as H
sys.path.insert(0, '/home/user/work/books')
import build_print_r3 as B
OUT = '/home/user/work/books/out_d04v3'; os.makedirs(OUT, exist_ok=True)
V3 = 'GPT_数量/D04/减量73题版_v3/'
PARTS = [(V3 + 'D04_第1册_效率与分段_题本.md', '数量 · 第1册 效率与分段（17 题）'),
         (V3 + 'D04_第2册_产出库存与周期_题本.md', '数量 · 第2册 产出库存与周期（13 题）'),
         (V3 + 'D04_第3册_累计分配与统筹_题本.md', '数量 · 第3册 累计分配与统筹（12 题）'),
         (V3 + 'D04_第4册_流水成本与人数_题本.md', '数量 · 第4册 流水成本与人数（13 题）'),
         (V3 + 'D04_数字推理_题本.md', '数量 · 数字推理（18 题）'),
         ('/home/user/work/books/r2_md/D04_言语.md', '言语 40 题')]
NOTES = {'D04_第1册_效率与分段_题本.md': '题号有跳号是正常删减，不是漏题。效率恒定、工作量可相加等条件以各题表述为准；不可拆分、停机、整数人数及工序先后等限制不可忽略。',
         'D04_数字推理_题本.md': '选择最符合常见数列规律的选项。a/b 表示分数，√ 表示根号；机械拆分按题面数字书写形式观察。本册不使用仅尾零不同但数值相同的选项。'}
TITLE = '第2轮 · D04 · 数量 73 题（减量版）＋ 言语 40 题'
VERSION = '数量为 GPT main 分支上的 D04-减量73题-v3-20261111（运算 55、数推 18）；言语 40 题与原题本相同'
NOTE = ('数量从 135 题减到 73 题，删去的 62 题不用补。原题本封面上列的待修订题（M018、M092、M049、M035、N007）和做过的题（M041、M084、N004、N025、N027）都已删去。'
        '题号保持原号，有跳号是正常的。')
def build(pass_label):
    parts = []
    for i, (p, t) in enumerate(PARTS):
        n = NOTES.get(os.path.basename(p))
        parts.append(f'<h1 class="part{" first" if i == 0 else ""}">{H.escape(t)}</h1>' + (f'<p class="partnote">{H.escape(n)}</p>' if n else '') + B.md_to_html(p))
    guide = ('数量第一遍做完即可核对答案。后面的“第二遍”是同一套题的空白副本，留给错题和没把握的题回做；要不要整本再做一遍，按你的时间定。言语只做一遍'
             if pass_label == '第一遍' else '同一套题的空白副本：回做错题和没把握的题，已掌握的不必重做；言语不用再做')
    cover = (f'<div class="cover"><div class="big">{H.escape(TITLE)}</div><div class="pass">题本 · {pass_label}</div>'
             f'<div class="meta">{VERSION}<br>只含题目，不含答案；答案见打包目录 README<br>{guide}</div>'
             f'<div class="note">{H.escape(NOTE)}</div></div>')
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>第2轮 D04 减量版 {pass_label}</title><style>{B.CSS}</style></head><body>{cover}{"".join(parts)}</body></html>'
if __name__ == '__main__':
    for k, label in (('1', '第一遍'), ('2', '第二遍')):
        open(f'{OUT}/D04_{k}.html', 'w', encoding='utf-8').write(build(label))
    print('html ok')
