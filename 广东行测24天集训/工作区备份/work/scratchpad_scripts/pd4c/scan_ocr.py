"""OCR a scanned PDF into scratchpad cache: python3 scan_ocr.py <name> <relpath> [pages 1-based ...]"""
import pymupdf, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
pymupdf.TOOLS.mupdf_display_errors(False)
name, rel = sys.argv[1], sys.argv[2]
P = '/home/user/' + rel
O = f'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd4c/ocr/{name}'
os.makedirs(O, exist_ok=True)
d = pymupdf.open(P); n = d.page_count
pages = [int(x) - 1 for x in sys.argv[3:]] or list(range(n))
def run(i):
    out = f'{O}/p{i+1:03d}'
    if os.path.exists(out + '.txt') and os.path.getsize(out + '.txt') > 0: return
    dd = pymupdf.open(P); pix = dd[i].get_pixmap(dpi=200); pix.save(out + '.png')
    subprocess.run(['tesseract', out + '.png', out, '-l', 'chi_sim', '--psm', '6'], capture_output=True, timeout=900, env=dict(os.environ, OMP_THREAD_LIMIT='1'))
with ThreadPoolExecutor(4) as ex: list(ex.map(run, pages))
print('done', name, len(pages))
