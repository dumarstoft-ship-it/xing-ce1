#!/usr/bin/env python3
"""Export current canonical revision; never regenerate obsolete v0.1 content."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
rows=json.loads((p.parent/"selection.json").read_text())
nums=[16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
assert json.loads((p.parent/"paper.json").read_text())["version"]=="0.2.0"
(p/"verbal.json").write_text(json.dumps([q for q in rows if q["number"] in nums],ensure_ascii=False,indent=2)+"\n")
