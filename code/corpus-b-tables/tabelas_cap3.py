#!/usr/bin/env python3
"""Números e tabelas do Cap. 3 (§3.4) a partir dos registos Stage C. Nível V0.
Escreve tabelas_cap3_<date>.json e corpus_b_<date>.bib (entradas BibTeX dos artigos de B, de data/articles.csv).
"""
import argparse, collections, csv, glob, json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
V = lambda e: e.get("value") if isinstance(e, dict) and "value" in e else e
CLOSE = {"refinery — model empirically applied there", "petrochemical — model empirically applied there"}


def ascii_(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--date", required=True); ap.add_argument("--decisoes"); a = ap.parse_args()
    recs = {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(f"{ROOT}/production/stage_c/claude/outputs/rayyan-*.json"))}
    T0 = {}
    if a.decisoes:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "verification_v1"))
        from overlay import effective
        recs, T0["verificacao_estados"] = effective(recs, a.decisoes)
    arts = {}
    with open(f"{ROOT}/data/articles.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            k = r["key"] if r["key"].startswith("rayyan-") else f"rayyan-{r['key']}"
            if k in recs:
                arts[k] = r
    # bib keys
    base = {}
    for k, r in sorted(arts.items(), key=lambda x: (x[1]["year"], x[0])):
        sur = re.sub(r"[^A-Za-z]", "", ascii_(r["authors"].split(",")[0]))
        base.setdefault(f"{sur}{r['year']}", []).append(k)
    bibkey = {}
    for b, ks in base.items():
        for i, k in enumerate(ks):
            bibkey[k] = b + ("abcdef"[i] if len(ks) > 1 else "")
    bib = []
    for k, r in arts.items():
        auth = re.sub(r"\s+and\s*$", "", r["authors"].strip())
        auth = auth + " and others" if r["authors"].strip().endswith("and") else auth
        conf = re.search(r"conference|proceedings|summit|symposium|congress|workshop", r["journal"], re.I)
        f = {"author": auth, "title": "{" + r["title"] + "}", "year": r["year"], "doi": r["doi"],
             ("booktitle" if conf else "journal"): r["journal"], "volume": r["volume"], "number": r["issue"],
             "pages": r["pages"].replace("-", "--") if r["pages"] else ""}
        body = ",\n".join(f"  {x} = {{{y}}}" for x, y in f.items() if y)
        bib.append(f"@{'inproceedings' if conf else 'article'}{{{bibkey[k]},\n{body},\n  note = {{Corpus B, {k}}}\n}}")
    open(f"{HERE}/corpus_b_{a.date}.bib", "w", encoding="utf-8").write("\n\n".join(bib) + "\n")

    T = {"bibkey": bibkey, "n_papers": len(recs), **T0}
    apps = [(k, x) for k, r in recs.items() for x in r["applications"]]
    models = [(k, x, m) for k, x in apps for m in x["models"]]
    T["n_apps"], T["n_models"] = len(apps), len(models)
    # composition by sector
    comp = collections.defaultdict(lambda: {"apps": 0, "papers": set(), "close_apps": 0})
    for k, x in apps:
        s = V(x["sector_registered"]); c = comp[s]; c["apps"] += 1; c["papers"].add(k)
        c["close_apps"] += V(x["refinery_or_petrochemical_case"]) in CLOSE
    T["composition"] = {s: {"apps": c["apps"], "papers": len(c["papers"]), "close_apps": c["close_apps"]} for s, c in comp.items()}
    T["scale"] = dict(collections.Counter(V(x["scale_of_application"]) for _, x in apps))
    T["context"] = dict(collections.Counter(V(x["refinery_or_petrochemical_case"]) for _, x in apps))
    T["close_papers"] = sorted({k for k, x in apps if V(x["refinery_or_petrochemical_case"]) in CLOSE})
    # family
    fam = collections.defaultdict(lambda: [0, set()])
    for k, _, m in models:
        for f in V(m["C2_model_form"]["model_family"]) or []:
            fam[f][0] += 1; fam[f][1].add(k)
    T["family"] = {f: [n, len(p)] for f, (n, p) in sorted(fam.items(), key=lambda x: -x[1][0])}
    T["quantity"] = dict(collections.Counter(V(m["C1_dependent_variable"]["quantity"]) for _, _, m in models))
    vt = collections.defaultdict(lambda: [0, set()])
    for k, _, m in models:
        for v in m.get("C3_variables") or []:
            vt[v["type"]][0] += 1; vt[v["type"]][1].add(k)
    T["var_type"] = {t: [n, len(p)] for t, (n, p) in sorted(vt.items(), key=lambda x: -x[1][0])}
    # models whose only non-denominator predictors are throughput
    only_tp = 0
    for k, _, m in models:
        types = {v["type"] for v in m.get("C3_variables") or [] if v["role"] in ("predictor", "denominator")}
        only_tp += bool(types) and types <= {"throughput"}
    T["models_only_throughput"] = only_tp
    # mechanisms
    mechs = [(k, x) for k, r in recs.items() for x in r["mechanisms"]]
    eff = collections.defaultdict(lambda: {"all": [0, set()], "general": [0, set()], "applied to the case": [0, set()], "empirically demonstrated": [0, set()], "nongeneral": [0, set()]})
    for k, x in mechs:
        e = eff[x["mechanism_effect_on_model"]]
        for col in ("all", x["claim_status"]) + (("nongeneral",) if x["claim_status"] != "general" else ()):
            e[col][0] += 1; e[col][1].add(k)
    T["effects"] = {ef: {c: [n, len(p)] for c, (n, p) in d.items()} for ef, d in sorted(eff.items(), key=lambda x: -x[1]["all"][0])}
    T["claim"] = {c: [sum(1 for _, x in mechs if x["claim_status"] == c), len({k for k, x in mechs if x["claim_status"] == c})] for c in ("general", "applied to the case", "empirically demonstrated")}
    T["mech_papers"] = len({k for k, _ in mechs}); T["n_mechs"] = len(mechs)
    T["cause"] = {c: [n, len({k for k, x in mechs if x["mechanism_cause"] == c})] for c, n in collections.Counter(x["mechanism_cause"] for _, x in mechs).most_common()}
    T["support_inference"] = [sum(1 for _, x in mechs if x["support_class"] == "requires inference"), len({k for k, x in mechs if x["support_class"] == "requires inference"})]
    # adaptations
    adps = [(k, x) for k, r in recs.items() for x in r["adaptations"]]
    ad = collections.defaultdict(lambda: collections.Counter())
    adp_pap = collections.defaultdict(set)
    for k, x in adps:
        t = ad[x["adaptation"]]; t["n"] += 1; t[x["status"]] += 1; t[x["normative_framing"]] += 1; t["linked"] += bool(x["addresses_mechanism"]); adp_pap[x["adaptation"]].add(k)
    T["adaptations"] = {t: dict(c, papers=len(adp_pap[t])) for t, c in sorted(ad.items(), key=lambda x: -x[1]["n"])}
    T["n_adps"], T["adp_papers"] = len(adps), len({k for k, _ in adps})
    # 13 closest
    rows = []
    for k in T["close_papers"]:
        r = recs[k]; ms = [m for x in r["applications"] for m in x["models"]]
        bc = collections.Counter(c["boundary_correspondence"] for m in ms for c in m.get("C5_measurement") or [])
        rows.append({"key": k, "bib": bibkey[k], "year": arts[k]["year"], "author": arts[k]["authors"].split(",")[0],
                     "sector": sorted({V(x["sector_registered"]) for x in r["applications"]}),
                     "scale": sorted({V(x["scale_of_application"]) for x in r["applications"]}),
                     "n_models": len(ms), "families": sorted({f for m in ms for f in V(m["C2_model_form"]["model_family"]) or []}),
                     "data": sorted({V(m["C4_data"].get("data_type")) or "?" for m in ms}),
                     "var_types": sorted({v["type"] for m in ms for v in m.get("C3_variables") or [] if v["role"] != "excluded"}),
                     "boundary": dict(bc), "regime": sorted({V(m["C6_re_estimation"]["regime"]) for m in ms}),
                     "envelope": sorted({V(m["C7_validity_envelope"]["statement"]) for m in ms}),
                     "oos": sorted({V(m["C8_metrics"]["out_of_sample_validation"]["status"]) for m in ms}),
                     "ins": sorted({V(m["C8_metrics"]["in_sample_fit"]["status"]) for m in ms}),
                     "mechs": len(r["mechanisms"]), "adps": len(r["adaptations"]),
                     "title": arts[k]["title"]})
    T["close13"] = rows
    # C5-C8, C13
    c5 = [c for _, _, m in models for c in m.get("C5_measurement") or []]
    T["c5_boundary"] = dict(collections.Counter(c["boundary_correspondence"] for c in c5)); T["c5_origin"] = dict(collections.Counter(c["data_origin"] for c in c5)); T["n_c5"] = len(c5)
    pm = lambda f: {v: [n, len({k for k, _, m in models if f(m) == v})] for v, n in collections.Counter(f(m) for _, _, m in models).items()}
    T["c6_regime"] = pm(lambda m: V(m["C6_re_estimation"]["regime"])); T["c6_update"] = pm(lambda m: V(m["C6_re_estimation"]["update_status"]))
    T["c7"] = pm(lambda m: V(m["C7_validity_envelope"]["statement"]))
    T["c8_oos"] = pm(lambda m: V(m["C8_metrics"]["out_of_sample_validation"]["status"])); T["c8_ins"] = pm(lambda m: V(m["C8_metrics"]["in_sample_fit"]["status"]))
    T["c8_design"] = pm(lambda m: V(m["C8_metrics"]["out_of_sample_validation"]["validation_design"]))
    T["c13"] = {f: dict(collections.Counter(V(r["C13_reproducibility"][f]) for r in recs.values())) for f in ("equations_given", "coefficients_given", "data_available", "code_available")}
    lim = [x for r in recs.values() for x in r["study_limitations"]]; bar = [(k, x) for k, r in recs.items() for x in r["implementation_barriers"]]
    T["limitations"] = [dict(collections.Counter(x["limitation"] for x in lim)), len(lim), len({k for k, r in recs.items() if r["study_limitations"]})]
    T["barriers"] = [len(bar), len({k for k, _ in bar})]
    T["span_months"] = sorted(V(m["C4_data"].get("span_months")) for _, _, m in models if isinstance(V(m["C4_data"].get("span_months")), (int, float)))
    json.dump(T, open(f"{HERE}/tabelas_cap3_{a.date}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
    print(json.dumps({k: v for k, v in T.items() if k not in ("bibkey", "close13", "span_months")}, ensure_ascii=False, indent=0, default=list)[:9000])
    for r in rows:
        print(r["bib"], r["sector"], r["scale"], r["n_models"], r["families"], r["data"], r["var_types"], r["boundary"], r["regime"], r["envelope"], r["oos"], r["mechs"], r["adps"])


if __name__ == "__main__":
    main()
