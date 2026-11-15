"""Whitespace-only source layout; no rewriting."""
import re

def compact(s):
    return re.sub(r'\s+', '', s)


def format_source_text(s):
    """Whitespace only: preserve generic speaker, question and condition boundaries."""
    out = ''
    last = ''
    boundary = re.compile(r'^(?:[\u4e00-\u9fff]{1,4}[：:]|[（(]\d+[）)]|[①②③④⑤⑥⑦⑧⑨⑩]|以下|下列|根据|由此|依次|这段|上述|如果体型|将以上)')
    for line in s.splitlines():
        line = line.strip()
        if not line:
            if out and not out.endswith('\n'):
                out += '\n'
            last = ''
            continue
        sep = '\n' if out and (boundary.match(line) or last.endswith(('：', '？', '。', '；', '?'))) else ''
        if out.endswith('\n'):
            sep = ''
        out += sep + line
        last = line
    out = re.sub(r'(?<=[\u4e00-\u9fff\d]) +(?=[\u4e00-\u9fff])', '', out)
    out = re.sub(r'\s*(_{2,})\s*', r'\1', out)
    assert compact(out) == compact(s), 'Formatting changed characters or punctuation'
    return out.strip()
