"""数字推理精选本：页面规划。

生成页（封面、认知地图、目录、导读、附录）走 data-flow 流式分页；
题页成对出现：正面贴练习块、背面贴同一组题的解析块，坐标在这里算好。
"""
from common import E, shell, frame, CONTENT_TOP, CONTENT_H, PAGE_H

TAG_H, GAP, MH_FRONT, MH_BACK, BR_H = 13.0, 8.0, 46.0, 25.0, 15.0

def flow(name, seq, inner, tag="div", min_keep=1):
    return f'<{tag} data-flow="{name}" data-seq="{seq}" data-min="{min_keep}">{inner}</{tag}>'

def all_questions(sel):
    for mi, mod in enumerate(sel["modules"]):
        for g in mod["groups"]:
            for q in g["questions"]:
                yield mi, mod, g, q

def chips(g, seqno):
    return " ".join(
        f'<a class="qchip{"" if q["tier"] == "核心" else " adv"}" data-link="q:{q["id"]}"><b>{seqno[q["id"]]:02d}</b> {E(q["id"])}<i>{E(q["tier"])}</i></a>'
        for q in g["questions"])

def card(g, seqno):
    rows = []
    labels = g.get("labels", {})
    for k, label in (("essence", "本质"), ("signal", "信号"), ("first", "首式"), ("trap", "易错")):
        if g.get(k): rows.append(f'<div class="k">{labels.get(k, label)}</div><div class="v">{E(g[k])}</div>')
    rows.append(f'<div class="k">题目</div><div class="v">{chips(g, seqno)}</div>')
    tag = g.get("id") or g.get("no")
    no = f'<span class="no">{E(tag)}</span>' if tag else ""
    return f'<div class="card"><h3>{no}{E(g["name"])}</h3><div class="kv">{"".join(rows)}</div></div>'

def pack(mod, info):
    """把一个模块的题排成若干“正面/背面”页对。info[id] = {"hq": 练习块高, "hs": 解析块高, "br": 回练文字}"""
    pairs, cur = [], None
    def new():
        return {"front": [], "back": [], "fh": 0.0, "bh": 0.0}
    cur = new()
    for g in mod["groups"]:
        pending, cont = True, False
        for q in g["questions"]:
            d = info[q["id"]]
            def need(withhead):
                nf = (MH_FRONT if withhead else 0) + TAG_H + d["hq"] + GAP
                nb = (MH_BACK if withhead else 0) + TAG_H + d["hs"] + (BR_H if d.get("br") else 0) + GAP
                return nf, nb
            nf, nb = need(pending)
            if cur["fh"] + nf > CONTENT_H or cur["bh"] + nb > CONTENT_H:
                pairs.append(cur); cur = new()
                if not pending: cont = True
                pending = True; nf, nb = need(True)
            if pending:
                cur["front"].append({"kind": "head", "g": g, "y": CONTENT_TOP + cur["fh"], "cont": cont})
                cur["back"].append({"kind": "head", "g": g, "y": CONTENT_TOP + cur["bh"], "cont": cont})
                cur["fh"] += MH_FRONT; cur["bh"] += MH_BACK; pending = False
            cur["front"].append({"kind": "q", "q": q, "g": g, "y": CONTENT_TOP + cur["fh"]})
            cur["fh"] += TAG_H + d["hq"] + GAP
            cur["back"].append({"kind": "s", "q": q, "g": g, "y": CONTENT_TOP + cur["bh"]})
            cur["bh"] += TAG_H + d["hs"] + (BR_H if d.get("br") else 0) + GAP
    if cur["front"]: pairs.append(cur)
    return pairs

def head_html(it, side, mod):
    g = it["g"]
    tag = g.get("id") or g.get("no")
    gid = f'<span class="id">{E(tag)}</span>' if tag else ""
    cont = '<span class="cont">（续）</span>' if it["cont"] else ""
    hint = ""
    if side == "front" and g.get("hint"):
        hint = f'<div class="h"><b>{E(g.get("hint_label", "首式"))}</b>{E(g["hint"])}</div>'
    return f'<div class="mh" style="top:{it["y"]:.2f}pt"><div class="t">{gid}{E(g["name"])}{cont}</div>{hint}</div>'

