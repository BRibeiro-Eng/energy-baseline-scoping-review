#!/usr/bin/env python3
"""build_tasks.py — Emenda 3 ao TDW6C (verificação tardia).

Gera as listas de tarefas da bancada a partir dos artefactos congelados do repositório.
Só corre depois de o depósito da emenda estar registado em AMENDMENT_FILED.txt (interlock).

    python3 verificacao_2026-10/build_tasks.py            # gera tarefas/ (recusa sem interlock)
    python3 verificacao_2026-10/build_tasks.py --check    # só verifica entradas e interlock, não sorteia

Os sorteios seguem a emenda: frames ordenados, random.Random(44), sem reposição.
Escreve:
    tarefas/<modulo>.json        o que a bancada mostra (sem valores de referência nos módulos cegos)
    tarefas/_ref/<modulo>.json   valores de referência dos módulos cegos (revelados só após commit)
    tarefas/MANIFEST.json        frames, sementes, tamanhos, hashes das entradas, commit git
Só usa a biblioteca padrão.
"""
import argparse, copy, csv, glob, hashlib, json, os, random, re, subprocess, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("VT_ROOT") or HERE.parent).resolve()  # VT_ROOT só para testes
OUT = HERE / "tarefas"
SEED = 44

# ---------------------------------------------------------------- utilitários
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def jdump(obj, p):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)

def V(x):
    return x.get("value") if isinstance(x, dict) else x

def norm_title(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()

def norm_page(text):
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text or "")
    t = t.replace("­", "")
    return re.sub(r"\s+", " ", t).strip().lower()

def git_head():
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

INPUTS = {}
def use(rel):
    p = ROOT / rel
    if not p.exists():
        sys.exit(f"[erro] entrada em falta: {rel}")
    if p.is_file():
        INPUTS[rel] = sha256(p)
    return p

# ---------------------------------------------------------------- interlock
def interlock():
    f = HERE / "AMENDMENT_FILED.txt"
    if not f.exists():
        sys.exit("[interlock] AMENDMENT_FILED.txt não existe. Deposita a emenda no OSF e preenche-o (ver MANUAL.md, etapa 0).")
    txt = f.read_text(encoding="utf-8")
    kv = dict(re.findall(r"^\s*(deposited|osf_file|sha256)\s*:\s*(\S+)", txt, re.M))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", kv.get("deposited", "")):
        sys.exit("[interlock] falta 'deposited: AAAA-MM-DD'.")
    if not re.fullmatch(r"[a-z0-9]{5}", kv.get("osf_file", "")):
        sys.exit("[interlock] falta 'osf_file: xxxxx' (GUID de 5 caracteres do ficheiro no OSF).")
    if not re.fullmatch(r"[0-9a-f]{64}", kv.get("sha256", "")):
        sys.exit("[interlock] falta 'sha256: <64 hex>' do ficheiro depositado.")
    local = [p for p in (HERE / "emenda").glob("*") if p.is_file() and sha256(p) == kv["sha256"]]
    if not local:
        sys.exit("[interlock] nenhum ficheiro em verificacao_2026-10/emenda/ tem o SHA-256 registado. Põe lá a cópia exata do que depositaste.")
    return {**kv, "local_copy": local[0].name}

# ---------------------------------------------------------------- dados comuns
def articles():
    rows = list(csv.DictReader(open(use("data/articles.csv"), encoding="utf-8")))
    out = {}
    for x in rows:
        m = re.search(r'RAYYAN-INCLUSION: \{"Bernardo"=>"([A-Za-z]+)"', x.get("notes") or "")
        x["_label"] = m.group(1) if m else None
        out[x["key"]] = x
    return out

def meta(art, k):
    a = art.get(k, {})
    au = (a.get("authors") or "?").split(" and ")[0].split(";")[0].strip()
    return {"title": a.get("title"), "year": a.get("year"), "journal": a.get("journal"), "authors": a.get("authors"),
            "first_author": au, "doi": (a.get("doi") or "").strip() or None}

def stage_c_records():
    recs = {}
    for p in sorted(glob.glob(str(use("production/stage_c/claude/outputs") / "rayyan-*.json"))):
        recs[Path(p).stem] = jload(p)
        INPUTS[os.path.relpath(p, ROOT)] = sha256(p)
    return recs

