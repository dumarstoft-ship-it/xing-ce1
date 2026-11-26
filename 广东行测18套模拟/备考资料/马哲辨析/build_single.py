"""把网页和题库打包成一个可以离线打开的HTML文件：马哲辨析日课.html。

用法：python3 广东行测18套模拟/备考资料/马哲辨析/build_single.py
做题记录存在打开它的浏览器里（localStorage），与在线版的记录不互通。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE / "site"


def main():
    page = (SITE / "index.html").read_text(encoding="utf-8")
    data = {"cards": json.loads((SITE / "cards.json").read_text(encoding="utf-8")),
            "questions": json.loads((SITE / "questions.json").read_text(encoding="utf-8")),
            "meta": json.loads((SITE / "meta.json").read_text(encoding="utf-8"))}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    i = page.index("<script>")
    out = ("<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">"
           "<style>html,body{margin:0}[hidden]{display:none!important}img{max-width:100%}"
           ":root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>"
           "</head><body>\n" + page[:i] + "<script id=\"mz-data\" type=\"application/json\">" + blob + "</script>\n"
           + page[i:] + "\n</body></html>\n")
    f = HERE / "马哲辨析日课.html"
    f.write_text(out, encoding="utf-8")
    print(f.name, round(len(out.encode("utf-8")) / 1024), "KB", len(data["questions"]), "题")


if __name__ == "__main__":
    main()
