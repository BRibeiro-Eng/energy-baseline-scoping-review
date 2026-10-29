#!/usr/bin/env python3
"""Progresso da triagem do censo FN. Read-only."""
import json, collections, statistics
from pathlib import Path
T = Path(__file__).resolve().parent

sample = None
if (T / "SAMPLE.json").is_file():
    sm = json.loads((T / "SAMPLE.json").read_text()); sample = set(sm["keys"])

Q = {}
for tier in ("A", "B"):
    for c in json.loads((T / f"QUEUE_{tier}.json").read_text()):
        Q[c["key"]] = c.get("tier", tier)
frame_total = len(Q)
if sample is not None:
    Q = {k: v for k, v in Q.items() if k in sample}

V = {p.stem: json.loads(p.read_text()) for p in (T / "verdicts").glob("rayyan-*.json")}
Vq = {k: v for k, v in V.items() if k in Q}

per = collections.defaultdict(collections.Counter)
for k, tier in Q.items():
    per[tier][Vq[k]["verdict"] if k in Vq else "pendente"] += 1

if sample is not None:
    print(f"MODO AMOSTRA — n={len(Q)} sorteados (seed {sm['seed']}) de um frame de {frame_total}")
    print(f"cobertura do frame: {100*len(Q)/frame_total:.0f}%\n")
print(f"decididos {len(Vq)}/{len(Q)}")
for tier in sorted(per):
    c = per[tier]; done = sum(v for kk, v in c.items() if kk != "pendente")
    print(f"  Tier-{tier}  {done:>3}/{sum(c.values()):<3}  {dict(c)}")

dw = [v["dwell_seconds"] for v in Vq.values() if v.get("dwell_seconds") is not None]
if dw:
    dw_s = sorted(dw)
    print(f"\ntempo de decisao (n={len(dw)}): mediana {statistics.median(dw):.0f}s | "
          f"min {dw_s[0]:.0f}s | max {dw_s[-1]:.0f}s")
    quick = sum(1 for d in dw if d < 30)
    print(f"  decisoes com menos de 30 s: {quick}")
    if quick:
        print("  ATENCAO: um Tier-A decidido em menos de 30 s nao e' leitura completa.")
        print("  Este campo vai para o relatorio — e' a evidencia de que a triagem foi feita.")
missing = [k for k, v in Vq.items() if v.get("dwell_seconds") is None]
if missing:
    print(f"  sem dwell registado (decididos por CLI ou antes desta versao): {len(missing)}")

fn = [v for v in Vq.values() if v["verdict"] == "confirmed_fn"]
prom = [v for v in Vq.values() if v["verdict"] == "promoted_to_A"]
print(f"\nfalsos negativos confirmados: {len(fn)}")
for v in fn:
    print(f"  {v['key']}  {v['sector']}  p.{v['page']}")
if prom:
    print(f"promovidos B->A (por decidir): {len(prom)}  {[v['key'] for v in prom]}")

print()
if len(Vq) < len(Q):
    print(f"POR FECHAR — faltam {len(Q)-len(Vq)}.")
elif sample is not None:
    n, e = len(Q), len(fn)
    print(f"AMOSTRA COMPLETA: {e}/{n} falsos negativos.")
    print("Isto NAO e' o censo do §3-Step-4 — e' uma amostra. O relatorio tem de dizer")
    print(f"'triagem por amostragem, n={n}, seed {sm['seed']}, cobertura {100*n/frame_total:.0f}% do frame',")
    print("com IC exacto de Clopper-Pearson, e a emenda datada tem de estar submetida.")
    if e:
        print("Com FN confirmados na amostra, a taxa extrapola para o frame — e o §6a")
        print("obriga a expandir o lexicon e re-correr o detector (b).")