def overlay_effective(recs):
    sys.path.insert(0, str(ROOT / "stage_c" / "verification_v1"))
    from overlay import effective  # noqa
    dec = use("stage_c/verification_v1/verificacao_modelo/decisoes_2026-09-17.json")
    eff, _ = effective(recs, str(dec))
    return eff

def pages_of(k):
    p = use(f"output/stage0/{k}.json")
    return jload(p)["pdf"]["pages"]

# ---------------------------------------------------------------- D13
def build_d13(art):
    sys.path.insert(0, str(ROOT / "output"))
    import fn_hunt  # noqa
    INPUTS["output/fn_hunt.py"] = sha256(ROOT / "output" / "fn_hunt.py")
    excl = sorted(k for k, a in art.items() if a["_label"] == "Excluded")
    # abstracts: export Rayyan novo (se existir) > OpenAlex (pré-carregado) > nenhum
    abstracts = {}
    oa = HERE / "dados" / "abstracts_openalex_excluded.json"
    if oa.exists():
        INPUTS[os.path.relpath(oa, ROOT)] = sha256(oa)
        for k, v in jload(oa).items():
            if v.get("abstract"):
                abstracts[k] = (v["abstract"], v.get("source") or "openalex")
    ray = sorted((HERE / "dados").glob("rayyan_export*.csv"))
    if ray:
        INPUTS[os.path.relpath(ray[-1], ROOT)] = sha256(ray[-1])
        by_title = {}
        for r in csv.DictReader(open(ray[-1], encoding="utf-8-sig")):
            ab = (r.get("abstract") or r.get("Abstract") or "").strip()
            if not ab:
                continue
            key = (r.get("key") or "").strip()
            if key and not key.startswith("rayyan-"):
                key = f"rayyan-{key}"
            if key in art:
                abstracts[key] = (ab, "rayyan_export")
            else:
                by_title[norm_title(r.get("title") or r.get("Title"))] = ab
        for k in excl:
            t = norm_title(art[k].get("title"))
            if t in by_title:
                abstracts[k] = (by_title[t], "rayyan_export:title")
    items = []
    for k in excl:
        ab, src = abstracts.get(k, (None, "unavailable"))
        text = f"{art[k].get('title') or ''} {ab or ''}"
        terms = fn_hunt.scan_text(text)
        items.append({"key": k, "terms": terms, "abstract": ab, "abstract_source": src})
    hits = [i for i in items if i["terms"]]
    remainder = sorted(i["key"] for i in items if not i["terms"])
    n = min(50, len(remainder))
    sample = random.Random(SEED).sample(remainder, n)
    idx = {i["key"]: i for i in items}
    tasks = []
    for k in [i["key"] for i in hits] + sample:
        i = idx[k]
        tasks.append({"id": k, "key": k, "stratum": "lexicon" if i["terms"] else "sample",
                      **meta(art, k), "abstract": i["abstract"], "abstract_source": i["abstract_source"],
                      "lexicon_terms": i["terms"]})
    frame = {"excluded": len(excl), "lexicon_hits": len(hits), "remainder": len(remainder), "n_sample": n,
             "with_abstract": sum(1 for i in items if i["abstract"]),
             "abstract_sources": {s: sum(1 for i in items if i["abstract_source"] == s) for s in sorted({i["abstract_source"] for i in items})}}
    return {"module": "d13", "kind": "triage", "title": "D13 · Exclusões no rastreio (título/resumo)",
            "registered": "C-2.3 §3 item 2; VP §3-Step-4b", "frame": frame, "sample_order": sample,
            "tasks": tasks}, None

# ---------------------------------------------------------------- D11
Q_ELIG = ("O relatório apresenta, propõe, avalia ou critica um modelo EnPI/EnB com detalhe suficiente para o identificar "
          "e caracterizar? (limiar registado; emenda C-2.3 §2.4; prompts/stage1_system.md). Validação, tipo e qualidade "
          "não são requisitos. Uma revisão é elegível se caracteriza os modelos centrais da síntese.")
Q_3B = ("O contexto de aplicação está EXPLICITAMENTE numa indústria de processo contínuo da lista fechada — refinação de "
        "petróleo; petroquímica; cimento; pasta e papel; aço e metais primários em produção contínua; química contínua "
        "(ácido sulfúrico, amoníaco, fertilizantes…); gases industriais; vidro de fusão contínua? 'Could be applied to', "
        "trabalho futuro ou discussão não contam. Se não for elegível, level_3b = falso.")

