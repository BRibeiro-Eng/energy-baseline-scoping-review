#!/usr/bin/env python3
"""Validate a Stage-C record against the schema and run the three grounding checks."""
import json, os, sys, argparse, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
from stage_c_grounding import check_record  # noqa: E402

SCHEMA_PATH = "stage_c/schema.json"

def schema_digest():
    """The recorded digest must match the file actually being used, or the run is not the
    run that was declared. Previously computed and never compared."""
    blob = open(SCHEMA_PATH, "rb").read().rstrip(b"\n")
    actual = hashlib.sha256(blob).hexdigest()
    p = "stage_c/SCHEMA_SHA256.txt"
    declared = open(p).read().split()[0] if os.path.isfile(p) else None
    return declared, actual


def load_validator():
    import jsonschema
    declared, actual = schema_digest()
    if declared is None:
        raise SystemExit("stage_c/SCHEMA_SHA256.txt is missing — the schema in use is not "
                         "the schema that was declared. Write the digest and re-run.")
    if declared != actual:
        raise SystemExit(f"SCHEMA DIGEST MISMATCH\n  declared {declared}\n  actual   {actual}\n"
                         "The schema on disk is not the one recorded. Either the freeze was "
                         "broken or the digest is stale. Resolve before extracting anything.")
    s = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    return jsonschema.Draft202012Validator(s), declared, actual

def _norm_label(x):
    import re as _re
    return _re.sub(r"[^a-z0-9]+", " ", str(x).lower()).strip()


def snap_enums(rec, max_rounds=3):
    """Deterministically snap an unambiguous enum near-miss to its legal value.

    Snaps ONLY differences of case, punctuation and spacing — 'OLS' for 'ols', 'Partial' for
    'partial'. Nothing else.

    Containment matching was removed after it changed meanings: 'not absolute energy' snapped
    to 'absolute energy', and 'energy consumption' is a unique whole-word substring of
    'specific energy consumption', which would silently change a model's dependent variable.
    A unique textual match does not establish semantic equivalence. Paraphrases now go to the
    repair loop, which costs one re-read and returns the extractor's own corrected value.

    EVERY snap is recorded and reported. A silent snap would be a value the reviewer never
    saw being changed by a script.
    """
    import jsonschema
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    snaps = []
    for _ in range(max_rounds):
        changed = False
        for e in list(v.iter_errors(rec)):
            if e.validator != "enum" or not isinstance(e.instance, str):
                continue
            legal = [x for x in e.validator_value if isinstance(x, str)]
            got = _norm_label(e.instance)
            cand = [x for x in legal if _norm_label(x) == got]
            if len(cand) != 1:
                continue
            node = rec
            for step in list(e.absolute_path)[:-1]:
                node = node[step]
            last = list(e.absolute_path)[-1]
            node[last] = cand[0]
            snaps.append({"path": "/".join(map(str, e.absolute_path)),
                          "from": e.instance, "to": cand[0],
                          "basis": "exact after case and punctuation folding"})
            changed = True
        if not changed:
            break
    return rec, snaps


