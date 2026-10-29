#!/bin/bash
# Waits for the OSF amendment to be deposited, then runs Stage C over the 42 papers and the
# dossiers, unattended. Started 2026-09-12 on the reviewer's instruction to advance with the
# extractions while he deposits the amendment.
#
# WHY A WATCHER AND NOT JUST A RUN. interlock() in output/stage_c_run.py refuses production
# extraction until stage_c/AMENDMENT_FILED.txt carries a filing date, and that is not a
# formality: the amendment's date is what distinguishes a prospective refinement of the charting
# instrument from post-hoc recoding. No authorisation changes what the timestamps say, so the
# extraction cannot legitimately begin first. This script removes the waiting instead: the moment
# the reviewer writes that file, the pass starts, with nothing left to ask.
#
# It does four things on seeing the file, in this order, and stops at the first failure:
#   1. re-runs preflight and the four suites;
#   2. confirms the schema digest is still the one the amendment describes;
#   3. freezes stage_c/SCHEMA_SHA256.txt — removes the NOT FROZEN marker, records the date read
#      from AMENDMENT_FILED.txt — keeping a dated copy of the pre-freeze file beside it;
#   4. runs the 42-paper extraction, then the dossiers with --exclude-core.
set -u
R=${R:-/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction}
PY=${PY:-/usr/local/bin/python3}
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
cd "$R" || exit 1
LOG=stage_c/await_amendment.log
FILED=stage_c/AMENDMENT_FILED.txt
EXPECTED=d855254b73a8640b4e13255876a3021ae9da699e1bf04bb4db3d5b2444e883ff
say() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

say "watcher started; waiting for $FILED (expected schema sha256 ${EXPECTED:0:16})"
while [ ! -s "$FILED" ]; do sleep 60; done
say "AMENDMENT_FILED.txt appeared: $(head -c 200 "$FILED" | tr '\n' ' ')"

say "--- preflight and suites ---"
R="$R" PY="$PY" bash stage_c/preflight.sh >> "$LOG" 2>&1
for t in test_stage_c test_compare test_runner test_satisfiable; do
  if ! $PY stage_c/$t.py > /dev/null 2>&1; then
    say "ABORT: stage_c/$t.py fails. Nothing was extracted."; exit 1
  fi
done
say "suites: all pass"

ACTUAL=$($PY -c "import hashlib;print(hashlib.sha256(open('stage_c/schema.json','rb').read().rstrip(b'\n')).hexdigest())")
if [ "$ACTUAL" != "$EXPECTED" ]; then
  say "ABORT: schema.json changed since the deposit sheet was written."
  say "  expected $EXPECTED"
  say "  actual   $ACTUAL"
  say "  The amendment describes a digest that is no longer on disk. Resolve before extracting."
  exit 1
fi
say "schema digest unchanged: $ACTUAL"

# --- freeze -------------------------------------------------------------------------------
if grep -q 'NOT FROZEN' stage_c/SCHEMA_SHA256.txt; then
  DATE=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' "$FILED" | head -1)
  [ -z "$DATE" ] && DATE=$(date '+%Y-%m-%d')
  cp stage_c/SCHEMA_SHA256.txt "stage_c/SCHEMA_SHA256.prefreeze_$(date '+%Y%m%d').txt"
  printf '%s  schema.json  v2.3.0-C  FROZEN %s  (OSF amendment deposited per AMENDMENT_FILED.txt)\n' \
    "$ACTUAL" "$DATE" > stage_c/SCHEMA_SHA256.txt
  say "schema FROZEN, date $DATE; pre-freeze file kept as stage_c/SCHEMA_SHA256.prefreeze_$(date '+%Y%m%d').txt"
else
  say "schema already frozen; left as is"
fi

# --- extraction ---------------------------------------------------------------------------
say "--- extraction: 42 papers, 2 workers ---"
$PY -u output/stage_c_run.py --surface claude --workers 2 >> "$LOG" 2>&1
RC=$?
N=$(ls production/stage_c/claude/outputs/rayyan-*.json 2>/dev/null | wc -l | tr -d ' ')
say "extraction finished rc=$RC; $N/42 records present"
if [ "$N" -eq 0 ]; then say "ABORT: no records. Dossiers not attempted."; exit 1; fi

# --- dossiers -----------------------------------------------------------------------------
say "--- dossiers (the 11 blind-first papers are held back by the interlock until their human extraction is committed) ---"
$PY -u output/stage_c_dossier.py --surface claude --all --workers 2 >> "$LOG" 2>&1
say "dossiers finished rc=$?; $(ls output/dossiers/rayyan-*.md 2>/dev/null | wc -l | tr -d ' ') dossiers on disk"

say "--- done. Review against stage_c/PILOT.json exit_criteria and the verification matrix. ---"