def build_d11(art):
    base = use("production/reviewer_workspace/reviews/membership/blind")
    frame, ref = [], {}
    for p in sorted(base.glob("*.blind.json")):
        k = p.name[: -len(".blind.json")]
        blind = jload(p); final = jload(base / f"{k}.json"); state = jload(base / f"{k}.state.json")
        for f in (p, base / f"{k}.json", base / f"{k}.state.json"):
            INPUTS[os.path.relpath(f, ROOT)] = sha256(f)
        if state.get("state") != "finalised":
            continue
        for fld in blind.get("review_fields", []):
            sec, name = fld.split(".")
            frame.append((k, fld))
            ref[f"{k}|{fld}"] = {"original_final": final[sec][name], "original_blind": blind[sec][name],
                                 "evidence": (final.get("reviewer_evidence") or {}).get(fld),
                                 "committed_at": state.get("committed_at"), "finalised_at": state.get("finalised_at"),
                                 "notes": final.get("reviewer_notes") or ""}
    frame.sort()
    tagged = []  # o formulário não registou etiqueta borderline em nenhuma decisão (ver emenda §3.2)
    sample = random.Random(SEED).sample(frame, 30)
    tasks = []
    for k, fld in sample:
        name = fld.split(".")[1]
        tasks.append({"id": f"{k}|{fld}", "key": k, "field": fld, **meta(art, k),
                      "question": Q_ELIG if name == "methodological_eligibility" else Q_3B,
                      "field_label": "Elegibilidade metodológica (Corpus A)" if name == "methodological_eligibility" else "Pertença ao Corpus B (level_3b)"})
    frame_info = {"decisions": len(frame), "by_field": {f: sum(1 for _, x in frame if x == f) for f in sorted({x for _, x in frame})},
                  "papers": len({k for k, _ in frame}), "borderline_tagged": len(tagged), "n_sample": len(sample)}
    return ({"module": "d11", "kind": "retest", "blind": True, "title": "D11 · Teste–reteste do revisor",
             "registered": "C-2.3 §3 item 5, §4", "frame": frame_info, "sample_order": [t["id"] for t in tasks], "tasks": tasks},
            {t["id"]: ref[t["id"]] for t in tasks})

# ---------------------------------------------------------------- D7 camada A
def summarise(rec, fam):
    out = []
    models = [(a["application_id"], m) for a in rec["applications"] for m in a["models"]]
    if fam == "T":
        for aid, m in models:
            o = m["C8_metrics"]["out_of_sample_validation"]
            out.append(f"{aid}/{m['model_id']}: out-of-sample = {V(o['status'])}; desenho = {V(o.get('validation_design'))}"
                       + (f"; p.{o['status'].get('page')}" if isinstance(o.get('status'), dict) and o['status'].get('page') else ""))
    elif fam in ("F", "K"):
        for x in rec.get("mechanisms", []):
            out.append(f"{x.get('mechanism_id')}: causa = {x.get('mechanism_cause')}; efeito = {x.get('mechanism_effect_on_model')}; {x.get('claim_status')}; p.{x.get('page')}")
        if not out:
            out.append("(sem mecanismos codificados)")
    elif fam == "C":
        for k, v in rec["C13_reproducibility"].items():
            out.append(f"{k} = {V(v)}" + (f"; p.{v.get('page')}" if isinstance(v, dict) and v.get("page") else ""))
    elif fam == "Q":
        for aid, m in models:
            vs = "; ".join(f"{x.get('verbatim')} [{x.get('type')}/{x.get('role')}]" for x in (m.get("C3_variables") or []))
            out.append(f"{aid}/{m['model_id']}: {vs or '(sem variáveis)'}")
    elif fam == "R":
        for aid, m in models:
            c6 = m["C6_re_estimation"]
            out.append(f"{aid}/{m['model_id']}: regime = {V(c6['regime'])}; execução = {V(c6['update_status'])}")
    elif fam == "V":
        for aid, m in models:
            out.append(f"{aid}/{m['model_id']}: domínio = {V(m['C7_validity_envelope']['statement'])}")
    return out

