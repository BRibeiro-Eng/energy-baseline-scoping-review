#!/usr/bin/env python3
"""Runner regression suite — the failure modes that silently abort a 42-paper pass.

Run from the repo root:  /usr/local/bin/python3 stage_c/test_runner.py
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT + "/output")
import stage_c_run as R                                              # noqa: E402

KEY = sorted(os.path.basename(p)[:-5] for p in
             __import__("glob").glob("output/stage0/rayyan-*.json"))[0]
fails = []


def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (("  | " + str(detail)[:170]) if not ok else ""))
    if not ok:
        fails.append(name)


def run_with(fake, **kw):
    """Run one paper with subprocess.run replaced, in throwaway directories."""
    real = R.subprocess.run
    R.subprocess.run = fake
    try:
        with tempfile.TemporaryDirectory() as td:
            wd, od = td + "/work", td + "/out"
            os.makedirs(wd); os.makedirs(od)
            try:
                out = (None, R.run_paper(KEY, "_test", wd, od))
            except BaseException as exc:                            # noqa: BLE001
                out = (exc, None)
            return out + (sorted(os.listdir(wd)),)
    finally:
        R.subprocess.run = real


# -------------------------------------------------------- (3) timeout -> quarantine
# subprocess.run sat OUTSIDE the try that caught TimeoutExpired, so a 900 s hang raised
# out of run_paper as a bare TimeoutExpired. The main loop catches Exhausted (quarantine,
# continue) and Availability (abort cleanly); anything else ABORTS the whole pass and
# cancels the remaining papers. One slow paper killed the other 41.
def timeout_run(*a, **k):
    raise subprocess.TimeoutExpired(cmd="claude", timeout=900)


exc, _, files = run_with(timeout_run)
check("a CLI timeout raises Exhausted (quarantine), not TimeoutExpired (abort)",
      isinstance(exc, R.Exhausted), f"{type(exc).__name__}: {exc}")
check("the timeout is recorded in the attempt metadata on disk",
      isinstance(exc, R.Exhausted) and "timeout" in exc.detail
      and any(f.endswith(".metadata.json") for f in files), (getattr(exc, "detail", exc), files))


# -------------------------------------------------------- availability still aborts
class Res:
    def __init__(self, out, rc=0, err=""):
        self.stdout, self.returncode, self.stderr = out, rc, err


def quota_run(*a, **k):
    return Res(json.dumps({"is_error": True,
                           "result": "You've hit your session limit. Try again later."}), rc=1)


exc, _, _ = run_with(quota_run)
check("a session-limit envelope raises Availability, not Exhausted",
      isinstance(exc, R.Availability), f"{type(exc).__name__}: {exc}")


# a validation error whose TEXT contains an availability word must NOT abort the pass:
# an emissions corpus quotes the word 'quota' in its own sentences.
def quota_word_in_payload(*a, **k):
    return Res(json.dumps({"is_error": False, "modelUsage": {"m": 1},
                           "structured_output": {"paper_key": KEY,
                                                 "note": "the EU emissions quota was exceeded"}}))


exc, _, _ = run_with(quota_word_in_payload)
check("the word 'quota' inside the PAYLOAD does not abort the pass",
      isinstance(exc, R.Exhausted), f"{type(exc).__name__}: {exc}")

# a missing model identifier is a provenance failure, not a valid record
def no_model_id(*a, **k):
    return Res(json.dumps({"is_error": False, "modelUsage": {},
                           "structured_output": {"paper_key": KEY}}))


exc, _, _ = run_with(no_model_id)
check("a CLI envelope with no model identifier is never accepted",
      isinstance(exc, R.Exhausted) and "model identifier" in exc.detail,
      getattr(exc, "detail", exc))

# ------------------- 2026-09-12 adversarial audit: the prologue escapes
# Everything before the first try -- bundle load, existing-record load, validate() -- raised
# its own exception type out of run_paper. main() re-raises anything that is not Exhausted or
# Availability, so one unreadable file aborted the remaining 41 papers. A digest mismatch was
# worse: SystemExit is a BaseException and was matched by no handler at all.
def nofile(*a, **k):
    raise AssertionError("subprocess must not be reached")


def with_paths(stage0=None, existing=None, fake=nofile):
    real = R.subprocess.run
    R.subprocess.run = fake
    try:
        with tempfile.TemporaryDirectory() as td:
            wd, od = td + "/work", td + "/out"
            os.makedirs(wd); os.makedirs(od)
            if existing is not None:
                open(f"{od}/{KEY}.json", "w", encoding="utf-8").write(existing)
            key = stage0 if stage0 is not None else KEY
            try:
                return None, R.run_paper(key, "_test", wd, od)
            except BaseException as exc:                                # noqa: BLE001
                return exc, None
    finally:
        R.subprocess.run = real


exc, _ = with_paths(stage0="rayyan-000000000")
check("a missing bundle quarantines one paper, it does not abort the pass",
      isinstance(exc, R.Exhausted) and "bundle unreadable" in exc.detail,
      f"{type(exc).__name__}: {exc}")

exc, _ = with_paths(existing="{ not json")
check("a half-written existing record quarantines, it does not abort",
      isinstance(exc, R.Exhausted) and "unreadable" in exc.detail,
      f"{type(exc).__name__}: {exc}")

exc, _ = with_paths(existing='[{"paper_key": "x"}]')
check("an existing record of the wrong JSON shape quarantines",
      isinstance(exc, R.Exhausted), f"{type(exc).__name__}: {exc}")

exc, _ = with_paths(existing=json.dumps({"paper_key": KEY, "applications": [],
                                         "mechanisms": [{"evidence_quote": 7}]}))
check("a non-string quote in an existing record quarantines",
      isinstance(exc, R.Exhausted), f"{type(exc).__name__}: {exc}")


# a digest mismatch is GLOBAL: it must stop the pass, but as a handled Abort, never as a
# SystemExit escaping a worker thread
def digest_mismatch(*a, **k):
    raise SystemExit("SCHEMA DIGEST MISMATCH\n  declared aaa\n  actual bbb")


real_validate = R.validate
R.validate = digest_mismatch
try:
    exc, _ = with_paths(existing=json.dumps({"paper_key": KEY}))
finally:
    R.validate = real_validate
check("a digest mismatch raises Abort, not SystemExit",
      isinstance(exc, R.Abort) and not isinstance(exc, SystemExit),
      f"{type(exc).__name__}: {exc}")
check("Abort is an Exception, so a handler can catch it",
      issubclass(R.Abort, Exception) and not issubclass(R.Abort, R.Exhausted))

# a stray work file with no attempt number raised ValueError out of the prologue
def one_shot(*a, **k):
    raise subprocess.TimeoutExpired(cmd="claude", timeout=1)


real = R.subprocess.run
R.subprocess.run = one_shot
try:
    with tempfile.TemporaryDirectory() as td:
        wd, od = td + "/work", td + "/out"
        os.makedirs(wd); os.makedirs(od)
        open(f"{wd}/{KEY}.attempt-.raw.json", "w").write("{}")
        try:
            R.run_paper(KEY, "_test", wd, od)
            exc = None
        except BaseException as e:                                      # noqa: BLE001
            exc = e
finally:
    R.subprocess.run = real
check("a stray work file with no attempt number does not abort the pass",
      isinstance(exc, R.Exhausted), f"{type(exc).__name__}: {exc}")

print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILURES: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
