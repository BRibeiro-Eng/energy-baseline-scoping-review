#!/usr/bin/env python3
"""Blind-first extraction (V3) — the form that withholds the model until you commit.

  /usr/local/bin/python3 output/stage_c_blind.py start   --key rayyan-472535351
  /usr/local/bin/python3 output/stage_c_blind.py commit  --key rayyan-472535351
  /usr/local/bin/python3 output/stage_c_blind.py reveal  --key rayyan-472535351
  /usr/local/bin/python3 output/stage_c_blind.py amend   --key rayyan-472535351
  /usr/local/bin/python3 output/stage_c_blind.py status

WHAT THIS IS FOR. Protocol C-2.3 §3-Step-5: on blind-first papers "the form withholds model
outputs until commit, then reveals both as post-hoc discrepancy checkers; reveal-changes are
logged." Reviewer decision 2026-09-13: V3 is done on the 11 refining/petrochemical papers, which
carry the SQ4 transferability argument (R15). Until this existed, that decision was an intention
rather than an instrument -- which is exactly what the amendment says is not claimed as one.

THE THREE THINGS THAT MAKE IT REAL, rather than a promise about what was read when.

  1. `start` writes a worksheet and records when. `commit` refuses to run if the model record
     for this paper has been opened by this tool since `start` -- and it can tell, because
     `reveal` is the only way to open it here and it stamps the sidecar. That is not proof you
     did not read the record in an editor; nothing in software can prove that. It is a record of
     what this tool did, and it is stated as no more than that.
  2. Committed values are IMMUTABLE. `amend` never rewrites them: a post-reveal change is
     appended, with the before, the after, and your reason. The reveal-change rate is then a
     count of real edits rather than an impression, and it is reported for what it is -- a
     descriptive rate, not a measure of anchoring and not a measure of correctness.
  3. The clock runs from `start` to `commit`, and you are asked for ACTIVE minutes separately,
     because wall-clock includes the coffee. Both are recorded. A blank is missing, not zero.

WHAT YOU EXTRACT BLIND. Not all 13 field groups: the ones that feed a registered result
(verification matrix §3), listed in FIELDS below. Everything else stays single-surface
extraction, and the worksheet says so rather than leaving you to assume you covered it.
"""
import argparse, datetime, difflib, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT); sys.path.insert(0, HERE)
import yaml                                                        # noqa: E402

WS = "production/stage_c/blind_first_worksheets"
OUT = "production/stage_c/human_verdicts/blind_first"
SCHEMA = json.load(open("stage_c/schema.json", encoding="utf-8"))
CORE = [r["key"] for r in json.load(open(
    "output/fn_census/detector_c/ROSTER_LOCK_2026-09-12.json", encoding="utf-8"))["order"]
    if r["priority_group"] in ("refining", "petrochemicals")]


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def enum_at(*path):
    n = SCHEMA
    for k in path:
        n = n["items"] if k == "[]" else n["properties"][k]
        while "$ref" in n or "allOf" in n:
            if "$ref" in n:
                t = SCHEMA
                for part in n["$ref"].lstrip("#/").split("/"):
                    t = t[part]
                n = t
            else:
                merged = {}
                for sub in n["allOf"]:
                    s2 = sub
                    if "$ref" in s2:
                        t = SCHEMA
                        for part in s2["$ref"].lstrip("#/").split("/"):
                            t = t[part]
                        s2 = t
                    for kk, vv in s2.items():
                        if kk == "properties":
                            pr = dict(merged.get("properties") or {}); pr.update(vv)
                            merged["properties"] = pr
                        else:
                            merged[kk] = vv
                n = merged
    return n.get("enum") or []


