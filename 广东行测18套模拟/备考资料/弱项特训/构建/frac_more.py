# 分数数列真题第二部分：国考（2003、2005、2009年）和粉笔模考第16—33季。
# 国考用官方答案；粉笔模考原卷没有答案，答案由解题人算出、Python 逐项复核（只收“解出且无歧义”的题）。输出 frac_more.json。
import json, re
from pathlib import Path

SP = Path("/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad")
REG = Path("/home/user/xing-ce1/广东行测18套模拟/用题登记.jsonl")
used = {}
for l in open(REG, encoding="utf8"):
    r = json.loads(l); used[r["source_id"]] = f"{r['paper_id']}第{r['number']}题"

Q = []
def item(x, **extra):
    q = dict(id=x["id"], set="num-frac", module="数推", sub="分数数列", tag=x["rule"], src=re.sub(r"（[^（）]*(PDF|仅)[^（）]*）", "", x["src"]), stem=x["stem"], seq=True,
             opts=x["options"], answer=x["answer"], exp={k: x["exp"][k] for k in ("题眼", "推导", "易错")})
    q.update(extra); Q.append(q)

# 国考：2009年1道；2000—2007年4道（2005年卷二第31题是根式，不收）
gk = json.load(open(SP / "drill/frac_gk/items.json", encoding="utf8")) + json.load(open(SP / "drill/frac_gk/items_pre2008_supplement.json", encoding="utf8"))
for x in gk:
    if x["id"] == "GK2005B-Q31" or not x.get("answer_ok", True): continue
    item(x)

# 粉笔模考：第24—33季是新题；第16—23季做过的（M01—M08里用过）标“做过”
fbp = SP / "drill/frac_fb/items.json"
if fbp.exists():
    for x in json.load(open(fbp, encoding="utf8")):
        if not x.get("solved", True) or x.get("ambiguous"): continue
        s, n = x["id"].replace("fb-s", "").split("-q")
        sid = f"gd-mock-2026h2-s{s}-q{n}"
        extra = {"srcNote": "粉笔模考原卷没有附答案，答案由解题人算出，并用程序把每一项都按规律复算过。"}
        if sid in used: extra["review"] = used[sid]
        item(x, **extra)

json.dump(Q, open(SP / "xc/frac_more.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(Q), "items", sum(1 for q in Q if q.get("review")), "review")
