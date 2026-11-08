#!/bin/bash
# 一批出题交回后：检查、扫描、出作答卷。zz_post.sh <批次，如 Z01>
SP=/tmp/claude-0/-home-user-xingce/c27c4f14-7f89-5a62-8e0a-9c6994ddaec0/scratchpad
k="$1"; f=$SP/zz/out/Z_$k.json
python3 -I $SP/tools/check_zz.py $f $SP/zz/in > $SP/zz/out/check_$k.log 2>&1; echo "check exit $?"; grep "！\|有问题的题\|Traceback\|Error" $SP/zz/out/check_$k.log | head -20
python3 -I $SP/tools/zz_leak_scan.py $f $SP/zz/in > $SP/zz/out/leak_$k.log 2>&1
python3 -I $SP/tools/make_zz_sheet.py $f $SP/zz/sheets/卷_$k.md && mv $SP/zz/sheets/卷_$k.md.key.json $SP/zz/keys/卷_$k.key.json
python3 -I - "$f" <<'PY'
import json,sys,collections
r=json.load(open(sys.argv[1]))
qs=[q for a in r['articles'] for q in a['questions']]
print(len(r['articles']),'篇',len(qs),'题', dict(collections.Counter(q['type'] for q in qs)), '答案', dict(sorted(collections.Counter(q['answer'] for q in qs).items())))
for a in r['articles']: print(' ',a['id'],len(a['questions']),[(q['type'],q['from_p'],q['to_p'],q.get('hide_p')) for q in a['questions']])
PY
