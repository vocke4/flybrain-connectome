#!/bin/bash
# Experiment B2: re-derive the DES decomposition at a NON-saturated anchor.
# The DES edge sets are w_syn-independent (swap acts on topology; weights travel
# with the edge and the transform is applied at sim time), so we simply re-run
# the existing DES npz at lognormal sigma=1.6, w_syn=0.04, where neither sex is
# saturated (female ~17%, male ~50%).
cd "$(dirname "$0")"
PY="${PYTHON:-./venv/bin/python}"
LOG=results/crit_probe/reanchor_des.log
mkdir -p results/crit_probe

run () {  # $1 source  $2 tag  $3 w_syn
  echo "=== $(date '+%H:%M:%S') $1 $3 ===" >> $LOG
  $PY ssot_run.py --source $1 --tag $2 --transform lognormal --sigma 1.6 \
     --w-syn $3 --weight-seed $4 --sim-seed $5 >> $LOG 2>&1
}

# real at the new anchor
run banc_female anchor2_real_f 0.04 0 42
run mcns_male   anchor2_real_m 0.04 0 42
# DES nulls at the new anchor (3 build seeds each)
for S in 0 1 2; do
  run banc_female_des_$S anchor2_des_f_s$S 0.04 $S 42
done
for S in 0 1 2; do
  run mcns_male_des_$S anchor2_des_m_s$S 0.04 $S 42
done
echo "B2 COMPLETE $(date)" >> $LOG