def fields():
    """Result-bearing groups only, with their legal values read from the frozen schema."""
    A = ("applications", "[]"); M = A + ("models", "[]")
    return [
      ("mechanisms", "R1-R5", "one block per distinct limitation the paper STATES about the "
       "model. cause is usually 'not stated' -- papers report what breaks, not why.",
       {"mechanism_cause": enum_at("mechanisms", "[]", "mechanism_cause"),
        "mechanism_effect_on_model": enum_at("mechanisms", "[]", "mechanism_effect_on_model"),
        "claim_status": enum_at("mechanisms", "[]", "claim_status"),
        "evidence_quote": "verbatim", "page": "int"}),
      ("adaptations", "R6-R8",
       "addresses_mechanism ONLY when the paper states the link.",
       {"adaptation": enum_at("adaptations", "[]", "adaptation"),
        "status": enum_at("adaptations", "[]", "status"),
        "normative_framing": enum_at("adaptations", "[]", "normative_framing"),
        "addresses_mechanism": "mechanism index or null",
        "evidence_quote": "verbatim", "page": "int"}),
      ("implementation_barriers", "R9", "free text, one per line, each with a page.",
       {"barrier": "free text", "page": "int"}),
      ("C5_measurement", "R10, R15",
       "PER MODEL, per energy vector. A calculated historian tag is not a meter.",
       {"model": "model index", "energy_vector": enum_at(*M, "C5_measurement", "[]",
                                                         "energy_vector"),
        "data_origin": enum_at(*M, "C5_measurement", "[]", "data_origin"),
        "boundary_correspondence": enum_at(*M, "C5_measurement", "[]",
                                           "boundary_correspondence"),
        "evidence_quote": "verbatim or blank if absent", "page": "int or blank"}),
      ("C6_re_estimation", "R11",
       "PER MODEL. 'explicitly none in period' needs the sentence; silence is "
       "'fixed, not mentioned'.",
       {"model": "model index",
        "regime": enum_at(*M, "C6_re_estimation", "regime", "value"),
        "update_status": enum_at(*M, "C6_re_estimation", "update_status", "value"),
        "evidence_quote": "verbatim or blank", "page": "int or blank"}),
      ("C7_validity_envelope", "R12", "PER MODEL.",
       {"model": "model index",
        "statement": enum_at(*M, "C7_validity_envelope", "statement", "value"),
        "evidence_quote": "verbatim or blank", "page": "int or blank"}),
      ("C8_metrics", "R13",
       "PER MODEL, the three blocks. status must match whether numbers are actually given.",
       {"model": "model index",
        "in_sample_fit_status": enum_at(*M, "C8_metrics", "in_sample_fit", "status", "value"),
        "out_of_sample_status": enum_at(*M, "C8_metrics", "out_of_sample_validation", "status",
                                        "value"),
        "validation_design": enum_at(*M, "C8_metrics", "out_of_sample_validation",
                                     "validation_design", "value"),
        "energy_result_status": enum_at(*M, "C8_metrics", "energy_result", "status", "value")}),
      ("C13_reproducibility", "R14", "paper level, four items.",
       {"equations_given": enum_at("C13_reproducibility", "equations_given", "value"),
        "coefficients_given": enum_at("C13_reproducibility", "coefficients_given", "value"),
        "data_available": enum_at("C13_reproducibility", "data_available", "value"),
        "code_available": enum_at("C13_reproducibility", "code_available", "value")}),
      ("refinery_or_petrochemical_case", "R15", "per application.",
       {"application": "application index",
        "value": enum_at("applications", "[]", "refinery_or_petrochemical_case", "value"),
        "evidence_quote": "verbatim", "page": "int"}),
    ]


def worksheet(key):
    L = [f"# Blind-first extraction (V3) — {key}", "",
         "> Read the PDF. Do not open the Stage C record for this paper, and do not open its",
         "> dossier. Fill this in, then run `commit`. The model's reading is shown only after.",
         "",
         "## 0. Decomposition — do this first, it governs everything below",
         "How many APPLICATIONS (distinct cases/installations) and how many MODELS in each?",
         "This is the judgement the whole record hangs on: a number from one model must never",
         "appear under another.", "",
         "```yaml",
         "decomposition:",
         "  applications: 1        # integer",
         "  models_per_application: [1]   # one integer per application, in order",
         "  note: ''               # anything that made this hard",
         "```", ""]
    for name, results, hint, spec in fields():
        L += [f"## {name}   → {results}", hint, "", "```yaml", f"{name}:"]
        L += ["  - " + "\n    ".join(f"{k}:" for k in spec)]
        L += ["```", ""]
        L += ["Legal values:"]
        for k, v in spec.items():
            L.append(f"- `{k}`: " + (" · ".join(f"`{x}`" for x in v) if isinstance(v, list)
                                     else f"*{v}*"))
        L += ["", "Leave the block empty (`" + name + ": []`) if the paper has none — and say",
              "in `absence_note` below how you searched.", ""]
    L += ["## absence declarations", "",
          "```yaml", "absence_note:",
          "  mechanisms: ''", "  adaptations: ''", "  implementation_barriers: ''",
          "```", "",
          "## what you did NOT extract blind", "",
          "Everything outside the groups above (C1, C2, C3, C4, C12 and the application",
          "descriptors) stays single-surface extraction. That is by design; it is recorded so",
          "the chapter does not imply a coverage this form did not give.", "",
          "## time", "", "```yaml", "active_minutes:      # minutes actually working, not "
          "wall-clock. A blank is missing, not zero.", "```", ""]
    return "\n".join(L)


