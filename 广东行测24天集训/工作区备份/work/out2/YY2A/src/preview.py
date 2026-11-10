# -*- coding: utf-8 -*-
"""Preview books for YY2A's part only (uses the shared /home/user/work/tools/build_books.py). Not the merged day package."""
import json, sys, os, collections
sys.path.insert(0, '/home/user/work/tools')
from build_books import build_question_book, build_answer_book
OUT = '/home/user/work/out2/YY2A'
Q = [json.loads(l) for l in open(f'{OUT}/questions.jsonl')]
A = {a['aid']: a for a in (json.loads(l) for l in open(f'{OUT}/articles.jsonl'))}
by = collections.defaultdict(list)
for q in Q:
    by[q['day']].append(q)
for day, recs in sorted(by.items()):
    t = f'{day} 言语·YY2A 部分（选词 12＋语句 6）'
    open(f'{OUT}/preview/{day}_言语_YY2A_题目册.html', 'w').write(
        build_question_book(recs, {}, A, OUT, t + '｜题目册预览', '仅 YY2A 负责的选词、语句填空 18 题；合并后与 YY2B 的片段、排序共 40 题。同一篇文章的题做完再看原文。'))
    open(f'{OUT}/preview/{day}_言语_YY2A_答案原文册.html', 'w').write(
        build_answer_book(recs, A, t + '｜答案与原文册预览', '只给原参考答案和原文，不附解析；原有争议标记照录。', verbal=True))
print(sorted(os.listdir(f'{OUT}/preview')))
