"""Analysed state of the Corpus B records, as used in the article.

1. data/05-extraction-corpus-b/records/: the 39 charted records, as extracted.
2. The decisions of the September 2026 model verification (code/verification_v1/overlay.py).
3. The corrections of the later checks that the article applies:
   (d) the 12 values found incorrect in the random sample of 80 (data/06-late-verification, module d7b);
   (c) the omissions found by the full-text search that change a charted field (module d7a): three
       out-of-sample results and two data-availability statements; the mechanisms it found are not added;
   (f) the three values adopted from the reading of the 13 refinery reports (d7c_adoption.json).
Returns the records, the September statistics, a log of every later correction, and the five reports in
which the search found feed or product characteristics discussed but not used as variables."""
import copy, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # code/
from verification_v1.overlay import effective, _walk

def load(root):
    recs = {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8"))
            for p in sorted(glob.glob(f"{root}/data/05-extraction-corpus-b/records/rayyan-*.json"))}
    eff, stats = effective(recs, f"{root}/data/05-extraction-corpus-b/model-reread-2026-09/verifier/decisoes_2026-09-17.json")
    return eff, stats

def setv(obj_parent, key, new):
    o = obj_parent[key]
    if isinstance(o, dict) and "value" in o: o["value"] = new
    else: obj_parent[key] = new

def final_state(root):
    eff, stats = load(root)
    R = copy.deepcopy(eff); log = []
    L = f"{root}/data/06-late-verification"
    # (d) random sample of 80 values: the 12 incorrect values, corrected to the reviewer's value
    tasks = {t["id"]: t for t in json.load(open(f"{L}/tasks/d7b.json", encoding="utf-8"))["tasks"]}
    for line in open(f"{L}/responses/d7b.jsonl", encoding="utf-8"):
        x = json.loads(line); a = x["answer"]
        if a["decision"] != "incorrect": continue
        t = tasks[x["task_id"]]; rec = R[t["key"]]
        if t["type"] in ("MEC", "ADP"):
            coll, idk = ("mechanisms", "mechanism_id") if t["type"] == "MEC" else ("adaptations", "adaptation_id")
            hits = [o for o in rec[coll] if o[idk] == t["current"][idk]]
            assert len(hits) == 1, t["id"]
            obj = hits[0]
            for part in re.split(r";\s*(?=[a-z_]+:)", a["correct_value"]):
                f, v = part.split(":", 1); f, v = f.strip(), v.strip()
                old = obj.get(f); obj[f] = v
                log.append(dict(check="(d) sample of 80 values", item=t["id"], key=t["key"], path=t["path"], field=f, before=old, after=v))
        else:
            parent, key, obj = _walk(rec, t["path"])
            cur = t["current"].get("value") if isinstance(t["current"], dict) else t["current"]
            assert (obj.get("value") if isinstance(obj, dict) else obj) == cur, (t["id"], obj, cur)
            f, v = a["correct_value"].split(":", 1); v = v.strip()
            old = obj.get("value") if isinstance(obj, dict) else obj
            setv(parent, key, v)
            log.append(dict(check="(d) sample of 80 values", item=t["id"], key=t["key"], path=t["path"], field=f.strip(), before=old, after=v))
    # (c) search for omissions: omissions applied in the article
    def model(k, app, mid):
        for x in R[k]["applications"]:
            if x["application_id"] == app:
                for m in x["models"]:
                    if m["model_id"] == mid: return m
        raise KeyError((k, app, mid))
    for k, app, mid in [("rayyan-472536379", "A1", "M1"), ("rayyan-472536379", "A1", "M2"), ("rayyan-472536695", "A1", "M1")]:
        o = model(k, app, mid)["C8_metrics"]["out_of_sample_validation"]
        before = (o["status"].get("value") if isinstance(o["status"], dict) else o["status"])
        setv(o, "status", "reported")
        d0 = o.get("validation_design"); dv = d0.get("value") if isinstance(d0, dict) else d0
        if "validation_design" in o: setv(o, "validation_design", "held-out split")
        log.append(dict(check="(c) search for omissions", item="T", key=k, path=f"{app}/{mid} C8 out_of_sample_validation", field="status; validation_design", before=f"{before}; {dv}", after="reported; held-out split"))
    for k in ["rayyan-472536588", "rayyan-472536606"]:
        c = R[k]["C13_reproducibility"]["data_available"]; before = c["value"]; c["value"] = "partial"
        log.append(dict(check="(c) search for omissions", item="C", key=k, path="C13_reproducibility.data_available", field="data_available", before=before, after="partial"))
    # (f) reading of the 13 refinery reports: the three adopted values (data/06-late-verification/d7c_adoption.json)
    for x in R["rayyan-472536551"]["applications"]:
        for m in x["models"]:
            r = m["C6_re_estimation"]["regime"]; before = r["value"] if isinstance(r, dict) else r
            if before == "not stated":
                setv(m["C6_re_estimation"], "regime", "event-triggered, trigger stated")
                log.append(dict(check="(f) reading of the 13 refinery reports", item="c6", key="rayyan-472536551", path=f"{x['application_id']}/{m['model_id']} C6 regime", field="regime", before=before, after="event-triggered, trigger stated"))
    for x in R["rayyan-472536532"]["applications"]:
        for m in x["models"]:
            s = m["C7_validity_envelope"]["statement"]; before = s["value"] if isinstance(s, dict) else s
            if before == "stated qualitatively" and m["model_id"] in ("M2", "M3"):
                setv(m["C7_validity_envelope"], "statement", "stated with numeric bounds")
                log.append(dict(check="(f) reading of the 13 refinery reports", item="c7", key="rayyan-472536532", path=f"{x['application_id']}/{m['model_id']} C7 statement", field="statement", before=before, after="stated with numeric bounds"))
    for x in R["rayyan-472535351"]["applications"]:
        for m in x["models"]:
            o = m["C8_metrics"]["out_of_sample_validation"]; before = o["status"]["value"] if isinstance(o["status"], dict) else o["status"]
            if before == "reported":
                setv(o, "status", "not reported")
                log.append(dict(check="(f) reading of the 13 refinery reports", item="oos", key="rayyan-472535351", path=f"{x['application_id']}/{m['model_id']} C8 out_of_sample_validation", field="status", before=before, after="not reported"))
    feed_discussed = ["rayyan-472535480", "rayyan-472535585", "rayyan-472535794", "rayyan-472536532", "rayyan-472536606"]
    return R, stats, log, feed_discussed
