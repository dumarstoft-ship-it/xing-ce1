"""M09起：按编排.json的 sources 把第31—90题导出为解题用的输入文件（不含答案），来源答案另存 prior.json。

用法：python3 广东行测18套模拟/重编/tools/extract_sources.py M09
输出：重编/<套卷>/输入/{quant_sci,fig_logic,data}.{json,md} 与 prior.json
（quant_sci：第31—45题与第66—70题；fig_logic：第46—65题；data：第71—90题）

题图、资料里的表格和统计图都是原卷裁图，写绝对路径，用Read工具看图；题库对图里的文字、数字另有转写，
一并给出（转写可能有误，以图为准）。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "广东行测18套模拟/重编"
DIRS = ("广东/行测/2013-2021", "广东/行测/2022-2026", "广东/事业单位/结构化", "国考/资料分析")


JZ = "江浙行测_AI题库"
IMG = re.compile(r"!\[[^\]]*\]\((images/[^)]+)\)")
HD = re.compile(r"\[代码描摹高清 PNG\]\([^)]*\)\s*·\s*\[SVG\]\([^)]*\)（原图为准）")


def jz_as_bank(q, a):
    """江浙题库的一题转成与广东题库相同的字段（M12起数学运算可用江苏卷难题）：文字里的原图链接转为题图。"""
    figs = []

    def strip(s):
        s = HD.sub("", s or "")
        for m in IMG.finditer(s):
            figs.append({"path": m.group(1), "role": "question"})
        return IMG.sub("", s).strip()
    stem = strip(q["stem"])
    opts = []
    for k in sorted(q["options"]):
        before = len(figs)
        t = strip(q["options"][k])
        if len(figs) > before:
            figs[-1]["role"] = "option"
            figs[-1]["option_label"] = k
        opts.append({"label": k, "text": t})
    return {"id": q["question_id"], "section": q["section"], "stem": stem, "options": opts, "figures": figs,
            "answer": {"values": [[a.get("correct_answer")]] if a.get("correct_answer") else [], "status": "known",
                       "source_pages": (a.get("source") or {}).get("pdf_pages")},
            "source": {"answer_pdf": (a.get("source") or {}).get("file")}}


def bank():
    out = {}
    for d in DIRS:
        for f in sorted(list((ROOT / d).glob("GD*.jsonl")) + list((ROOT / d).glob("SYDW20*.jsonl"))
                        + list((ROOT / d).glob("GK20*.jsonl"))):
            if f.name == "all.jsonl":
                continue
            for line in open(f, encoding="utf-8"):
                q = json.loads(line)
                out[q["id"]] = (d, q)
    jq = {q["question_id"]: q for q in map(json.loads, open(ROOT / JZ / "questions.jsonl", encoding="utf-8"))}
    ja = {x["question_id"]: x for x in map(json.loads, open(ROOT / JZ / "answers.jsonl", encoding="utf-8"))}
    for i, q in jq.items():
        out[i] = (JZ, jz_as_bank(q, ja.get(i, {})))
    return out


def fig(d, f):
    x = {"path": str(ROOT / d / f["path"]), "role": f.get("role")}
    if f.get("option_label"):
        x["option_label"] = f["option_label"]
    if f.get("transcription"):
        x["transcription"] = f["transcription"]
    return x


def material(d, m):
    out = []
    for b in m.get("content") or []:
        if b.get("type") == "text":
            out.append({"type": "text", "text": b["text"]})
        else:
            x = {"type": "image", "path": str(ROOT / d / b["path"])}
            if b.get("transcription"):
                x["transcription"] = b["transcription"]
            out.append(x)
    return {"id": m["id"], "content": out}


def q_md(x):
    s = [f"### 第{x['number']}题　`{x['id']}`", x["stem"]]
    for f in x["figures"]:
        s.append(f"[图（{f.get('role')}{'，' + f['option_label'] + '项' if f.get('option_label') else ''}）：{f['path']}]")
        if f.get("transcription"):
            s.append("图中文字、数字的转写（以图为准）：\n" + f["transcription"])
    for o in x["options"]:
        s.append(f"{o['label']}. {o['text']}")
    return "\n\n".join(s)


def m_md(m):
    s = [f"#### 资料 `{m['id']}`"]
    for b in m["content"]:
        if b["type"] == "text":
            s.append(b["text"])
        else:
            s.append(f"[图：{b['path']}]")
            if b.get("transcription"):
                s.append("图表的转写（以图为准）：\n" + b["transcription"])
    return "\n\n".join(s)


def main(paper):
    plan = json.loads((R / paper / "编排.json").read_text(encoding="utf-8"))
    src = {int(n): sid for n, sid in plan["sources"].items()}
    B = bank()
    groups = {"quant_sci": [n for n in sorted(src) if n <= 45 or 66 <= n <= 70],
              "fig_logic": [n for n in sorted(src) if 46 <= n <= 65],
              "data": [n for n in sorted(src) if n >= 71]}
    out = R / paper / "输入"
    out.mkdir(parents=True, exist_ok=True)
    prior = {}
    for name, nums in groups.items():
        items, md, seen = [], [f"# {paper} 输入：{name}（不含答案）\n"], set()
        for n in nums:
            d, q = B[src[n]]
            x = {"id": q["id"], "number": n, "section": q["section"], "stem": q["stem"],
                 "options": [{"label": o["label"], "text": o["text"]} for o in q["options"]],
                 "figures": [fig(d, f) for f in q.get("figures") or []]}
            if q.get("material"):
                x["material"] = material(d, q["material"])
                if q["material"]["id"] not in seen:
                    seen.add(q["material"]["id"])
                    md.append(m_md(x["material"]))
            items.append(x)
            md.append(q_md(x))
            a = q.get("answer") or {}
            prior[q["id"]] = {"answer": "".join(a["values"][0]) if a.get("values") and len(a["values"]) == 1 else a.get("values"),
                              "status": a.get("status"), "answer_pdf": (q.get("source") or {}).get("answer_pdf"),
                              "answer_pages": a.get("source_pages"), "note": a.get("note") or ""}
        (out / f"{name}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        (out / f"{name}.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
        print(name, len(items))
    (out / "prior.json").write_text(json.dumps(prior, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
