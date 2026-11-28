# 把生成器和SVG代码嵌进页面：page.html → <site>/index.html
import sys, re
site = sys.argv[1] if len(sys.argv) > 1 else "site"
page = open("page.html", encoding="utf8").read()
strip = lambda s: "\n".join(l for l in s.splitlines() if not l.startswith("if (typeof module"))
gen = strip(open("gen.js", encoding="utf8").read()); svg = strip(open("svg.js", encoding="utf8").read())
assert page.count("/*GEN*/") == 1 and page.count("/*SVG*/") == 1
out = page.replace("/*GEN*/", gen).replace("/*SVG*/", svg)
assert "</script" not in gen + svg
open(f"{site}/index.html", "w", encoding="utf8").write(out)
print("index.html", len(out.encode("utf8")) // 1024, "KB")
