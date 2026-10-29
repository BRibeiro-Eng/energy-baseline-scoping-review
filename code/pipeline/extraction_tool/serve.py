#!/usr/bin/env python3
"""C-2.3 extraction tool — local Flask app for blind-first human charting.

Serves a schema-driven form (v2.2.1) beside the PDF so the reviewer charts
without editing raw JSON. Enum fields are dropdowns, multi-enums are checkbox
groups, bools are tri-state, lists have add/remove — so the saved JSON is
always schema-valid.

Run from the generated reviewer workspace:
    python3 extraction_tool/serve.py --data-root reviews
    # open http://127.0.0.1:5051

Phases (auto-detected from the folder a template lives in):
    blind         -> manual/blind/{key}.json         (empty; you chart first)
    verification  -> manual/verification/{key}.json  (AI-prefilled later)
    ai_blind_test -> ai_blind_test/{key}.json        (AI-filled test copy)

Blind-first withhold/commit/reveal (C-2 §3-Step-3 / §3-Step-5):
    Each paper carries a state machine persisted in {key}.state.json:
        blind -> committed -> revealed -> finalised
    AI model outputs live in side files ({key}.ai.json, one or both models);
    a verification template that ships AI-prefilled has its prefill moved
    into {key}.ai.json on first touch. While state is `blind`, /api/paper
    returns NO AI values and /api/ai returns 403 (attempts logged).
    POST /api/commit freezes the reviewer's answers into {key}.blind.json
    and reveals the model outputs; every post-commit field change is
    appended to {key}.reveal_changes.jsonl (the §3 reveal-change log).
    POST /api/finalise locks the paper (further saves 409).

Saving writes the same JSON shape back in place (value-only schema),
validated against schema.py. No network calls.
"""
import argparse
import datetime
import glob
import json
import os
import re
import shutil
import threading
from functools import wraps
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_file

try:
    from .schema import SCHEMA  # package import in tests
except ImportError:  # direct execution from extraction_tool/
    from schema import SCHEMA

try:
    from local_storage import is_prohibited
except ImportError:  # standalone reviewer-workspace copy
    from .local_storage import is_prohibited

try:
    from review_evidence import EVIDENCE_MODES, evidence_errors
except ImportError:  # direct execution from extraction_tool/
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from review_evidence import EVIDENCE_MODES, evidence_errors

HERE = Path(__file__).resolve().parent
CANONICAL_ROOT = HERE.parent.parent
DATA_ROOT = CANONICAL_ROOT / "production" / "reviewer_workspace" / "reviews"
PAPER_KEY = re.compile(r"^rayyan-\d+$")
STATE_LOCK = threading.RLock()

BLOCKS = ("eligibility", "level_a", "level_b")
DEFAULTS = {b: {f["name"]: ([] if f["type"] in ("multienum", "list_str", "list_obj")
                            else None) for f in spec["fields"]}
            for b, spec in SCHEMA.items()}

app = Flask(__name__)


