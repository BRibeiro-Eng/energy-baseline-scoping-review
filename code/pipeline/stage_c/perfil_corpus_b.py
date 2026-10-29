#!/usr/bin/env python3
"""Perfil quantitativo do Corpus B a partir dos registos Stage C (production/stage_c/claude/outputs).

  python3 stage_c/perfil_corpus_b.py --date 2026-09-17   ->  stage_c/PERFIL_CORPUS_B_<date>.md

Nível V0: leitura única do extractor, citações ancoradas por script, sem verificação humana por
ocorrência. Substitui o gerador ad hoc que produziu PERFIL_CORPUS_B_2026-09-16.md (41 registos).
Desde 2026-09-17 só estão em outputs/ os registos de B ∩ A (ver stage_c/B_SUBSET_A_2026-09-17.md).
"""
import argparse, collections, csv, glob, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REC = f"{ROOT}/production/stage_c/claude/outputs"


def V(e):
    return e.get("value") if isinstance(e, dict) and "value" in e else e


def G(o, *path):
    for p in path:
        if not isinstance(o, dict) or p not in o:
            return "(sem campo)"
        o = o[p]
    return V(o)


def cnt(pairs):
    """pairs: iterable of (value, paper_key) -> '{value} occ·papers' sorted desc."""
    occ, pap = collections.Counter(), collections.defaultdict(set)
    for v, k in pairs:
        v = "(vazio)" if v in (None, "") else str(v)
        occ[v] += 1; pap[v].add(k)
    return occ, pap


def line(title, pairs, unit="modelos · papers"):
    occ, pap = cnt(pairs)
    return f"**{title}** ({unit}): " + "; ".join(f"{v} {n}·{len(pap[v])}" for v, n in occ.most_common())


