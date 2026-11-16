#!/usr/bin/env python3
"""把旧版（GPT编制的0.x版）流程文件和成品移入 <套卷>/历史版本/<旧版本号>/，用 git mv 保留历史。

不移动：README.md（重写）、Claude 的审核与修订记录（Claude*.md）、核验记录/、历史版本/、assets/
（重编M04第35题用到M03/assets中的重画数阵图）。

    python3 广东行测18套模拟/重编/tools/archive_old.py M01 [--dry]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "广东行测18套模拟"
KEEP = {"README.md", ".gitignore", "核验记录", "历史版本", "assets"}


def main():
    paper = sys.argv[1]
    dry = "--dry" in sys.argv
    d = S / paper
    ver = json.loads((d / "paper.json").read_text(encoding="utf-8"))["version"]
    dest = d / "历史版本" / ver
    moves = []
    for p in sorted(d.iterdir()):
        if p.name in KEEP or p.name.startswith("Claude"):
            continue
        moves.append(p)
    print(paper, ver, "→", dest.relative_to(ROOT), f"{len(moves)}项")
    for p in moves:
        print("  ", p.name)
    if dry:
        return
    dest.mkdir(parents=True, exist_ok=True)
    for p in moves:
        subprocess.check_call(["git", "mv", str(p.relative_to(ROOT)), str((dest / p.name).relative_to(ROOT))], cwd=ROOT)


if __name__ == "__main__":
    main()
