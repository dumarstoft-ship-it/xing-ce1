"""精选本生成页：封面说明、认知地图、目录、模块导读、附录。

长内容（目录、导读卡片、速查表）放进 data-flow 容器，由 render.js 在浏览器里实际排版后
顺延到下一页；每组页数由 counts 给定，放不下时 build.py 加页重排（导读页成对增加，
保证练习页始终落在正面）。
"""
import math
from build import E, shell, tier_badge, short_src

def model_card(m, seqno):
    rows = []
    for k, label in (("essence", "本质"), ("signal", "信号"), ("first", "第一笔"), ("trap", "易错")):
        if m.get(k):
            rows.append(f'<div class="k">{label}</div><div class="v">{E(m[k])}</div>')
    chips = "".join(
        f'<a class="qchip{"" if q["tier"] == "核心" else " adv" if q["tier"] == "进阶" else " trap"}" data-link="q:{q["idx"]}">'
        f'<b>{seqno[q["idx"]]:02d}</b> 原{q["idx"]:02d}<i>{E(q["tier"])}</i></a>'
        for q in m["questions"])
    rows.append(f'<div class="k">题目</div><div class="v">{chips}</div>')
    return (f'<div class="card"><h3><span class="no">{E(m["no"])}</span>{E(m["name"])}</h3>'
            f'<div class="kv">{"".join(rows)}</div></div>')

def flow(name, seq, inner, tag="div", cls="", min_keep=1):
    return f'<{tag} class="{cls}" data-flow="{name}" data-seq="{seq}" data-min="{min_keep}">{inner}</{tag}>'

def default_counts(sel):
    c = {"toc": 2, "app": 4}
    for mi, _ in enumerate(sel["modules"]):
        c[f"m{mi+1}"] = 2
    return c

