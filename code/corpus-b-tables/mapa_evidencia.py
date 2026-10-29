#!/usr/bin/env python3
"""Mapa de evidência do Corpus B (Cap. 3, figura F05) — PROTÓTIPO para decidir o desenho.

Uma linha por artigo cartografado, agrupada por setor; colunas = o que o estudo declara sobre
fronteira, validade temporal, validação, avaliação de adaptações e partilha. Nível V0 (extração
assistida, sem verificação humana) até existir v1_overrides_*.json.
Regra de agregação por artigo (modelo -> artigo): o nível MAIS declarado entre os modelos.
"""
import argparse, csv, glob, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
V = lambda e: e.get("value") if isinstance(e, dict) else e
CLOSE = {"refinery — model empirically applied there", "petrochemical — model empirically applied there"}
SECT = {"petroleum refining": "Refinação", "petrochemicals": "Petroquímica", "cement, lime, clinker": "Cimento e cal",
        "steel and primary metals": "Aço e metais primários", "pulp & paper": "Pasta e papel", "glass": "Vidro",
        "continuous chemical production": "Química contínua", "industrial gases": "Gases industriais",
        "multiple of the above": "Vários setores", "not one of the registered sectors": "Outro"}
ORDER = ["Refinação", "Petroquímica", "Química contínua", "Gases industriais", "Cimento e cal",
         "Aço e metais primários", "Pasta e papel", "Vidro", "Vários setores", "Outro"]
NA = -1
COLS = [
    ("Fronteira\nmedida", "C5", "exata · alocada · reconhece desvio"),
    ("Re-\nestimação", "C6", "executada · declarada"),
    ("Domínio\nde validade", "C7", "numérico · qualitativo"),
    ("Ajuste\nno treino", "C8", "reportado"),
    ("Fora da\namostra", "C8", "reportada"),
    ("Adaptação\n(estado)", "SQ3", "avaliada · implementada · proposta"),
    ("Dados ou\ncódigo", "C13", "código · dados · dados parciais"),
]


