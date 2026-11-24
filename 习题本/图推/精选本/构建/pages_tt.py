"""图形推理精选本：页面规划。

生成页（封面、认知地图、目录、导读、附录）走 data-flow 流式分页。
题型训练模块“题后即看答案”：标签、题块、解析块自上而下排，放不下就换页，过高的单题等比缩小。
限时组：先排一组题块，再排这一组的答案页。
"""
from common import E, shell, frame, CONTENT_TOP, CONTENT_H

TAG_H, GAP, MID, HEAD_H, SET_HEAD_H, ANS_HEAD_H, NOTE_LINE = 13.0, 12.0, 3.0, 48.0, 50.0, 28.0, 14.5

def head_h(g):
    """组标题：标题行＋提示框。提示超过一行时加高（按 9.2pt 汉字、5.2pt 西文估算，框内宽 487pt，标签约占 42pt）。"""
    import math
    if not g.get("hint"): return HEAD_H - 18
    w = 42 + sum(9.2 if ord(c) > 255 else 5.2 for c in g["hint"])
    return HEAD_H + 14.0 * (math.ceil(w / 480) - 1)

def note_h(q):
    import math
    return 0.0 if not q.get("note") else 4 + NOTE_LINE * math.ceil(len(q["note"]) / 46)

def flow(name, seq, inner, tag="div", min_keep=1):
    return f'<{tag} data-flow="{name}" data-seq="{seq}" data-min="{min_keep}">{inner}</{tag}>'

def all_questions(sel):
    for mi, mod in enumerate(sel["modules"]):
        for g in mod["groups"]:
            for q in g["questions"]:
                yield mi, mod, g, q

def chips(g, seqno):
    return " ".join(
        f'<a class="qchip{"" if q["tier"] == "核心" else " adv"}" data-link="q:{q["id"]}"><b>{seqno[q["id"]]:03d}</b> {E(q["id"])}'
        + (f'<i>{E(q["tier"])}</i>' if q["tier"] in ("核心", "进阶") else "") + '</a>'
        for q in g["questions"])

def card(g, seqno):
    rows = []
    labels = g.get("labels", {})
    for k, label in (("essence", "方法"), ("signal", "信号"), ("first", "最快路径"), ("trap", "易错")):
        if g.get(k): rows.append(f'<div class="k">{labels.get(k, label)}</div><div class="v">{E(g[k])}</div>')
    if g.get("limit"): rows.append(f'<div class="k">限时</div><div class="v">{E(g["limit"])}</div>')
    elif g.get("time"): rows.append(f'<div class="k">限时</div><div class="v">每题 {g["time"]} 秒</div>')
    rows.append(f'<div class="k">题目</div><div class="v">{chips(g, seqno)}</div>')
    no = f'<span class="no">{E(g["no"])}</span>' if g.get("no") else ""
    return f'<div class="card"><h3>{no}{E(g["name"])}</h3><div class="kv">{"".join(rows)}</div></div>'

def fit_scale(h_total, avail):
    return 1.0 if h_total <= avail else avail / h_total

def pack_inline(mod, info):
    pages, cur, h = [], [], 0.0
    for g in mod["groups"]:
        pending, cont = True, False
        for q in g["questions"]:
            d = info[q["id"]]
            raw = d["hq"] + MID + d["hs"]
            nh = note_h(q)
            HH = head_h(g)
            s = fit_scale(raw, CONTENT_H - HH - TAG_H - nh - 2)
            need = TAG_H + raw * s + nh + GAP
            hd = HH if pending else 0
            if cur and h + hd + need > CONTENT_H:
                pages.append(cur); cur, h = [], 0.0
                if not pending: cont = True
                pending, hd = True, HH
            if pending:
                cur.append({"kind": "head", "g": g, "y": CONTENT_TOP + h, "cont": cont}); h += HH; pending = False
            y = CONTENT_TOP + h
            cur.append({"kind": "item", "q": q, "g": g, "y": y, "scale": s,
                        "q_top": y + TAG_H, "s_top": y + TAG_H + (d["hq"] + MID) * s,
                        "note_top": y + TAG_H + raw * s + 3})
            h += need
    if cur: pages.append(cur)
    return pages