def build_d7a(art, eff):
    lex = jload(HERE / "lexico_camada_A.json")
    INPUTS[os.path.relpath(HERE / "lexico_camada_A.json", ROOT)] = sha256(HERE / "lexico_camada_A.json")
    tasks, auto = [], []
    for k in sorted(eff):
        pages = pages_of(k)
        npages = [(pg.get("page", i + 1), norm_page(pg.get("text"))) for i, pg in enumerate(pages)]
        for fam in lex["families"]:
            pats = [(t, re.compile(r"\b" + t + r"\b", re.I)) for t in fam["terms"]]
            hits = []
            for pno, txt in npages:
                for t, pat in pats:
                    for mm in pat.finditer(txt):
                        a, b = mm.start(), mm.end()
                        hits.append({"page": pno, "term": t, "match": txt[a:b],
                                     "before": txt[max(0, a - 160):a], "after": txt[b:b + 160]})
            hits.sort(key=lambda h: (h["page"], h["before"][-40:]))
            unit = {"id": f"{k}|{fam['id']}", "key": k, "family": fam["id"], "family_name": fam["name"],
                    "priority": fam["priority"], "field": fam["field"], "relevant_if": fam["relevant_if"],
                    **meta(art, k), "n_hits": len(hits)}
            if hits:
                unit["hits"] = hits
                unit["coded"] = summarise(eff[k], fam["id"])
                tasks.append(unit)
            else:
                auto.append(unit)
    order = {"core": 0, "second": 1}
    fam_order = {f["id"]: i for i, f in enumerate(lex["families"])}
    tasks.sort(key=lambda u: (order[u["priority"]], fam_order[u["family"]], u["key"]))
    frame = {"reports": len(eff), "families": [f["id"] for f in lex["families"]], "units": len(tasks) + len(auto),
             "units_with_hits": len(tasks), "units_no_hit": len(auto),
             "by_family": {f["id"]: {"with_hits": sum(1 for u in tasks if u["family"] == f["id"]),
                                     "no_hit": sum(1 for u in auto if u["family"] == f["id"]),
                                     "hits": sum(u["n_hits"] for u in tasks if u["family"] == f["id"])} for f in lex["families"]}}
    return {"module": "d7a", "kind": "absence", "title": "D7·A · Censo de ausências por léxico (Corpus B)",
            "registered": "Emenda 3 §4.1", "frame": frame, "auto_no_hit": auto, "tasks": tasks}, None

# ---------------------------------------------------------------- D7 camada B
TOK = re.compile(r"([A-Za-z0-9_]+)(?:\[(\d+)\])?")
def walk(rec, path):
    o = rec
    for p in path.split("."):
        m = TOK.fullmatch(p)
        o = o[m.group(1)]
        if m.group(2) is not None:
            o = o[int(m.group(2))]
    return o

def build_d7b(art, recs):
    items = jload(use("stage_c/verification_v1/v1_items_2026-09-17.json"))["items"]
    D = jload(use("stage_c/verification_v1/verificacao_modelo/decisoes_2026-09-17.json"))["itens"]
    kept = []
    for it in items:
        d = D.get(it["id"], {})
        if d.get("keep", True) is False:
            continue
        kept.append(it)
    frame = sorted(it["id"] for it in kept)
    sample = random.Random(SEED).sample(frame, 80)
    byid = {it["id"]: it for it in kept}
    tasks = []
    for iid in sample:
        it = byid[iid]; d = D.get(iid, {})
        obj = copy.deepcopy(walk(recs[it["key"]], it["path"]))
        for f, (old, new) in (d.get("changes") or {}).items():
            if it["type"] in ("MEC", "ADP"):
                obj[{"effect": "mechanism_effect_on_model", "cause": "mechanism_cause", "claim": "claim_status"}.get(f, f)] = new
            elif isinstance(obj, dict) and "value" in obj:
                obj["value"] = new
            else:
                obj = new
        if isinstance(obj, dict):
            shown = {kk: vv for kk, vv in obj.items() if kk not in ("evidence_quote",)}
        else:
            shown = {"value": obj}
        tasks.append({"id": iid, "key": it["key"], "author_year": it.get("author_year"), **meta(art, it["key"]),
                      "type": it["type"], "path": it["path"], "field": it.get("field"), "refers_to": it.get("refers_to") or it.get("rid"),
                      "state_sept": d.get("estado"), "current": shown, "quote": it.get("quote"), "page": it.get("page"),
                      "page_as_recorded": it.get("page_as_recorded"), "support_class": it.get("support_class"), "extra": it.get("extra")})
    info = {"items_368": len(items), "kept": len(kept), "removed": len(items) - len(kept), "n_sample": len(sample),
            "by_type": {t: sum(1 for x in tasks if x["type"] == t) for t in ("MEC", "MOD", "ADP")}}
    return {"module": "d7b", "kind": "cell", "title": "D7·B · Amostra de células (Corpus B)", "registered": "Emenda 3 §4.2",
            "frame": info, "sample_order": sample, "tasks": tasks}, None

