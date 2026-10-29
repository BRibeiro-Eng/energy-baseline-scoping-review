#!/usr/bin/env python3
"""Satisfiability suite — for EVERY legal value in the schema, a record exists that validates.

The pilot paid twice for the same method gap. The other suites test what the instrument
REJECTS, starting from a fixture; they cannot find a value the instrument makes impossible to
write, because the fixture does not contain one. Two did:

  * `other` on a mechanism axis: the validator demanded a companion key that
    additionalProperties:false rejects, so no response could satisfy the error;
  * `fixed, not mentioned`: rejected as a substantive value with no quote, when the value
    literally means the paper does not mention it.

This suite enumerates every enum in the schema, writes each legal value into the fixture with
each reasonable completion a surface could produce, and fails if no completion validates. It is
a property, not a case list: a new field or value is covered the moment it is added.

  /usr/local/bin/python3 stage_c/test_satisfiable.py
"""
import copy, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT + "/output")
from stage_c_validate import validate, _verbatim_name            # noqa: E402

FX = "stage_c/fixtures"
REC = json.load(open(f"{FX}/record_valid.json", encoding="utf-8"))
PAGES = json.load(open(f"{FX}/bundle_rayyan-000000001.json", encoding="utf-8"))["pdf"]["pages"]
SCHEMA = json.load(open("stage_c/schema.json", encoding="utf-8"))

# a sentence that exists verbatim on page 1 of the fixture bundle
QUOTE = "The plant is a single facility operated"
assert QUOTE.lower() in (PAGES[0].get("text") or "").lower(), "fixture anchor moved"
fails = []


def deref(n):
    if not isinstance(n, dict):
        return n
    if "$ref" in n:
        t = SCHEMA
        for part in n["$ref"].lstrip("#/").split("/"):
            t = t[part]
        return deref(t)
    if "allOf" in n:
        out = {k: v for k, v in n.items() if k != "allOf"}
        for sub in n["allOf"]:
            d = deref(sub)
            if isinstance(d, dict):
                for k, v in d.items():
                    if k == "properties":
                        pr = dict(out.get("properties") or {}); pr.update(v)
                        out["properties"] = pr
                    elif k == "required":
                        out["required"] = sorted(set(out.get("required") or []) | set(v))
                    else:
                        out[k] = v
        return out
    return n


def enum_sites(node, path=(), out=None):
    """(path tuple, field name, legal values, True if the field sits inside an envelope)."""
    out = [] if out is None else out
    node = deref(node)
    if not isinstance(node, dict):
        return out
    props = node.get("properties") or {}
    for k, v in props.items():
        dv = deref(v)
        if isinstance(dv, dict) and dv.get("enum"):
            vals = [x for x in dv["enum"] if isinstance(x, str)]
            if vals:
                # the keys this holder object legally accepts: a study_limitations item has no
                # support_class, so offering it one is the harness's error, not the schema's
                out.append((path + (k,), k, vals, set(props)))
        enum_sites(v, path + (k,), out)
    if node.get("items"):
        enum_sites(node["items"], path, out)
    return out


def holders(rec, path):
    """Every object in the record that the schema path addresses, walking lists."""
    cur = [rec]
    for seg in path[:-1]:
        nxt = []
        for o in cur:
            if not isinstance(o, dict) or seg not in o:
                continue
            v = o[seg]
            nxt.extend(v if isinstance(v, list) else [v])
        cur = nxt
    return [o for o in cur if isinstance(o, dict) and path[-1] in o]


# Completions a surface can actually write. The suite passes if ANY of them validates.
def completions(field, value, allowed):
    base = {field: value}
    vb = _verbatim_name(field)
    keep = lambda d: {k: v for k, v in d.items() if k in allowed}
    quoted = keep({"evidence_quote": QUOTE, "page": 1, "support_class": "direct statement"})
    silent = keep({"evidence_quote": None, "page": None, "support_class": "absence checked",
                   "absence_basis": "searched full text"})
    for extra in ({}, keep({vb: "the paper's own wording"})):
        for ev in (quoted, silent):
            yield {**base, **extra, **ev}, ("quoted" if ev is quoted else "silent",
                                            "with verbatim" if extra else "bare")


# DOUBLE ENTRY. These lists are the suite's OWN reading of what each value means, written here
# and not imported from stage_c_grounding, so that a disagreement between the instrument's
# classification and this one is a failure rather than a tautology. "some completion works" is
# too weak a property: 'fixed, not mentioned' validates fine WITH a quote, and the defect was
# that the form the value actually occurs in -- no sentence anywhere in the paper -- was
# impossible. So each value must be writable in the form that matches its meaning.
SILENT_REQUIRED = {"not reported", "not applicable", "not stated", "explicitly absent"}
BOTH_REQUIRED = {"fixed, not mentioned", "no selection", "none", "none (absolute)",
                 "none reported"}