def pack_timed(g, info):
    """一组：题页若干＋答案页若干。"""
    qpages, cur, h = [], [], SET_HEAD_H
    for q in g["questions"]:
        d = info[q["id"]]
        s = fit_scale(d["hq"], CONTENT_H - SET_HEAD_H - TAG_H - 2)
        need = TAG_H + d["hq"] * s + GAP
        if cur and h + need > CONTENT_H:
            qpages.append(cur); cur, h = [], 0.0
        y = CONTENT_TOP + h
        cur.append({"kind": "q", "q": q, "g": g, "y": y, "scale": s, "q_top": y + TAG_H}); h += need
    if cur: qpages.append(cur)
    apages, cur, h = [], [], ANS_HEAD_H
    for q in g["questions"]:
        d = info[q["id"]]
        s = fit_scale(d["hs"], CONTENT_H - ANS_HEAD_H - TAG_H - 2)
        need = TAG_H + d["hs"] * s + GAP
        if cur and h + need > CONTENT_H:
            apages.append(cur); cur, h = [], 0.0
        y = CONTENT_TOP + h
        cur.append({"kind": "s", "q": q, "g": g, "y": y, "scale": s, "s_top": y + TAG_H}); h += need
    if cur: apages.append(cur)
    return qpages, apages

def plan(sel, recs, info, counts):
    seqno, n = {}, 0
    for _, _, _, q in all_questions(sel):
        n += 1; seqno[q["id"]] = n
    total = n
    P = []
    def gen(keys, build): P.append({"kind": "gen", "keys": keys, "build": build, "stamps": []})
    # 封面
    def b_cover(pno, pg):
        c = sel["cover"]
        how = "".join(f"<li>{E(x)}</li>" for x in c["how"]); use = "".join(f"<li>{E(x)}</li>" for x in c["use"])
        return shell(pno, "封面与说明",
                     f'<h1>{E(sel["title"])}</h1><div class="sub">{E(sel["subtitle"])}</div><p class="lead">{E(c["lead"])}</p>'
                     f'<h2>怎么挑的</h2><ul class="plain">{how}</ul><h2>怎么用</h2><ul class="plain">{use}</ul>'
                     f'<div class="box"><p class="muted" style="font-size:9.8pt;line-height:16.5pt">{E(c["stats"])}</p></div>')
    gen(["cover"], b_cover)
    # 认知地图（流式分页）
    def map_body(pg):
        mp = sel["map"]
        paras = "".join(f"<p>{E(x)}</p>" for x in mp["paras"])
        rows = "".join(f'<tr><td class="n">{E(r[0])}</td><td>{E(r[1])}</td><td>{E(r[2])}</td></tr>' for r in mp["table"])
        mods = "".join(
            f'<tr><td class="n"><a data-link="mod:{i+1}">{E(m["no"])} {E(m["name"])}</a></td><td>{E(m["tagline"])}</td>'
            f'<td style="text-align:right">{sum(len(g["questions"]) for g in m["groups"])} 题</td>'
            f'<td class="p"><a data-link="mod:{i+1}">{pg.get(f"mod:{i+1}", "")}</a></td></tr>' for i, m in enumerate(sel["modules"]))
        tail = "".join(f"<p>{E(x)}</p>" for x in mp.get("tail", []))
        return (f'<h1 style="font-size:21pt;line-height:29pt;margin-top:0">{E(mp["title"])}</h1>{paras}'
                f'<table class="t compact"><tr><th style="width:150pt">看到什么</th><th>先做什么</th><th style="width:60pt">限时</th></tr>{rows}</table>'
                f'<h2 class="keep-next">各模块练什么</h2>'
                f'<table class="t compact"><tr><th style="width:150pt">模块</th><th>练什么</th><th style="width:36pt;text-align:right">题数</th>'
                f'<th style="width:32pt;text-align:right">页码</th></tr>{mods}</table>{tail}')
    for k in range(counts["map"]):
        def b(pno, pg, k=k):
            return shell(pno, "认知地图", flow("map", k, map_body(pg) if k == 0 else ""), body_id=f"map-{k}")
        gen(["map"] if k == 0 else [], b)
    # 目录
    def toc_entries(pg):
        out = []
        for mi, mod in enumerate(sel["modules"]):
            out.append(f'<a class="toc-mod keep-next" data-link="mod:{mi+1}"><span>{E(mod["no"])} · {E(mod["name"])}</span><span>{pg.get(f"mod:{mi+1}", "")}</span></a>')
            for g in mod["groups"]:
                fq = g["questions"][0]["id"]
                cs = " ".join(f'<a class="chip{"" if q["tier"] == "核心" else " adv"}" data-link="q:{q["id"]}">{seqno[q["id"]]:03d} {E(q["id"])}</a>' for q in g["questions"])
                tg = g.get("no")
                gid = f'<span class="muted" style="margin-right:6pt">{E(tg)}</span>' if tg else ""
                out.append(f'<div class="toc-row"><a class="toc-line" data-link="q:{fq}"><span class="toc-name">{gid}{E(g["name"])}</span>'
                           f'<span class="toc-pg">{pg.get(f"q:{fq}", "")}</span></a><div class="chips">{cs}</div></div>')
        out.append(f'<div class="toc-row"><a class="toc-line" data-link="app"><span class="toc-name">附录 · 最快路径速查</span><span class="toc-pg">{pg.get("app", "")}</span></a></div>')
        out.append(f'<div class="toc-row" style="border-bottom:none"><a class="toc-line" data-link="cut"><span class="toc-name">选题说明：删去了什么、为什么</span><span class="toc-pg">{pg.get("cut", "")}</span></a></div>')
        return "".join(out)
    for k in range(counts["toc"]):
        def b(pno, pg, k=k):
            head = '<h1 style="font-size:21pt;line-height:29pt;margin-top:0">目录</h1>' if k == 0 else ""
            return shell(pno, "目录", head + flow("toc", k, toc_entries(pg) if k == 0 else ""), body_id=f"toc-{k}")
        gen(["toc"] if k == 0 else [], b)
    # 模块
    for mi, mod in enumerate(sel["modules"]):
        ng = counts[f"m{mi+1}"]
        for k in range(ng):
            def b(pno, pg, k=k, mod=mod, mi=mi, ng=ng):
                if k == 0:
                    intro = "".join(f"<p>{E(p)}</p>" for p in mod["intro"])
                    head = (f'<div class="modno">模块 {E(mod["no"])}</div><h1 style="margin-top:2pt">{E(mod["name"])}</h1>'
                            f'<div class="sub">{E(mod["tagline"])}</div>{intro}')
                    inner = head + flow(f"m{mi+1}", 0, "".join(card(g, seqno) for g in mod["groups"]))
                    if ng == 1: inner += _tail(mod, recs)
                    return shell(pno, f'{mod["no"]} · 导读', inner, body_id=f"m{mi+1}-0")
                tail = _tail(mod, recs) if k == ng - 1 else ""
                return shell(pno, f'{mod["no"]} · 导读（续）', f'<div class="flowcol">{flow(f"m{mi+1}", k, "")}{tail}</div>', body_id=f"m{mi+1}-{k}")
            gen([f"mod:{mi+1}"] if k == 0 else [], b)
        if mod.get("kind") == "timed":
            for g in mod["groups"]:
                qpages, apages = pack_timed(g, info)
                for pi, items in enumerate(qpages):
                    P.append(_timed_page(items, g, mod, seqno, recs, info, first=(pi == 0), answers=False))
                for pi, items in enumerate(apages):
                    P.append(_timed_page(items, g, mod, seqno, recs, info, first=(pi == 0), answers=True))
        else:
            for items in pack_inline(mod, info):
                P.append(_inline_page(items, mod, seqno, recs, info))
    # 附录
    def app_rows():
        out = []
        for mod in sel["modules"]:
            out.append(f'<tr class="keep-next"><th colspan="3" style="font-size:10pt">{E(mod["no"])} · {E(mod["name"])}</th></tr>')
            for g in mod["groups"]:
                if mod.get("kind") == "timed":
                    out.append(f'<tr class="keep-next"><td colspan="3" style="color:#17675F;font-weight:500;padding-top:6pt">{E(g["no"])} {E(g["name"])}</td></tr>')
                for q in g["questions"]:
                    out.append(f'<tr><td class="n" style="width:28pt"><a data-link="q:{q["id"]}">{seqno[q["id"]]:03d}</a></td>'
                               f'<td style="width:46pt;color:#4E666A">{E(q["id"])}</td><td>{E(q["move"])}</td></tr>')
        return "".join(out)
    for k in range(counts["app"]):
        def b(pno, pg, k=k):
            head = ('<h1 style="font-size:21pt;line-height:29pt;margin-top:0">附录 · 最快路径速查</h1>'
                    '<p class="lead">复盘用：盖住右栏，看编号回忆这题先看什么、凭什么排除；想不起来就翻回去重做。</p>') if k == 0 else ""
            return shell(pno, "附录", head + f'<table class="t">{flow("app", k, app_rows() if k == 0 else "", tag="tbody")}</table>', body_id=f"app-{k}")
        gen(["app"] if k == 0 else [], b)
    # 选题说明（放在最后，流式分页）
    def cut_body():
        ct = sel["appendix"]
        rows = "".join(f'<tr><td class="n">{E(r[0])}</td><td style="text-align:right">{r[1]}</td><td style="text-align:right">{r[2]}</td><td>{E(r[3])}</td></tr>' for r in ct["table"])
        items = "".join(f"<li>{E(x)}</li>" for x in ct["issues"])
        return (f'<h1 style="font-size:21pt;line-height:29pt;margin-top:0">选题说明</h1><p class="lead">{E(ct["lead"])}</p>'
                f'<table class="t"><tr><th style="width:118pt">原书部分</th><th style="width:30pt;text-align:right">原题</th>'
                f'<th style="width:30pt;text-align:right">入选</th><th>删去的主要是</th></tr>{rows}</table>'
                f'<h2>核对时发现的问题</h2><ul class="plain">{items}</ul>')
    for k in range(counts["cut"]):
        def b(pno, pg, k=k):
            return shell(pno, "选题说明", flow("cut", k, cut_body() if k == 0 else ""), body_id=f"cut-{k}")
        gen(["cut"] if k == 0 else [], b)
    return P, seqno, total

