#!/usr/bin/env python3
"""Progress on the Tier-1 membership blind census. Read-only."""
import json, collections
from pathlib import Path

D = Path(__file__).resolve().parent / "reviews" / "membership" / "blind"
Q = Path(__file__).resolve().parent / "queues" / "tier1_membership.json"

contested = collections.defaultdict(set)
for i in json.loads(Q.read_text()):
    contested[i["paper_key"]].add(i["field"])
BATCH = lambda v: "A sector" if v == {"level_3b"} else ("B both" if len(v) == 2 else "C eligibility")

state = collections.Counter(); per_batch = collections.defaultdict(collections.Counter)
reveal_changes = 0; done_cells = 0
for key in sorted(contested):
    st_path = D / f"{key}.state.json"
    st = json.loads(st_path.read_text())["state"] if st_path.is_file() else "blind"
    state[st] += 1
    per_batch[BATCH(contested[key])][st] += 1
    if st in ("committed", "revealed", "finalised"):
        done_cells += len(contested[key])
    rc = D / f"{key}.reveal_changes.jsonl"
    if rc.is_file():
        reveal_changes += sum(1 for line in rc.read_text().splitlines() if line.strip())

total_p, total_c = len(contested), sum(len(v) for v in contested.values())
print(f"papers {sum(state[s] for s in ('committed','revealed','finalised'))}/{total_p}"
      f"   cells {done_cells}/{total_c}")
print("  state:", dict(state))
for b in sorted(per_batch):
    c = per_batch[b]
    done = sum(c[s] for s in ("committed", "revealed", "finalised"))
    print(f"  {b:14} {done:>3}/{sum(c.values()):<3} {dict(c)}")
committed = sum(state[s] for s in ("revealed", "finalised"))
if committed:
    print(f"\nreveal-changes logged: {reveal_changes} over {committed} revealed papers"
          f"  ({reveal_changes/committed:.2f}/paper)")
    print("  = the §3-Step-3 anchoring-exposure figure. Reported raw; not a target to minimise.")
else:
    print("\nreveal-changes: none yet (nothing revealed)")
