#!/usr/bin/env python3
"""Grounding check corpus-wide — VALIDATION_PROTOCOL_C.md §12.2.

Verifica TODAS as citações de evidência de TODAS as extrações dos dois modelos
contra o texto Stage-0 do próprio paper, com as 8 regras de normalização v2.2.1.

    /usr/local/bin/python3 output/grounding_corpus_wide.py

Escreve output/grounding_corpus_wide/{report.json, failures.jsonl, REPORT.md}.
Não altera nenhuma extração: só mede.
"""
import json, sys, collections, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "output"))
from grounding import ground_quote

IMPORTS = ROOT / "production/reviewer_workspace/imports"
STAGE0 = ROOT / "output/stage0"
OUT = ROOT / "output/grounding_corpus_wide"
OUT.mkdir(exist_ok=True)

def envelopes(obj, prefix=""):
    """Percorre a extração e devolve (campo, quote, page) de cada envelope de evidência."""
    if isinstance(obj, dict):
        if "evidence_quote" in obj and ("value" in obj or "page" in obj):
            yield prefix, obj.get("evidence_quote"), obj.get("page")
            return
        for k, v in obj.items():
            yield from envelopes(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from envelopes(v, f"{prefix}[{i}]")

pages_cache = {}
def pages_of(key):
    if key not in pages_cache:
        p = STAGE0 / f"{key}.json"
        pages_cache[key] = ((json.loads(p.read_text()).get("pdf") or {}).get("pages") or []
                            if p.is_file() else [])
    return pages_cache[key]

stats = collections.Counter()
per_field = collections.defaultdict(lambda: {"n": 0, "fail": 0})
per_model = collections.defaultdict(lambda: {"n": 0, "fail": 0})
patterns = collections.Counter()
fails = []

for model in ("claude", "chatgpt"):
    for f in sorted((IMPORTS / model).glob("rayyan-*.json")):
        try:
            rec = json.loads(f.read_text())
        except Exception:
            stats["ficheiros_ilegiveis"] += 1; continue
        key = rec.get("paper_key") or f.stem
        pages = pages_of(key)
        if not pages:
            stats["sem_stage0"] += 1; continue
        stats["ficheiros"] += 1
        for field, quote, page in envelopes(rec):
            if not quote or page in (None, ""):
                stats["sem_citacao"] += 1; continue
            stats["verificadas"] += 1
            per_field[field]["n"] += 1; per_model[model]["n"] += 1
            g = ground_quote(quote, page, pages)
            if g.get("grounded"):
                if g.get("page_unverified"):
                    stats["pagina_nao_confirmada"] += 1
            else:
                stats["FALHAS"] += 1
                per_field[field]["fail"] += 1; per_model[model]["fail"] += 1
                sc = g.get("score")
                patterns["score<50 (provavel fabricacao)" if (sc or 0) < 50
                         else "score 50-80 (transcricao imprecisa)" if (sc or 0) < 80
                         else "score>=80 (quase bate — encoding/pagina)"] += 1
                fails.append({"model": model, "key": key, "field": field,
                              "page": page, "score": sc, "quote": quote[:300]})

rep = {"corrido_em": datetime.datetime.now().isoformat(timespec="seconds"),
       "stats": dict(stats),
       "taxa_falha_global": round(100 * stats["FALHAS"] / max(stats["verificadas"], 1), 2),
       "por_modelo": {m: {**v, "taxa": round(100*v["fail"]/max(v["n"],1), 2)}
                      for m, v in per_model.items()},
       "padroes_de_falha": dict(patterns),
       "piores_campos": sorted(
           [{"campo": k, **v, "taxa": round(100*v["fail"]/max(v["n"],1), 2)}
            for k, v in per_field.items() if v["fail"]],
           key=lambda x: -x["taxa"])[:15]}
(OUT / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
with open(OUT / "failures.jsonl", "w", encoding="utf-8") as fh:
    for x in fails:
        fh.write(json.dumps(x, ensure_ascii=False) + "\n")

print(json.dumps(rep, indent=1, ensure_ascii=False)[:2200])
