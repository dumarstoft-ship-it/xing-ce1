#!/bin/bash
# 对最终文件把全部测试重跑一遍。用法：bash run_rc.sh pw|sim1|sim2
SP=/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad
RC=$SP/rc
mkdir -p $RC
cd $SP
run() { # 名字 目录 命令...
  local name=$1 dir=$2; shift 2
  ( cd $dir && timeout 1500 "$@" > $RC/$name.txt 2>&1 ); echo "$name exit $?" | tee -a $RC/_status_$PART.txt
}
PART=$1
if [ "$PART" = "pw" ]; then
  : > $RC/_status_pw.txt
  md5sum $SP/v7c/index.html | tee -a $RC/_status_pw.txt
  export SITE=$SP/v7c
  run cloud $SP node v7_cloud_test.js v7c
  run plan $SP node v7_plan_test.js v7c
  run wake $SP/v7c_tests node t_wake.js
  run mz5 $SP node mz_test5.js v7c $RC/mz5
  run mz4 $SP node mz_test4.js v7c_noplan $RC/mz4
  run plan_sim $SP node plan_sim.js v7c 2026-11-28 0.75 0.9
  run conv_pw_stale $SP/v7b_conv node pw_stale_run.js site_v7c
  run conv_pw_settle $SP/v7b_conv node pw_settle_fight.js site_v7c
  run walk_s3 $SP/v7b_walk node s3_wander.js
  for v in X Y Z; do VARIANT=$v run walk_s4_$v $SP/v7b_walk node s4_two.js; done
  run walk_s5 $SP/v7b_walk node s5_tz.js
  run walk_s6 $SP/v7b_walk node s6_misc.js
  run walk_s7 $SP/v7b_walk node s7_more.js
  run walk_s8 $SP/v7b_walk node s8_writes.js
  for v in A B C; do VARIANT=$v run walk_s2_$v $SP/v7b_walk node s2_lazy.js; done
  DAILY=50 TAG=rc_n50 run walk_s1_n50 $SP/v7b_walk node s1_normal.js
  DAILY=40 TAG=rc_m40 run walk_s1_m40 $SP/v7b_walk node s1_normal.js
  unset SITE
  for f in t1_reset t1b_reset_single t2_midrun t2b_midrun_regress t3_stale_open t4_plan_dropped t4b_settings_wait t5_skew t6_keyorder t6b_realdoc t6c_pingpong t7_unavailable t8_close900 t9_size t10_checked t11_e_settings; do run sync_$f $SP/rev2_sync node $f.js v7c; done
  run rp_t1 $SP/rev2_plan node t1_fuzz.js realdraft 30
  run rp_t4 $SP/rev2_plan node t4_settle.js v7
  run rp_t5_new $SP/rev2_plan node t5_session.js v7_noplan
  run rp_t5_old $SP/rev2_plan node t5_session.js old_noplan
  run rp_t6 $SP/rev2_plan node t6_null.js
  run rp_t7 $SP/rev2_plan node t7_ui.js realdraft
  for s in 2 3 4 5; do run rp_monkey_real_$s $SP/rev2_plan node t8_monkey.js realdraft $s 500; done
  for s in 11 12; do run rp_monkey_np_$s $SP/rev2_plan node t8_monkey.js v7_noplan $s 300; done
  run rp_t9 $SP/rev2_plan node t9_cross.js v7
  run rp_t10 $SP/rev2_plan node t10_misc.js realdraft
  run rp_t11 $SP/rev2_plan node t11_noplan_sync.js
  run rp_t12 $SP/rev2_plan node t12_order.js realdraft
  run rp_t13 $SP/rev2_plan node t13_scan.js
  run rp_t14 $SP/rev2_plan node t14_noplan_due.js v7_noplan
  echo "pw done" | tee -a $RC/_status_pw.txt
elif [ "$PART" = "sim1" ]; then
  : > $RC/_status_sim1.txt
  export SITE=site_v7c
  run sim_scen $SP/v7b_conv node sim.js scen s1 s1same settlefight latereset epoch oldloop wrong days midnight
  run sim_A $SP/v7b_conv node sim.js fuzz 1 300 200 keepLater=1 focus=1
  run sim_B $SP/v7b_conv node sim.js fuzz 8000 150 200 noreset=1 focus=1
  run sim_G $SP/v7b_conv node sim.js fuzz 6000 100 200 midnight=1 noreset=1 focus=1
  run sim_N1 $SP/v7b_conv node sim.js fuzz 20000 300 200 keepLater=1 focus=1
  echo "sim1 done" | tee -a $RC/_status_sim1.txt
elif [ "$PART" = "sim2" ]; then
  : > $RC/_status_sim2.txt
  export SITE=site_v7c
  run sim_F $SP/v7b_conv node sim.js fuzz 5000 150 200 reset=1 keepLater=1 focus=1
  run sim_D $SP/v7b_conv node sim.js fuzz 3000 120 200 old=1 ndev=3 keepLater=1 focus=1
  run sim_E $SP/v7b_conv node sim.js fuzz 4000 100 200 old=1 ndev=2 noreset=1 focus=1
  run sim_N2 $SP/v7b_conv node sim.js fuzz 21000 200 200 keepLater=1
  run sim_calm $SP/v7b_conv node sim.js fuzz 1000 200 200 noreset=1 noday=1 noskew=1 nofail=1
  run sim_N3 $SP/v7b_conv node sim.js fuzz 22000 150 200 midnight=1 keepLater=1 focus=1
  echo "sim2 done" | tee -a $RC/_status_sim2.txt
fi
