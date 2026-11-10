"""Rebuild the HTML books of an assembled package from its own jsonl files (no re-assembly).
  python3 rebuild_books.py <pkg_dir>
"""
import json, sys, os, collections, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from build_books import build_question_book, build_answer_book
PKG = sys.argv[1]
final = [json.loads(l) for l in open(f'{PKG}/questions.jsonl')]
mats = {m['mid']: m for m in (json.loads(l) for l in open(f'{PKG}/materials.jsonl'))}
arts = {a['aid']: a for a in (json.loads(l) for l in open(f'{PKG}/articles.jsonl'))}
MOD = {'ZL': '资料', 'PD': '判断', 'YY': '言语'}
INTRO = {'ZL': '专项：做两遍后再核对答案。题号旁为原题来源（卷号·原题号）；材料先读后答。',
         'PD': '专项：图推在前；做两遍后再核对答案。题号旁为原题来源（卷号·原题号）。',
         'YY': '言语：做一遍再看答案原文册。题号旁为原题来源；同一篇文章的题做完再看原文。'}
by = collections.defaultdict(list)
for r in final: by[(r['day'], r['id'].split('-')[1])].append(r)
for (day, mc), recs in sorted(by.items()):
    t = f'{day} {MOD[mc]} {len(recs)} 题'
    open(f'{PKG}/{day}_{MOD[mc]}_题目册.html', 'w').write(build_question_book(recs, mats, arts, PKG, t + '｜题目册', INTRO[mc]))
    if mc == 'YY':
        open(f'{PKG}/{day}_{MOD[mc]}_答案原文册.html', 'w').write(build_answer_book(recs, arts, t + '｜答案与原文册', '只给原参考答案和原文，不附解析；原有争议标记照录。', verbal=True))
    else:
        open(f'{PKG}/{day}_{MOD[mc]}_答案册.html', 'w').write(build_answer_book(recs, arts, t + '｜答案册', '核验后答案＋简短解法；“原答案”与核验一致时不重复列出。'))
    print(day, mc, len(recs))