def plan(sel, recs, info, counts):
    seqno, n = {}, 0
    for _, _, _, q in all_questions(sel):
        n += 1; seqno[q["id"]] = n
    total = n
    P = []      # 每页：{"kind": "gen"/"front"/"back", "keys": [...], "build": fn(pno, pg) -> html, "stamps": [...]}
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
    # 认知地图
    def b_map(pno, pg):
        mp = sel["map"]
        paras = "".join(f"<p>{E(x)}</p>" for x in mp["paras"])
        rows = "".join(f'<tr><td class="n">{E(r[0])}</td><td>{E(r[1])}</td><td>{E(r[2])}</td></tr>' for r in mp["table"])
        mods = "".join(
            f'<tr><td class="n"><a data-link="mod:{i+1}">{E(m["no"])} {E(m["name"])}</a></td><td>{E(m["tagline"])}</td>'
            f'<td style="text-align:right">{sum(len(g["questions"]) for g in m["groups"])} 题</td>'
            f'<td class="p"><a data-link="mod:{i+1}">{pg.get(f"mod:{i+1}", "")}</a></td></tr>' for i, m in enumerate(sel["modules"]))
        tail = "".join(f"<p>{E(x)}</p>" for x in mp.get("tail", []))
        return shell(pno, "认知地图",
                     f'<h1 style="font-size:21pt;line-height:29pt">{E(mp["title"])}</h1>{paras}'
                     f'<table class="t compact"><tr><th style="width:120pt">看到什么</th><th style="width:150pt">先写什么</th><th>对应模型</th></tr>{rows}</table>'
                     f'<table class="t compact"><tr><th style="width:110pt">模块</th><th>练什么</th><th style="width:36pt;text-align:right">题数</th>'
                     f'<th style="width:32pt;text-align:right">页码</th></tr>{mods}</table>{tail}')
    gen(["map"], b_map)
    # 目录
    def toc_entries(pg):
        out = []
        for mi, mod in enumerate(sel["modules"]):
            out.append(f'<a class="toc-mod keep-next" data-link="mod:{mi+1}"><span>模块 {E(mod["no"])} · {E(mod["name"])}</span><span>{pg.get(f"mod:{mi+1}", "")}</span></a>')
            for g in mod["groups"]:
                fq = g["questions"][0]["id"]
                cs = " ".join(f'<a class="chip{"" if q["tier"] == "核心" else " adv"}" data-link="q:{q["id"]}">{seqno[q["id"]]:02d} {E(q["id"])}</a>' for q in g["questions"])
                tg = g.get("id") or g.get("no")
                gid = f'<span class="muted" style="margin-right:6pt">{E(tg)}</span>' if tg else ""
                out.append(f'<div class="toc-row"><a class="toc-line" data-link="q:{fq}"><span class="toc-name">{gid}{E(g["name"])}</span>'
                           f'<span class="toc-pg">{pg.get(f"q:{fq}", "")}</span></a><div class="chips">{cs}</div></div>')
        out.append(f'<div class="toc-row"><a class="toc-line" data-link="app"><span class="toc-name">附录 · 首式速查</span><span class="toc-pg">{pg.get("app", "")}</span></a></div>')
        out.append(f'<div class="toc-row" style="border-bottom:none"><a class="toc-line" data-link="cut"><span class="toc-name">选题说明：删去了什么、为什么</span><span class="toc-pg">{pg.get("cut", "")}</span></a></div>')
        return "".join(out)
    for k in range(counts["toc"]):
        def b(pno, pg, k=k):
            head = '<h1 style="font-size:21pt;line-height:29pt;margin-top:0">目录</h1>' if k == 0 else ""
            return shell(pno, "目录", head + flow("toc", k, toc_entries(pg) if k == 0 else ""), body_id=f"toc-{k}")
        gen(["toc"] if k == 0 else [], b)
    # 选题说明
    def b_cut(pno, pg):
        ct = sel["appendix"]
        rows = "".join(f'<tr><td class="n">{E(r[0])}</td><td style="text-align:right">{r[1]}</td><td style="text-align:right">{r[2]}</td><td>{E(r[3])}</td></tr>' for r in ct["table"])
        items = "".join(f"<li>{E(x)}</li>" for x in ct["issues"])
        return shell(pno, "选题说明",
                     f'<h1 style="font-size:21pt;line-height:29pt;margin-top:0">选题说明</h1><p class="lead">{E(ct["lead"])}</p>'
                     f'<table class="t"><tr><th style="width:96pt">原书部分</th><th style="width:30pt;text-align:right">原题</th>'
                     f'<th style="width:30pt;text-align:right">入选</th><th>删去的主要是</th></tr>{rows}</table>'
                     f'<h2>重算时发现的问题</h2><ul class="plain">{items}</ul>', body_id="cut")
    cut_front = (2 + counts["toc"]) % 2 == 1
    if cut_front: gen(["cut"], b_cut)
    # 模块
    for mi, mod in enumerate(sel["modules"]):
        ng = counts[f"m{mi+1}"]
        for k in range(ng):
            def b(pno, pg, k=k, mod=mod, mi=mi, ng=ng):
                if k == 0:
                    intro = "".join(f"<p>{E(p)}</p>" for p in mod["intro"])
                    head = (f'<div class="modno">模块 {E(mod["no"])}</div><h1 style="margin-top:2pt">{E(mod["name"])}</h1>'
                            f'<div class="sub">{E(mod["tagline"])}</div>{intro}')
                    return shell(pno, f'模块 {mod["no"]} · 导读', head + flow(f"m{mi+1}", 0, "".join(card(g, seqno) for g in mod["groups"])), body_id=f"m{mi+1}-0")
                tail = ""
                if k == ng - 1:
                    nq = sum(len(g["questions"]) for g in mod["groups"])
                    nc = sum(1 for g in mod["groups"] for q in g["questions"] if q["tier"] == "核心")
                    tail += (f'<h2>本模块怎么做</h2><p class="backup">共 {nq} 题。{E(mod.get("how", ""))}'
                             + (f'先做 {nc} 道“核心”，再做“进阶”；时间紧只做核心题。' if 0 < nc < nq else "") + '</p>')
                    if mod.get("backup"):
                        items = "、".join(f'{b}（第{recs[b]["page"]}页）' for b in mod["backup"])
                        tail += f'<h2>加练备选</h2><p class="backup">{E(items)}。与上面的题动作重复，某个模型错得多时再练；页码指原书。</p>'
                    tail += '<div class="notes"><div class="nt">笔记 · 盖住卡片，写下每个模型的首式</div></div>'
                return shell(pno, f'模块 {mod["no"]} · 导读（续）', f'<div class="flowcol">{flow(f"m{mi+1}", k, "")}{tail}</div>', body_id=f"m{mi+1}-{k}")
            gen([f"mod:{mi+1}"] if k == 0 else [], b)
        for pair in pack(mod, info):
            for side in ("front", "back"):
                items = pair[side]
                keys = []
                if side == "front":
                    keys = [f"q:{it['q']['id']}" for it in items if it["kind"] == "q"]
                    keys += [f"group:{it['g'].get('id') or it['g']['name']}" for it in items if it["kind"] == "head"]
                def b(pno, pg, items=items, side=side, mod=mod):
                    parts = []
                    for it in items:
                        if it["kind"] == "head":
                            parts.append(head_html(it, side, mod))
                        elif it["kind"] == "q":
                            q = it["q"]; r = recs[q["id"]]
                            tier = f'<span class="tier{" core" if q["tier"] == "核心" else ""}">{E(q["tier"])}</span>'
                            parts.append(f'<div class="tag" style="top:{it["y"]:.2f}pt"><span><b>精选 {seqno[q["id"]]:02d}</b>原书 {E(q["id"])} · 第{r["page"]}页</span><span>{tier}</span></div>')
                        else:
                            q = it["q"]; d = info[q["id"]]
                            parts.append(f'<div class="tag" style="top:{it["y"]:.2f}pt"><span><b>精选 {seqno[q["id"]]:02d}</b>解析</span><span></span></div>')
                            if d.get("br"):
                                y = it["y"] + TAG_H + d["hs"] + 1
                                br = d["br"]
                                link = f' data-link="{br["link"]}"' if br.get("link") else ""
                                where = f'本册第{pg.get(br["link"], "")}页' if br.get("link") else br.get("where", "")
                                parts.append(f'<a class="br" style="top:{y:.2f}pt"{link}>回练 · {E(br["text"])} → {E(where)}</a>')
                    label = f'模块 {mod["no"]} · {"练习" if side == "front" else "解析"}'
                    return frame(pno, label, "".join(parts))
                stamps = []
                for it in items:
                    if it["kind"] in ("q", "s"):
                        stamps.append({"id": it["q"]["id"], "which": "q" if it["kind"] == "q" else "s", "top": it["y"] + TAG_H})
                P.append({"kind": side, "keys": keys, "build": b, "stamps": stamps})
    # 附录：首式速查
    def app_rows():
        out = []
        for mod in sel["modules"]:
            out.append(f'<tr class="keep-next"><th colspan="3" style="font-size:10pt">模块 {E(mod["no"])} · {E(mod["name"])}</th></tr>')
            for g in mod["groups"]:
                for q in g["questions"]:
                    out.append(f'<tr><td class="n" style="width:28pt"><a data-link="q:{q["id"]}">{seqno[q["id"]]:02d}</a></td>'
                               f'<td style="width:62pt;color:#4E666A">{E(q["id"])}</td><td>{E(q["move"])}</td></tr>')
        return "".join(out)
    for k in range(counts["app"]):
        def b(pno, pg, k=k):
            head = ('<h1 style="font-size:21pt;line-height:29pt;margin-top:0">附录 · 首式速查</h1>'
                    '<p class="lead">复盘用：盖住右栏，看编号回忆这题的首式；想不起来就翻回去重做。</p>') if k == 0 else ""
            return shell(pno, "附录", head + f'<table class="t">{flow("app", k, app_rows() if k == 0 else "", tag="tbody")}</table>', body_id=f"app-{k}")
        gen(["app"] if k == 0 else [], b)
    if not cut_front: gen(["cut"], b_cut)
    return P, seqno, total
