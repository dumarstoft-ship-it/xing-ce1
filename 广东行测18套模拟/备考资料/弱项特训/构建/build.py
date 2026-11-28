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

def tex2txt(t):
    """解析里的 $\\frac{a}{b}$ 写成 a/b（页面会排成上下分数）"""
    def fr(m):
        x, y = m.group(1), m.group(2)
        x = x if re.fullmatch(r"[0-9.]+", x) else "(" + x + ")"
        y = y if re.fullmatch(r"[0-9.]+", y) else "(" + y + ")"
        return x + "/" + y
    t = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", fr, t)
    t = t.replace("^2", "²").replace("^3", "³").replace("$", "")
    return t

def split_exp(a):
    """把“题眼：…推导：…易错：…”拆成三段（专项、M卷解析的写法）"""
    a = tex2txt(a.replace("\r", ""))
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
    for f in sorted((REPO / "广东行测18套模拟/重编").glob("[MS]*/解题/*.json")):
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

# ---------- S01 原题（用户2026-11-28：S01第46、47、34题不会） ----------
S01Q = {json.loads(l)["number"]: json.loads(l) for l in open(REPO / "广东行测18套模拟/S01/题目.jsonl", encoding="utf8")}
S01A = json.load(open(REPO / "广东行测18套模拟/S01/答案.json", encoding="utf8"))
for n, sid, mod, sub, tag, src in [(34, "SYDW2022-Q055", "数推", "分数数列", "反约分：分子平方、分母连续", "2022年广东事业单位统考第55题"),
                                    (46, "SYDW2024-Q074", "图推", "点沿边框移动", "端点沿边框移动（也可数交点6、5、6、5）", "2024年广东事业单位统考第74题"),
                                    (47, "SYDW2022-Q068", "图推", "数面数线", "面数比线条数多1（2、3、4块用1、2、3条线）", "2022年广东事业单位统考第68题")]:
    q = S01Q[n]; e, x = zx_exp(sid)
    e.setdefault("易错", {34: "不还原直接看1、9/5、8/3，分子1、1、9、8显得乱；1要写成4/4、8/3要写成16/6（分子分母同乘2），分子才凑成1、4、9、16，分母3、4、5、6也跟着连上。只推分子、分母照抄最后一项加2，会误选C项25/8。",
                          46: "三个端点要分开追：两个逆时针各走一格，一个顺时针走一格；只盯一个端点会觉得乱。图4有两个端点重合，只剩一条线，数交点时（6、5、6、5）别把它当成规律被打断。",
                          47: "C项也是5个区域，只数面会在B、C之间犹豫，再看线条数（C只有3条）或笔画数（C为3笔）就能排除。"}[n])
    kw = dict(id=f"S01-Q{n}", set="m10", module=mod, sub=sub, tag=tag, src=f"S01第{n}题（{src}）", stem=m10stem(q), answer=S01A[str(n)], exp=e, o=10 + n)
    fp = m10figpath(q)
    if fp: kw["fig"] = fig(fp, f"S01-Q{n}"); kw["optsInFig"] = True
    else: kw["stem"] = m10stem(q).replace("（    ）", "（　　）"); kw["seq"] = True; kw["opts"] = {L: q["options"][L][0]["text"] for L in "ABCD"}
    add(**kw)

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

# ---------- 第二批（2026-11-28 用户说做过的、留给后面卷子的都可以出）：广东旧卷里同类的题，解析用专项、M卷、S卷里写过的 ----------
SRC_GD = {"GD2020-XJ-Q046": "2020年广东县级卷第46题", "SYDW2025-Q070": "2025年广东事业单位统考第70题", "SYDW2023-Q068": "2023年广东事业单位统考第68题",
          "GD2013-1-Q072": "2013年广东一卷第72题", "GD2018-Q031": "2018年广东卷第31题", "GD2017-Q040": "2017年广东卷第40题", "GD2016-XJ-Q060": "2016年广东县级卷第60题"}
for qid, set_, tag, kind, where in [
        ("GD2020-XJ-Q046", "fig-pts", "交点数依次加1（含曲线）", "also", "S06第47题"),
        ("SYDW2025-Q070", "fig-pts", "小方块都标在十字交叉点上", "review", "专项第4天"),
        ("GD2017-Q040", "fig-grid", "黑格点连接还是线连接（分组）", "review", "专项第3天"),
        ("GD2016-XJ-Q060", "fig-grid", "黑珠、白珠每段几颗", "review", "专项第3天")]:
    r, base = gd_rec(qid); e, x = zx_exp(qid)
    stem = r["stem"] if r["stem"] and "见题图" not in r["stem"] else (x.get("stem_fill") or "从所给的四个选项中，选择最合适的一个填入问号处，使之呈现一定的规律性：")
    kw = dict(id=qid, set=set_, module="图推", sub="数交点" if set_ == "fig-pts" else "灰格计数", tag=tag, src=SRC_GD[qid], stem=stem,
              fig=fig(base / r["figures"][0]["path"], qid), answer=r["answer"]["values"][0][0], exp=e, o=30)
    opts = {o["label"]: o["text"] for o in r.get("options") or [] if o.get("text") and o["text"] not in "ABCD"}
    if len(opts) == 4: kw["opts"] = opts
    else: kw["optsInFig"] = True
    if kind == "review": kw["review"] = where
    else: kw["srcNote"] = f"这道题也编在{where}，做那套卷子时会再见到。"
    add(**kw)