def plan_pages(sel, recs, counts):
    seqno, n = {}, 0
    for mod in sel["modules"]:
        for m in mod["models"]:
            for q in m["questions"]:
                n += 1; seqno[q["idx"]] = n
    plan = []
    # ---- 封面与选题说明 ----
    def b_cover(pno, pg):
        c = sel["cover"]
        how = "".join(f"<li>{E(x)}</li>" for x in c["how"])
        use = "".join(f"<li>{E(x)}</li>" for x in c["use"])
        body = (f'<h1>{E(sel["title"])}</h1><div class="sub">{E(sel["subtitle"])}</div>'
                f'<p class="lead">{E(c["lead"])}</p>'
                f'<h2>怎么挑的</h2><ul class="plain">{how}</ul>'
                f'<h2>怎么用</h2><ul class="plain">{use}</ul>'
                + (f'<div class="box"><p class="muted" style="font-size:10pt;line-height:17pt">{E(c["stats"])}</p></div>' if c.get("stats") else ""))
        return shell(pno, "封面与说明", body)
    plan.append(("gen", {"keys": ["cover"], "build": b_cover}))
    # ---- 认知地图 ----
    def b_map(pno, pg):
        mp = sel["map"]
        paras = "".join(f"<p>{E(x)}</p>" for x in mp["paras"])
        rows = "".join(
            f'<tr><td class="n"><a data-link="mod:{i+1}">{E(r[0])}</a></td><td>{E(r[1])}</td>'
            f'<td style="text-align:right;white-space:nowrap">{sum(len(m["questions"]) for m in sel["modules"][i]["models"])} 题</td>'
            f'<td class="p"><a data-link="mod:{i+1}">{pg.get(f"mod:{i+1}", "")}</a></td></tr>'
            for i, r in enumerate(mp["rows"]))
        tail = "".join(f"<p>{E(x)}</p>" for x in mp.get("tail", []))
        body = (f'<h1 style="font-size:22pt;line-height:30pt">{E(mp["title"])}</h1>{paras}'
                f'<table class="qlist" style="margin:6pt 0 12pt"><tr><th style="width:92pt">模块</th><th>它在练什么</th>'
                f'<th style="width:36pt;text-align:right">题数</th><th style="width:34pt;text-align:right">页码</th></tr>{rows}</table>{tail}')
        return shell(pno, "认知地图", body)
    plan.append(("gen", {"keys": ["map"], "build": b_map}))
    # ---- 目录 ----
    def toc_entries(pg):
        out = []
        for mi, mod in enumerate(sel["modules"]):
            out.append(f'<a class="toc-mod keep-next" data-link="mod:{mi+1}"><span>模块 {mod["no"]} · {E(mod["name"])}</span>'
                       f'<span>{pg.get(f"mod:{mi+1}", "")}</span></a>')
            for m in mod["models"]:
                fq = m["questions"][0]["idx"]
                chips = "".join(
                    f'<a class="chip{" adv" if q["tier"] != "核心" else ""}" data-link="q:{q["idx"]}">{seqno[q["idx"]]:02d} 原{q["idx"]:02d}</a>'
                    for q in m["questions"])
                out.append(f'<div class="toc-row"><a class="toc-line" data-link="q:{fq}"><span class="toc-name">'
                           f'<span class="muted" style="margin-right:6pt">{E(m["no"])}</span>{E(m["name"])}</span>'
                           f'<span class="toc-pg">{pg.get(f"q:{fq}", "")}</span></a><div class="chips">{chips}</div></div>')
        out.append('<div class="toc-row"><a class="toc-line" data-link="app"><span class="toc-name">附录 · 突破口速查</span>'
                   f'<span class="toc-pg">{pg.get("app", "")}</span></a></div>')
        out.append('<div class="toc-row" style="border-bottom:none"><a class="toc-line" data-link="cut"><span class="toc-name">选题说明：删去了什么、为什么</span>'
                   f'<span class="toc-pg">{pg.get("cut", "")}</span></a></div>')
        return "".join(out)
    nt = counts["toc"]
    def mk_toc(k):
        def b(pno, pg):
            head = '<h1 style="font-size:22pt;line-height:30pt;margin-top:0">目录</h1>' if k == 0 else ""
            return shell(pno, "目录", head + flow("toc", k, toc_entries(pg) if k == 0 else ""), body_id=f"toc-{k}")
        return b
    for k in range(nt):
        plan.append(("gen", {"keys": ["toc"] if k == 0 else [], "build": mk_toc(k)}))
    def b_cut(pno, pg):
        ct = sel["appendix"]
        rows = "".join(f'<tr><td class="n">{E(r[0])}</td><td style="text-align:right">{r[1]}</td>'
                       f'<td style="text-align:right">{r[2]}</td><td>{E(r[3])}</td></tr>' for r in ct["table"])
        items = "".join(f"<li>{E(x)}</li>" for x in ct["issues"])
        body = (f'<h1 style="font-size:22pt;line-height:30pt;margin-top:0">选题说明</h1>'
                f'<p class="lead">{E(ct["lead"])}</p>'
                f'<table class="qlist" style="margin:4pt 0 10pt"><tr><th style="width:84pt">原书大类</th><th style="width:34pt;text-align:right">原题</th>'
                f'<th style="width:34pt;text-align:right">入选</th><th>删去的主要是</th></tr>{rows}</table>'
                f'<h2>重解时发现的问题</h2><ul class="plain">{items}</ul>')
        return shell(pno, "选题说明", body, body_id="cut")
    cut_in_front = (2 + nt) % 2 == 1
    if cut_in_front:
        plan.append(("gen", {"keys": ["cut"], "build": b_cut}))
    # ---- 各模块：导读页（成对）＋题目 ----
    for mi, mod in enumerate(sel["modules"]):
        key, ng = f"mod:{mi+1}", counts[f"m{mi+1}"]
        assert ng % 2 == 0
        def mk_g(k, mod=mod, mi=mi, ng=ng):
            def b(pno, pg):
                cards = "".join(model_card(m, seqno) for m in mod["models"]) if k == 0 else ""
                if k == 0:
                    intro = "".join(f"<p>{E(p)}</p>" for p in mod["intro"])
                    head = (f'<div class="modno">模块 {mod["no"]}</div><h1 style="margin-top:2pt">{E(mod["name"])}</h1>'
                            f'<div class="sub">{E(mod["tagline"])}</div>{intro}')
                    return shell(pno, f'模块 {mod["no"]} · 导读', head + flow(f"m{mi+1}", 0, cards), body_id=f"m{mi+1}-0")
                tail = ""
                if k == ng - 1:
                    nq = sum(len(m["questions"]) for m in mod["models"])
                    ncore = sum(1 for m in mod["models"] for q in m["questions"] if q["tier"] == "核心")
                    tail += (f'<h2>本模块怎么做</h2><p class="backup">共 {nq} 题，按卡片顺序做。'
                             + (f'先做 {ncore} 道“核心”，再回头做“进阶”；时间紧只做核心题。' if ncore < nq and ncore else "")
                             + '</p>')
                    if mod.get("backup"):
                        items = "、".join(f'原{b["idx"]:02d}（第{recs[b["idx"]]["page"]}页）' for b in mod["backup"])
                        tail += (f'<h2>加练备选</h2><p class="backup">{E(items)}。这些题质量不错，但与上面的题动作重复；'
                                 f'某个模型错得多时再练。页码指原书《综合推理二刷题本》。</p>')
                    tail += '<div class="notes"><div class="nt">笔记 · 盖住卡片，用自己的话写下每个模型的第一笔</div></div>'
                body = f'<div class="flowcol">{flow(f"m{mi+1}", k, "")}{tail}</div>'
                return shell(pno, f'模块 {mod["no"]} · 导读（续）', body, body_id=f"m{mi+1}-{k}")
            return b
        for k in range(ng):
            plan.append(("gen", {"keys": [key] if k == 0 else [], "build": mk_g(k)}))
        for m in mod["models"]:
            for q in m["questions"]:
                plan.append(("q", q["idx"]))
    # ---- 附录：突破口速查 ----
    def app_rows():
        out = []
        for mod in sel["modules"]:
            out.append(f'<tr class="keep-next"><th colspan="3" style="font-size:10.5pt">模块 {mod["no"]} · {E(mod["name"])}</th></tr>')
            for m in mod["models"]:
                for q in m["questions"]:
                    out.append(f'<tr><td class="n" style="width:30pt"><a data-link="q:{q["idx"]}">{seqno[q["idx"]]:02d}</a></td>'
                               f'<td style="width:44pt;color:#50656A">原{q["idx"]:02d}</td><td>{E(q["move"])}</td></tr>')
        return "".join(out)
    na = counts["app"]
    def mk_app(k):
        def b(pno, pg):
            head = ""
            if k == 0:
                head = ('<h1 style="font-size:22pt;line-height:30pt;margin-top:0">附录 · 突破口速查</h1>'
                        '<p class="lead">做完全书后复盘用：盖住右栏，看题号回忆这题的第一笔；想不起来就翻回去重做。</p>')
            table = f'<table class="qlist">{flow("app", k, app_rows() if k == 0 else "", tag="tbody")}</table>'
            return shell(pno, "附录", head + table, body_id=f"app-{k}")
        return b
    for k in range(na):
        plan.append(("gen", {"keys": ["app"] if k == 0 else [], "build": mk_app(k)}))
    if not cut_in_front:
        plan.append(("gen", {"keys": ["cut"], "build": b_cut}))
    return plan

