#!/usr/bin/env python3
"""Build one paste-ready payload per Corpus-B paper, so nothing is improvised by hand."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
B = json.load(open("output/fn_census/detector_c/ROSTER_LOCK_2026-09-12.json", encoding="utf-8"))
keys = [r["key"] for r in B["order"]]
out = "stage_c/payloads"; os.makedirs(out, exist_ok=True)
tot = 0
for k in keys:
    pages = json.load(open(f"output/stage0/{k}.json", encoding="utf-8"))["pdf"]["pages"]
    payload = {"key": k, "pdf": {"pages": [{"page": p["page"], "text": p.get("text") or ""}
                                           for p in pages]}}
    blob = json.dumps(payload, ensure_ascii=False)
    open(f"{out}/{k}.json", "w", encoding="utf-8").write(blob)
    tot += len(blob)
    print(f"{k}  {len(pages):3d} pages  {len(blob)//1024:5d} KB")
print(f"\n{len(keys)} payloads, {tot//1024} KB total, in {out}/")