# ---------------------------------------------------------------- D7 camada C
REFMAP = ["rayyan-472536695", "rayyan-472535680", "rayyan-472535365", "rayyan-472536532", "rayyan-472535550",
          "rayyan-472535524", "rayyan-472535649", "rayyan-472535582", "rayyan-472535351", "rayyan-472535625",
          "rayyan-472536551", "rayyan-472536518", "rayyan-472536425"]
FIELDS_C = [
    {"id": "c5", "label": "Correspondência da fronteira dos dados de energia (C5)",
     "options": ["exact", "allocated (by rule or estimate)", "mismatch acknowledged", "not reported"]},
    {"id": "c6", "label": "Regime de re-estimação (C6)",
     "options": ["declared and executed", "declared, not executed", "fixed or not stated"]},
    {"id": "c7", "label": "Domínio de validade (C7)", "options": ["numerical bounds", "qualitative", "not stated"]},
    {"id": "oos", "label": "Resultado fora da amostra (C8)", "options": ["reported", "not reported", "not applicable"]},
    {"id": "tb", "label": "Teste em observações de um período posterior ao do ajuste", "options": ["yes", "no", "not applicable"]},
]
def levels_ref(r):
    models = [m for a in r["applications"] for m in a["models"]]
    b = {"exact": 3, "allocated by rule": 2, "allocated by estimate": 2, "mismatch acknowledged": 1}
    c5 = max([b.get(c.get("boundary_correspondence"), 0) for m in models for c in (m.get("C5_measurement") or [])] or [0])
    c6 = 0
    for m in models:
        reg, st = V(m["C6_re_estimation"]["regime"]), V(m["C6_re_estimation"]["update_status"])
        if reg not in ("fixed, not mentioned", "not stated"):
            c6 = max(c6, 3 if st == "executed" else 2)
    c7 = max([{"stated with numeric bounds": 3, "stated qualitatively": 2}.get(V(m["C7_validity_envelope"]["statement"]), 0) for m in models] or [0])
    vals = [V(m["C8_metrics"]["out_of_sample_validation"]["status"]) for m in models]
    oos = "not applicable" if all(v == "not applicable" for v in vals) else ("reported" if "reported" in vals else "not reported")
    return {"c5": {3: "exact", 2: "allocated (by rule or estimate)", 1: "mismatch acknowledged", 0: "not reported"}[c5],
            "c6": {3: "declared and executed", 2: "declared, not executed", 0: "fixed or not stated"}[c6],
            "c7": {3: "numerical bounds", 2: "qualitative", 0: "not stated"}[c7],
            "oos": oos, "tb": "not applicable" if oos == "not applicable" else "no"}

def build_d7c(art, eff):
    tasks, ref = [], {}
    for k in REFMAP:
        tasks.append({"id": k, "key": k, **meta(art, k), "fields": FIELDS_C})
        ref[k] = levels_ref(eff[k])
    return ({"module": "d7c", "kind": "refmap", "blind": True, "title": "D7·C · Mapa de refinação/petroquímica (13)",
             "registered": "Emenda 3 §4.3", "frame": {"reports": len(tasks)}, "tasks": tasks,
             "note": "Valores ocultados durante a leitura, após exposição prévia — não é blind-first."}, ref)

# ---------------------------------------------------------------- D10
LEVEL_A = ["paper_type", "multi_site", "country_region", "sector_of_activity", "type_of_organisation",
           "ems_standard", "mv_protocol", "regulatory_driver", "enpi_enb_model_types", "complementary_methodologies"]
