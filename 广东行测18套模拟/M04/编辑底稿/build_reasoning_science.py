#!/usr/bin/env python3
"""Export current canonical revision; never regenerate obsolete v0.1 content."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
rows=json.loads((p.parent/"selection.json").read_text())
nums=[46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70]
assert json.loads((p.parent/"paper.json").read_text())["version"]=="0.2.0"
(p/"reasoning_science.json").write_text(json.dumps([q for q in rows if q["number"] in nums],ensure_ascii=False,indent=2)+"\n")
