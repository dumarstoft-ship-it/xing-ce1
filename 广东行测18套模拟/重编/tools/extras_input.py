"""按 编排.json 导出“换入题、改写题、编辑新写的题”的盲做输入（不含答案）。

    python3 广东行测18套模拟/重编/tools/extras_input.py M08 [第31题 ...]

输出 重编/<套卷>/复核/extras_input.md。命令行可另加编号（如31），把改了选项的原题也放进来。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_season import BANK, blocks_md, q_md   # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "广东行测18套模拟" / "重编"
JZ = ROOT / "江浙行测_AI题库"
IMG = re.compile(r"!\[[^\]]*\]\((images/[^)]+)\)")


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def jz_md(s):
    return IMG.sub(lambda m: f"[图：{JZ / m.group(1)}]", s or "").strip()


def apply_plan(q, plan):
    """套用编排里的题干整段替换和文字改动，使盲做题面与印出来的一致。"""
    sid = q["id"]
    ov = (plan.get("stem_override") or {}).get(sid)
    if ov:
        q["stem"] = [dict(b) for b in ov["stem"]]
    q["options"] = {k: [dict(b) for b in v] for k, v in q["options"].items()}
    q["stem"] = [dict(b) for b in q["stem"]]
    for e in plan.get("edits", []):
        if e["source"] != sid:
            continue
        blocks = q["stem"] if e["where"] == "stem" else q["options"][e["where"]]
        hit = [b for b in blocks if b["type"] == "text" and e["old"] in b["text"]]
        assert len(hit) == 1, (sid, e["old"])
        hit[0]["text"] = hit[0]["text"].replace(e["old"], e["new"])
    return q


def main(paper, extra_numbers):
    plan = json.loads((R / paper / "编排.json").read_text(encoding="utf-8"))
    mock = {q["id"]: q for q in jl(BANK / "全部题目.jsonl")}
    jzq = {q["question_id"]: q for q in jl(JZ / "questions.jsonl")}
    orig_p = R / paper / "原创.json"
    orig = {o["id"]: o for o in json.loads(orig_p.read_text(encoding="utf-8"))} if orig_p.exists() else {}
    season = plan["season"]
    picks = {}
    for pos in plan["positions"]:
        for n, sid in pos["numbers"].items():
            if isinstance(sid, str):
                picks[int(n)] = sid
    moved = {v: int(k) for pos in plan["positions"] for k, v in pos["numbers"].items() if isinstance(v, int)}
    for sid in (plan.get("rewrite") or {}):
        n = int(sid.rsplit("q", 1)[1])
        picks[moved.get(n, n)] = sid       # 调了位置的改写题按新题号
    for n in extra_numbers:
        picks.setdefault(n, f"gd-mock-2026h2-s{season}-q{n}")
    out = [f"# {paper} 换入题、改写题与编辑新写的题（盲做用，不含答案）\n",
           "只看题面独立作答，写清理由；逻辑题能枚举的写枚举脚本；资料题按选项精度计算；图形题写清规律并逐项排除。\n"]
    for n in sorted(picks):
        sid = picks[n]
        rw = (plan.get("rewrite") or {}).get(sid)
        if sid in orig:
            o = orig[sid]
            q = {"number": n, "id": sid, "stem": o["stem"], "options": o["options"]}
            out.append(q_md(q).replace(str(BANK) + "/", ""))
        elif sid in jzq:
            g = jzq[sid]
            s = [f"### 第{n}题　`{sid}`", jz_md(g["stem"])]
            s += [f"{k}. {jz_md(v)}" for k, v in g["options"].items()]
            out.append("\n\n".join(s))
        elif rw:
            q = mock[sid]
            m = q.get("material")
            if m:
                out.append(f"## 资料：第{n}题所在材料\n\n" + blocks_md(m["blocks"]))
            s = [f"### 第{n}题　`{sid}`（改写）", rw["stem"]] + [f"{k}. {v}" for k, v in rw["options"].items()]
            out.append("\n\n".join(s))
        else:
            q = apply_plan(dict(mock[sid], number=n), plan)
            if q.get("material"):
                out.append(f"## 资料：第{n}题所在材料\n\n" + blocks_md(q["material"]["blocks"]))
            md = q_md(q).replace(f"[图：{BANK}/广东行测18套模拟/", f"[图：{ROOT}/广东行测18套模拟/")
            for svg in re.findall(r"\[图：([^\]]+\.svg)\]", md):     # 编辑重画的SVG另给渲染好的PNG
                png = Path(svg).with_name(Path(svg).stem + "_preview.png")
                if png.exists():
                    md = md.replace(f"[图：{svg}]", f"[图：{svg}]（渲染PNG：{png}）")
            out.append(md)
    dst = R / paper / "复核" / "extras_input.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n\n".join(out) + "\n", encoding="utf-8")
    print(dst, sorted(picks))


if __name__ == "__main__":
    main(sys.argv[1], [int(x) for x in sys.argv[2:]])