# ---------- 数推·三项关系 真题 ----------
# GD2020-XZ-Q035 与M12第35题（2020年县级卷第30题）同题，用户要做完M系列，不放进特训

for qid, set_, tag, src in [("GDXD2019-SW-Q068", "num-rec", "前两项之和", "2019年广东选调第68题"), ("SYDW2025-Q053", "num-rec", "相邻三项：（首＋尾）×2＝中", "2025年广东事业单位统考第53题"), ("GD2014-XZ-Q060", "num-tab", "九宫格：每行左右两数运算得中间数", "2014年广东乡镇卷第60题")]:
    r, base = gd_rec(qid); e, x = zx_exp(qid)
    kw = dict(id=qid, set=set_, module="数推", sub="递推" if set_ == "num-rec" else "数表", tag=tag, src=src, review="专项第4天", opts={o["label"]: o["text"] for o in r["options"]}, answer=r["answer"]["values"][0][0], exp=e)
    if r.get("figures"): kw["fig"] = fig(base / r["figures"][0]["path"], qid); kw["stem"] = "从所给的选项中，选择最合适的一个填入问号处："
    else: kw["stem"] = r["stem"].replace("（    ）", "（　　）"); kw["seq"] = True
    add(**kw)

# ---------- 第二批数推（2026-11-28）：广东旧卷里留给后面各套、或做过的三项关系题 ----------
SRC_N = {"GD2014-XZ-Q058": "2014年广东乡镇卷第58题", "GD2019-XJ-Q017": "2019年广东县级卷第17题", "GDXD2019-SW-Q069": "2019年广东选调第69题",
         "SYDW2025-Q052": "2025年广东事业单位统考第52题", "GD2017-Q019": "2017年广东卷第19题", "GD2020-XZ-Q032": "2020年广东乡镇卷第32题",
         "GD2016-XJ-Q040": "2016年广东县级卷第40题", "GDXD2019-SW-Q067": "2019年广东选调第67题", "GDXD2020-SW-Q090": "2020年广东选调第90题",
         "GD2023-XJ-Q030": "2023年广东县级卷第30题", "SYDW2025-Q055": "2025年广东事业单位统考第55题", "GD2022-XZ-Q034": "2022年广东乡镇卷第34题"}
OWN = {
 "GD2017-Q019": {"题眼": "数列增长越来越快，后项大约是前项的3倍左右，又时多时少（2×3＝6，6×3＝18＞16），提示递推，拿相邻三项试“前两项之和”的倍数。",
                 "推导": "6＝(1＋2)×2，16＝(2＋6)×2，44＝(6＋16)×2，120＝(16＋44)×2，即从第三项起，每项等于前两项之和的2倍。所求项＝(44＋120)×2＝328。故选D。",
                 "易错": "只看相邻两项的倍数（3、2.67、2.75、2.73）会以为是“乘约2.7”，凑不出整数；要把前两项合起来看。"},
 "GD2020-XZ-Q032": {"题眼": "数列平稳增大，相邻两项之和与后一项很接近（23＋34＝57，后项58），提示“前两项之和＋常数”的递推。",
                 "推导": "58＝23＋34＋1，93＝34＋58＋1，152＝58＋93＋1，即从第三项起，每项等于前两项之和再加1。所求项＝93＋152＋1＝246。故选C。",
                 "易错": "算出93＋152＝245后忘了加修正项1；修正项要在每一组都核对一遍。"},
}
YICUO = {
 "GDXD2019-SW-Q069": "只看前一项会被负数和忽大忽小绕晕，递推要同时看前两项；2倍乘的是再前一项，放到前一项上（22×2＋18＝62）选项里没有。",
 "SYDW2025-Q052": "也可以看成“×2后交替减3、加3”，两种看法答案相同；只凑上一组就选容易错，每一组都要核对。",
 "GD2016-XJ-Q040": "单看第1行能凑出很多种算法，要拿带负数的第3行验证；第2行第3个数是6.5，它的2倍是13。",
 "SYDW2025-Q055": "三数之和（19、23）不相等，按列看也没有规律；积相等时用积除以已知的两个数求第三个数。",
}
for qid, set_, tag, kind, where in [
        ("GD2014-XZ-Q058", "num-rec", "前两项之和", "also", "S04第33题"),
        ("SYDW2025-Q052", "num-rec", "后项＝前一项＋再前一项的2倍", "review", "S01第33题"),
        ("GD2017-Q019", "num-rec", "（前两项之和）×2", "review", "24天集训"),
        ("GD2020-XZ-Q032", "num-rec", "前两项之和＋1", "review", "24天集训"),
        ("GD2023-XJ-Q030", "num-tab", "每列三个数成等差", "review", "M09第35题"),
        ("SYDW2025-Q055", "num-tab", "每行三数之积相等", "review", "S02第35题"),
        ("GD2022-XZ-Q034", "num-adv", "作差后：差列前两项之和＝第三项", "review", "M09第33题")]:
    r, base = gd_rec(qid)
    e = OWN[qid] if qid in OWN else zx_exp(qid)[0]
    if "易错" not in e and qid in YICUO: e["易错"] = YICUO[qid]
    kw = dict(id=qid, set=set_, module="数推", sub={"num-rec": "递推", "num-tab": "数表", "num-adv": "进阶"}[set_], tag=tag, src=SRC_N[qid],
              opts={o["label"]: o["text"] for o in r["options"]}, answer=r["answer"]["values"][0][0], exp=e, o=30)
    if r.get("figures"):
        kw["fig"] = fig(base / r["figures"][0]["path"], qid); kw["stem"] = "从所给的选项中，选择最合适的一个填入问号处："
    else:
        kw["stem"] = re.sub(r"\s+", "，", r["stem"].replace("（    ）", "").replace("（）", "").strip(" ，")) + "，（　　）"; kw["seq"] = True
    if kind == "review": kw["review"] = where
    else: kw["srcNote"] = f"这道题也编在{where}，做那套卷子时会再见到。"
    add(**kw)

