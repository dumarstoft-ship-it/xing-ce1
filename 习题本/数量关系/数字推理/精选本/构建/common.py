"""数字推理精选本：共用样式与页面外框。配色取自原书。"""
import html, re

E = lambda s: html.escape(str(s), quote=True)
TEAL, DARK, GRAY, RULE, BORDER, FILL = "#17675F", "#162B36", "#4E666A", "#D3DEDC", "#A7B8B5", "#EEF4F2"
PAGE_W, PAGE_H = 595.28, 841.89
CONTENT_TOP, CONTENT_H = 66.0, 722.0

CSS = f"""
@page {{ size: 595.28pt 841.89pt; margin: 0 }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: "JX"; font-weight: 300; color: {DARK}; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.page {{ width: 595.28pt; height: 841.89pt; position: relative; overflow: hidden; page-break-after: always; break-after: page; background: #fff; }}
.page:last-child {{ page-break-after: auto; break-after: auto; }}
.hd-l {{ position: absolute; left: 45pt; top: 30pt; font: 500 8.6pt/12pt "JX"; color: {TEAL}; letter-spacing: .3pt; }}
.hd-r {{ position: absolute; right: 45.28pt; top: 30pt; font: 300 8.6pt/12pt "JX"; color: {GRAY}; }}
.rule-t {{ position: absolute; left: 45pt; width: 505.28pt; top: 48pt; border-top: .65pt solid {RULE}; }}
.rule-b {{ position: absolute; left: 45pt; width: 505.28pt; top: 796pt; border-top: .65pt solid {RULE}; }}
.ft-l {{ position: absolute; left: 45pt; top: 802pt; font: 300 8.6pt/12pt "JX"; color: {TEAL}; }}
.ft-r {{ position: absolute; right: 45.28pt; top: 801pt; font: 500 9.6pt/13pt "JX"; color: {DARK}; }}
.fit {{ position: absolute; left: 45pt; width: 505.28pt; top: {CONTENT_TOP}pt; height: {CONTENT_H}pt; overflow: hidden; }}
a {{ color: inherit; text-decoration: none; }}
.teal {{ color: {TEAL}; }} .muted {{ color: {GRAY}; }} .med {{ font-weight: 500; }}
h1 {{ font-weight: 500; font-size: 24pt; line-height: 32pt; margin: 6pt 0 6pt; color: {DARK}; letter-spacing: .5pt; }}
.sub {{ font-weight: 500; font-size: 12.5pt; line-height: 19pt; color: {TEAL}; margin: 0 0 10pt; }}
p {{ font-size: 10.6pt; line-height: 18pt; margin: 0 0 7pt; text-align: justify; }}
.lead {{ font-size: 11pt; line-height: 19pt; color: {GRAY}; }}
h2 {{ font-weight: 500; font-size: 12.5pt; line-height: 17pt; color: {TEAL}; margin: 14pt 0 5pt; }}
h2:first-child {{ margin-top: 2pt; }}
.box {{ border: .5pt solid {BORDER}; background: #F6FAF9; padding: 8pt 11pt; margin: 6pt 0 10pt; }}
.box p:last-child {{ margin-bottom: 0; }}
ul.plain {{ list-style: none; padding: 0; margin: 0 0 8pt; }}
ul.plain li {{ font-size: 10.6pt; line-height: 18pt; padding-left: 13pt; position: relative; }}
ul.plain li::before {{ content: "·"; position: absolute; left: 3pt; color: {TEAL}; font-weight: 500; }}
table.t {{ width: 100%; border-collapse: collapse; margin: 4pt 0 10pt; }}
table.t th {{ font-weight: 500; font-size: 9.4pt; color: {TEAL}; background: {FILL}; text-align: left; padding: 3.5pt 5pt;
             border-top: .5pt solid {BORDER}; border-bottom: .5pt solid {BORDER}; }}
table.t td {{ font-size: 9.8pt; line-height: 14.5pt; padding: 4pt 5pt; border-bottom: .5pt solid {RULE}; vertical-align: top; }}
table.t td.n {{ color: {TEAL}; font-weight: 500; white-space: nowrap; }}
table.t td.p {{ text-align: right; color: {TEAL}; white-space: nowrap; }}
table.t.compact td {{ padding: 2.6pt 5pt; line-height: 13.6pt; font-size: 9.6pt; }}
table.t.compact th {{ padding: 2.6pt 5pt; }}
.toc-mod {{ display: flex; justify-content: space-between; align-items: baseline; font-weight: 500; font-size: 12.5pt; line-height: 17pt;
           color: {TEAL}; margin: 11pt 0 2pt; padding-bottom: 4pt; border-bottom: .65pt solid {BORDER}; }}
.toc-mod:first-child {{ margin-top: 0; }}
.toc-row {{ border-bottom: .65pt solid {RULE}; padding: 5pt 2pt; }}
.toc-line {{ display: flex; justify-content: space-between; align-items: baseline; }}
.toc-name {{ font-size: 10.8pt; line-height: 15pt; }}
.toc-pg {{ font-size: 10.2pt; font-weight: 500; color: {TEAL}; }}
.chips {{ font-size: 9pt; line-height: 13.5pt; color: {GRAY}; margin-top: 1pt; }}
.chip {{ color: {TEAL}; margin-right: 7pt; white-space: nowrap; }}
.chip.adv {{ color: {GRAY}; }}
.modno {{ font-weight: 500; font-size: 10.5pt; color: {TEAL}; letter-spacing: 1pt; margin-top: 2pt; }}
.card {{ border-top: .65pt solid {RULE}; padding: 6pt 0 5pt; }}
.card h3 {{ margin: 0 0 2pt; font-weight: 500; font-size: 11.8pt; line-height: 16pt; color: {TEAL}; }}
.card h3 .no {{ color: {GRAY}; font-weight: 300; margin-right: 6pt; }}
.kv {{ display: grid; grid-template-columns: 40pt 1fr; column-gap: 6pt; row-gap: 1pt; }}
.kv .k {{ font-size: 9.2pt; line-height: 15.4pt; font-weight: 500; color: {GRAY}; }}
.kv .v {{ font-size: 9.9pt; line-height: 15.4pt; text-align: justify; }}
.qchip {{ display: inline-block; margin: 0 9pt 0 0; white-space: nowrap; color: {TEAL}; font-size: 9.4pt; }}
.qchip b {{ font-weight: 500; }}
.qchip i {{ font-style: normal; font-size: 7.8pt; margin-left: 3pt; padding: 0 3pt; border: .5pt solid {TEAL}; border-radius: 2pt; }}
.qchip.adv {{ color: {GRAY}; }} .qchip.adv i {{ border-color: {BORDER}; }}
.flowcol {{ display: flex; flex-direction: column; height: 100%; }}
.notes {{ flex: 1 1 auto; min-height: 0; overflow: hidden; margin-top: 12pt; border-top: .65pt solid {BORDER};
         background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 25.5pt, {RULE} 25.5pt, {RULE} 26pt);
         background-position: 0 22pt; }}
.notes .nt {{ font-size: 9.4pt; line-height: 22pt; color: {GRAY}; background: #fff; }}
.backup {{ font-size: 9.6pt; line-height: 15.5pt; color: {GRAY}; }}
/* 题页框架 */
.mh {{ position: absolute; left: 45pt; width: 505.28pt; }}
.mh .t {{ font: 500 11.5pt/16pt "JX"; color: {TEAL}; border-bottom: .65pt solid {TEAL}; padding-bottom: 3pt; }}
.mh .t .id {{ color: {GRAY}; font-weight: 300; margin-right: 6pt; }}
.mh .t .cont {{ color: {GRAY}; font-weight: 300; font-size: 9pt; margin-left: 6pt; }}
.mh .h {{ margin-top: 4pt; font: 300 9.2pt/14pt "JX"; color: {DARK}; background: {FILL}; padding: 3pt 8pt; border-left: 2pt solid {TEAL}; }}
.mh .h b {{ font-weight: 500; color: {TEAL}; margin-right: 5pt; }}
.tag {{ position: absolute; left: 45pt; width: 505.28pt; font: 300 8.4pt/11pt "JX"; color: {GRAY}; display: flex; justify-content: space-between; }}
.tag b {{ font-weight: 500; color: {TEAL}; margin-right: 6pt; }}
.tag .tier {{ font-size: 7.6pt; padding: 0 3pt; border: .5pt solid {BORDER}; border-radius: 2pt; margin-left: 5pt; }}
.tag .tier.core {{ border-color: {TEAL}; color: {TEAL}; }}
.br {{ position: absolute; left: 45pt; width: 505.28pt; font: 300 9pt/13pt "JX"; color: {TEAL}; }}
"""

def shell(page_no, hd_right, body, body_id="", footer="目录"):
    return (f'<div class="page"><div class="hd-l">数字推理 / 精选本</div><div class="hd-r">{E(hd_right)}</div>'
            f'<div class="rule-t"></div><div class="fit" id="{E(body_id)}">{body}</div>'
            f'<div class="rule-b"></div><a class="ft-l" data-link="toc">{E(footer)}</a><div class="ft-r">{page_no}</div></div>')

def frame(page_no, hd_right, inner):
    """题页框架：不含 .fit，元素都按绝对坐标放。"""
    return (f'<div class="page"><div class="hd-l">数字推理 / 精选本</div><div class="hd-r">{E(hd_right)}</div>'
            f'<div class="rule-t"></div>{inner}'
            f'<div class="rule-b"></div><a class="ft-l" data-link="toc">目录</a><div class="ft-r">{page_no}</div></div>')

def short_src(s):
    s = re.sub(r"\s+", " ", s).strip()
    return s
