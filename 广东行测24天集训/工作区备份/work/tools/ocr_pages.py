"""OCR every page of scanned (no text layer) Guangdong analysis PDFs + GD2021X 题本. Output: /home/user/work/ocr/<tag>/p<NNN>.txt (+ .png)"""
import pymupdf, os, sys, json, subprocess
from concurrent.futures import ThreadPoolExecutor
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0, os.path.dirname(__file__))
from papers import registry
jobs = []
for r in registry():
    if r['prov'] != 'GD' or not r['path'].startswith('xing-ce1') or not r['path'].endswith('.pdf'): continue
    if r['text'] > 3000 or (r['year'] or 0) < 2013: continue
    tag = r['pid'] + ('_ans' if r['kind'] == 'ans' else '_q')
    d = pymupdf.open('/home/user/' + r['path'])
    os.makedirs(f'/home/user/work/ocr/{tag}', exist_ok=True)
    json.dump(dict(file=r['path'], pages=d.page_count), open(f'/home/user/work/ocr/{tag}/_meta.json', 'w'), ensure_ascii=False)
    for i in range(d.page_count): jobs.append((tag, r['path'], i))
def run(job):
    tag, path, i = job
    out = f'/home/user/work/ocr/{tag}/p{i+1:03d}'
    if os.path.exists(out + '.txt') and os.path.getsize(out + '.txt') > 0: return
    d = pymupdf.open('/home/user/' + path)
    pix = d[i].get_pixmap(dpi=250); pix.save(out + '.png')
    subprocess.run(['tesseract', out + '.png', out, '-l', 'chi_sim', '--psm', '6'], capture_output=True, timeout=600, env=dict(os.environ, OMP_THREAD_LIMIT='1'))
print(len(jobs), 'pages')
with ThreadPoolExecutor(4) as ex: list(ex.map(run, jobs))
print('done')
