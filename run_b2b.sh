#!/bin/bash
# B2b: map the DES decomposition across anchors (real + DES, both sexes).
cd "$(dirname "$0")"
PY="${PYTHON:-./venv/bin/python}"
LOG=results/crit_probe/reanchor_des.log

run () {  # $1 source  $2 tag  $3 w_syn  $4 weight_seed
  echo "=== $(date '+%H:%M:%S') $1 w=$3 ===" >> $LOG
  $PY ssot_run.py --source $1 --tag $2 --transform lognormal --sigma 1.6 \
     --w-syn $3 --weight-seed $4 --sim-seed 42 >> $LOG 2>&1
}

for WS in 0.05 0.06 0.07 0.08; do
  run banc_female     anchor2_real_f  $WS 0
  run mcns_male       anchor2_real_m  $WS 0
  run banc_female_des_0 anchor2_des_f_s0 $WS 0
  run mcns_male_des_0   anchor2_des_m_s0 $WS 0
done
echo "B2b COMPLETE $(date)" >> $LOG
