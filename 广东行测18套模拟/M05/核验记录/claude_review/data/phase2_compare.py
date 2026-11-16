# -*- coding: utf-8 -*-
"""第二阶段：M05 第71—90题 材料/题面/选项 与题源逐字逐格比对（只读仓库）。"""
import json, os, difflib, hashlib
REPO = "/home/user/xing-ce1"
M05 = os.path.join(REPO, "广东行测18套模拟/M05")
SRC = os.path.join(REPO, "模考/2026下半年广东卷_16-33季_AI可读")
HERE = os.path.dirname(os.path.abspath(__file__))

blind = {q["number"]: q for q in json.load(open(os.path.join(HERE, "blind_input.json"), encoding="utf-8"))}
m05 = {r["number"]: r for r in (json.loads(l) for l in open(os.path.join(M05, "题目.jsonl"), encoding="utf-8") if l.strip())}
sel = {r["number"]: r for r in json.load(open(os.path.join(M05, "selection.json"), encoding="utf-8"))}
bank = {r["id"]: r for r in (json.loads(l) for l in open(os.path.join(SRC, "全部题目.jsonl"), encoding="utf-8") if l.strip())}
imgs = {x["id"]: x for x in json.load(open(os.path.join(SRC, "图片清单.json"), encoding="utf-8"))}

def strip_ids(blocks):
    out = []
    for b in blocks:
        b = dict(b)
        for k in ("source_asset_id",):
            b.pop(k, None)
        out.append(b)
    return out

def tdiff(a, b, label):
    if a == b:
        return []
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    res = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            res.append("%s %s: 源[%d:%d]=%r → M05[%d:%d]=%r" % (label, op, i1, i2, a[i1:i2], j1, j2, b[j1:j2]))
    return res

def cmp_blocks(src_blocks, m_blocks, label):
    diffs = []
    if len(src_blocks) != len(m_blocks):
        diffs.append("%s 块数不同：源 %d，M05 %d" % (label, len(src_blocks), len(m_blocks)))
    for i, (s, m) in enumerate(zip(src_blocks, m_blocks)):
        L = "%s 块%d(%s)" % (label, i, s.get("type"))
        if s.get("type") != m.get("type"):
            diffs.append("%s 类型不同 %s→%s" % (L, s.get("type"), m.get("type")))
            continue
        if s["type"] == "text":
            diffs += tdiff(s["text"], m["text"], L)
        elif s["type"] == "table":
            diffs += tdiff(s.get("title", ""), m.get("title", ""), L + " 标题")
            if s.get("headers") != m.get("headers"):
                for j, (h1, h2) in enumerate(zip(s.get("headers", []), m.get("headers", []))):
                    diffs += tdiff(h1, h2, L + " 表头列%d" % j)
                if len(s.get("headers", [])) != len(m.get("headers", [])):
                    diffs.append(L + " 表头列数不同")
            sr, mr = s.get("rows", []), m.get("rows", [])
            if len(sr) != len(mr):
                diffs.append("%s 行数不同 源%d M05%d" % (L, len(sr), len(mr)))
            ncell = 0
            for r, (a, b) in enumerate(zip(sr, mr)):
                if len(a) != len(b):
                    diffs.append("%s 行%d 列数不同" % (L, r))
                for c, (x, y) in enumerate(zip(a, b)):
                    ncell += 1
                    if x != y:
                        diffs.append("%s 行%d列%d：源%r → M05%r" % (L, r, c, x, y))
            sn, mn = s.get("notes", None), m.get("notes", None)
            if sn != mn:
                diffs.append("%s notes：源%r → M05%r" % (L, sn, mn))
            extra_s = set(s) - {"type", "title", "headers", "rows", "notes", "source_asset_id"}
            extra_m = set(m) - {"type", "title", "headers", "rows", "notes", "source_asset_id"}
            if extra_s or extra_m:
                diffs.append("%s 其他字段 源%s M05%s" % (L, sorted(extra_s), sorted(extra_m)))
            diffs.append("%s（逐格比对 %d 格完成）" % (L, ncell))
        elif s["type"] == "figure":
            if s.get("asset_id") != m.get("asset_id"):
                diffs.append("%s 图 asset 不同 %s→%s" % (L, s.get("asset_id"), m.get("asset_id")))
    return diffs

seen_mat = set()
for n in range(71, 91):
    S = sel[n]; sid = S["source_id"]; B = bank[sid]; M = m05[n]
    print("=" * 20, "第%d题 ← %s（源第%d题，%s）" % (n, sid, B["number"], B["source"]["source_name"]))
    # 0. 盲解输入与 M05 题目.jsonl 一致性
    def norm_meta(x):
        if isinstance(x, dict):
            return {k: norm_meta(v) for k, v in x.items() if k not in ("source_asset_id", "abs_path")}
        if isinstance(x, list):
            return [norm_meta(v) for v in x]
        return x
    same_blind = all(norm_meta(blind[n][k]) == norm_meta(M[k]) for k in ("stem", "options", "materials"))
    print("盲解输入 == M05/题目.jsonl（忽略 source_asset_id/abs_path 元数据）：", same_blind)
    # 1. selection.source_question 快照 == 题源
    snap = S["source_question"]
    snap_ok = all(snap.get(k) == B.get(k) for k in ("stem", "options", "material", "answer"))
    print("selection.source_question 快照 == 题源记录：", snap_ok)
    # 2. 题干、选项
    d = tdiff(json.dumps(B["stem"], ensure_ascii=False), json.dumps(M["stem"], ensure_ascii=False), "题干")
    print("题干差异：", d or "无")
    od = []
    for k in "ABCD":
        sb, mb = B["options"][k], M["options"][k]
        if sb != mb:
            od.append("%s: 源%s → M05%s" % (k, json.dumps(sb, ensure_ascii=False), json.dumps(mb, ensure_ascii=False)))
    print("选项差异：", od or "无")
    for k in "ABCD":
        for b in M["options"][k]:
            if b.get("type") == "figure":
                p = os.path.join(REPO, b["path"])
                h = hashlib.sha256(open(p, "rb").read()).hexdigest()
                print("  选项%s 图 %s sha256=%s… 与图片清单%s" % (k, b["asset_id"], h[:12],
                      "一致" if imgs.get(b["asset_id"], {}).get("sha256") == h else "不一致"))
    # 3. 材料
    mid = B["material_id"]
    if mid in seen_mat:
        print("材料：同组前题已比对（M05 材料与前题%s）" % ("相同" if M["materials"] == m05[n - 1]["materials"] else "不同！"))
        continue
    seen_mat.add(mid)
    srcb = B["material"]["blocks"]
    mb = []
    for mm in M["materials"]:
        mb += mm["blocks"]
    diffs = cmp_blocks(srcb, mb, "材料")
    print("材料差异/比对：")
    for x in diffs:
        print("   ", x)
    # selection 中的 materials 覆盖（76-80）
    if "materials" in S:
        smb = []
        for mm in S["materials"]:
            smb += mm.get("blocks", [])
        print("selection.materials 覆盖 == M05/题目.jsonl 材料：", smb == mb)
    print("edits：", json.dumps(S["edits"], ensure_ascii=False))
