"""Merge each day's 第一遍/第二遍 PDFs into one file with bookmarks (round 3)."""
import fitz, os, sys
SRC = '/home/user/work/books/out_r3'
DST = sys.argv[1] if len(sys.argv) > 1 else '/home/user/work/books/final_r3'
os.makedirs(DST, exist_ok=True)
NAMES = {'D07': '第3轮_D07_数量135+言语40_题本（第一遍+第二遍）',
         'D08': '第3轮_D08_资料135+言语40_题本（第一遍+第二遍）',
         'D09': '第3轮_D09_判断135+言语40_题本（第一遍+第二遍）'}
PARTS = {'D07': ['数量 · 数字推理（N001—N030）', '数量 · 数学运算（M001—M040）', '数量 · 数学运算（M041—M080）', '数量 · 数学运算（M081—M105）', '言语 40 题'],
         'D08': ['资料分析 135 题', '言语 40 题'],
         'D09': ['判断推理 135 题', '言语 40 题']}

def part_pages(doc, titles):
    out = []
    for t in titles:
        for p in range(1, doc.page_count):  # skip the cover
            if any(l.strip() == t for l in doc[p].get_text().split('\n')):
                out.append((t, p + 1)); break
    return out

for day, name in NAMES.items():
    a = fitz.open(f'{SRC}/{day}_1.pdf'); b = fitz.open(f'{SRC}/{day}_2.pdf')
    n1 = a.page_count
    toc = [[1, '第一遍', 1]] + [[2, t, p] for t, p in part_pages(a, PARTS[day])]
    toc += [[1, '第二遍', n1 + 1]] + [[2, t, p + n1] for t, p in part_pages(b, PARTS[day])]
    m = fitz.open(); m.insert_pdf(a); m.insert_pdf(b)
    m.set_toc(toc)
    m.set_metadata({'title': name, 'author': 'Claude（GPT 第3轮审核后修订）；D07 数量为 GPT 强化版 v2',
                    'subject': '广东省考行测24天集训 第3轮', 'creator': 'Chromium', 'producer': 'Skia/PDF'})
    m.save(f'{DST}/{name}.pdf', garbage=4, deflate=True)
    print(day, m.page_count, 'pages;', toc)
