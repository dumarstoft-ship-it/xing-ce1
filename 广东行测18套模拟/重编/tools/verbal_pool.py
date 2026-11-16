"""言语题池：国考言语＋江浙言语，粗分题型，标出旧卷用过、撤下、旧专项出现过的题。

输出：重编/言语/pool.json（每题一项）与 pool_summary.txt。题型是按设问关键词粗分的，选题时以读题为准。
"""
import json, re, html, unicodedata, subprocess
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "广东行测18套模拟"
OUT = S / "重编/言语"


def old_selection(paper_dir):
    """旧版（0.x）选编记录：归档前在套卷目录，归档后在 历史版本/<版本>/。"""
    p = paper_dir / "selection.json"
    if p.exists():
        return p
    cands = sorted(paper_dir.glob("历史版本/0.*/selection.json"))
    return cands[-1]

def norm(s):
    s = html.unescape(unicodedata.normalize("NFKC", str(s)))
    s = re.sub(r"<[^>\n]{0,300}>", "", s)
    return re.sub(r"[\W_]+", "", s)

def subtype(stem, opts):
    st = stem.replace("\n", "")
    tail = st[-60:]
    blanks = len(re.findall(r"_{2,}|＿{2,}|（\s*）|\(\s*\)", st))
    if re.search(r"(重新排列|排序|语序正确|顺序最恰当|排列顺序)", tail) or re.search(r"①.*②.*③", st) and re.search(r"(排列|顺序)", st):
        n = len(set(re.findall(r"[①②③④⑤⑥⑦⑧]", st)))
        return f"语句排序{n}句", blanks
    if re.search(r"填入.*(横线|空白|划线|画线).*(一句|句子|语句)", tail) or re.search(r"最恰当的一句", tail):
        return "语句填空", blanks
    if re.search(r"填入.*(横线|空白|划线|画线|括号)|依次填入", tail):
        k = 1
        o = [v if isinstance(v, str) else "" for v in opts.values()]
        parts = [len([p for p in re.split(r"[ 　，、；]+", x.strip()) if p]) for x in o]
        if parts and min(parts) >= 2:
            k = min(parts)
        elif blanks >= 2:
            k = blanks
        return ("逻辑填空-单空" if k == 1 else f"逻辑填空-{k}空"), blanks
    if re.search(r"标题", tail):
        return "标题", blanks
    if re.search(r"接下来|下文|后文.*(讲|介绍|论述)", tail):
        return "接语", blanks
    if re.search(r"(画线|划线|加点|文中.*指|这里的.*是指|所指|理解为)", tail):
        return "词句理解", blanks
    if re.search(r"(不符合|不正确|错误|无法得出|不能得出|不能推出|理解准确|符合文意|说法正确|与原文|可以推出|能够推出|可以得出|能够得出|由此可知|根据这段文字|下列说法|以下说法|理解正确|不属于)", tail):
        return "细节判断", blanks
    if re.search(r"(意在|旨在|主要(说明|讲|介绍|强调|论述|谈|阐述|是|说的)|重在|作者.*(认同|观点|态度|赞同|主张)|概括|主旨|中心|核心|观点是|想要说明|想表达|强调的是|论述的重点)", tail):
        return "主旨意图", blanks
    return "?", blanks

def load_bank():
    pool = []
    for l in open(ROOT / "国考/言语理解/2016-2025/all.jsonl", encoding="utf-8"):
        q = json.loads(l)
        stem = (q.get("passage") or "") + "\n" + q["stem"]
        pool.append({"id": q["id"], "bank": "国考", "year": q["year"], "stem": stem, "options": q["options"],
                     "answer": q.get("answer"), "answer_status": q.get("answer_status"),
                     "has_analysis": False, "flags": q.get("notes") or []})
    qs = [json.loads(l) for l in open(ROOT / "江浙行测_AI题库/questions.jsonl", encoding="utf-8")]
    an = {a["question_id"]: a for a in (json.loads(l) for l in open(ROOT / "江浙行测_AI题库/answers.jsonl", encoding="utf-8"))}
    for q in qs:
        if q.get("section") != "言语理解与表达":
            continue
        a = an.get(q["question_id"], {})
        stem = q["stem"]
        if q.get("materials"):
            stem = "\n".join(m.get("text", "") if isinstance(m, dict) else str(m) for m in q["materials"]) + "\n" + stem
        opts = {k: (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)) for k, v in (q.get("options") or {}).items()}
        pool.append({"id": q["question_id"], "bank": "江浙", "year": q["year"], "stem": stem, "options": opts,
                     "answer": a.get("correct_answer"), "answer_status": "single" if a.get("correct_answer") else "none",
                     "has_analysis": bool(a.get("analysis")), "flags": q.get("flags") or q.get("quality_flags") or []})
    return pool

def old_corpus():
    """旧24天集训、习题本的全部文本（按当前提交读取已跟踪文件）。"""
    files = subprocess.check_output(["git", "-c", "core.quotepath=off", "ls-files", "广东行测24天集训", "习题本"], cwd=ROOT).decode().splitlines()
    text = []
    for f in files:
        if Path(f).suffix.lower() in {".md", ".json", ".jsonl", ".txt", ".html", ".py", ".csv"}:
            try:
                text.append(norm((ROOT / f).read_text(encoding="utf-8", errors="ignore")))
            except FileNotFoundError:
                pass
    return "".join(text)

def used_and_withdrawn():
    used, withdrawn = {}, {}
    for p in ["M01", "M02", "M03", "M04", "M05"]:
        for q in json.load(open(old_selection(S / p), encoding="utf-8")):
            if q.get("source_id"):
                used[q["source_id"]] = f"{p}第{q['number']}题"
    for p in ["M01", "M02", "M03", "M04", "M05"]:
        for f in (S / p).rglob("*撤*"):
            if f.suffix == ".json":
                try:
                    d = json.load(open(f, encoding="utf-8"))
                except Exception:
                    continue
                for r in (d if isinstance(d, list) else d.get("records", [])):
                    if isinstance(r, dict) and r.get("source_id"):
                        withdrawn.setdefault(r["source_id"], r.get("reason", ""))
    return used, withdrawn

def main():
    pool = load_bank()
    corpus = old_corpus()
    used, withdrawn = used_and_withdrawn()
    for q in pool:
        q["subtype"], q["blank_marks"] = subtype(q["stem"], q["options"])
        n = norm(q["stem"])
        q["chars"] = len(n)
        hit = None
        if q["id"] in corpus:
            hit = "id"
        else:
            for i in range(0, max(1, len(n) - 40), 30):
                w = n[i:i + 40]
                if len(w) >= 30 and w in corpus:
                    hit = "text"
                    break
        q["exposed_old_drill"] = hit
        q["used_in_old"] = used.get(q["id"])
        q["withdrawn_reason"] = withdrawn.get(q["id"])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pool.json").write_text(json.dumps(pool, ensure_ascii=False, indent=0), encoding="utf-8")
    c = defaultdict(Counter)
    for q in pool:
        ok = not q["exposed_old_drill"] and not q["withdrawn_reason"] and q["answer"] and q["answer_status"] == "single"
        c[q["subtype"]]["可用" if ok else "不可用"] += 1
    lines = [f"{k}: {dict(v)}" for k, v in sorted(c.items())]
    lines.append(f"旧专项出现过: {sum(1 for q in pool if q['exposed_old_drill'])}；撤下: {sum(1 for q in pool if q['withdrawn_reason'])}；旧卷用过: {sum(1 for q in pool if q['used_in_old'])}")
    (OUT / "pool_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
