#!/usr/bin/env python3
"""Constroi o pacote de triagem do censo FN (C-2.3 §3-Step-4).
Nao decide nada: organiza a fila, pre-extrai os excertos e da onde gravar veredictos."""
import json, os, re, sys
from pathlib import Path

O = Path(os.environ["HOME"]) / "mnt/Screening/level3_extraction/output"
sys.path.insert(0, str(O))
from fn_hunt import _compile, CONTINUOUS_PROCESS_TERMS

T = O / "fn_census/triage"
(T / "contexts").mkdir(parents=True, exist_ok=True)
(T / "verdicts").mkdir(parents=True, exist_ok=True)

# termos especificos vs ambiguos: so para ORDENAR a fila, nunca para decidir
STRONG = {"refinery", "refining", "petrochemical", "clinker", "blast furnace",
          "steelmaking", "pulp and paper", "paper mill", "ammonia", "ethylene",
          "olefin", "sulfuric acid", "sulphuric acid", "chlor-alkali",
          "industrial gases", "air separation", "glass furnace", "glass melting", "kiln"}

cands = json.loads((O / "fn_census/candidates.json").read_text())

def score(c):
    terms = set(c.get("terms") or [])
    return (len(terms & STRONG) * 10 + len(terms)
            + (5 if "model_flags" in c.get("detectors", []) else 0))

for c in cands:
    c["_score"] = score(c)
    c["_strong_terms"] = sorted(set(c.get("terms") or []) & STRONG)

A = sorted([c for c in cands if c["tier"] == "A"], key=lambda c: (-c["_score"], c["key"]))
B = sorted([c for c in cands if c["tier"] == "B"], key=lambda c: (-c["_score"], c["key"]))

# ---------- excertos ----------
def contexts_for(key, terms):
    p = O / "stage0" / f"{key}.json"
    if not p.is_file():
        return None, "Stage-0 ausente"
    d = json.loads(p.read_text())
    pages = (d.get("pdf") or {}).get("pages") or []
    pats = dict(_compile(terms or CONTINUOUS_PROCESS_TERMS))
    out = {}
    for pg in pages:
        n, text = pg.get("page"), pg.get("text") or ""
        for term, pat in pats.items():
            for m in pat.finditer(text):
                hits = out.setdefault(term, [])
                if len(hits) >= 3:
                    break
                s = max(0, m.start() - 180); e = min(len(text), m.end() + 180)
                frag = re.sub(r"\s+", " ", text[s:e]).strip()
                hits.append((n, frag))
    return out, (d.get("metadata") or {})

written = 0
for c in cands:
    ctx, meta = contexts_for(c["key"], c.get("terms"))
    lines = [f"# {c['key']} — {c.get('title','(sem titulo)')}", "",
             f"**{c.get('year','?')}** · tier **{c['tier']}** · detectores: "
             f"{', '.join(c.get('detectors',[]))}"]
    if c.get("model_flag_reasons"):
        lines += ["", f"**Model flags:** {', '.join(c['model_flag_reasons'])}"]
    if not c.get("terms"):
        lines += ["", "_Sem termos de lexicon — entrou por model flag. Leitura completa._"]
    lines += ["", "---", ""]
    if isinstance(ctx, dict):
        for term in sorted(ctx, key=lambda t: (t not in STRONG, t)):
            mark = " **(especifico)**" if term in STRONG else ""
            lines.append(f"## `{term}`{mark}")
            for pg, frag in ctx[term]:
                lines.append(f"- **p.{pg}** … {frag} …")
            lines.append("")
    elif ctx is None:
        lines.append(f"_{meta}_")
    (T / "contexts" / f"{c['key']}.md").write_text("\n".join(lines), encoding="utf-8")
    written += 1

# ---------- filas ----------
def fila_md(rows, tier, nota):
    out = [f"# Fila Tier-hit-{tier} — {len(rows)} candidatos", "", nota, "",
           "Ordenada por especificidade do sinal: os mais arriscados primeiro. Se parares a",
           "meio, paraste no sitio menos mau.", "",
           "| # | key | ano | termos | sinal | titulo |", "|--:|---|--:|---|--:|---|"]
    for i, c in enumerate(rows, 1):
        terms = ", ".join(f"**{t}**" if t in STRONG else t for t in (c.get("terms") or [])) or "—"
        flag = " ⚑" if "model_flags" in c.get("detectors", []) else ""
        out.append(f"| {i} | `{c['key']}`{flag} | {c.get('year','?')} | {terms} "
                   f"| {c['_score']} | {(c.get('title') or '')[:70]} |")
    return "\n".join(out) + "\n"

(T / "FILA_A.md").write_text(fila_md(
    A, "A", "**Leitura completa, ~10-12 min cada.** Termo multi-palavra, match de "
    "metadados de setor, ou flag de modelo (⚑)."), encoding="utf-8")
(T / "FILA_B.md").write_text(fila_md(
    B, "B", "**Skim de 2 min + uma linha de justificacao.** Qualquer duvida promove a "
    "Tier-A — usa `--promote`, nao decidas na duvida."), encoding="utf-8")

for name, rows in (("QUEUE_A.json", A), ("QUEUE_B.json", B)):
    (T / name).write_text(json.dumps(
        [{k: v for k, v in c.items() if not k.startswith("_")} for c in rows],
        indent=1, ensure_ascii=False), encoding="utf-8")

print(f"contextos escritos : {written}")
print(f"Tier A: {len(A)}  Tier B: {len(B)}")
print(f"top-5 A: {[(c['key'], c['_strong_terms']) for c in A[:5]]}")
print(f"top-5 B: {[(c['key'], c.get('terms')) for c in B[:5]]}")
