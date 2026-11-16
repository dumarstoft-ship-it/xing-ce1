# 只读模拟：用当前 打印排版/build_print.py 的 norm_text + reflow 处理 M05 第16—30题题干与选项，
# 输出排版后的段落，并与原卷图核实的应有段落数对照。以 -B 运行，不在仓库写 __pycache__。
import sys, json, subprocess
sys.dont_write_bytecode = True
TOOL = "/home/user/xing-ce1/广东行测18套模拟/打印排版"
sys.path.insert(0, TOOL)
import build_print as bp
head = subprocess.run(["git", "-C", "/home/user/xing-ce1", "log", "-1", "--format=%h %s", "--", "广东行测18套模拟/打印排版/build_print.py"], capture_output=True, text=True).stdout.strip()
print("build_print.py 版本:", head)
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
tm = {json.loads(l)["number"]: json.loads(l) for l in open(f"{M05}/题目.jsonl", encoding="utf-8")}
# 原卷图核实的段落结构：文段一段 + 设问一行；第30题六个编号句各占一行 + 设问
expected = {n: 2 for n in range(16, 31)}; expected[30] = 7
log = bp.Log()
allok = True
for n in range(16, 31):
    q = tm[n]
    text = "".join(b["text"] for b in q["stem"] if b["type"] == "text")
    paras = bp.reflow(bp.norm_text(text, n, "题干", log), n, "题干", log)
    ok = len(paras) == expected[n]
    allok &= ok
    print(f"### {n}  段落数={len(paras)} 应为={expected[n]} {'OK' if ok else 'MISMATCH'}")
    for p in paras:
        print("   ¶", p)
    for k in "ABCD":
        t = "".join(b["text"] for b in q["options"][k] if b["type"] == "text")
        o = bp.reflow(bp.norm_text(t, n, f"选项{k}", log), n, f"选项{k}", log)
        print(f"   {k}.", " | ".join(repr(x) for x in o))
print("全部段落结构与原卷一致:", allok)
print("\n排版日志（规范化记录）:")
for it in log.items:
    print("  ", it)
