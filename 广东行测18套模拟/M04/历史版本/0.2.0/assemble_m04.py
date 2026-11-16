#!/usr/bin/env python3
"""把四个有版本记录的选编模块合并成M04单一底稿；不改原题库。"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
cfg = json.loads((HERE/'paper.json').read_text())
rows, inputs = [], []
for rel in cfg['editorial_inputs']:
    data=(HERE/rel).read_bytes()
    part=json.loads(data)
    rows.extend(part)
    inputs.append({'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'count':len(part)})
rows.sort(key=lambda x:x['number'])
assert [r['number'] for r in rows] == list(range(1,91))
assert len({r['source_id'] for r in rows}) == 90
(HERE/'selection.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
manifest={'paper_id':'M04','version':cfg['version'],'inputs':inputs,'selection_sha256':hashlib.sha256((HERE/'selection.json').read_bytes()).hexdigest()}
(HERE/'核验记录/assembly_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('M04：90题合并完成。')
