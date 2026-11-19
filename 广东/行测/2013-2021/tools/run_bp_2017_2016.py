#!/usr/bin/env python3
"""Build a paper with tools/build_patched.py's logic on top of tools/extract.py + 3 small in-memory fixes.
Neither file is modified on disk.

  P1  parse_question, option re-split: a later option letter may follow whitespace
  P2  parse_question: a lone option letter as the first segment of a line (its separator was a U+3000
      ideographic space, which load_pages drops) followed by option text counts as that option's label
  P4  segment: a text line is ordered by the top of its text characters, not by a taller inline image

usage: run_bp.py <paper> [--work DIR] [--unpatched] [--outroot DIR]
"""
import sys
import types
from pathlib import Path

TOOLS = Path('/home/user/xing-ce1/广东/行测/2013-2021/tools')
EXTRACT, BP = TOOLS / 'extract.py', TOOLS / 'build_patched.py'

PATCHES = [
    ('P1',
     "mo = re.compile(rf'(?<=[\\u4e00-\\u9fff\\d）)”%])({L})[、.．](?=[^、.．\\s])').search(whole, pos)",
     "mo = re.compile(rf'(?<=[\\u4e00-\\u9fff\\d）)”%\\s])({L})[、.．](?=[^、.．\\s])').search(whole, pos)"),
    ('P2a',
     "RE_OPT = re.compile(r'^([A-D])\\s*[、.．:：]')\n",
     "RE_OPT = re.compile(r'^([A-D])\\s*[、.．:：]')\n\n\n"
     "def bare_label(segs, L: str) -> bool:\n"
     "    \"\"\"行首单独一个选项字母、隔开后紧跟选项文字（字母后的分隔符是全角空格等空白，读入时已丢弃）。\"\"\"\n"
     "    return (len(segs) > 1 and segs[0][0] == L and not RE_OPT.match(segs[1][0])\n"
     "            and re.match(r'[^\\sA-Za-z]', segs[1][0]) is not None)\n"),
    ('P2b',
     "opt_i = next((i for i, ln in enumerate(q.lines) if i > 0 and RE_OPT.match(ln.text)), None)",
     "opt_i = next((i for i, ln in enumerate(q.lines) if i > 0 and (RE_OPT.match(ln.text) or bare_label(ln.segs, 'A'))), None)"),
    ('P2c',
     "        for text, _, _ in segs:\n            mo = RE_OPT.match(text)\n",
     "        for j, (text, _, _) in enumerate(segs):\n"
     "            mo = RE_OPT.match(text) or (re.match(r'([A-D])', text) if j == 0 and want < 4 and bare_label(segs, 'ABCD'[want]) else None)\n"),
    ('P4',
     "stream += [('line', ln, ln.top, ln.x0) for ln in p.lines]",
     "stream += [('line', ln, min((t.top for t in ln.toks if not t.image), default=ln.top), ln.x0) for ln in p.lines]"),
]
LOADER = ("spec = importlib.util.spec_from_file_location('extract', EXTRACT)\n"
          "ex = importlib.util.module_from_spec(spec)\n"
          "sys.modules['extract'] = ex\n"
          "spec.loader.exec_module(ex)\n")


def load_extract(patched=True):
    src = EXTRACT.read_text(encoding='utf-8')
    if patched:
        for pid, old, new in PATCHES:
            if src.count(old) != 1:
                raise SystemExit(f'patch {pid}: expected exactly 1 occurrence in extract.py, found {src.count(old)}')
            src = src.replace(old, new)
    mod = types.ModuleType('extract')
    mod.__file__ = str(EXTRACT)
    sys.modules['extract'] = mod
    exec(compile(src, str(EXTRACT), 'exec'), mod.__dict__)
    return mod


def run(paper, work=None, patched=True, outroot=None):
    ex = load_extract(patched)
    if outroot:
        outroot = Path(outroot)
        ex.OUT, ex.TOOLS = outroot, outroot / 'tools'
        ex.PAPERS_DIR, ex.CORR_DIR = outroot / 'tools' / 'papers', outroot / 'tools' / 'corrections'
    bp = BP.read_text(encoding='utf-8')
    if bp.count(LOADER) != 1:
        raise SystemExit('build_patched.py: module-loading block not found exactly once')
    bp = bp.replace(LOADER, "ex = sys.modules['extract']\n")
    sys.argv = [str(BP), paper] + (['--work', str(work)] if work else [])
    exec(compile(bp, str(BP), 'exec'), {'__name__': '__main__', '__file__': str(BP)})


if __name__ == '__main__':
    a = sys.argv[1:]
    paper = a[0]
    work = a[a.index('--work') + 1] if '--work' in a else None
    outroot = a[a.index('--outroot') + 1] if '--outroot' in a else None
    run(paper, work, patched='--unpatched' not in a, outroot=outroot)