def add_outline(w, sel, recs, pg):
    w.add_outline_item("封面与说明", pg["cover"] - 1)
    w.add_outline_item("认知地图", pg["map"] - 1)
    w.add_outline_item("目录", pg["toc"] - 1)
    if pg["cut"] < pg["mod:1"]: w.add_outline_item("选题说明", pg["cut"] - 1)
    n = 0
    for mi, mod in enumerate(sel["modules"]):
        top = w.add_outline_item(f'模块 {mod["no"]} · {mod["name"]}', pg[f"mod:{mi+1}"] - 1)
        w.add_outline_item("导读", pg[f"mod:{mi+1}"] - 1, parent=top)
        for m in mod["models"]:
            mo = w.add_outline_item(f'{m["no"]} {m["name"]}', pg[f'q:{m["questions"][0]["idx"]}'] - 1, parent=top)
            for q in m["questions"]:
                n += 1
                w.add_outline_item(f'精选{n:02d} · 原{q["idx"]:02d} · {short_src(recs[q["idx"]]["source"], 24)}', pg[f'q:{q["idx"]}'] - 1, parent=mo)
    w.add_outline_item("附录 · 突破口速查", pg["app"] - 1)
    if pg["cut"] > pg["app"]: w.add_outline_item("选题说明", pg["cut"] - 1)
