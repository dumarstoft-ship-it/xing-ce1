#!/usr/bin/env python3
"""Check saved outputs; semantic proofs are in the versioned report."""
import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
r=json.loads((p/"核验记录/修订核验_v020.json").read_text())
assert r["status"]=="PASS" and json.loads((p/"paper.json").read_text())["version"]==r["version"]
for f,h in r["output_sha256"].items():
 assert hashlib.sha256((p/f).read_bytes()).hexdigest()==h,f
print("M04 v0.2.0 output fingerprints verified; incremental external review pending")
