#!/usr/bin/env python3
"""escalada_d11.py — Emenda 3 §3.2 (escalada do reteste).

Regra depositada: "if more than one flip occurs on the same field, all other decisions on that field
among the 90 are re-decided under the same procedure". Este script lê o D11 concluído, conta os flips
por campo a partir de respostas/d11.jsonl e da referência, e gera o módulo d11x (cego, mesmo
procedimento) com TODAS as outras decisões dos campos que excederam o limiar. Não sorteia nada.

    python3 verificacao_2026-10/escalada_d11.py
"""
import json, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_tasks as bt  # noqa: E402

def main():
    d11 = json.load(open(HERE / "tarefas" / "d11.json", encoding="utf-8"))
    ref = json.load(open(HERE / "tarefas" / "_ref" / "d11.json", encoding="utf-8"))
    st = {}
    for line in open(HERE / "respostas" / "d11.jsonl", encoding="utf-8"):
        if line.strip():
            e = json.loads(line)
            if e["phase"] in ("commit", "final"):
                st.setdefault(e["task_id"], {})[e["phase"]] = e["answer"]
    sampled = [t["id"] for t in d11["tasks"]]
    missing = [k for k in sampled if "final" not in st.get(k, {})]
    if missing:
        sys.exit(f"[parado] D11 ainda tem {len(missing)} itens por concluir.")
    flips = Counter()
    for t in d11["tasks"]:
        mine = st[t["id"]]["commit"].get("value") == "true"
        if mine != (ref[t["id"]]["original_final"] is True):
            flips[t["field"]] += 1
    fields = sorted(f for f, c in flips.items() if c > 1)
    print("flips por campo:", dict(flips), "-> escalada:", fields or "nenhuma")
    if not fields:
        return
    art = bt.articles()
    pub, allref = bt.build_d11(art)  # reconstrói o frame completo das 90 (determinístico)
    # frame completo: reutiliza a leitura do build_d11 sem amostragem
    base = bt.ROOT / "production/reviewer_workspace/reviews/membership/blind"
    frame = []
    for p in sorted(base.glob("*.blind.json")):
        k = p.name[: -len(".blind.json")]
        blind = bt.jload(p); final = bt.jload(base / f"{k}.json")
        for fld in blind.get("review_fields", []):
            if fld in fields and f"{k}|{fld}" not in sampled:
                sec, name = fld.split(".")
                frame.append((k, fld, final, blind))
    order = {"eligibility.level_3b": 0, "eligibility.methodological_eligibility": 1}
    frame.sort(key=lambda x: (order.get(x[1], 9), x[0]))
    tasks, xref = [], {}
    for k, fld, final, blind in frame:
        sec, name = fld.split(".")
        tid = f"{k}|{fld}"
        tasks.append({"id": tid, "key": k, "field": fld, **bt.meta(art, k),
                      "question": bt.Q_ELIG if name == "methodological_eligibility" else bt.Q_3B,
                      "field_label": "Elegibilidade metodológica (Corpus A)" if name == "methodological_eligibility" else "Pertença ao Corpus B (level_3b)"})
        xref[tid] = {"original_final": final[sec][name], "original_blind": blind[sec][name],
                     "evidence": (final.get("reviewer_evidence") or {}).get(fld), "notes": final.get("reviewer_notes") or ""}
    mod = {"module": "d11x", "kind": "retest", "blind": True,
           "title": "D11·E · Escalada do reteste (re-decisão integral)",
           "registered": "Emenda 3 §3.2 (escalada)", "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "frame": {"trigger_flips": dict(flips), "fields": fields,
                     "by_field": {f: sum(1 for t in tasks if t["field"] == f) for f in fields}, "n": len(tasks)},
           "tasks": tasks}
    out = HERE / "tarefas" / "d11x.json"
    if out.exists():
        sys.exit("[parado] tarefas/d11x.json já existe.")
    bt.jdump(mod, out); bt.jdump(xref, HERE / "tarefas" / "_ref" / "d11x.json")
    print(f"d11x: {len(tasks)} decisões", mod["frame"]["by_field"])

if __name__ == "__main__":
    main()
