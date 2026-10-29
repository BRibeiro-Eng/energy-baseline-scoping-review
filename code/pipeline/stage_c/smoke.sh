#!/bin/bash
R=/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction
cd $R
nohup /usr/local/bin/python3 output/stage_c_run.py --smoke "${1:-rayyan-472535365}" --workers 1 \
      > $R/stage_c/smoke.log 2>&1 &
sleep 3
echo "PID: $(pgrep -f stage_c_run.py | tr '\n' ' ')"