def levels(r):
    models = [m for a in r["applications"] for m in a["models"]]
    b = {"exact": 3, "allocated by rule": 2, "allocated by estimate": 2, "mismatch acknowledged": 1}
    c5 = max([b.get(c.get("boundary_correspondence"), 0) for m in models for c in m.get("C5_measurement") or []] or [0])
    c6 = 0
    for m in models:
        reg, st = V(m["C6_re_estimation"]["regime"]), V(m["C6_re_estimation"]["update_status"])
        if reg not in ("fixed, not mentioned", "not stated"):
            c6 = max(c6, 3 if st == "executed" else 2)
    c7 = max([{"stated with numeric bounds": 3, "stated qualitatively": 2}.get(V(m["C7_validity_envelope"]["statement"]), 0) for m in models] or [0])

    def c8(block, lvl):
        vals = [V(m["C8_metrics"][block]["status"]) for m in models]
        if all(v == "not applicable" for v in vals):
            return NA
        return lvl if "reported" in vals else 0
    ins, oos = c8("in_sample_fit", 2), c8("out_of_sample_validation", 3)
    ad = max([{"evaluated": 3, "implemented": 2, "proposed": 1}[d["status"]] for d in r["adaptations"]] or [0])
    c13 = r["C13_reproducibility"]
    rep = 3 if V(c13["code_available"]) in ("yes", "partial") else 2 if V(c13["data_available"]) == "yes" else 1 if V(c13["data_available"]) == "partial" else 0
    return [c5, c6, c7, ins, oos, ad, rep]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--decisoes")
    ap.add_argument("--out", default=f"{HERE}/mapa_evidencia_PROTOTIPO.png")
    a = ap.parse_args()
    meta = {}
    with open(f"{ROOT}/data/articles.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            k = row["key"] if row["key"].startswith("rayyan-") else f"rayyan-{row['key']}"
            meta[k] = ((row.get("authors") or "?").split(";")[0].split(",")[0].strip(), row.get("year") or "s.d.")
    rows = []
    recs = {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(f"{ROOT}/production/stage_c/claude/outputs/rayyan-*.json"))}
    if a.decisoes:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "verification_v1"))
        from overlay import effective
        recs, _ = effective(recs, a.decisoes)
    for k, r in recs.items():
        if k in a.exclude:
            continue
        sec = SECT.get(V(r["applications"][0]["sector_registered"]), "Outro")
        close = any(V(x.get("refinery_or_petrochemical_case")) in CLOSE for x in r["applications"])
        au, yr = meta.get(k, ("?", "?"))
        rows.append((ORDER.index(sec), sec, int(yr) if str(yr).isdigit() else 0, f"{au} {yr}", close, levels(r)))
    rows.sort(key=lambda x: (x[0], x[2], x[3]))
    seen = {}
    for r in rows:
        seen[r[3]] = seen.get(r[3], 0) + 1
    cnt = {}
    for i, r in enumerate(rows):
        if seen[r[3]] > 1:
            cnt[r[3]] = cnt.get(r[3], 0) + 1
            rows[i] = r[:3] + (r[3] + "abcdef"[cnt[r[3]] - 1],) + r[4:]

    # ------------------------------------------------------------------
    # 2026-09-21 (prototipo A): dois paineis de setores lado a lado.
    # A versao de uma coluna media 6.3 x 10.6 pol (racio 0.60). Com
    # width=textwidth, height=0.86 textheight e keepaspectratio, o limite
    # efectivo era a ALTURA: a figura era escalada para ~4.7 pol de largura,
    # 60% da mancha, e o texto interno caia para ~4 pt. Em dois paineis o
    # racio sobe acima de 1, o limite passa a ser a largura e o texto fica
    # legivel. Etiquetas de coluna a 40 graus: assim o seu comprimento deixa
    # de estar preso a largura da coluna.
    # Rampa P3_RAMPA (_gerador/figuras.py). O nivel 0 nao e um passo da
    # rampa -- e ausencia, e leva o NEUTRO do capitulo.
    shade = {0: "#CFCFCF", 1: "#80BCD6", 2: "#3F92B7", 3: "#186C8C"}
    n, m = len(rows), len(COLS)
    groups = [s for s in ORDER if any(r[1] == s for r in rows)]
    # 2026-09-21: reparticao explicita em vez de corte por indice, para os
    # gases industriais (um so artigo) poderem passar para o painel direito.
    # Com o corte a seguir ao cimento, os paineis ficavam em 27 e 21 linhas;
    # assim ficam em 25 e 23. Cada painel mantem a ordem de ORDER.
    ESQUERDA = ["Refinação", "Petroquímica", "Química contínua", "Cimento e cal"]
    parts = [[g for g in groups if g in ESQUERDA],
             [g for g in groups if g not in ESQUERDA]]

    GAP_G = 0.55            # espaco entre grupos de setor
    ROT = 5.4               # goteira dos rotulos, em unidades de celula
    SEP = 1.3               # separacao entre os dois paineis
    PASSO = ROT + m + SEP

    def altura(grp):
        y = 0.0
        for k, g in enumerate(grp):
            if k:
                y += GAP_G
            y += 0.95 + sum(1 for r in rows if r[1] == g)
        return y
    H = max(altura(g) for g in parts)

    fig_w, RACIO = 7.8, 1.22
    fig_h = fig_w / RACIO
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(-ROT, 2 * PASSO - ROT - SEP)
    ax.set_ylim(H + 4.0, -4.2)
    ax.axis("off")

    tot = [[0, 0] for _ in range(m)]
    for pan, grp in enumerate(parts):
        x0 = pan * PASSO
        for (lab, code, key), j in zip(COLS, range(m)):
            ax.text(x0 + j + 0.72, -0.95, lab.replace("\n", " ").replace("- ", ""),
                    ha="left", va="bottom", rotation=40, rotation_mode="anchor",
                    fontsize=6.4, color="#222222", fontweight="bold")
        ax.plot([x0 - 0.02, x0 + m], [-0.35, -0.35], color="#9A9A9A", lw=0.55)
        y = 0.0
        for k, g in enumerate(grp):
            if k:
                y += GAP_G
            ax.text(x0 - ROT + 0.05, y + 0.18, g, fontsize=7.0, fontweight="bold",
                    color="#222222", va="center")
            y += 0.95
            for r in [r for r in rows if r[1] == g]:
                ax.text(x0 - ROT + 0.28, y + 0.5, ("\u25c6 " if r[4] else "    ") + r[3],
                        fontsize=6.2, va="center", color="#222222")
                for j, v in enumerate(r[5]):
                    if v == NA:
                        ax.add_patch(Rectangle((x0 + j + 0.05, y + 0.10), 0.90, 0.80,
                                               facecolor="white", edgecolor="#BBBBBB",
                                               hatch="////", linewidth=0.4))
                    else:
                        ax.add_patch(Rectangle((x0 + j + 0.05, y + 0.10), 0.90, 0.80,
                                               facecolor=shade[v], edgecolor="white", linewidth=0.9))
                        tot[j][0] += v >= 2
                    if v != NA:
                        tot[j][1] += 1
                y += 1

    # totais, por baixo do painel esquerdo
    yt = H + 1.25
    ax.plot([-0.02, m], [yt - 0.62, yt - 0.62], color="#9A9A9A", lw=0.55)
    ax.text(-ROT + 0.05, yt, "Dois níveis mais escuros", fontsize=6.2,
            color="#222222", va="center", linespacing=1.2)
    for j in range(m):
        ax.text(j + 0.5, yt, f"{tot[j][0]}/{tot[j][1]}", ha="center", va="center",
                fontsize=6.0, color="#222222")

    # legenda numa linha propria, por baixo de tudo e a toda a largura
    yt = H + 3.0
    lx = -ROT + 0.05
    for lvl, txt in ((3, "nível mais forte"), (2, "declarado"), (1, "parcial ou proposto"),
                     (0, "não reportado"), (NA, "não aplicável")):
        if lvl == NA:
            ax.add_patch(Rectangle((lx, yt - 0.30), 0.40, 0.60, facecolor="white",
                                   edgecolor="#BBBBBB", hatch="////", linewidth=0.4))
        else:
            ax.add_patch(Rectangle((lx, yt - 0.30), 0.40, 0.60, facecolor=shade[lvl], edgecolor="none"))
        ax.text(lx + 0.52, yt, txt, fontsize=6.2, va="center", color="#333333")
        lx += 0.52 + 0.175 * len(txt) + 0.35

    fig.savefig(a.out, dpi=220, bbox_inches="tight")
    print("ok", a.out, n, "artigos |", fig_w, "x", round(fig_h, 2), "pol | racio", round(fig_w / fig_h, 2))


if __name__ == "__main__":
    main()