def _tail(mod, recs):
    nq = sum(len(g["questions"]) for g in mod["groups"])
    nc = sum(1 for g in mod["groups"] for q in g["questions"] if q["tier"] == "核心")
    t = (f'<h2>本模块怎么做</h2><p class="backup">共 {nq} 题。{E(mod.get("how", ""))}'
         + (f'先做 {nc} 道“核心”，再做“进阶”；时间紧只做核心题。' if 0 < nc < nq else "") + '</p>')
    if mod.get("backup"):
        items = "、".join(f'{b}（{"178题" if b[0] == "S" else "200题"}第{recs[b]["page"]}页）' for b in mod["backup"])
        t += f'<h2>加练备选</h2><p class="backup">{E(items)}。与上面的题动作重复，某类错得多时再练；页码指原书。</p>'
    return t

def src_label(r):
    """178题的来源去掉“原题本第x页;解析第y页”（指原试卷页码，不是本书或178题的页码）。"""
    import re
    s = r["source"]
    if r["id"][0] == "S":
        s = s.split("|")[0]
        s = re.sub(r"\s*全站正确率\s*(\d+%)", r" · 正确率\1", s)
    return re.sub(r"\s+", " ", s).strip()

def _tag(q, recs, seqno, mod, extra=""):
    r = recs[q["id"]]
    src = src_label(r)
    tier = "" if mod.get("kind") == "timed" else f'<span class="tier{" core" if q["tier"] == "核心" else ""}">{E(q["tier"])}</span>'
    return f'<span><b>{seqno[q["id"]]:03d}</b>原 {E(q["id"])} · {E(src)}{E(extra)}</span><span>{tier}</span>'

