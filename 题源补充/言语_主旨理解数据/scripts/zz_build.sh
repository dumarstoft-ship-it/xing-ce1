#!/bin/bash
# 用仓库里存档的遮词句和主旨题建网页并实测：zz_build.sh <输出.html> <版本号> <说明> <截图目录> [只放到哪一批，如 Z02]
set -e
SP=/tmp/claude-0/-home-user-xingce/c27c4f14-7f89-5a62-8e0a-9c6994ddaec0/scratchpad
R=/home/user/xingce/言语试点/工作区/词句新版
Z=/home/user/xingce/言语试点/工作区/主旨理解
out="$1"; ver="$2"; note="$3"; shots="$4"; upto="${5:-Z99}"
mkdir -p "$shots"
cd $SP/build
ZF=( $Z/试点/Z_ZP*.json )
for f in $Z/全量/Z_Z*.json; do t=$(basename "$f" .json); t=${t#Z_}; [ -e "$f" ] && [[ ! "$t" > "$upto" ]] && ZF+=( "$f" ); done
echo "主旨题：${ZF[*]##*/}"
python3 -I build_v2.py --base base0/data.json --ref base0/ref1310.json --head base0/head.html --css extra.css --js app_v2.js \
  --masks $R/试点/M1.json $R/试点/M2.json $R/试点/M3.json $R/试点/M4.json $(ls $R/全量/M_B*.json | sort) \
  --items $R/试点/P1.json $R/试点/P2.json --zz "${ZF[@]}" --out "$out" --ver "$ver" --note "$note"
for t in test_v2 test_mobile; do
  node $t.js "$out" "$shots" > "$shots/$t.log" 2>&1 || true
  grep -v '^ok' "$shots/$t.log" || true
  echo "--- $t: $(grep -c '^ok' "$shots/$t.log") ok, $(grep -c '^FAIL' "$shots/$t.log") fail"
done
