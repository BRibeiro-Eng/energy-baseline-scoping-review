#!/bin/bash
# One-shot: release the 11 blind-first core dossiers after SQ4 was cut (2026-09-16).
set -u
R=${R:-/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction}
PY=${PY:-/usr/local/bin/python3}
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
cd "$R" || exit 1
LOG=stage_c/run_until_done.log
say() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }
limited() { tail -25 "$1" 2>/dev/null | grep -qiE "hit your [^ ]+ limit|session limit|rate limit|usage limit|weekly limit|monthly limit|limits? .{0,40}resets?"; }
doss() { ls output/dossiers/rayyan-*.md 2>/dev/null | wc -l | tr -d ' '; }
say "SQ4 cortada: a libertar os 11 do nucleo com --include-core-without-blind-first"
for round in $(seq 1 40); do
  OUT=stage_c/.core_round_${round}.out
  $PY -u output/stage_c_dossier.py --surface claude --all --include-core-without-blind-first --workers 2 > "$OUT" 2>&1
  RC=$?; cat "$OUT" >> "$LOG"
  say "core round $round — rc=$RC, $(doss) dossiers"
  if [ "$(doss)" -ge 41 ]; then say "CORE DONE — $(doss) dossiers"; exit 0; fi
  if limited "$OUT"; then say "availability stop; sleeping 10 min"; sleep 600; continue; fi
  if [ "$RC" -ne 0 ]; then say "STOPPED: core dossiers failed, nao e limite. Ler $OUT."; exit 1; fi
done
say "STOPPED: MAX_ROUNDS."
exit 1