def _id_uniqueness(rec):
    errs = []
    seen_app = set()
    seen_models = set()
    for a in rec.get("applications") or []:
        if a.get("application_id") in seen_app:
            errs.append(f"duplicate application_id {a.get('application_id')!r}")
        seen_app.add(a.get("application_id"))
        for m in a.get("models") or []:
            if m.get("model_id") in seen_models:
                errs.append(f"duplicate model_id {m.get('model_id')!r}: model ids must be "
                            f"unique across the whole record, because mechanisms refer to "
                            f"them globally")
            seen_models.add(m.get("model_id"))
    for field, key in (("mechanisms", "mechanism_id"), ("adaptations", "adaptation_id")):
        seen = set()
        for it in rec.get(field) or []:
            if it.get(key) in seen:
                errs.append(f"duplicate {key} {it.get(key)!r}")
            seen.add(it.get(key))
    # refers_to must name something that exists
    valid = seen_app | seen_models | {"paper-level argument"}
    for m in rec.get("mechanisms") or []:
        if m.get("refers_to") not in valid:
            errs.append(f"mechanism {m.get('mechanism_id')}: refers_to "
                        f"{m.get('refers_to')!r} names nothing in this record")
    for dd in rec.get("adaptations") or []:
        if dd.get("refers_to") not in valid:
            errs.append(f"adaptation {dd.get('adaptation_id')}: refers_to "
                        f"{dd.get('refers_to')!r} names nothing in this record")
    mech_ids = {m.get("mechanism_id") for m in rec.get("mechanisms") or []}
    for d in rec.get("adaptations") or []:
        am = d.get("addresses_mechanism")
        if am is not None and am not in mech_ids:
            errs.append(f"adaptation {d.get('adaptation_id')}: addresses_mechanism {am!r} "
                        f"names no mechanism in this record")
    # One sentence MAY support more than one limitation — "the model assumes stationarity and
    # cannot be extrapolated" states two. Forbidding quote reuse destroyed information, so it
    # is allowed and recorded; de-duplication happens at COUNTING time, per paper per category,
    # not at extraction time. An exact duplicate (same quote, same cause, same effect) is still
    # an error, because that is a transcription slip and not a second finding.
    qseen = {}
    for m in rec.get("mechanisms") or []:
        q = (m.get("evidence_quote") or "").strip().lower()
        sig = (m.get("mechanism_cause"), m.get("mechanism_effect_on_model"),
               m.get("claim_status"))
        # A sub-span of an already-recorded quote is the same sentence, so an exact-string
        # test was defeated by dropping a word. Containment either way, same axes, same
        # claim_status: one finding recorded twice.
        dup = next((oq for oq, sigs in qseen.items()
                    if sig in sigs and q and oq and (q in oq or oq in q)), None)
        if dup is not None:
            errs.append(f"mechanism {m.get('mechanism_id')}: duplicate — same cause, same "
                        f"effect, same claim_status, and the quote is the same sentence as one "
                        f"already recorded ({dup[:60]!r}). One finding, one occurrence.")
        qseen.setdefault(q, set()).add(sig)

    # an empty list asserts nothing unless the extractor declares it searched
    decl = rec.get("absence_declarations") or {}
    for field in ("mechanisms", "adaptations", "study_limitations", "implementation_barriers"):
        if not (rec.get(field) or []):
            d = decl.get(field) or {}
            if d.get("searched") is not True:
                errs.append(f"{field} is empty and absence_declarations.{field}.searched is "
                            f"not true: an unsearched field is not a finding and cannot be "
                            f"counted. Search it, or say why it is meaningless here.")
    # an 'other' enum value must carry its verbatim
    for m in rec.get("mechanisms") or []:
        # the 'other' requirement is enforced generically by _other_verbatim(), for every enum
        if (m.get("mechanism_cause") == "not stated"
                and m.get("mechanism_effect_on_model") == "not stated"):
            errs.append(f"mechanism {m.get('mechanism_id')}: both cause and effect are "
                        f"'not stated' — the occurrence asserts nothing; remove it")
    errs += _other_verbatim(rec)
    errs += _block_consistency(rec)
    errs += _locator_claims(rec)
    return errs


# Every enum in the instrument that admits 'other' must be accompanied by the paper's own
# wording. Only mechanisms and adaptations were checked, so 'other' passed unexplained on C1,
# C2, C3, C5 and study_limitations -- an uninterpretable value that still enters a count.
# The companion key is <field>_other_verbatim, or other_verbatim on an envelope.
def _has_other(v):
    if isinstance(v, str):
        return v == "other"
    if isinstance(v, list):
        return "other" in v
    return False


