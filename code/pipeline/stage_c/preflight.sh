#!/bin/bash
R=${R:-/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction}
cd $R
PY=${PY:-/usr/local/bin/python3}
echo "=== Stage C preflight ==="
$PY -c "import json,jsonschema;jsonschema.Draft202012Validator.check_schema(json.load(open('stage_c/schema.json')));print('schema: valido draft 2020-12')"
$PY -c "
import hashlib
b=open('stage_c/schema.json','rb').read().rstrip(b'\n')
a=hashlib.sha256(b).hexdigest(); d=open('stage_c/SCHEMA_SHA256.txt').read().split()[0]
print('digest:', 'OK' if a==d else 'MISMATCH', a[:16])"
echo "prompt:        $(wc -c < stage_c/PROMPT_EXTRACTION.md | tr -d ' ') bytes"
$PY output/stage_c_prompt_build.py --check | sed 's/^/               /' 
echo "schema:        $(wc -c < stage_c/schema.json | tr -d ' ') bytes"
echo "payloads:      $(ls stage_c/payloads/rayyan-*.json 2>/dev/null | wc -l | tr -d ' ')/42"
echo "roster lock:   $($PY -c "import json;print(len(json.load(open('output/fn_census/detector_c/ROSTER_LOCK_2026-09-12.json'))['order']))") papers"
echo "pilot papers:  $($PY -c "import json;print(len(json.load(open('stage_c/PILOT.json'))['papers']))")"
echo "amendment:     $([ -s stage_c/AMENDMENT_FILED.txt ] && echo 'FILED' || echo 'not filed (pilot does not need it)')"
for d in claude pilot_claude; do
  echo "dir $d:   $(ls production/stage_c/$d/outputs/rayyan-*.json 2>/dev/null | wc -l | tr -d ' ') records"
done
echo "--- suites ---"
$PY stage_c/test_stage_c.py >/dev/null 2>&1 && echo "test_stage_c:  ALL PASS" || echo "test_stage_c:  FAIL"
$PY stage_c/test_compare.py >/dev/null 2>&1 && echo "test_compare:  ALL PASS (comparator RETAINED, out of the pipeline -- one extraction surface)" || echo "test_compare:  FAIL"
$PY stage_c/test_runner.py  >/dev/null 2>&1 && echo "test_runner:   ALL PASS" || echo "test_runner:   FAIL"
$PY stage_c/test_satisfiable.py >/dev/null 2>&1 && echo "satisfiable:   ALL VALUES WRITABLE" || echo "satisfiable:   SOME VALUE IS UNWRITABLE"
$PY stage_c/test_satisfiable.py --selftest >/dev/null 2>&1 && echo "  selftest:    the suite still catches the two pilot defects" || echo "  selftest:    BLIND — the suite cannot fail"
echo "--- triage (one extraction surface: the worklist replaces divergence routing) ---"
$PY output/stage_c_triage.py --surface pilot_claude 2>/dev/null | grep -E "^TOTAL|^must read|^per paper" | sed 's/^/  /'
echo "--- git ---"
GIT_OPTIONAL_LOCKS=0 git status --porcelain stage_c/ | grep -v '^??' | head -3
echo "docs HEAD:   $(GIT_OPTIONAL_LOCKS=0 git log --oneline -1)"
cd $R/output && echo "code HEAD:   $(GIT_OPTIONAL_LOCKS=0 git log --oneline -1)"
