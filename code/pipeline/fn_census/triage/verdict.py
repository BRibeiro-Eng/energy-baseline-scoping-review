#!/usr/bin/env python3
"""Registar veredictos da triagem do censo FN (C-2.3 §3-Step-4).

  python3 verdict.py --next [A|B]        proximo candidato por decidir
  python3 verdict.py <key> not_fn "razao numa linha"
  python3 verdict.py <key> confirmed_fn --sector cement --page 4 --quote "..."
  python3 verdict.py <key> --promote "porque e que a duvida existe"   (so Tier-B)

Nada e apagado. Um veredicto ja escrito so muda com --force, e a versao
anterior fica em verdicts/_superseded/.
"""
import argparse, datetime, json, os, re, shutil, sys
from pathlib import Path

T = Path(__file__).resolve().parent
O = T.parent.parent
sys.path.insert(0, str(O))

def _ground(quote, page, pages):
    """Usa o grounding.py canonico (8 regras v2.2.1). Se o rapidfuzz nao estiver
    disponivel neste interpretador, cai para substring normalizada e diz-o."""
    try:
        from grounding import ground_quote
        return ground_quote(quote, page, pages), "canonico"
    except ImportError:
        norm = lambda s: re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", s or "")).strip().lower()
        tgt = next((p.get("text") for p in pages if p.get("page") == page), "")
        ok = norm(quote) in norm(tgt)
        return {"grounded": ok, "score": None}, "reduzido (sem rapidfuzz)"

SECTORS = ["petroleum refining", "petrochemicals", "cement/lime/clinker",
           "pulp and paper", "steel/primary metals", "continuous chemicals",
           "industrial gases", "glass", "continuous-unlisted"]

def load_queues():
    q = {}
    for tier in ("A", "B"):
        for c in json.loads((T / f"QUEUE_{tier}.json").read_text()):
            c["tier"] = tier
            q[c["key"]] = c
    return q

def decided():
    return {p.stem for p in (T / "verdicts").glob("rayyan-*.json")}

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("key", nargs="?")
    ap.add_argument("verdict", nargs="?", choices=["not_fn", "confirmed_fn"])
    ap.add_argument("reason", nargs="?", default="")
    ap.add_argument("--next", nargs="?", const="any", metavar="TIER")
    ap.add_argument("--promote", metavar="REASON")
    ap.add_argument("--sector", choices=SECTORS)
    ap.add_argument("--quote"); ap.add_argument("--page", type=int)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    Q, done = load_queues(), decided()

    if a.next:
        pend = [c for k, c in Q.items() if k not in done
                and (a.next == "any" or c["tier"] == a.next.upper())]
        if not pend:
            print("fila vazia — nada por decidir neste tier."); return
        pend.sort(key=lambda c: (c["tier"] != "B", list(Q).index(c["key"])))
        c = pend[0]
        print(f"{c['key']}  [tier {c['tier']}]  {c.get('year','?')}")
        print(f"  {c.get('title','')}")
        print(f"  termos: {', '.join(c.get('terms') or []) or '— (model flag)'}")
        if c.get("model_flag_reasons"): print(f"  flags : {', '.join(c['model_flag_reasons'])}")
        print(f"  excertos: contexts/{c['key']}.md")
        print(f"  faltam {len(pend)} neste filtro, {len(Q)-len(done)} no total")
        return

    if not a.key or a.key not in Q:
        ap.error("key desconhecida ou em falta (usa --next)")
    c = Q[a.key]
    out = T / "verdicts" / f"{a.key}.json"
    if out.exists() and not a.force:
        ap.error(f"{a.key} ja tem veredicto. Usa --force para substituir.")

    rec = {"key": a.key, "tier": c["tier"], "ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "detectors": c.get("detectors"), "terms": c.get("terms")}

    if a.promote:
        if c["tier"] != "B": ap.error("--promote so faz sentido em Tier-B")
        if len(a.promote.strip()) < 10: ap.error("justifica a promocao numa linha real")
        rec.update({"verdict": "promoted_to_A", "reason": a.promote.strip()})
        qa = json.loads((T / "QUEUE_A.json").read_text())
        if not any(x["key"] == a.key for x in qa):
            entry = {k: v for k, v in c.items() if k != "tier"}; entry["tier"] = "A"
            entry["promoted_from_B"] = True
            qa.append(entry)
            (T / "QUEUE_A.json").write_text(json.dumps(qa, indent=1, ensure_ascii=False))
        print(f"{a.key}: promovido a Tier-A. Decide-o na leitura completa.")
    elif a.verdict == "confirmed_fn":
        if not (a.sector and a.quote and a.page):
            ap.error("confirmed_fn exige --sector, --quote e --page")
        pages = (json.loads((O / "stage0" / f"{a.key}.json").read_text())
                 .get("pdf") or {}).get("pages") or []
        g, mode = _ground(a.quote, a.page, pages)
        if not g.get("grounded"):
            print(f"CITACAO NAO VERIFICADA na p.{a.page} (modo {mode}, score {g.get('score')}).")
            print("Corrige a pagina ou a transcricao. Nada foi gravado.")
            sys.exit(2)
        rec.update({"verdict": "confirmed_fn", "sector": a.sector, "quote": a.quote,
                    "page": a.page, "grounded": True, "grounding_mode": mode,
                    "reason": a.reason.strip()})
        if mode.startswith("reduzido"):
            print("  NOTA: verificacao em modo reduzido; reconfirma no ambiente com rapidfuzz.")
        print(f"{a.key}: FALSO NEGATIVO CONFIRMADO ({a.sector}), citacao verificada.")
        print("  -> dispara expansao do lexicon + re-run do detector (b), §6a.")
    elif a.verdict == "not_fn":
        if len(a.reason.strip()) < 10:
            ap.error("not_fn exige uma razao real (uma linha)")
        rec.update({"verdict": "not_fn", "reason": a.reason.strip()})
        print(f"{a.key}: exclusao mantida.")
    else:
        ap.error("indica um veredicto (not_fn / confirmed_fn) ou --promote")

    if out.exists():
        sup = T / "verdicts" / "_superseded"; sup.mkdir(exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        shutil.move(str(out), str(sup / f"{a.key}.{stamp}.json"))
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"  gravado: verdicts/{a.key}.json   ({len(decided())}/{len(Q)} decididos)")

if __name__ == "__main__":
    main()