def build_d10(art):
    sys.path.insert(0, str(ROOT / "production" / "reviewer_workspace"))
    import field_contract as fc  # noqa
    INPUTS["production/reviewer_workspace/field_contract.py"] = sha256(ROOT / "production/reviewer_workspace/field_contract.py")
    spec = {}
    for f in LEVEL_A:
        r = (fc.STAGE2_FIELDS.get(f) or {}).get("reviewer") if f in fc.STAGE2_FIELDS else None
        if f == "paper_type":
            r = {"type": "enum", "options": list(fc.PAPER_TYPE)}
        spec[f] = r or {"type": "text"}
    cp = use("bibliometrics/results/corpus_a_registado/tables/cell_provenance.csv")
    cells = {}
    for x in csv.DictReader(open(cp, encoding="utf-8-sig")):
        cells.setdefault(x["paper_id"], {})[x["field"]] = x
    frame = sorted(cells)
    draw = random.Random(SEED).sample(frame, 40)   # mesma sequência que audit_sampler.select_audit (que devolve sorted(draw))
    sys.path.insert(0, str(ROOT / "output"))
    try:
        import audit_sampler  # noqa
        chk = audit_sampler.select_audit([{"key": k} for k in frame], n=40, seed=SEED)["srs_sample"]
        assert chk == sorted(draw), "o sorteio diverge de audit_sampler.select_audit"
        INPUTS["output/audit_sampler.py"] = sha256(ROOT / "output" / "audit_sampler.py")
    except ImportError:
        pass
    tasks, ref = [], {}
    for k in draw:
        c = cells[k]
        auditable = [f for f in LEVEL_A if c.get(f, {}).get("status", "").startswith("concordância")]
        tasks.append({"id": k, "key": k, **meta(art, k), "fields": [{"id": f, **spec[f]} for f in auditable],
                      "not_auditable": {f: c.get(f, {}).get("status") for f in LEVEL_A if f not in auditable}})
        ref[k] = {f: {"status": c[f]["status"], "claude": c[f]["claude"], "chatgpt": c[f]["chatgpt"]} for f in auditable}
    info = {"frame": len(frame), "n_sample": 40, "auditable_cells": sum(len(t["fields"]) for t in tasks),
            "by_field": {f: sum(1 for t in tasks if any(x["id"] == f for x in t["fields"])) for f in LEVEL_A}}
    return ({"module": "d10", "kind": "audit", "blind": True, "title": "D10 · Auditoria Level-A (Corpus A)",
             "registered": "C-2.3 §3 item 4, §4; VP §4a", "frame": info, "sample_order": draw, "tasks": tasks}, ref)

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verifica entradas sem sortear nem escrever")
    ap.add_argument("--force", action="store_true", help="regenera mesmo que já existam tarefas (nunca apaga respostas)")
    a = ap.parse_args()
    filed = None if a.check else interlock()
    if not a.check and (OUT / "MANIFEST.json").exists() and not a.force:
        sys.exit("[parado] tarefas/ já existe. Os sorteios são deterministas; usa --force só se mudaste uma entrada, e regista porquê.")
    art = articles()
    recs = stage_c_records()
    eff = overlay_effective(recs)
    if a.check:
        for k in eff:
            pages_of(k); use(f"data/pdfs/{k}.pdf")
        print(f"[ok] entradas presentes: {len(art)} registos, {len(eff)} relatórios Stage C. Interlock: "
              + ("ok" if (HERE / 'AMENDMENT_FILED.txt').exists() else "AINDA NÃO DEPOSITADO"))
        return
    built = [build_d13(art), build_d11(art), build_d7a(art, eff), build_d7b(art, recs), build_d7c(art, eff), build_d10(art)]
    OUT.mkdir(exist_ok=True); (OUT / "_ref").mkdir(exist_ok=True)
    man = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "seed": SEED,
           "amendment": filed, "git_head": git_head(), "python": sys.version.split()[0], "modules": {}}
    for pub, ref in built:
        m = pub["module"]
        jdump(pub, OUT / f"{m}.json")
        if ref is not None:
            jdump(ref, OUT / "_ref" / f"{m}.json")
        man["modules"][m] = {"title": pub["title"], "n_tasks": len(pub["tasks"]), "frame": pub["frame"],
                             "sha256": sha256(OUT / f"{m}.json")}
    man["inputs_sha256"] = dict(sorted(INPUTS.items()))
    jdump(man, OUT / "MANIFEST.json")
    for m, v in man["modules"].items():
        print(f"{m:5s} {v['n_tasks']:4d} tarefas  {v['title']}")
    print("Tarefas em", OUT)

if __name__ == "__main__":
    main()
