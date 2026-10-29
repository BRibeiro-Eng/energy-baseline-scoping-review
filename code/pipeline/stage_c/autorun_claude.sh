#!/bin/bash
# Relaunch the Stage C Claude pass across quota windows until all 42 are done.
# Stop with: pkill -f autorun_claude.sh
R=/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction
PY=/usr/local/bin/python3
LOG=$R/stage_c/autorun_claude.log
OUT=$R/production/stage_c/claude/outputs
MAX=24
for i in $(seq 1 $MAX); do
  N=$(ls $OUT/rayyan-*.json 2>/dev/null | wc -l | tr -d ' ')
  echo "[$(date '+%F %T')] tentativa $i/$MAX — $N/42 feitos" >> $LOG
  if [ "$N" -ge 42 ]; then echo "[$(date '+%F %T')] COMPLETO" >> $LOG; break; fi
  cd $R && $PY output/stage_c_run.py --surface claude --workers 2 \
        >> $R/stage_c/runner_claude.log 2>&1
  M=$(ls $OUT/rayyan-*.json 2>/dev/null | wc -l | tr -d ' ')
  echo "[$(date '+%F %T')] parou em $M/42 (+$((M-N)))" >> $LOG
  if [ "$M" -ge 42 ]; then echo "[$(date '+%F %T')] COMPLETO" >> $LOG; break; fi
  if [ "$M" -eq "$N" ]; then echo "  sem progresso — espera 45 min" >> $LOG; sleep 2700
  else sleep 900; fi
done