# ---------- 分数数列（2026-11-28 用户：数推分数加强、多加量） ----------
for qid, tag, src, kind, where in [
        ("GD2019-XZ-Q015", "分子等差、分母等比", "2019年广东乡镇卷第15题", "also", "S05第34题"),
        ("SYDW2024-Q054", "反约分：第n项为n/(n＋6)", "2024年广东事业单位统考第54题", "also", "S03第35题"),
        ("GD2022-XZ-Q033", "反约分：分子连续、分母等差", "2022年广东乡镇卷第33题", "review", "M09第34题"),
        ("GD2021-XZ-Q035", "约分后再统一分子：2/2、2/3、2/4……", "2021年广东乡镇卷第35题", "review", "M10第34题"),
        ("SYDW2023-Q052", "反约分：分子连续，分母n²＋1", "2023年广东事业单位统考第52题", "review", "S02第34题"),
        ("GD2014-XJ-Q044", "整数、小数化成同分母分数", "2014年广东县级卷第44题", "review", "专项第4天"),
        ("GD2015-XJ-Q024", "分子分母交叉：后项分母＝前项分母×后项分子", "2015年广东县级卷第24题", "review", "专项第4天"),
        ("SYDW2026-Q054", "分子、分母各作差成等比", "2026年广东事业单位统考第54题", "review", "专项第4天")]:
    r, base = gd_rec(qid); e, x = zx_exp(qid)
    toks = [t for t in re.split(r"[，、\s]+", re.sub(r"（\s*）", " ＿ ", r["stem"]).strip(" 。.")) if t]
    stem = "，".join("（　　）" if t == "＿" else t for t in toks)
    kw = dict(id=qid, set="num-frac", module="数推", sub="分数数列", tag=tag, src=src, stem=stem, seq=True,
              opts={o["label"]: o["text"].strip("，。 ") for o in r["options"]}, answer=r["answer"]["values"][0][0], exp=e, o=30)
    if kind == "review": kw["review"] = where
    else: kw["srcNote"] = f"这道题也编在{where}，做那套卷子时会再见到。"
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
for extra in [SP / "xc/ss_extra.json", SP / "xc/fig_extra.json", SP / "xc/fig_more.json", SP / "xc/frac_real.json", SP / "xc/frac_more.json"]:
    if not extra.exists(): continue
    for it in json.load(open(extra, encoding="utf8")):
        if it.get("figsrc"): it["fig"] = fig(it.pop("figsrc"), it["id"].replace("/", "_"))
        Q.append(it)

# 组内排序：新题在前、复习题在后
order = {"m10": 0, "fig-pts": 1, "fig-grid": 2, "num-frac": 3, "num-rec": 4, "num-tab": 5, "num-adv": 6, "data-pct": 7}
Q.sort(key=lambda q: (order[q["set"]], 1 if q.get("review") else 0, q.get("o", 20)))
cfg = json.load(open(SP / "xc/config.json", encoding="utf8"))
data = {**cfg, "questions": Q}
for st in data["sets"]:
    st["count"] = sum(1 for q in Q if q["set"] == st["id"])
json.dump(data, open(OUT / "data.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print("questions", len(Q), {s["id"]: s["count"] for s in data["sets"]}, "figs", len(list(FIG.iterdir())), "data.json KB", round((OUT / "data.json").stat().st_size / 1024))