def blocks(text):
    """Every fenced yaml block, merged. A block that does not parse is named, not guessed."""
    out, bad = {}, []
    for i, m in enumerate(re.finditer(r"```yaml\s*\n(.*?)```", text, re.S)):
        try:
            d = yaml.safe_load(m.group(1))
        except yaml.YAMLError as exc:
            bad.append(f"block {i + 1}: {str(exc).splitlines()[0]}")
            continue
        if isinstance(d, dict):
            for k, v in d.items():
                if v is not None or k not in out:
                    out[k] = v
    return out, bad


def side(key):
    return f"{WS}/{key}.state.json"


def cmd_start(a):
    os.makedirs(WS, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    p = f"{WS}/{a.key}.md"
    if os.path.isfile(p) and not a.force:
        sys.exit(f"{p} already exists. Finish it, or pass --force to start over (the existing "
                 f"one is kept with a dated suffix).")
    if os.path.isfile(p):
        os.rename(p, f"{p}.restarted_{datetime.date.today():%Y%m%d}")
    open(p, "w", encoding="utf-8").write(worksheet(a.key))
    json.dump({"key": a.key, "started_at": now(), "revealed_at": None},
              open(side(a.key), "w"), indent=2)
    core = " (one of the 11 blind-first core)" if a.key in CORE else ""
    print(f"worksheet: {p}{core}\nstarted_at recorded. Read the PDF; do not open "
          f"production/stage_c/*/outputs/{a.key}.json until after commit.")


def cmd_commit(a):
    st = json.load(open(side(a.key)))
    if st.get("revealed_at"):
        sys.exit(f"REFUSED: the model record for {a.key} was revealed by this tool at "
                 f"{st['revealed_at']}, before commit. This extraction is no longer blind-first "
                 f"and must not be recorded as one. Use `amend` to log a post-reveal reading, or "
                 f"`start --force` to redo it on a different paper.")
    text = open(f"{WS}/{a.key}.md", encoding="utf-8").read()
    data, bad = blocks(text)
    if bad:
        sys.exit("the worksheet has YAML that does not parse:\n  " + "\n  ".join(bad))
    if not data.get("decomposition"):
        sys.exit("decomposition is empty: how many applications and models did you find?")
    am = data.get("active_minutes")
    t0 = datetime.datetime.fromisoformat(st["started_at"])
    elapsed = round((datetime.datetime.now() - t0).total_seconds() / 60)
    rec = {"record_type": "blind_first_extraction_v3", "paper_key": a.key,
           "reviewer": "B. Ribeiro", "started_at": st["started_at"], "committed_at": now(),
           "wall_clock_minutes": elapsed,
           "active_minutes": am if isinstance(am, (int, float)) else None,
           "in_blind_first_core": a.key in CORE,
           "scope": "result-bearing field groups only (verification matrix §3); C1, C2, C3, C4, "
                    "C12 and the application descriptors are NOT covered by this form",
           "committed_values": {k: v for k, v in data.items() if k != "active_minutes"},
           "post_reveal_changes": [],
           "note": "Committed values are immutable. A change made after seeing the model record "
                   "is appended to post_reveal_changes with its reason, never written over "
                   "these."}
    p = f"{OUT}/{a.key}.json"
    json.dump(rec, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"committed: {p}\nwall-clock {elapsed} min" +
          (f", active {am} min" if am else ", active minutes NOT recorded (a blank is "
                                            "missing, not zero)"))
    print(f"\nThe dossier interlock for {a.key} is now released.")
    print(f"Next: `reveal --key {a.key}` to see the model's reading.")


def cmd_reveal(a):
    p = f"{OUT}/{a.key}.json"
    if not os.path.isfile(p):
        sys.exit(f"nothing committed for {a.key}: reveal before commit is what this tool exists "
                 f"to prevent. Run `commit` first.")
    st = json.load(open(side(a.key)))
    st["revealed_at"] = now(); json.dump(st, open(side(a.key), "w"), indent=2)
    mine = json.load(open(p, encoding="utf-8"))["committed_values"]
    recs = glob.glob(f"production/stage_c/*/outputs/{a.key}.json")
    if not recs:
        sys.exit(f"no model record on disk for {a.key} yet.")
    model = json.load(open(recs[0], encoding="utf-8"))
    print(f"=== {a.key} — your reading, then the model's ({recs[0]}) ===\n")
    nm = sum(len(x["models"]) for x in model["applications"])
    d = mine.get("decomposition") or {}
    print(f"decomposition   you: {d.get('applications')} app / "
          f"{d.get('models_per_application')} models    model: "
          f"{len(model['applications'])} app / {nm} models")
    print(f"mechanisms      you: {len(mine.get('mechanisms') or [])}    "
          f"model: {len(model.get('mechanisms') or [])}")
    print(f"adaptations     you: {len(mine.get('adaptations') or [])}    "
          f"model: {len(model.get('adaptations') or [])}")
    print("\nThe model's record is not the answer key. Where you differ, the page decides.")
    print(f"Log every change you now make with `amend --key {a.key}`.")


def cmd_amend(a):
    p = f"{OUT}/{a.key}.json"
    rec = json.load(open(p, encoding="utf-8"))
    print("Record one post-reveal change. Empty field to stop.")
    while True:
        f = input("  field path (e.g. mechanisms[0].claim_status): ").strip()
        if not f:
            break
        rec["post_reveal_changes"].append(
            {"field": f, "from": input("  from: ").strip(), "to": input("  to: ").strip(),
             "reason": input("  reason (what on the page decided it): ").strip(),
             "at": now()})
    json.dump(rec, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    n = len(rec["post_reveal_changes"])
    print(f"{n} post-reveal change(s) logged. The committed values are unchanged.")


def cmd_status(a):
    print(f"{'paper':20s} {'core':5s} {'started':17s} {'committed':17s} {'wall':>5s} "
          f"{'active':>7s} {'changes':>8s}")
    for k in CORE:
        p, s = f"{OUT}/{k}.json", side(k)
        if os.path.isfile(p):
            r = json.load(open(p, encoding="utf-8"))
            print(f"{k:20s} {'yes':5s} {r['started_at'][5:16]:17s} {r['committed_at'][5:16]:17s} "
                  f"{r['wall_clock_minutes']:5d} "
                  f"{(str(r['active_minutes']) if r['active_minutes'] else '—'):>7s} "
                  f"{len(r['post_reveal_changes']):8d}")
        elif os.path.isfile(s):
            print(f"{k:20s} {'yes':5s} {json.load(open(s))['started_at'][5:16]:17s} "
                  f"{'IN PROGRESS':17s}")
        else:
            print(f"{k:20s} {'yes':5s} {'—':17s} {'—':17s}")
    done = [k for k in CORE if os.path.isfile(f"{OUT}/{k}.json")]
    mins = [json.load(open(f"{OUT}/{k}.json"))["active_minutes"] for k in done]
    mins = [m for m in mins if m]
    print(f"\n{len(done)}/11 committed." + (
        f" Active minutes recorded on {len(mins)}: mean {sum(mins)/len(mins):.0f} min → "
        f"{sum(mins)/len(mins)*11/60:.1f} h for the 11." if mins else
        " No active minutes recorded yet — that is the figure the amendment says is unmeasured."))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("start", cmd_start), ("commit", cmd_commit), ("reveal", cmd_reveal),
                     ("amend", cmd_amend), ("status", cmd_status)):
        s = sub.add_parser(name); s.set_defaults(fn=fn)
        if name != "status":
            s.add_argument("--key", required=True)
        if name == "start":
            s.add_argument("--force", action="store_true")
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
