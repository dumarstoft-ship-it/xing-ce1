"""ans.py <pdf rel/abs path> <qno> [chars] : print analysis text snippets that start a question qno."""
import sys, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
p = sys.argv[1]; p = p if p.startswith('/') else '/home/user/' + p
q = sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 700
doc = pymupdf.open(p)
pages = [unicodedata.normalize('NFKC', pg.get_text()) for pg in doc]
full = ''; starts = []
for i, t in enumerate(pages):
    starts.append(len(full)); full += t + '\n'
pat = re.compile(r'(?:(?:(?<=\n)|^)\s*(?:【\s*)?(?:第\s*)?' + q + r'(?:\s*题)?\s*(?:[\.、．:：】]|\s))|【解析' + q + r'—|【题目' + q + r'】|第【' + q + r'】题')
hits = [m.start() for m in pat.finditer(full)]
for h in hits:
    pg = max(i for i, s in enumerate(starts) if s <= h) + 1
    print(f'===== hit at page {pg}')
    print(full[h:h + n])
if not hits: print('no hits; pages', len(pages), 'chars', len(full))