def _state_locked(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        with STATE_LOCK:
            return func(*args, **kwargs)
    return wrapped


# --------------------------------------------------------------- data helpers
def _within(path: Path, root: Path):
    return path == root or root in path.parents


def configure(*, data_root, canonical_root):
    """Bind the UI to one local reviewer dataset and its canonical corpus."""
    global DATA_ROOT, CANONICAL_ROOT
    supplied_data = Path(data_root).expanduser()
    supplied_canonical = Path(canonical_root).expanduser()
    if is_prohibited(supplied_data) or is_prohibited(supplied_canonical):
        raise RuntimeError("prohibited Desktop/Documents/iCloud-backed root")
    try:
        canonical = supplied_canonical.resolve(strict=True)
        data = supplied_data.resolve(strict=True)
    except OSError as exc:
        raise RuntimeError(f"missing local reviewer root: {exc}") from exc
    if is_prohibited(data) or is_prohibited(canonical):
        raise RuntimeError("prohibited Desktop/Documents/iCloud-backed root")
    if not canonical.is_dir() or not data.is_dir():
        raise RuntimeError("canonical_root and data_root must be directories")
    if not _within(data, canonical):
        raise RuntimeError(f"reviewer data escapes canonical root: {data}")
    CANONICAL_ROOT = canonical
    DATA_ROOT = data


def _phase_dirs():
    if DATA_ROOT.name in {"blind", "verification", "ai_blind_test"}:
        return [(DATA_ROOT.name, DATA_ROOT)]
    phases = [
        (name, DATA_ROOT / name)
        for name in ("blind", "verification", "ai_blind_test")
        if (DATA_ROOT / name).is_dir()
    ]
    return phases or [(DATA_ROOT.name, DATA_ROOT)]


def _template_path(key):
    if not PAPER_KEY.fullmatch(key):
        return None, None
    for phase, d in _phase_dirs():
        p = (d / f"{key}.json").resolve(strict=False)
        if _within(p, DATA_ROOT) and p.is_file():
            return phase, p
    return None, None


def _list_papers():
    out = []
    for phase, d in _phase_dirs():
        for p in sorted(d.glob("rayyan-*.json")):
            if "." in p.name[:-5]:                     # skip .state/.blind/.ai side files
                continue
            tpl = json.loads(p.read_text(encoding="utf-8"))
            out.append({
                "key": tpl["key"],
                "phase": phase,
                "title": tpl["metadata"]["title"],
                "year": tpl["metadata"]["year"],
                "rayyan_decision": tpl["metadata"]["rayyan_decision"],
                "done": bool(tpl.get("_done")),
                "state": _peek_state(p)["state"],
            })
    out.sort(key=lambda r: (r["phase"], r["key"]))
    return out


# ------------------------------------------------------ state machine helpers
def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def _side(p, suffix):
    p = Path(p)
    return p.with_name(p.stem + "." + suffix)          # {key}.json -> {key}.state.json


def _atomic_write(path, obj):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _backup(p, key):
    p = Path(p)
    bdir = p.parent / "backups"
    bdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    shutil.copy2(p, bdir / f"{key}.{stamp}.json")


def _peek_state(p):
    sp = _side(p, "state.json")
    if sp.exists():
        return json.load(open(sp, encoding="utf-8"))
    return {"state": "blind"}


def _save_state(p, st):
    _atomic_write(_side(p, "state.json"), st)


def _ensure_state(key, p):
    """Load (or lazily create) {key}.state.json. On first touch of an
    AI-prefilled verification template, move the prefill into {key}.ai.json
    and blank the template so blind mode never serves model values."""
    with STATE_LOCK:
        sp = _side(p, "state.json")
        if sp.exists():
            return json.load(open(sp, encoding="utf-8"))
        tpl = json.load(open(p, encoding="utf-8"))
        if not _side(p, "ai.json").exists():
            prefilled = (tpl.get("eligibility") or {}).get("methodological_eligibility") is not None
            if tpl.get("_legacy_ai_prefill") is True and not tpl.get("_done") and prefilled:
                _backup(p, key)
                _atomic_write(_side(p, "ai.json"),
                              {"models": {"prefill": {b: tpl.get(b) for b in BLOCKS}}})
                for b in BLOCKS:
                    tpl[b] = {k: (list(v) if isinstance(v, list) else v)
                              for k, v in DEFAULTS[b].items()}
                _atomic_write(p, tpl)
        initial_state = "blind" if tpl.get("_blind_required", True) else "revealed"
        created = _now()
        st = {"key": key, "state": initial_state, "created_at": created,
              "committed_at": None,
              "revealed_at": created if initial_state == "revealed" else None,
              "finalised_at": None,
              "blind_access_denials": []}
        _save_state(p, st)
        return st


def _ai_values(p):
    """Model outputs for a paper: {model: {eligibility, level_a, level_b}}.
    {key}.ai.json holds {"models": {...}} (or flat single-model blocks);
    {key}.ai.<model>.json holds one model's blocks."""
    out = {}
    p = Path(p)
    base = str(p.with_suffix(""))
    for f in sorted(glob.glob(base + ".ai*.json")):
        d = json.load(open(f, encoding="utf-8"))
        name = os.path.basename(f)[len(os.path.basename(base)):-5].strip(".")  # "ai" / "ai.claude"
        if isinstance(d, dict) and "models" in d:
            out.update(d["models"])
        else:
            out[name[3:] if name.startswith("ai.") else "ai"] = d
    return out


# ------------------------------------------------------------ schema validate
def _bad(msg, field):
    return {"error": msg, "field": field}


def _validate_value(f, v, fq):
    t = f["type"]
    if t == "bool":
        if v is not None and not isinstance(v, bool):
            return _bad(f"{fq}: expected true/false/null", fq)
    elif t == "enum":
        if v is not None and v not in f["options"]:
            return _bad(f"{fq}: {v!r} not an allowed value", fq)
    elif t == "multienum":
        if not isinstance(v, list):
            return _bad(f"{fq}: expected a list", fq)
        for item in v:
            if item in f["options"]:
                continue
            if f.get("other") and isinstance(item, str) and item.startswith("other-named:"):
                continue
            return _bad(f"{fq}: {item!r} not an allowed value", fq)
    elif t == "list_str":
        if not isinstance(v, list) or any(not isinstance(x, str) for x in v):
            return _bad(f"{fq}: expected a list of strings", fq)
    elif t == "list_obj":
        if not isinstance(v, list):
            return _bad(f"{fq}: expected a list", fq)
        item_fields = {g["name"]: g for g in f["item_fields"]}
        for obj in v:
            if not isinstance(obj, dict):
                return _bad(f"{fq}: expected a list of objects", fq)
            for k, v2 in obj.items():
                g = item_fields.get(k)
                if g is None:
                    return _bad(f"{fq}.{k}: unknown item field", fq)
                if g["type"] == "enum":
                    if v2 is not None and v2 not in g["options"]:
                        return _bad(f"{fq}.{k}: {v2!r} not an allowed value", fq)
                elif v2 is not None and not isinstance(v2, str):
                    return _bad(f"{fq}.{k}: expected string/null", fq)
    else:  # text / textarea
        if v is not None and not isinstance(v, str):
            return _bad(f"{fq}: expected string/null", fq)
    return None


def _validate(incoming):
    if not isinstance(incoming, dict):
        return _bad("payload must be an object", None)
    allowed = set(BLOCKS) | {"reviewer_notes", "reviewer_evidence", "_done"}
    for k in incoming:
        if k not in allowed:
            return _bad(f"unknown field: {k}", k)
    if "reviewer_notes" in incoming and not isinstance(incoming["reviewer_notes"], str):
        return _bad("reviewer_notes must be a string", "reviewer_notes")
    if "reviewer_evidence" in incoming:
        evidence = incoming["reviewer_evidence"]
        valid_fields = {
            f"{block}.{field['name']}"
            for block in BLOCKS for field in SCHEMA[block]["fields"]
        }
        if not isinstance(evidence, dict):
            return _bad("reviewer_evidence must be an object", "reviewer_evidence")
        for field, item in evidence.items():
            if field not in valid_fields or not isinstance(item, dict):
                return _bad(f"invalid reviewer evidence field: {field}", "reviewer_evidence")
            if set(item) - {"mode", "quote", "page", "rule"}:
                return _bad(f"unknown reviewer evidence property: {field}", field)
            mode = item.get("mode")
            if mode is not None and mode not in EVIDENCE_MODES:
                return _bad(f"{field}.mode is not registered", field)
            if item.get("quote") is not None and not isinstance(item.get("quote"), str):
                return _bad(f"{field}.quote must be string/null", field)
            page = item.get("page")
            if page is not None and (not isinstance(page, int) or isinstance(page, bool) or page < 1):
                return _bad(f"{field}.page must be a positive integer/null", field)
            if item.get("rule") is not None and not isinstance(item.get("rule"), str):
                return _bad(f"{field}.rule must be string/null", field)
    if "_done" in incoming and not isinstance(incoming["_done"], bool):
        return _bad("_done must be a boolean", "_done")
    for block in BLOCKS:
        if block not in incoming:
            continue
        vals = incoming[block]
        if not isinstance(vals, dict):
            return _bad(f"{block} must be an object", block)
        specs = {f["name"]: f for f in SCHEMA[block]["fields"]}
        for name, v in vals.items():
            f = specs.get(name)
            fq = f"{block}.{name}"
            if f is None:
                return _bad(f"unknown field: {fq}", fq)
            err = _validate_value(f, v, fq)
            if err:
                return err
    return None


def _review_evidence_errors(tpl, *, require_complete):
    evidence = tpl.get("reviewer_evidence") or {}
    errors = []
    for field in tpl.get("_review_fields") or []:
        section, _, name = field.partition(".")
        value = (tpl.get(section) or {}).get(name)
        item = evidence.get(field) or {}
        errors.extend(
            f"{field}: {message}"
            for message in evidence_errors(value, item, require_complete=require_complete)
        )
    return errors


def _unanswered_review_fields(tpl):
    """Assigned scalar review fields still at their blank-template value.

    Lists/multienums are excluded: [] is a legitimate answer (e.g. B9 empty
    when B8 is false) and indistinguishable from the blank template, so
    list-typed fields are guarded by the evidence requirement instead.
    """
    unanswered = []
    for field in tpl.get("_review_fields") or []:
        section, _, name = field.partition(".")
        value = (tpl.get(section) or {}).get(name)
        if value is None or (isinstance(value, str) and not value.strip()):
            unanswered.append(field)
    return unanswered


# --------------------------------------------------------------- routes: API
@app.route("/api/papers")
@_state_locked
def api_papers():
    return jsonify(_list_papers())


@app.route("/api/schema")
def api_schema():
    return jsonify(SCHEMA)


@app.route("/api/paper/<key>")
@_state_locked
def api_paper(key):
    phase, p = _template_path(key)
    if not p:
        abort(404)
    st = _ensure_state(key, p)
    tpl = json.load(open(p, encoding="utf-8"))
    tpl.pop("_ai", None)                               # never trust template-borne AI keys
    tpl.pop("_blind", None)
    tpl["_state"] = st["state"]
    tpl["_saved_at"] = tpl.get("saved_at")
    if st["state"] in ("committed", "revealed", "finalised"):
        tpl["_ai"] = _ai_values(p)
        bp = _side(p, "blind.json")
        tpl["_blind"] = json.load(open(bp, encoding="utf-8")) if bp.exists() else None
        if st["state"] == "committed":                 # first post-commit fetch = reveal
            st["state"] = "revealed"
            st["revealed_at"] = _now()
            _save_state(p, st)
            tpl["_state"] = "revealed"
    return jsonify(tpl)


@app.route("/api/ai/<key>")
@_state_locked
def api_ai(key):
    phase, p = _template_path(key)
    if not p:
        abort(404)
    st = _ensure_state(key, p)
    if st["state"] == "blind":
        st.setdefault("blind_access_denials", []).append(_now())
        _save_state(p, st)
        print(f"  BLIND-INTEGRITY: refused pre-commit AI fetch for {key}")
        return jsonify({"error": "model outputs are withheld until you commit your "
                                 "blind answers (§3-Step-5)"}), 403
    return jsonify(_ai_values(p))


@app.route("/api/commit/<key>", methods=["POST"])
@_state_locked
def api_commit(key):
    phase, p = _template_path(key)
    if not p:
        abort(404)
    st = _ensure_state(key, p)
    if st["state"] != "blind":
        return jsonify({"error": f"already {st['state']}"}), 409
    tpl = json.load(open(p, encoding="utf-8"))
    if (tpl.get("eligibility") or {}).get("methodological_eligibility") is None:
        return jsonify({"error": "cannot commit: methodological_eligibility is unanswered"}), 400
    unanswered = _unanswered_review_fields(tpl)
    if unanswered:
        return jsonify({"error": "cannot commit: assigned review fields are unanswered: "
                                 + ", ".join(unanswered)}), 400
    evidence_issues = _review_evidence_errors(tpl, require_complete=True)
    if evidence_issues:
        return jsonify({"error": "cannot commit: invalid/missing human evidence: "
                                 + "; ".join(evidence_issues)}), 400
    blind = {"key": key, "committed_at": _now(),
             **{b: tpl.get(b) for b in BLOCKS},
             "reviewer_notes": tpl.get("reviewer_notes", ""),
             "reviewer_evidence": tpl.get("reviewer_evidence", {}),
             "review_fields": tpl.get("_review_fields", []),
             "_done": bool(tpl.get("_done"))}
    _atomic_write(_side(p, "blind.json"), blind)
    st["state"] = "committed"
    st["committed_at"] = blind["committed_at"]
    _save_state(p, st)
    return jsonify({"ok": True, "key": key, "state": "committed",
                    "ai": _ai_values(p), "blind": blind})


@app.route("/api/finalise/<key>", methods=["POST"])
@_state_locked
def api_finalise(key):
    phase, p = _template_path(key)
    if not p:
        abort(404)
    st = _ensure_state(key, p)
    if st["state"] not in ("committed", "revealed"):
        return jsonify({"error": "commit blind answers before finalising"}), 409
    tpl = json.load(open(p, encoding="utf-8"))
    if tpl.get("_done") is not True:
        return jsonify({"error": "save with mark done enabled before finalising"}), 409
    evidence_issues = _review_evidence_errors(tpl, require_complete=True)
    if evidence_issues:
        return jsonify({"error": "invalid/missing human evidence: "
                                 + "; ".join(evidence_issues)}), 409
    st["state"] = "finalised"
    st["finalised_at"] = _now()
    _save_state(p, st)
    return jsonify({"ok": True, "key": key, "state": "finalised"})


@app.route("/api/save/<key>", methods=["POST"])
@_state_locked
def api_save(key):
    phase, p = _template_path(key)
    if not p:
        abort(404)
    st = _ensure_state(key, p)
    if st["state"] == "finalised":
        return jsonify({"error": "paper is finalised; edits are locked"}), 409
    incoming = request.get_json(force=True)
    err = _validate(incoming)
    if err:
        return jsonify(err), 400
    tpl = json.load(open(p, encoding="utf-8"))
    old = {b: dict(tpl.get(b) or {}) for b in BLOCKS}
    # only the three data blocks + notes + done flag are writable from the UI
    for block in BLOCKS:
        if block in incoming:
            tpl.setdefault(block, {}).update(incoming[block])
    tpl["reviewer_notes"] = incoming.get("reviewer_notes", tpl.get("reviewer_notes", ""))
    old_evidence = dict(tpl.get("reviewer_evidence") or {})
    if "reviewer_evidence" in incoming:
        tpl["reviewer_evidence"] = incoming["reviewer_evidence"]
    tpl["_done"] = bool(incoming.get("_done", tpl.get("_done", False)))
    if tpl["_done"] and (tpl.get("eligibility") or {}).get("methodological_eligibility") is None:
        return jsonify({"error": "cannot mark done: methodological_eligibility is unanswered"}), 400
    evidence_issues = _review_evidence_errors(tpl, require_complete=tpl["_done"])
    if evidence_issues:
        return jsonify({"error": "invalid/missing human evidence: "
                                 + "; ".join(evidence_issues)}), 400
    if st["state"] in ("committed", "revealed"):       # §3 reveal-change log
        bp = _side(p, "blind.json")
        anchor = json.load(open(bp, encoding="utf-8")) if bp.exists() else {}
        ts = _now()
        rows = [{"field": f"{b}.{name}",
                 "blind_value": (anchor.get(b) or {}).get(name),
                 "new_value": v, "ts": ts}
                for b in BLOCKS if b in incoming
                for name, v in incoming[b].items() if v != old[b].get(name)]
        rows += [
            {"field": field + ".reviewer_evidence",
             "blind_value": (anchor.get("reviewer_evidence") or {}).get(field),
             "new_value": item, "ts": ts}
            for field, item in (incoming.get("reviewer_evidence") or {}).items()
            if item != old_evidence.get(field)
        ]
        if rows:
            with open(_side(p, "reveal_changes.jsonl"), "a", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    if p.exists():
        _backup(p, key)
    saved_at = _now()
    tpl["saved_at"] = saved_at
    _atomic_write(p, tpl)
    return jsonify({"ok": True, "key": key, "done": tpl["_done"],
                    "state": st["state"], "saved_at": saved_at})


@app.route("/pdf/<key>")
def pdf(key):
    if not PAPER_KEY.fullmatch(key):
        abort(404)
    b_path = CANONICAL_ROOT / "output" / "stage0" / f"{key}.json"
    if not b_path.is_file():
        abort(404)
    bundle = json.load(open(b_path, encoding="utf-8"))
    rel = bundle.get("pdf", {}).get("path")
    if not rel:
        abort(404)
    full = (CANONICAL_ROOT / rel).resolve(strict=False)
    if is_prohibited(full) or not _within(full, CANONICAL_ROOT) or not full.is_file():
        abort(404)
    return send_file(full, mimetype="application/pdf")


@app.route("/")
def index():
    return send_file(HERE / "index.html")


@app.route("/app.js")
def appjs():
    return send_file(HERE / "app.js", mimetype="application/javascript")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-root", type=Path, default=CANONICAL_ROOT)
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    args = parser.parse_args()
    configure(data_root=args.data_root, canonical_root=args.canonical_root)
    print("C-2.3 extraction tool  ->  http://127.0.0.1:5051")
    for phase, d in _phase_dirs():
        print(f"  {phase}: {d}")
    app.run(host="127.0.0.1", port=5051, debug=False)
