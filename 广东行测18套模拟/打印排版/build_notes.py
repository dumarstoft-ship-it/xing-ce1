"""把备考资料的Markdown排成A4打印版PDF（pandoc转HTML，Chromium打印）。

用法：python3 广东行测18套模拟/打印排版/build_notes.py <输入.md> <输出.pdf> <字体目录>

用于备考资料（如 备考资料/广东时政易错点.md）。要装pandoc和Node版Playwright；字体文件不入库。
"""
import subprocess
import sys
from pathlib import Path


src, out, fonts = (Path(x).resolve() for x in sys.argv[1:4])   # 绝对路径：Chromium要file://绝对地址
body = subprocess.run(["pandoc", "-f", "gfm", "-t", "html5", str(src)], check=True,
                      capture_output=True, text=True).stdout
# 【重点】【坑】单独成段时加标签样式
body = body.replace("<p>【重点】</p>", '<p class="tag key">【重点】</p>').replace("<p>【坑】</p>", '<p class="tag pit">【坑】</p>')
body = body.replace("<p>【重点】（", '<p><span class="tag key">【重点】</span>（')
body = body.replace("<p>【重点】", '<p><span class="tag key">【重点】</span>')

css = f"""
@font-face {{ font-family: "FZSS"; src: url("file://{fonts}/方正书宋简体.TTF"); }}
@font-face {{ font-family: "FZHT"; src: url("file://{fonts}/方正黑体简体.TTF"); }}
@font-face {{ font-family: "FZKT"; src: url("file://{fonts}/方正楷体简体.TTF"); }}
@font-face {{ font-family: "BZ"; src: url("file://{fonts}/补字_后备_noto-serif-cjk-sc-regular.otf"); }}
@page {{ size: A4; margin: 13mm 15mm 14mm 15mm; }}
html {{ font-family: "FZSS", "BZ", serif; font-size: 10pt; line-height: 1.5; color: #000; orphans: 2; widows: 2; }}
body {{ margin: 0; }}
h1 {{ font-family: "FZHT", "BZ"; font-weight: normal; font-size: 17pt; text-align: center; margin: 0 0 8pt; }}
h2 {{ font-family: "FZHT", "BZ"; font-weight: normal; font-size: 13pt; margin: 12pt 0 4pt; padding-bottom: 2pt;
      border-bottom: 1.2pt solid #000; break-after: avoid; }}
h3 {{ font-family: "FZHT", "BZ"; font-weight: normal; font-size: 11pt; margin: 8pt 0 2pt; break-after: avoid; }}
p {{ margin: 3pt 0; }}
ul, ol {{ margin: 2pt 0 4pt; padding-left: 1.6em; }}
li {{ margin: 1.5pt 0; }}
strong {{ font-family: "FZHT", "BZ"; font-weight: normal; }}
hr {{ border: none; border-top: 0.6pt solid #888; margin: 8pt 0; }}
.tag {{ font-family: "FZHT", "BZ"; margin: 4pt 0 1pt; }}
span.tag {{ margin: 0; }}
.pit {{ color: #000; }}
table {{ border-collapse: collapse; }}
"""
html = f"<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
tmp = out.with_suffix(".tmp.html")
tmp.write_text(html, encoding="utf-8")
js = out.with_suffix(".print.js")
js.write_text("""
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage();
  await pg.goto('file://' + process.argv[2]);
  await pg.waitForTimeout(500);
  await pg.pdf({ path: process.argv[3], format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: "<div style='width:100%;text-align:center;font-size:8pt;font-family:serif;'>第<span class='pageNumber'></span>页　共<span class='totalPages'></span>页</div>",
    margin: { top: '13mm', bottom: '14mm', left: '15mm', right: '15mm' } });
  await b.close();
})();
""", encoding="utf-8")
subprocess.run(["node", str(js), str(tmp), str(out)], check=True)
js.unlink()
tmp.unlink()
print("ok", out)