def simple(title, values):
    c = collections.Counter("(vazio)" if v in (None, "") else str(v) for v in values)
    return f"**{title}:** " + "; ".join(f"{v} {n}" for v, n in c.most_common())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    meta = {}
    with open(f"{ROOT}/data/articles.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            k = r["key"] if r["key"].startswith("rayyan-") else f"rayyan-{r['key']}"
            meta[k] = {"year": r.get("year") or "", "author": (r.get("authors") or "?").split(";")[0].split(",")[0].strip(),
                       "title": r.get("title") or ""}
    recs = {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(f"{REC}/rayyan-*.json"))}
    N = len(recs)
    apps = [(k, ap_) for k, r in recs.items() for ap_ in r["applications"]]
    models = [(k, ap_, m) for k, ap_ in apps for m in ap_["models"]]
    mechs = [(k, x) for k, r in recs.items() for x in r["mechanisms"]]
    adps = [(k, x) for k, r in recs.items() for x in r["adaptations"]]
    out = [f"# Perfil do Corpus B — {N} registos Stage C (leitura do extractor, citações ancoradas, sem verificação humana por ocorrência)", "",
           f"Gerado {a.date} por `stage_c/perfil_corpus_b.py` a partir de `production/stage_c/claude/outputs/`. "
           f"Denominadores: papers = {N}; applications = {len(apps)}; modelos = {len(models)}; mecanismos = {len(mechs)}; adaptações = {len(adps)}. "
           "'(sem campo)' = o extractor não preencheu o campo. Registos de B∖A fora desde 2026-09-17 (`stage_c/B_SUBSET_A_2026-09-17.md`).", ""]
    short = {"refinery — model empirically applied there": "refinery*", "petrochemical — model empirically applied there": "petrochemical*",
             "no": ""}
    # 1
    out += [f"## 1. Os {N} papers", "", "| key | ano | 1.º autor | sector(es) | escala | refinaria/petroq. | modelos | famílias | mecan. | adapt. |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in recs.items():
        ms = [m for ap_ in r["applications"] for m in ap_["models"]]
        fam = collections.Counter(f for m in ms for f in (G(m, "C2_model_form", "model_family") or []))
        ctx = sorted({short.get(G(x, "refinery_or_petrochemical_case"), G(x, "refinery_or_petrochemical_case")) for x in r["applications"]} - {""})
        out.append(f"| {k[7:]} | {meta.get(k, {}).get('year', '')} | {meta.get(k, {}).get('author', '?')} | "
                   f"{'; '.join(G(x, 'sector_registered') for x in r['applications'])} | {'; '.join(G(x, 'scale_of_application') for x in r['applications'])} | "
                   f"{'; '.join(ctx)} | {len(ms)} | {', '.join(f'{f} ({n})' for f, n in fam.most_common())} | {len(r['mechanisms'])} | {len(r['adaptations'])} |")
    out += ["", "\\* = modelo aplicado empiricamente nesse contexto.", ""]
    # 2
    out += ["## 2. Sector, escala, contexto", "", f"Applications: {len(apps)} em {N} papers.", "",
            simple("Sector registado (applications)", [G(x, "sector_registered") for _, x in apps]), "",
            simple("Escala (applications)", [G(x, "scale_of_application") for _, x in apps]), "",
            simple("Caso refinaria/petroquímica (applications)", [G(x, "refinery_or_petrochemical_case") for _, x in apps]), "",
            simple("País/região (applications)", [G(x, "country_region") for _, x in apps]), "",
            "**Ano (papers):** " + "; ".join(f"{y} {n}" for y, n in sorted(collections.Counter(meta.get(k, {}).get("year", "") for k in recs).items())), ""]
    # 3
    M = lambda *path: [(G(m, *path), k) for k, _, m in models]
    ML = lambda *path: [(v, k) for k, _, m in models for v in (G(m, *path) if isinstance(G(m, *path), list) else [G(m, *path)])]
    out += [f"## 3. Os modelos (n = {len(models)} modelos em {N} papers)", "",
            line("Família do modelo", ML("C2_model_form", "model_family")), "",
            line("Variável dependente", M("C1_dependent_variable", "quantity")), "",
            line("Denominador", M("C1_dependent_variable", "denominator")), "",
            line("Vector energético", ML("C1_dependent_variable", "energy_vector")), "",
            line("Método de estimação", M("C2_model_form", "estimation_method")), "",
            line("Selecção de variáveis", M("C2_model_form", "variable_selection")), "",
            line("Tipo de dados", M("C4_data", "data_type")), "",
            line("Frequência de aquisição", M("C4_data", "acquisition_frequency")), "",
            line("Frequência de modelação", M("C4_data", "modelling_frequency")), "",
            line("Regime de re-estimação (C6)", M("C6_re_estimation", "regime")), "",
            line("Estado da actualização (C6)", M("C6_re_estimation", "update_status")), "",
            line("Domínio de validade (C7)", M("C7_validity_envelope", "statement")), "",
            line("Ajuste in-sample (C8)", M("C8_metrics", "in_sample_fit", "status")), "",
            line("Validação out-of-sample (C8)", M("C8_metrics", "out_of_sample_validation", "status")), "",
            line("Desenho de validação (C8)", M("C8_metrics", "out_of_sample_validation", "validation_design")), "",
            line("Resultado energético (C8)", M("C8_metrics", "energy_result", "status")), "",
            line("Método de construção da baseline (campo livre, presença)",
                 [("preenchido" if G(m, "baseline_construction_method") not in (None, "", "(sem campo)") else "vazio", k) for k, _, m in models]), ""]
    for lab, path in (("Duração em meses", ("C4_data", "span_months")), ("N observações", ("C4_data", "n_observations"))):
        vals = [G(m, *path) for _, _, m in models]
        vals = [v for v in vals if isinstance(v, (int, float))]
        if vals:
            out += [f"**{lab} (modelos com valor):** n={len(vals)}, mediana {statistics.median(vals):g}, min {min(vals):g}, max {max(vals):g}", ""]
    c3 = [(v, k) for k, _, m in models for v in m.get("C3_variables") or []]
    out += [line("Variáveis (C3) por tipo", [(v["type"], k) for v, k in c3], "ocorrências · papers"), "",
            simple("Variáveis (C3) por papel", [v["role"] for v, _ in c3]), "",
            simple("Variáveis (C3) tipo × papel", [f"{v['type']}/{v['role']}" for v, _ in c3]), ""]
    c5 = [(c, k) for k, _, m in models for c in m.get("C5_measurement") or []]
    out += [f"C5: {len(c5)} entradas.", "", simple("Medição (C5) origem", [c["data_origin"] for c, _ in c5]), "",
            simple("Medição (C5) correspondência de fronteira", [c["boundary_correspondence"] for c, _ in c5]), ""]
    # 4
    papers_m = {k for k, _ in mechs}
    ng = [(k, x) for k, x in mechs if x["claim_status"] != "general"]
    ed = [(k, x) for k, x in mechs if x["claim_status"] == "empirically demonstrated"]
    out += [f"## 4. Mecanismos (SQ2) — {len(mechs)} ocorrências em {len(papers_m)} papers ({N - len(papers_m)} papers sem nenhum)", "",
            line("claim_status", [(x["claim_status"], k) for k, x in mechs], "ocorrências · papers"), "",
            line("support_class", [(x["support_class"], k) for k, x in mechs], "ocorrências · papers"), "",
            line("refers_to (modelo ou argumento de paper)", [("paper-level" if x["refers_to"] == "paper-level argument" else "modelo", k) for k, x in mechs], "ocorrências · papers"), "",
            line("Efeito no modelo — todas", [(x["mechanism_effect_on_model"], k) for k, x in mechs], "ocorrências · papers"), "",
            line("Efeito no modelo — excluindo general", [(x["mechanism_effect_on_model"], k) for k, x in ng], "ocorrências · papers"), "",
            line("Efeito no modelo — só empirically demonstrated", [(x["mechanism_effect_on_model"], k) for k, x in ed], "ocorrências · papers"), "",
            line("Causa — todas", [(x["mechanism_cause"], k) for k, x in mechs], "ocorrências · papers"), "",
            line("Causa — excluindo general", [(x["mechanism_cause"], k) for k, x in ng], "ocorrências · papers"), "",
            line("Causa × claim_status", [(f"{x['mechanism_cause']} / {x['claim_status']}", k) for k, x in mechs], "ocorrências · papers"), "",
            "**Cruzamento efeito × causa (ocorrências não-general, causa ≠ not stated):**", ""]
    for v, n in collections.Counter(f"{x['mechanism_effect_on_model']} ← {x['mechanism_cause']}" for _, x in ng if x["mechanism_cause"] != "not stated").most_common():
        out.append(f"- {v}: {n}")
    out += ["", "**Efeito × sector (papers, ocorrências não-general):**", ""]
    sect = {k: sorted({G(x, "sector_registered") for x in r["applications"]}) for k, r in recs.items()}
    bys = collections.defaultdict(collections.Counter)
    for k, x in ng:
        for s in sect[k]:
            bys[s][x["mechanism_effect_on_model"]] += 1
    for s in sorted(bys):
        out.append(f"- {s}: " + "; ".join(f"{e} {n}" for e, n in bys[s].most_common()))
    out += ["", "**Efeitos 'other' (verbatim do extractor):**", ""]
    out += [f"- {k[7:]} [{x['claim_status']}]: {x.get('effect_other_verbatim')}" for k, x in mechs if x["mechanism_effect_on_model"] == "other"]
    out += ["", "**Causas 'other' (verbatim):**", ""]
    out += [f"- {k[7:]} [{x['claim_status']}]: {x.get('cause_other_verbatim')}" for k, x in mechs if x["mechanism_cause"] == "other"]
    out += ["", "**As poucas causas físicas nomeadas (todas as ocorrências com causa ≠ not stated/other):**", ""]
    out += [f"- {k[7:]} [{x['claim_status']}] {x['mechanism_cause']} → {x['mechanism_effect_on_model']}: «{(x['evidence_quote'] or '').replace(chr(10), ' ')[:150]}» (p.{x['page']})"
            for k, x in mechs if x["mechanism_cause"] not in ("not stated", "other")]
    # 5
    papers_a = {k for k, _ in adps}
    out += ["", f"## 5. Adaptações (SQ3) — {len(adps)} ocorrências em {len(papers_a)} papers ({N - len(papers_a)} sem nenhuma)", "",
            line("Tipo de adaptação", [(x["adaptation"], k) for k, x in adps], "ocorrências · papers"), "",
            line("Estado", [(x["status"], k) for k, x in adps], "ocorrências · papers"), "",
            line("Enquadramento normativo", [(x["normative_framing"], k) for k, x in adps], "ocorrências · papers"), "",
            line("Liga a um mecanismo (addresses_mechanism)", [("sim" if x["addresses_mechanism"] else "não", k) for k, x in adps], "ocorrências · papers"), "",
            line("Tipo × estado", [(f"{x['adaptation']} / {x['status']}", k) for k, x in adps], "ocorrências · papers"), "",
            line("Tipo × enquadramento", [(f"{x['adaptation']} / {x['normative_framing']}", k) for k, x in adps], "ocorrências · papers"), "",
            "**Adaptação → efeito do mecanismo que endereça (quando ligada):**", ""]
    mid = {(k, x["mechanism_id"]): x["mechanism_effect_on_model"] for k, x in mechs}
    for v, n in collections.Counter(f"{x['adaptation']} → {mid.get((k, x['addresses_mechanism']), '?')}" for k, x in adps if x["addresses_mechanism"]).most_common():
        out.append(f"- {v}: {n}")
    out += ["", "**Adaptações 'other' (verbatim):**", ""]
    out += [f"- {k[7:]} [{x['status']}, {x['normative_framing']}]: {x.get('adaptation_other_verbatim')}" for k, x in adps if x["adaptation"] == "other"]
    # 6
    lim = [(k, x) for k, r in recs.items() for x in r["study_limitations"]]
    bar = [(k, x) for k, r in recs.items() for x in r["implementation_barriers"]]
    out += ["", f"## 6. Limitações declaradas ({len(lim)} em {len({k for k, _ in lim})} papers) e barreiras ({len(bar)} em {len({k for k, _ in bar})} papers)", "",
            simple("Limitações por tipo", [x["limitation"] for _, x in lim]), "", "**Barreiras (verbatim curto):**", ""]
    out += [f"- {k[7:]}: {x['barrier']}" for k, x in bar]
    # 7
    out += ["", "## 7. Reprodutibilidade (C13, papers)", ""]
    for f in ("equations_given", "coefficients_given", "data_available", "code_available"):
        c = collections.Counter(V(r["C13_reproducibility"][f]) for r in recs.values())
        out.append(f"- {f}: " + "; ".join(f"{v} {n}" for v, n in c.most_common()))
    # 8
    refin = [k for k, r in recs.items() if any(G(x, "sector_registered") == "petroleum refining" for x in r["applications"])]
    out += ["", f"## 8. Os {len(refin)} papers de refinação (leitura mais fina)", ""]
    for k in refin:
        r = recs[k]
        out += [f"### {k} — {meta.get(k, {}).get('title', '')[:120]} ({meta.get(k, {}).get('year', '')})", ""]
        for x in r["applications"]:
            out.append(f"- Âmbito: {G(x, 'scope_description')}")
            for m in x["models"]:
                out.append(f"  - {m['model_id']} {m.get('label_verbatim')}: {G(m, 'C1_dependent_variable', 'quantity')} / {G(m, 'C2_model_form', 'model_family')} / "
                           f"dados {G(m, 'C4_data', 'data_type')} {G(m, 'C4_data', 'acquisition_frequency')} / re-est. {G(m, 'C6_re_estimation', 'regime')} / "
                           f"domínio {G(m, 'C7_validity_envelope', 'statement')} / OOS {G(m, 'C8_metrics', 'out_of_sample_validation', 'status')}")
        for x in r["mechanisms"]:
            out.append(f"  - mecanismo [{x['claim_status']}] {x['mechanism_effect_on_model']} ← {x['mechanism_cause']}: «{(x['evidence_quote'] or '').replace(chr(10), ' ')[:140]}» (p.{x['page']})")
        for x in r["adaptations"]:
            out.append(f"  - adaptação [{x['status']}, {x['normative_framing']}] {x['adaptation']}: «{(x['evidence_quote'] or '').replace(chr(10), ' ')[:120]}»")
        out += [f"  - notas do extractor: {(r.get('reviewer_notes') or '')[:300]}", ""]
    path = f"{HERE}/PERFIL_CORPUS_B_{a.date}.md"
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(path, N, "papers", len(apps), "applications", len(models), "modelos", len(mechs), "mecanismos", len(adps), "adaptações")


if __name__ == "__main__":
    main()