# The companion key is NOT always <field>_other_verbatim: the schema names the two mechanism
# axes' companions cause_other_verbatim and effect_other_verbatim. The generic rule demanded
# 'mechanism_effect_on_model_other_verbatim', which additionalProperties:false then rejects --
# an error no surface can satisfy, so the paper burned three attempts and was quarantined.
# Found by the pilot on rayyan-472535351 at a cost of one attempt. Names come from the schema.
_VERBATIM_KEY = {"mechanism_cause": "cause_other_verbatim",
                 "mechanism_effect_on_model": "effect_other_verbatim",
                 "adaptation": "adaptation_other_verbatim",
                 "value": "other_verbatim"}


def _verbatim_name(field):
    return _VERBATIM_KEY.get(field, f"{field}_other_verbatim")


def _other_verbatim(rec, prefix="", out=None):
    out = [] if out is None else out
    if isinstance(rec, dict):
        for k, v in rec.items():
            path = f"{prefix}.{k}" if prefix else k
            if _has_other(v):
                name = _verbatim_name(k)
                sib = rec.get(name)
                if not (isinstance(sib, str) and sib.strip()):
                    out.append(f"{path}: value is 'other' and {name} is missing or empty. "
                               f"An 'other' without the paper's own wording cannot be read "
                               f"back and cannot be counted.")
            if isinstance(v, (dict, list)):
                _other_verbatim(v, path, out)
    elif isinstance(rec, list):
        for i, v in enumerate(rec):
            _other_verbatim(v, f"{prefix}[{i}]", out)
    return out


def _locator_claims(rec, prefix="", out=None):
    """page_as_recorded and locator_corrected are written by the grounding check, not by an
    extracting surface. A surface cannot be stopped from inventing them, but an inconsistent
    claim is rejected: the flag requires a recorded page that differs from the corrected one."""
    out = [] if out is None else out
    if isinstance(rec, dict):
        if rec.get("locator_corrected") is True:
            par, pg = rec.get("page_as_recorded"), rec.get("page")
            if par is None or par == pg:
                out.append(f"{prefix or 'record'}: locator_corrected is true but "
                           f"page_as_recorded is {par!r} against page {pg!r}. The flag is set "
                           f"by the grounding check and means the cited page was replaced; it "
                           f"is not something to assert.")
        for k, v in rec.items():
            if isinstance(v, (dict, list)):
                _locator_claims(v, f"{prefix}.{k}" if prefix else k, out)
    elif isinstance(rec, list):
        for i, v in enumerate(rec):
            _locator_claims(v, f"{prefix}[{i}]", out)
    return out


def _block_consistency(rec):
    """Declarations that existed but gated nothing, each one reproduced before being closed."""
    errs = []
    for ai, a in enumerate(rec.get("applications") or []):
        for mi, m in enumerate(a.get("models") or []):
            tag = f"{a.get('application_id')}.{m.get('model_id')}"
            # C3: an empty variable list is a finding (a mean or a ratio), never a silence
            if not (m.get("C3_variables") or []):
                d = m.get("C3_variables_absence") or {}
                if d.get("searched") is not True:
                    errs.append(f"{tag}: C3_variables is empty and C3_variables_absence."
                                f"searched is not true. A model with no explanatory variable "
                                f"is a finding; an unsearched empty array is not.")
            # C8: 'reported' with no metric recorded is the B13b ambiguity all over again
            for blk in ("in_sample_fit", "out_of_sample_validation", "energy_result"):
                b = (m.get("C8_metrics") or {}).get(blk) or {}
                st = ((b.get("status") or {}).get("value"))
                n = len(b.get("metrics") or [])
                if st == "reported" and n == 0:
                    errs.append(f"{tag}: C8_metrics.{blk}.status is 'reported' but metrics is "
                                f"empty. Record the numbers, or set the status to what is "
                                f"true: 'not reported' (the paper fitted and did not publish) "
                                f"or 'not applicable'.")
                if st in ("not reported", "not applicable") and n:
                    errs.append(f"{tag}: C8_metrics.{blk}.status is {st!r} but {n} metric(s) "
                                f"are recorded.")
    return errs


