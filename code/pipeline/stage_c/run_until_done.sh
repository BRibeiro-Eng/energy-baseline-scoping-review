#!/bin/bash
# Runs the Stage C roster to completion across as many CLI session windows as it takes.
#
# WHY. 27 remaining extractions plus 31 dossiers do not fit in one session window: the run
# stopped at 13:04 on "You've hit your session limit · resets 2:50pm". That stop is by design --
# an availability error aborts the whole pass instead of burning attempts against a wall -- and
# the pass is resumable, because a paper whose record already validates is skipped. What was
# missing was something to wait out the window and start again. This is that.
#
# It retries every RETRY_MIN minutes. A premature attempt costs one CLI call that returns the
# limit error and aborts, which is near-free, so polling is cheaper than parsing the reset time
# out of a log line and getting the am/pm wrong.
#
# Stops on: the roster complete and the dossiers done; an abort that is NOT a session limit
# (those need a human); or MAX_ROUNDS, so it cannot spin forever.
set -u
R=${R:-/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction}
PY=${PY:-/usr/local/bin/python3}
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
cd "$R" || exit 1
LOG=stage_c/run_until_done.log
RETRY_MIN=${RETRY_MIN:-10}
MAX_ROUNDS=${MAX_ROUNDS:-200}
LONG_RETRY_MIN=${LONG_RETRY_MIN:-60}
say() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }
recs() { ls production/stage_c/claude/outputs/rayyan-*.json 2>/dev/null | wc -l | tr -d ' '; }
# 2026-09-15. "Done" used to mean 42 records, so a paper the instrument cannot extract kept the
# loop spinning forever and the dossiers never started. The roster is accounted for when every
# key has EITHER a record OR a quarantine entry that still stands.
# Counted by KEY, never by row: a quarantine line whose key later produced a record is stale
# (the runner retracts those at the end of a pass) and must not be counted as covering anything.
acct() { $PY - <<'EOF'
import json, glob, os
have = {os.path.basename(p)[:-5] for p in glob.glob("production/stage_c/claude/outputs/rayyan-*.json")}
q = set()
if os.path.isfile("production/stage_c/claude/quarantine.jsonl"):
    q = {json.loads(l)["key"] for l in open("production/stage_c/claude/quarantine.jsonl") if l.strip()}
print(len(have | q))
EOF
}
doss() { ls output/dossiers/rayyan-*.md 2>/dev/null | wc -l | tr -d ' '; }
# 2026-09-14. The list below used to read "session limit|rate limit|usage limit" and so did not
# match "You've hit your WEEKLY limit". Round 2 read a quota stop as an instrument failure and
# stopped the loop; the runner, whose detector had the same hole, wrote 16 papers to quarantine
# for a reason that says nothing about any paper. Both detectors now cover the family.
limited() { tail -25 "$1" 2>/dev/null | grep -qiE "hit your [^ ]+ limit|session limit|rate limit|usage limit|weekly limit|monthly limit|daily limit|hourly limit|limits? .{0,40}resets?"; }
# A weekly window does not reopen in ten minutes. When the stop names one, wait an hour a round.
long_limited() { tail -25 "$1" 2>/dev/null | grep -qiE "weekly limit|monthly limit"; }
wait_out() { # $1 = the .out file
  if long_limited "$1"; then M=$LONG_RETRY_MIN; else M=$RETRY_MIN; fi
  say "availability stop; sleeping ${M} min"; sleep $((M * 60))
}
qcount() { local n; n=$(wc -l < production/stage_c/claude/quarantine.jsonl 2>/dev/null | tr -d " "); echo "${n:-0}"; }

QWAS=$(qcount)
say "starting; $(recs)/42 records, $(doss) dossiers on disk, ${QWAS:-0} quarantined"
for round in $(seq 1 "$MAX_ROUNDS"); do
  N=$(recs)
  if [ "$(acct)" -lt 42 ]; then
    say "round $round — extraction, $N/42 done"
    OUT=stage_c/.round_${round}_extract.out
    $PY -u output/stage_c_run.py --surface claude --workers 2 > "$OUT" 2>&1
    RC=$?; cat "$OUT" >> "$LOG"
    NEW=$(recs); say "round $round — extraction exited rc=$RC, now $NEW/42 records, $(qcount) quarantined"
    QN=$(qcount); if [ "${QN:-0}" -gt "${QWAS:-0}" ]; then
      say "  NOTE: quarantine grew ${QWAS:-0} -> $QN this round. Quarantine is a claim about a"
      say "  record, not about availability. Read production/stage_c/claude/quarantine.jsonl."
    fi; QWAS=$QN
    if [ "$(acct)" -lt 42 ]; then
      if limited "$OUT"; then
        wait_out "$OUT"; continue
      fi
      if [ "$NEW" -eq "$N" ]; then
        say "STOPPED: extraction made no progress and it is not a session limit. A human should"
        say "  read $OUT before anything is relaunched."
        exit 1
      fi
      continue
    fi
  fi
  # roster complete -> dossiers. The 11 blind-first core are held back by the interlock unless
  # their human extraction is committed, so "done" is not 42.
  say "round $round — roster accounted for: $(recs) records + $(qcount) quarantined; dossiers"
  OUT=stage_c/.round_${round}_dossier.out
  $PY -u output/stage_c_dossier.py --surface claude --all --workers 2 > "$OUT" 2>&1
  RC=$?; cat "$OUT" >> "$LOG"
  HELD=$(grep -c "HELD BACK" "$OUT" 2>/dev/null || echo 0)
  say "round $round — dossiers exited rc=$RC, $(doss) on disk"
  if [ "$RC" -ne 0 ] && limited "$OUT"; then
    wait_out "$OUT"; continue
  fi
  if [ "$RC" -ne 0 ]; then
    say "STOPPED: dossiers failed and it is not a session limit. Read $OUT."
    exit 1
  fi
  say "DONE — $(recs) records, $(qcount) quarantined, $(doss) dossiers. The 11 blind-first core"
  say "  stay held back until their human extraction is committed (output/stage_c_blind.py)."
  exit 0
done
say "STOPPED: MAX_ROUNDS ($MAX_ROUNDS) reached."
exit 1