def _inline_page(items, mod, seqno, recs, info):
    keys, stamps = [], []
    for it in items:
        if it["kind"] == "head": keys.append(f'group:{it["g"].get("no") or it["g"]["name"]}')
        else:
            keys.append(f'q:{it["q"]["id"]}')
            stamps.append({"id": it["q"]["id"], "which": "q", "top": it["q_top"], "scale": it["scale"]})
            stamps.append({"id": it["q"]["id"], "which": "s", "top": it["s_top"], "scale": it["scale"]})
    def b(pno, pg):
        parts = []
        for it in items:
            if it["kind"] == "head":
                g = it["g"]
                gid = f'<span class="id">{E(g["no"])}</span>' if g.get("no") else ""
                cont = '<span class="cont">（续）</span>' if it["cont"] else ""
                hint = f'<div class="h"><b>{E(g.get("hint_label", "最快路径"))}</b>{E(g["hint"])}</div>' if g.get("hint") else ""
                parts.append(f'<div class="mh" style="top:{it["y"]:.2f}pt"><div class="t">{gid}{E(g["name"])}{cont}</div>{hint}</div>')
            else:
                g = it["g"]; extra = f' · 限时{g["time"]}秒' if g.get("time") else ""
                parts.append(f'<div class="tag" style="top:{it["y"]:.2f}pt">{_tag(it["q"], recs, seqno, mod, extra)}</div>')
                if it["q"].get("note"):
                    parts.append(f'<div class="note" style="top:{it["note_top"]:.2f}pt"><b>勘误</b>{E(it["q"]["note"])}</div>')
        return frame(pno, f'{mod["no"]} · {mod["name"]}', "".join(parts))
    return {"kind": "inline", "keys": keys, "build": b, "stamps": stamps}

