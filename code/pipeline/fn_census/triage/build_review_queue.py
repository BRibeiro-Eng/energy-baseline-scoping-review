#!/usr/bin/env python3
"""Monta a fila de revisao humana a partir da saida do classificador."""
import json, shutil
from pathlib import Path
T = Path(__file__).resolve().parent

rows = json.loads((T / "CLASSIFIER.json").read_text())
ctrl = set(json.loads((T / "CONTROL_SAMPLE.json").read_text())["keys"])
if (T / "SAMPLE.json").is_file():
    shutil.move(str(T / "SAMPLE.json"), str(T / "SAMPLE_superseded_seed45.json"))

AB = [r["key"] for r in rows if r["categoria"] in ("A_aplica", "B_contexto")]
keys = AB + [r["key"] for r in rows if r["key"] in ctrl]
(T / "SAMPLE.json").write_text(json.dumps({
    "desenho": "estratificado por risco (substitui a ASR seed 45, em SAMPLE_superseded_seed45.json)",
    "estrato_alto": "A_aplica + B_contexto do classificador — censo integral",
    "estrato_alto_n": len(AB),
    "estrato_baixo": "C_mencao + D_homonimo — amostra de controlo aleatoria",
    "estrato_baixo_n": 25, "estrato_baixo_frame": 129, "seed": 46,
    "n": len(keys), "keys": keys}, indent=1, ensure_ascii=False), encoding="utf-8")

by = {r["key"]: r for r in rows}
L = ["# Fila de revisão — triagem estratificada por risco", "",
     f"{len(keys)} papers: **{len(AB)}** do estrato de alto risco (integral) + **25** de controlo "
     "aleatório do estrato de baixo risco (seed 46, de um frame de 129).", "",
     "A coluna `cat` é a **recomendação** do classificador, não uma decisão. "
     "`A` = aplica num setor da lista · `B` = contexto contínuo ou setor não-listado · "
     "`C` = só menção · `D` = homónimo. Todas as citações foram verificadas contra o texto do paper.", "",
     "| # | key | tier | cat | conf | setor | razão |", "|--:|---|:--:|:--:|--:|---|---|"]
for i, k in enumerate(keys, 1):
    r = by[k]
    tag = " ⟨controlo⟩" if k in ctrl else ""
    L.append(f"| {i} | `{k}`{tag} | {r['tier']} | **{r['categoria'].split('_')[0]}** | "
             f"{r.get('confianca')} | {r.get('setor') or '—'} | {(r.get('razao') or '')[:160]} |")
(T / "FILA_REVISAO.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"fila: {len(keys)} papers ({len(AB)} alto risco + 25 controlo)")
print("SAMPLE.json e FILA_REVISAO.md escritos")
