#!/bin/bash
R=/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction
date '+%H:%M:%S'
echo "procs: $(pgrep -f stage_c_run.py | wc -l | tr -d ' ')"
echo "--- log ---"; cat $R/stage_c/smoke.log 2>/dev/null
echo "--- outputs ---"; ls $R/production/stage_c/_smoke/outputs/ 2>/dev/null
echo "--- attempts ---"
/usr/local/bin/python3 - <<'PY'
import json, glob
for p in sorted(glob.glob('/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction/production/stage_c/_smoke/work/*metadata.json')):
    m = json.load(open(p))
    print(p.split('/')[-1], '->', m.get('status'), '| dur', m.get('duration_ms'), '| cost', m.get('total_cost_usd'))
    if m.get('error'): print('    ERR:', m['error'][:500])
    if m.get('status') == 'valid':
        print('    grounding:', m.get('grounding'), '| support:', m.get('support_class'))
        print('    n_models:', m.get('n_models'), '| n_mechanisms:', m.get('n_mechanisms'))
PY