def _timed_page(items, g, mod, seqno, recs, info, first, answers):
    keys, stamps = [], []
    for it in items:
        if not answers: keys.append(f'q:{it["q"]["id"]}')
        stamps.append({"id": it["q"]["id"], "which": "s" if answers else "q",
                       "top": it["s_top"] if answers else it["q_top"], "scale": it["scale"]})
    if first and not answers: keys.append(f'group:{g.get("no") or g["name"]}')
    def b(pno, pg):
        parts = []
        if first:
            y0 = CONTENT_TOP
            if answers:
                parts.append(f'<div class="mh" style="top:{y0:.2f}pt"><div class="t">{E(g["name"])} · 答案</div></div>')
            else:
                parts.append(f'<div class="mh" style="top:{y0:.2f}pt"><div class="t">{E(g["name"])}</div>'
                             f'<div class="h"><b>限时</b>{E(g["hint"])}</div></div>')
        for it in items:
            q = it["q"]; k = [x["id"] for x in g["questions"]].index(q["id"]) + 1
            if answers:
                label = f'第{k}题答案 · 原 {q["id"]} · {src_label(recs[q["id"]])}'
            else:
                label = f'第{k}题'
            parts.append(f'<div class="tag" style="top:{it["y"]:.2f}pt"><span><b>{seqno[q["id"]]:03d}</b>{E(label)}</span><span></span></div>')
        return frame(pno, f'{mod["no"]} · {"答案" if answers else "限时"}', "".join(parts))
    return {"kind": "timed_a" if answers else "timed_q", "keys": keys, "build": b, "stamps": stamps}
