"""M04 0.2.0增量复核：比对0.1.0与0.2.0的考生可见文字，查空白改动，核对排版空白勘误与答案键。

只读仓库。缺省仓库根目录为 /home/user/xing-ce1，可用第一个参数另指。
在本目录运行：python3 -B check_v020.py
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/user/xing-ce1")
M04 = ROOT / "广东行测18套模拟/M04"
HERE = Path(__file__).resolve().parent
BASE = "a2d86fd"          # M04 0.1.0，Claude审核所据版本
BASE_SHA = "1ac5d186100f2a071a193aafba0562d026aa2b263b76edee701647fde00390c7"


def jl(text):
    return {json.loads(l)["number"]: json.loads(l) for l in text.splitlines() if l.strip()}


raw_old = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:广东行测18套模拟/M04/题目.jsonl"],
                         capture_output=True, check=True).stdout
assert hashlib.sha256(raw_old).hexdigest() == BASE_SHA, "0.1.0底稿指纹不符"
old = jl(raw_old.decode("utf-8"))
new = jl((M04 / "题目.jsonl").read_text(encoding="utf-8"))
sel = {r["number"]: r for r in json.loads((M04 / "selection.json").read_text(encoding="utf-8"))}
src = {r["number"]: r for r in map(json.loads, (M04 / "来源登记.jsonl").read_text(encoding="utf-8").splitlines()) if r}
jz = {r["question_id"]: r for r in map(json.loads, (ROOT / "江浙行测_AI题库/questions.jsonl").read_text(encoding="utf-8").splitlines()) if r}


def texts(q):
    """考生可见的文字块：(位置, 块序, 文字)。"""
    out = [("题干", i, b["text"]) for i, b in enumerate(q["stem"]) if b["type"] == "text"]
    for k, v in (q.get("options") or {}).items():
        out += [("选项" + k, i, b["text"]) for i, b in enumerate(v) if b["type"] == "text"]
    for m in q.get("materials") or []:
        out += [("材料", i, b["text"]) for i, b in enumerate(m["blocks"]) if b["type"] == "text"]
    return out


def visible(q):
    def strip(b):
        return {k: v for k, v in b.items() if k in ("type", "text", "path", "rows", "headers", "title", "notes")}
    return json.dumps({"stem": [strip(b) for b in q["stem"]],
                       "options": {k: [strip(b) for b in v] for k, v in (q.get("options") or {}).items()},
                       "materials": [[strip(b) for b in m["blocks"]] for m in q.get("materials") or []]},
                      ensure_ascii=False, sort_keys=True)


compact = lambda s: re.sub(r"\s", "", s)
report = {"base": BASE, "题目.jsonl_SHA256": hashlib.sha256((M04 / "题目.jsonl").read_bytes()).hexdigest()}

# 1. 考生可见改动；只改空白的单列
changed, ws_only = [], []
for n in range(1, 91):
    if visible(old[n]) != visible(new[n]):
        changed.append(n)
        a, b = texts(old[n]), texts(new[n])
        if len(a) == len(b):
            for (w, i, x), (_, _, y) in zip(a, b):
                if x != y and compact(x) == compact(y):
                    ws_only.append({"题号": n, "位置": w, "0.1.0": x[-40:], "0.2.0": y[-40:]})
report["考生可见改动题号"] = changed
report["只改空白的文字块"] = ws_only

# 2. 江浙来源题：选项汉字间空格是否与源题一致（源题多空选项词间有空格）
lost = []
for n, r in src.items():
    s = jz.get(r["source_id"])
    if not s:
        continue
    for k, v in (s.get("options") or {}).items():
        cur = "".join(b["text"] for b in new[n]["options"].get(k, []) if b["type"] == "text")
        if re.search(r"[一-鿿] +[一-鿿]", v) and compact(cur) == compact(v) \
                and not re.search(r"[一-鿿] +[一-鿿]", cur):
            lost.append({"题号": n, "选项": k, "源题": v, "0.2.0": cur})
report["源题有词间空格而0.2.0删去"] = lost

# 3. 排版空白勘误：只改空白；选项须与源题逐字（含空格）相同
fixes = json.loads((ROOT / "广东行测18套模拟/打印排版/排版空白勘误.json").read_text(encoding="utf-8"))
checked = []
for e in fixes:
    if e["套卷"] != "M04":
        continue
    q = new[e["题号"]]
    blocks = q["stem"] if e["位置"] == "题干" else q["options"][e["位置"].removeprefix("选项")]
    cur = blocks[e.get("块", 0)]["text"]
    ok_sha = hashlib.sha256(cur.encode("utf-8")).hexdigest() == e["底稿文字SHA256"]
    ok_ws = compact(cur) == compact(e["改为"])
    ok_src = True
    if e["位置"].startswith("选项"):
        ok_src = jz[src[e["题号"]]["source_id"]]["options"][e["位置"][-1]] == e["改为"]
    checked.append({"题号": e["题号"], "位置": e["位置"], "底稿未变": ok_sha, "只改空白": ok_ws, "与源题一致": ok_src})
report["排版空白勘误核对"] = checked

# 4. 答案键：0.1.0盲解（未改题）与本轮盲解（改动题）。0.1.0七个模块的盲解格式不一，逐层找题号与答案
def harvest(obj):
    found = {}

    def walk(v, key=None):
        if isinstance(v, dict):
            n = None
            for k in ("number", "no", "题号", "q", "id"):
                if k in v and str(v[k]).isdigit():
                    n = int(v[k])
            if n is None and key is not None:
                m = re.fullmatch(r"[Qq第]?0*(\d{1,2})题?", str(key))
                if m:
                    n = int(m.group(1))
            for k in ("answer_original", "answer", "blind_answer", "盲解", "answer_redrawn", "blind"):
                if k in v and n and 1 <= n <= 90:
                    a = v[k]
                    if isinstance(a, dict):
                        a = next((a[x] for x in ("answer", "original", "final") if isinstance(a.get(x), str)), None)
                    if isinstance(a, str):
                        found.setdefault(n, a)
                    break
            for k, x in v.items():
                walk(x, k)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(obj)
    return found


old_sel = {r["number"]: r for r in json.loads(subprocess.run(
    ["git", "-C", str(ROOT), "show", f"{BASE}:广东行测18套模拟/M04/selection.json"],
    capture_output=True, check=True).stdout.decode("utf-8"))}
report["答案键改动"] = [(n, old_sel[n]["answer"], sel[n]["answer"]) for n in range(1, 91)
                    if old_sel[n]["answer"] != sel[n]["answer"]]
blind = {}
for m in ("pol", "verbal", "quant", "fig", "logic", "sci", "data"):
    for n, a in harvest(json.loads((HERE.parent / "blind" / f"{m}.json").read_text(encoding="utf-8"))).items():
        if sel[n]["question_type"] == "true_false":
            a = {"A": "正确", "B": "错误"}.get(a, a)
        blind[n] = a.removeprefix("原图（未重绘）")
redo = {}
for f in ("text_answers.json", "quantlogic_answers.json"):
    for k, v in json.loads((HERE / "blind" / f).read_text(encoding="utf-8")).items():
        if k.isdigit():
            redo[int(k)] = v["answer"]
report["本轮重新盲解"] = {str(n): {"盲解": a, "答案键": sel[n]["answer"]} for n, a in sorted(redo.items())}
blind.update(redo)   # 换题（2、57）及改动题以本轮盲解为准
report["盲解覆盖题数"] = len(blind)
report["盲解与答案键不一致"] = [(n, blind.get(n), sel[n]["answer"]) for n in range(1, 91)
                          if str(blind.get(n)) != str(sel[n]["answer"])]

out = HERE / "check_v020.out.json"
out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: (v if not isinstance(v, list) or len(v) < 12 else f"{len(v)}项") for k, v in report.items()},
                 ensure_ascii=False, indent=1))
