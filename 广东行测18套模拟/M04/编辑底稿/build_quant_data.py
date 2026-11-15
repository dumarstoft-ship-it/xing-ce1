#!/usr/bin/env python3
"""Export current canonical revision; never regenerate obsolete v0.1 content."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
rows=json.loads((p.parent/"selection.json").read_text())
nums=[31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90]
assert json.loads((p.parent/"paper.json").read_text())["version"]=="0.2.0"
(p/"quant_data.json").write_text(json.dumps([q for q in rows if q["number"] in nums],ensure_ascii=False,indent=2)+"\n")
