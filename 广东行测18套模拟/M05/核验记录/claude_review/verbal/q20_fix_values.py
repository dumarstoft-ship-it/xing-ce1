# 只读：第20题选项当前底稿文字的SHA-256（供“排版空白勘误.json”备选方案使用）及据原卷应改为的文字
import json, hashlib, re
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
tm = {json.loads(l)["number"]: json.loads(l) for l in open(f"{M05}/题目.jsonl", encoding="utf-8")}
target = {"A": "如雷贯耳 刀光剑影 客观性", "B": "如数家珍 白纸黑字 严肃性", "C": "司空见惯 鼓角齐鸣 主体性", "D": "耳熟能详 只言片语 独立性"}
for k in "ABCD":
    blocks = tm[20]["options"][k]
    assert len(blocks) == 1 and blocks[0]["type"] == "text"
    cur = blocks[0]["text"]
    assert re.sub(r"\s", "", cur) == re.sub(r"\s", "", target[k]), k   # 只改空白
    print(json.dumps({"套卷": "M05", "题号": 20, "位置": f"选项{k}", "块": 0,
                      "底稿文字SHA256": hashlib.sha256(cur.encode("utf-8")).hexdigest(),
                      "当前": cur, "改为": target[k]}, ensure_ascii=False))