def validate(rec, pages, snap=True):
    snaps = []
    if snap:
        rec, snaps = snap_enums(rec)
    v, declared, actual = load_validator()
    errs = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in
            sorted(v.iter_errors(rec), key=lambda e: list(e.path))]
    errs += _id_uniqueness(rec)
    g = check_record(rec, pages)
    blocking = [f for f in g["failures"]
                if f.get("acceptance") not in ("interleaved — human reading required",
                                               "locator corrected")]
    g["routed_for_review"] = [f for f in g["failures"] if f not in blocking]
    if blocking:
        for f in blocking[:20]:
            errs.append(f"grounding {f['path']}: quote not found on physical page "
                        f"{f.get('page_cited')}"
                        + (f" (found on page {f['found_on_page']})" if f.get("found_on_page") else "")
                        + f": {f['quote']!r}")
    for p in g["absence_without_basis"]:
        errs.append(f"{p}: value is an absence but absence_basis is missing")
    for it in g.get("value_without_evidence", []):
        errs.append(f"{it['path']}: substantive value {it['value']!r} carries NO quote. "
                    f"Only a value whose content is an absence may omit evidence.")
    for it in g.get("stated_absence_without_quote", []):
        errs.append(f"{it}: absence_basis is 'explicitly stated absent' but no quote is given. "
                    f"If the paper states the absence there is a sentence saying so; quote it, "
                    f"or use 'searched full text'.")
    for it in g["invented_absence_quote"]:
        errs.append(f"{it['path']}: value is 'not reported'/'not applicable' but carries a "
                    f"quote — never justify an absence with a quote: {it['quote']!r}")
    g["enum_snaps"] = snaps
    return errs, g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", required=True,
                    choices=["claude", "chatgpt", "pilot_claude", "pilot_chatgpt", "_smoke"])
    ap.add_argument("--key"); ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    d = f"production/stage_c/{a.surface}/outputs"
    keys = ([a.key] if a.key else
            sorted(os.path.basename(p)[:-5] for p in __import__("glob").glob(d + "/rayyan-*.json")))
    bad = 0
    for k in keys:
        rec = json.load(open(f"{d}/{k}.json", encoding="utf-8"))
        pages = json.load(open(f"output/stage0/{k}.json", encoding="utf-8"))["pdf"]["pages"]
        errs, g = validate(rec, pages)
        sc = g["G3_support_class"]
        status = "OK " if not errs else "FAIL"
        if g.get("enum_snaps"):
            print(f"        snapped {len(g['enum_snaps'])} enum near-misses: "
                  + "; ".join(f"{x['from']!r}->{x['to']!r}" for x in g["enum_snaps"][:4]))
        # 'interleaved' was printed twice and 'wrong_page' and 'not_found' not at all, so the
        # two classes that actually fail a record were invisible in the run report.
        print(f"[{status}] {k}  exact={g['G1_G2']['exact']} "
              f"wrong_page={g['G1_G2']['wrong_page']} not_found={g['G1_G2']['not_found']} "
              f"interleaved={g['G1_G2']['interleaved']} "
              f"locator_corr={g['G1_G2']['locator_corrected']}"
              f"(+{g['locator_corrected_persisted']} from earlier passes) "
              f"line_num_amb={len(g.get('routed_for_review') or [])} "
              f"negation={g['G1_G2']['negation_mismatch']} "
              f"absent={g['G1_G2']['absent_no_quote']} | direct={sc['direct statement']} "
              f"inference={sc['requires inference']} absence={sc['absence checked']}")
        for e in errs:
            print("        " + e[:200]); bad += 1
    print(f"\n{len(keys)} records, {bad} problems")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
