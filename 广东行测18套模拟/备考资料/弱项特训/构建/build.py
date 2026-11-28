# 组装“行测弱项特训”的数据：data.json + fig/ 图片。用法：python3 build.py <输出目录>
import json, re, shutil, sys, os
from pathlib import Path
from PIL import Image

REPO = Path("/home/user/xing-ce1")
SP = Path("/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else SP / "xc/site")
FIG = OUT / "fig"
if OUT.exists(): shutil.rmtree(OUT)
FIG.mkdir(parents=True)
DRILL = SP / "drill"

def fig(src, name, maxw=1100):
    """复制题图：限制宽度，统一存成 PNG；返回页面里用的相对路径"""
    im = Image.open(src)
    if im.mode not in ("RGB", "L"): im = im.convert("RGB")
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    p = FIG / (name + ".png"); im.save(p, optimize=True)
    return "fig/" + p.name

def split_exp(a):
    """把“题眼：…推导：…易错：…”拆成三段（专项、M卷解析的写法）"""
    a = a.replace("\r", "")
    out = {}
    m = re.split(r"(题眼：|推导：|易错：)", a)
    if len(m) > 1:
        cur = None
        for part in m:
            if part in ("题眼：", "推导：", "易错："): cur = part[:2]; continue
            if cur: out[cur] = out.get(cur, "") + part.strip()
        if "推导" not in out:          # 有的解析题眼后直接接推导（没有“推导：”字样）
            t = out.get("题眼", "")
            i = t.find("\n")
            if i > 0: out["题眼"], out["推导"] = t[:i].strip(), t[i + 1:].strip()
    else: out["推导"] = a.strip()
    return {k: v.strip() for k, v in out.items() if v.strip()}

def gd_rec(qid):
    for f in ["广东/行测/2013-2021/all.jsonl", "广东/事业单位/结构化/all.jsonl", "广东/行测/2022-2026/all.jsonl"]:
        p = REPO / f
        if not p.exists(): continue
        for l in open(p, encoding="utf8"):
            q = json.loads(l)
            if q.get("id") == qid: return q, p.parent
    raise KeyError(qid)

def zx_exp(qid):
    for f in (REPO / "广东行测18套模拟/重编/专项/解题").glob("*.json"):
        if "blind" in f.name: continue
        for x in json.load(open(f, encoding="utf8")):
            if x.get("id") == qid: return split_exp(x["analysis"]), x
    for f in (REPO / "广东行测18套模拟/重编").glob("M*/解题/*.json"):
        if "blind" in f.name: continue
        try: d = json.load(open(f, encoding="utf8"))
        except Exception: continue
        if not isinstance(d, list): continue
        for x in d:
            if isinstance(x, dict) and x.get("id") == qid: return split_exp(x["analysis"]), x
    raise KeyError(qid)

Q = []
def add(**kw): Q.append(kw); return kw

# ---------- M10 原题（五道） ----------
m10 = {json.loads(l)["number"]: json.loads(l) for l in open(REPO / "广东行测18套模拟/M10/题目.jsonl", encoding="utf8")}
m10ans = json.load(open(REPO / "广东行测18套模拟/M10/答案.json", encoding="utf8"))
m10md = open(REPO / "广东行测18套模拟/M10/答案与解析.md", encoding="utf8").read()
def m10exp(n):
    i = m10md.find(f"**{n}.【答案】"); j = m10md.find(".【答案】", i + 10); j = m10md.rfind("\n", i, j) if j > 0 else len(m10md)
    t = m10md[i:j]
    t = re.sub(r"\*\*\d+\.【答案】[A-D]\*\*", "", t)
    t = t.replace("**题眼**：", "题眼：").replace("**易错**：", "易错：")
    # 题眼后面一段是推导
    parts = [p.strip() for p in t.strip().split("\n\n") if p.strip()]
    out = {}
    for p in parts:
        if p.startswith("题眼："): out["题眼"] = p[3:]
        elif p.startswith("易错："): out["易错"] = p[3:]
        else: out["推导"] = (out.get("推导", "") + "\n" + p).strip()
    return out
def m10stem(q):
    return "".join(b.get("text", "") for b in q["stem"] if b["type"] == "text")
def m10figpath(q):
    for b in q["stem"]:
        if b["type"] == "figure": return REPO / b["path"]
SRC10 = "M10第{}题（{}）"
q = m10[47]; add(id="M10-Q47", set="m10", module="图推", sub="数交点", tag="交点总数", src=SRC10.format(47, "2018年广东卷第39题"), stem=m10stem(q), fig=fig(m10figpath(q), "M10-Q47"), optsInFig=True, answer=m10ans["47"], exp=m10exp(47))
q = m10[48]; add(id="M10-Q48", set="m10", module="图推", sub="灰格计数", tag="上下两行灰格数相差1", src=SRC10.format(48, "2016年广东县级卷第58题"), stem=m10stem(q), fig=fig(m10figpath(q), "M10-Q48"), optsInFig=True, answer=m10ans["48"], exp=m10exp(48))
q = m10[33]; add(id="M10-Q33", set="m10", module="数推", sub="递推", tag="前两项之和×前项", src=SRC10.format(33, "2016年广东县级卷第38题"), stem="1，2，3，10，39，（　　）", seq=True, opts={L: q["options"][L][0]["text"] for L in "ABCD"}, answer=m10ans["33"], exp=m10exp(33))
q = m10[35]; add(id="M10-Q35", set="m10", module="数推", sub="数表", tag="b＝a²＋1，c＝a³＋2", src=SRC10.format(35, "2022年广东县级卷第28题"), stem="", rows=[[1, 2, 3], [2, 5, 10], [3, 10, 29], [4, 17, None]], opts={L: q["options"][L][0]["text"] for L in "ABCD"}, answer=m10ans["35"], exp=m10exp(35))
q = m10[73]
mat = q["materials"][0]["blocks"]
mblocks = []
for b in mat:
    if b["type"] == "text": mblocks.append({"type": "text", "text": b["text"]})
    elif b["type"] == "figure": mblocks.append({"type": "img", "src": fig(REPO / b["path"], "M10-M1", 1000), "alt": "2019年各地区用水量表"})
add(id="M10-Q73", set="m10", module="资料", sub="比重", tag="定义比率（基期）", src=SRC10.format(73, "2020年广东县级卷资料"), stem=m10stem(q), opts={L: q["options"][L][0]["text"] for L in "ABCD"}, answer=m10ans["73"], exp=m10exp(73), material={"blocks": mblocks})

# ---------- 图推·数交点 真题（官方答案） ----------
GKF = DRILL / "gkfig"
D03 = REPO / "广东行测24天集训/GPT_复核/第1批/assets/PD-A"
add(id="JS2020-076", set="fig-pts", module="图推", sub="数交点", tag="交点总数递增", src="2020年江苏A类第76题", stem="请从所给的四个选项中，选出最恰当的一项填入问号处，使之呈现一定的规律性。",
    fig=fig(REPO / "江浙行测_AI题库/images/original/413.png", "JS2020-076", 900), optsInFig=True, answer="B",
    exp={"题眼": "五幅图都是在三角形里一步步加线，线条交叉、相接越来越多，而线条数加得不整齐，提示数交点。",
         "推导": "图1：三角形3个顶点，共3个。\n图2：加一条从顶点到底边的竖线，底边上多1个T形点，共4个。\n图3：再加一条从右边到底边中点的斜线，右边上多1个点（底边中点已经数过），共5个。\n图4：左边对称再加一条，共6个。\n图5：加一条连接左右两边中点的横线，两端落在已有的点上，只和竖线交叉多出1个，共7个。\n交点数3、4、5、6、7，问号处应有8个。A项：3个顶点＋3个边中点＝6个；B项：在A的基础上，中间倒三角形里再加一条横线，两端各落在倒三角形的两条边上，多出2个，共8个；C项、D项都是在A的基础上加一条竖线，一端落在已有的点上，各多1个，共7个。故选B。",
         "易错": "线的端头接在别的线上（T形）要算交点；几条线交在同一点（如底边中点有三条线）只算1个。"})
add(id="GK2016-76", set="fig-pts", module="图推", sub="数交点", tag="圆与其他元素的交点数（分组）", src="2016年国考地市级第76题（副省级第82题）", stem="把下面的六个图形分为两类，使每一类图形都有各自的共同特征或规律，分类正确的一项是：",
    fig=fig(GKF / "GK2016D-76_full_t.png", "GK2016-76"), opts={"A": "①②④，③⑤⑥", "B": "①②⑤，③④⑥", "C": "①③④，②⑤⑥", "D": "①③⑥，②④⑤"}, answer="D",
    exp={"题眼": "六幅图都有一个圆，其他线条、图形都碰到这个圆，元素杂乱、属性看不出规律，提示数“圆与其他元素”的交点。",
         "推导": "①短横线、竖线各穿过圆一次，2个；②竖线从圆里伸出，与圆1个交点，下面的横线不碰圆，1个；③竖线上下两次穿过圆，2个，圆里的三角形不碰圆；④小圆挂在竖线下端，1个；⑤小正方形只有左下角顶在圆周上，1个；⑥小圆横跨正方形上边，2个。①③⑥都是2个，②④⑤都是1个，故选D。",
         "易错": "⑤是“一个角顶在圆上”（1个），⑥是“横跨一条边”（2个），看着都像“小图形和大图形相交”，要看清碰了几处。这题只数圆与其他元素的交点，其他线之间的交点不算。"})
add(id="GK2017-78", set="fig-pts", module="图推", sub="数交点", tag="黑点在交点上还是在线上（分组）", src="2017年国考地市级第78题（副省级第83题）", stem="把下面的六个图形分为两类，使每一类图形都有各自的共同特征或规律，分类正确的一项是：",
    fig=fig(GKF / "GK2017D-78_t.png", "GK2017-78"), opts={"A": "①④⑥，②③⑤", "B": "①②③，④⑤⑥", "C": "①⑤⑥，②③④", "D": "①③⑤，②④⑥"}, answer="D",
    exp={"题眼": "每幅图都有小黑点，黑点是用来标位置的（功能元素），提示看黑点落在什么位置：只是在线上，还是在线与线的交点上。",
         "推导": "①三个黑点都在三角形边的中间；③两个黑点在圆周上，里面的正方形不碰圆；⑤黑点在半圆弧上：这三幅黑点都只在线上。②一个黑点在左边与横线相接的T形处，一个在右下角拐角；④黑点在五角星中间几条线交汇的地方；⑥三个黑点都在方格线交叉处：这三幅黑点都在交点上。故选D。",
         "易错": "拐角和T形接头也是交点（两条线在那里相交、相接）。②的两个黑点就是这种点，看成“在线上”就会选错。"})
add(id="GK2018-71", set="fig-pts", module="图推", sub="数交点", tag="圆内交点（分区域数）", src="2018年国考地市级第71题（副省级第77题）", stem="从所给的四个选项中，选出最合适的一个填入问号处，使之呈现一定的规律性：",
    fig=fig(D03 / "GK2018D-71.png", "GK2018-71"), optsInFig=True, answer="C",
    exp={"题眼": "每幅图都是一个圆加几条直线，线线相交很多；先数交点总数（6、8、6、6、1），没规律；再数曲直交点（2、4、2、3、6），也没规律；而圆把图分成里、外两块，提示里外分开数。",
         "推导": "只数圆内部直线与直线的交点：0、1、2、3、4，依次加1，问号处应有5个。A项4个、B项2个、C项5个、D项8个，故选C。",
         "易错": "数总数、数曲直交点都不行时不要放弃“交点”，换成按区域分开数（圆内、圆外，框内、框上）。圆周上的曲直交点不算圆内交点。"})
add(id="GK2020-73", set="fig-pts", module="图推", sub="数交点", tag="曲直交点＝曲线数×2", src="2020年国考地市级第73题（副省级第78题）", stem="从所给的四个选项中，选择最合适的一个填入问号处，使之呈现一定的规律性：",
    fig=fig(D03 / "GK2020D-73.png", "GK2020-73"), optsInFig=True, answer="D",
    exp={"题眼": "图里曲线（圆、弧）和直线交叉明显，先数曲直交点：4、6、2、4、8，单看没有规律；再数曲线有几条：2、3、1、2、4，正好是交点数的一半。",
         "推导": "每幅图的曲直交点数都等于曲线数的2倍。四个选项都只有1条曲线，问号处应有2个曲直交点：A项4个、B项4个、C项1个、D项2个，故选D。",
         "易错": "单看交点数4、6、2、4、8找不到规律就乱猜；两种量“成倍”也是数量规律的常见考法。直线与直线的交点不算曲直交点。"})
add(id="GK2021-72", set="fig-pts", module="图推", sub="数交点", tag="切点与曲直交点", src="2021年国考地市级第72题", stem="从所给的四个选项中，选择最合适的一个填入问号处，使之呈现一定的规律性：",
    fig=fig(GKF / "GK2021D-72_t.png", "GK2021-72"), optsInFig=True, answer="C",
    exp={"题眼": "每幅图都有一个圆，圆和直线有的穿过去（相交）、有的只碰一下（相切），提示把切点和曲直交点分开数。",
         "推导": "题干每幅图都恰好有1个切点、1个曲直交点。A项圆被斜线穿过，交点不止1个；B项横线穿过圆就有2个交点；D项圆同时碰到右边和底边，有2个切点；只有C项圆碰着斜线（1个切点），竖线从圆里穿出（1个交点）。故选C。",
         "易错": "切点是曲线和直线“碰一下、不穿过”的点，和穿过去的交点要分开数；一条直线穿过整个圆要算2个交点。"})
# 复习（专项第3天做过）
r, base = gd_rec("GD2020-XZ-Q050"); e, x = zx_exp("GD2020-XZ-Q050")
add(id="GD2020-XZ-Q050", set="fig-pts", module="图推", sub="数交点", tag="黑点标出的点数", src="2020年广东乡镇卷第50题", review="专项第3天", stem=r["stem"], fig=fig(base / r["figures"][0]["path"], "GD2020-XZ-Q050"), optsInFig=True, answer=r["answer"]["values"][0][0], exp=e)

# ---------- 图推·灰格计数 真题 ----------
add(id="GK2014-85", set="fig-grid", module="图推", sub="灰格计数", tag="各种颜色的块各有几个（分组）", src="2014年国考第85题", stem="把下面的六个图形分为两类，使每一类图形都有各自的共同特征或规律，分类正确的一项是：",
    fig=fig(GKF / "GK2014-85_t.png", "GK2014-85"), opts={"A": "①③⑤，②④⑥", "B": "①③⑥，②④⑤", "C": "①③④，②⑤⑥", "D": "①④⑤，②③⑥"}, answer="B",
    exp={"题眼": "六个五角星形状、分块完全一样（五个尖角＋中间五边形，共6块），只是涂色不同，颜色有三种，位置又看不出平移、旋转，提示数每种颜色的块数。",
         "推导": "每幅图都是1块黑色。①③⑥：另外5块是2块网格、3块点状；②④⑤：另外5块是3块网格、2块点状。所以①③⑥一组、②④⑤一组，故选B。",
         "易错": "只盯黑块的位置会白费力气（黑块位置各不相同、没有规律）；颜色多的题，每种颜色各数一遍，再比较组合。"})
for qid, tag, rv in [("GD2017-Q038", "黑球、白球各几个", "专项第3天"), ("GD2018-Q036", "白格被分成几块", "M09第47题"), ("SYDW2024-Q071", "白球连成几部分", "专项第3天"), ("SYDW2025-Q068", "白块分成几部分、每部分几格", "专项第3天")]:
    r, base = gd_rec(qid); e, x = zx_exp(qid)
    src = {"GD2017-Q038": "2017年广东卷第38题", "GD2018-Q036": "2018年广东卷第36题", "SYDW2024-Q071": "2024年广东事业单位统考第71题", "SYDW2025-Q068": "2025年广东事业单位统考第68题"}[qid]
    add(id=qid, set="fig-grid", module="图推", sub="灰格计数", tag=tag, src=src, review=rv, stem=r["stem"], fig=fig(base / r["figures"][0]["path"], qid), optsInFig=True, answer=r["answer"]["values"][0][0], exp=e)

# ---------- 数推·三项关系 真题 ----------
r, base = gd_rec("GD2020-XZ-Q035")
add(id="GD2020-XZ-Q035", set="num-tab", module="数推", sub="数表", tag="每行三数之和成等差", src="2020年广东乡镇卷第35题", stem="", rows=[[4, 5, 7], [8, 8, 16], [12, 9, 27], [16, 10, None]],
    opts={o["label"]: o["text"] for o in r["options"]}, answer="C",
    exp={"题眼": "每行三个数，行内的和、积、平方都凑不出统一的运算（4、5、7用加法差2，8、8、16用加法正好），提示换成“每行三个数相加”。",
         "推导": "每行三数之和：4＋5＋7＝16，8＋8＋16＝32，12＋9＋27＝48，依次加16，第4行之和应为64。所求数＝64－16－10＝38。故选C。",
         "易错": "只看第3列7、16、27的差9、11，按二级等差推下一差13得40，选项里没有；只用第2行凑“前两数相加”得26，也不在选项里。"})
for qid, set_, tag, src in [("GDXD2019-SW-Q068", "num-rec", "前两项之和", "2019年广东选调第68题"), ("SYDW2025-Q053", "num-rec", "相邻三项：（首＋尾）×2＝中", "2025年广东事业单位统考第53题"), ("GD2014-XZ-Q060", "num-tab", "九宫格：每行左右两数运算得中间数", "2014年广东乡镇卷第60题")]:
    r, base = gd_rec(qid); e, x = zx_exp(qid)
    kw = dict(id=qid, set=set_, module="数推", sub="递推" if set_ == "num-rec" else "数表", tag=tag, src=src, review="专项第4天", opts={o["label"]: o["text"] for o in r["options"]}, answer=r["answer"]["values"][0][0], exp=e)
    if r.get("figures"): kw["fig"] = fig(base / r["figures"][0]["path"], qid); kw["stem"] = "从所给的选项中，选择最合适的一个填入问号处："
    else: kw["stem"] = r["stem"].replace("（    ）", "（　　）"); kw["seq"] = True
    add(**kw)

# ---------- 资料·比重 真题（粉笔模考，答案为本页解题人计算） ----------
fb = {}
for l in open(REPO / "模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl", encoding="utf8"):
    x = json.loads(l); fb[f"fb-s{x['season']}-q{x['number']}"] = x
FBA = REPO / "模考/2026下半年广东卷_16-33季_AI可读"
def fb_material(m, tag):
    blocks = []
    for b in m["blocks"]:
        if b["type"] == "text": blocks.append({"type": "text", "text": b["text"]})
        elif b["type"] == "table": blocks.append({"type": "table", "title": b.get("title"), "headers": b.get("headers"), "rows": b["rows"], "notes": b.get("notes")})
        elif b["type"] in ("figure", "image"):
            p = b.get("path") or ("assets/" + b.get("asset_id", "") + ".png")
            blocks.append({"type": "img", "src": fig(FBA / p, tag + "-" + os.path.basename(p).split(".")[0], 1000)})
    return {"blocks": blocks}
zl = json.load(open(DRILL / "zl_items.json", encoding="utf8"))
for it in zl:
    x = fb[it["id"]]
    stem = "".join(b.get("text", "") for b in x["stem"] if b["type"] == "text")
    add(id=it["id"], set="data-pct", module="资料", sub="比重", tag=it["type"], src=f"粉笔模考第{x['season']}季第{x['number']}题", stem=stem,
        opts={L: "".join(b.get("text", "") for b in x["options"][L]) for L in "ABCD"}, answer=it["answer"],
        exp={k: v for k, v in it["explanation"].items()}, material=fb_material(x["material"], it["id"]),
        srcNote="粉笔模考原卷没有附答案，答案和解析由本页解题人逐项计算（精确值：" + it["exact"][:120] + ("…" if len(it["exact"]) > 120 else "") + "）。")

# ---------- 待补：粉笔图推（交点、灰格）和数推（三项）——由 extra.json 并入 ----------
for extra in [SP / "xc/ss_extra.json", SP / "xc/fig_extra.json"]:
    if not extra.exists(): continue
    for it in json.load(open(extra, encoding="utf8")):
        if it.get("figsrc"): it["fig"] = fig(it.pop("figsrc"), it["id"].replace("/", "_"))
        Q.append(it)

# 组内排序：新题在前、复习题在后
order = {"m10": 0, "fig-pts": 1, "fig-grid": 2, "num-rec": 3, "num-tab": 4, "num-adv": 5, "data-pct": 6}
Q.sort(key=lambda q: (order[q["set"]], 1 if q.get("review") else 0, q.get("o", 20)))
cfg = json.load(open(SP / "xc/config.json", encoding="utf8"))
data = {**cfg, "questions": Q}
for st in data["sets"]:
    st["count"] = sum(1 for q in Q if q["set"] == st["id"])
json.dump(data, open(OUT / "data.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print("questions", len(Q), {s["id"]: s["count"] for s in data["sets"]}, "figs", len(list(FIG.iterdir())), "data.json KB", round((OUT / "data.json").stat().st_size / 1024))
