# 只读：逐字（含空白）比对 M05 题目.jsonl 与源库 questions.jsonl 第16—30题
import json, difflib, unicodedata
BANK = "/home/user/xing-ce1/江浙行测_AI题库"
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
sel = {q["number"]: q for q in json.load(open(f"{M05}/selection.json", encoding="utf-8"))}
tm = {}
for line in open(f"{M05}/题目.jsonl", encoding="utf-8"):
    r = json.loads(line); tm[r["number"]] = r
bank = {}
for line in open(f"{BANK}/questions.jsonl", encoding="utf-8"):
    r = json.loads(line); bank[r["question_id"]] = r
blind = {q["number"]: q for q in json.load(open("blind_input.json", encoding="utf-8"))}

def flat(blocks):
    if isinstance(blocks, str): return blocks
    out = []
    for b in blocks:
        if b.get("type") == "text": out.append(b["text"])
        else: out.append(f"<{b.get('type')}:{json.dumps(b, ensure_ascii=False)}>")
    return "".join(out)

def ws_profile(s):
    return {"newlines": s.count("\n"), "ascii_spaces": s.count(" "), "fullwidth_spaces": s.count("　"),
            "nbsp": s.count(" "), "tabs": s.count("\t"), "underscores": s.count("_")}

for n in range(16, 31):
    sid = sel[n]["source_id"]; src = bank[sid]; m = tm[n]
    print(f"### {n} {sid}  M05 keys={list(m.keys())}")
    ms, ss = flat(m["stem"]), src["stem"]
    print("  stem identical:", ms == ss, "| M05 ws:", ws_profile(ms), "| src ws:", ws_profile(ss))
    if ms != ss:
        for op in difflib.SequenceMatcher(None, ss, ms).get_opcodes():
            if op[0] != "equal": print("   DIFF", op[0], repr(ss[op[1]:op[2]]), "->", repr(ms[op[3]:op[4]]))
    for k in "ABCD":
        mo, so = flat(m["options"].get(k, [])), src["options"].get(k)
        if mo != so: print(f"  option {k} DIFF: src={so!r} m05={mo!r}")
    print("  options identical:", all(flat(m["options"][k]) == src["options"][k] for k in "ABCD"), {k: repr(flat(m['options'][k])) for k in "ABCD"})
    # 与盲解输入一致性
    b = blind[n]
    print("  blind_input == 题目.jsonl:", flat(b["stem"]) == ms and all(flat(b["options"][k]) == flat(m["options"][k]) for k in "ABCD"))
    # 源 stem 每行长度（判断软折行）
    lines = ss.split("\n")
    print("  src line lengths:", [len(l) for l in lines])
    # 非常规字符
    odd = sorted({c for c in ms if unicodedata.category(c)[0] in "CZ" and c not in "\n "})
    print("  odd chars in M05 stem:", [hex(ord(c)) for c in odd])