def required_forms(value):
    if value in SILENT_REQUIRED:
        return ("silent",)
    if value in BOTH_REQUIRED:
        return ("silent", "quoted")
    return ("quoted",)


def try_value(path, field, value, allowed):
    """Every form the value's meaning requires must validate. Returns (problem, forms_ok)."""
    need = required_forms(value)
    ok, errs = [], []
    for patch, how in completions(field, value, allowed):
        r = copy.deepcopy(REC)
        hs = holders(r, path)
        if not hs:
            return "unreachable in fixture", None
        for h in hs:
            if field == "value":                 # an enveloped value: replace the envelope
                h["value"] = patch["value"]
                for k, v in patch.items():
                    if k != "value":
                        h[k] = v
            else:                                # a bare enum on an item
                for k, v in patch.items():
                    h[k if k != field else field] = v
        errs, _ = validate(r, PAGES)
        mine = [e for e in errs if path[-1] in e or field in e
                or _verbatim_name(field) in e or ".".join(path[-2:]) in e]
        if not mine:
            ok.append(how[0])
    if not ok:
        return "no completion validates: " + str(errs[:2]), None
    missing = [f for f in need if f not in ok]
    if missing:
        return (f"the {'/'.join(missing)} form does not validate, and that is the form this "
                f"value occurs in: " + str(errs[:2])), None
    return None, sorted(set(ok))


# --selftest re-introduces the two defects the pilot found and asserts this suite flags them.
# A satisfiability suite that cannot fail is worth nothing.
if "--selftest" in sys.argv:
    import stage_c_validate as V
    import stage_c_grounding as G
    V._VERBATIM_KEY = {"value": "other_verbatim"}      # defect 1: wrong companion key
    G.SILENCE_DERIVED = set()                          # defect 2: silence owes a quote
    print("SELFTEST: the two pilot defects are re-introduced; this run MUST fail\n")

# A second satisfiability property, from the same pilot paper: the prompt advertises two
# optional bookkeeping keys as legal on every object that carries evidence. rayyan-472536694
# wrote `searched_terms` on three C5 entries and was rejected, because the C5 item did not
# declare it. A key the prompt calls legal and the schema refuses is an unsatisfiable
# instruction by another route, so it is asserted here rather than discovered per field.
ADVERTISED = ("searched_terms", "non_contiguous_evidence")
PROMPT = open("stage_c/PROMPT_EXTRACTION.md", encoding="utf-8").read()


def advertised_keys_accepted():
    bad = []

    def walk(node, path=""):
        node = deref(node)
        if not isinstance(node, dict):
            return
        props = node.get("properties")
        if (props is not None and node.get("additionalProperties") is False
                and ("evidence_quote" in props or "support_class" in props)):
            for k in ADVERTISED:
                if k not in props:
                    bad.append(f"{path or 'root'} rejects {k}")
        for k, v in (props or {}).items():
            walk(v, f"{path}.{k}".lstrip("."))
        if node.get("items"):
            walk(node["items"], path)

    walk(SCHEMA)
    for k in ADVERTISED:
        if f"`{k}`" not in PROMPT:
            bad.append(f"the prompt no longer mentions {k}; update ADVERTISED here too")
    if "`confidence`" in PROMPT and "no `confidence` field" not in PROMPT:
        bad.append("the prompt advertises `confidence`, which the instrument does not accept")
    if bad:
        print("FAIL  the prompt advertises keys the schema refuses:")
        for b in bad:
            print("      " + b)
    return not bad


if not advertised_keys_accepted():
    fails.append("advertised keys")
else:
    print("PASS  every key the prompt calls legal is accepted wherever evidence is carried\n")

sites = enum_sites(SCHEMA)
n_vals = sum(len(v) for _, _, v, _ in sites)
print(f"{len(sites)} enum sites, {n_vals} legal values\n")
skipped = 0
unreachable = set()
for path, field, vals, allowed in sites:
    label = ".".join(path)
    for v in vals:
        bad, how = try_value(path, field, v, allowed)
        if isinstance(bad, str) and bad == "unreachable in fixture":
            skipped += 1
            unreachable.add(label)
            continue
        if bad:
            fails.append(f"{label} = {v!r}")
            print(f"FAIL  {label} = {v!r}\n      {str(bad)[:220]}")

print(f"\n{n_vals - skipped} values exercised, {skipped} unreachable from the fixture")
if unreachable:
    # Honest coverage: these paths the fixture does not instantiate, so nothing is claimed
    # about them. Extending the fixture is how that list shrinks.
    print("NOT COVERED (fixture does not instantiate the holder):")
    for u in sorted(unreachable):
        print("  " + u)
print("ALL SATISFIABLE" if not fails else f"{len(fails)} UNSATISFIABLE: " + ", ".join(fails[:8]))
if "--selftest" in sys.argv:
    print("SELFTEST " + ("PASS — the suite catches both defects" if fails
                         else "FAIL — the suite is blind to them"))
    sys.exit(0 if fails else 1)
sys.exit(1 if fails else 0)
