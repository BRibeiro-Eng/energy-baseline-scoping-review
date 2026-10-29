#!/usr/bin/env python3
"""Tabela artigo a artigo do Corpus B para o Apendice B (2026-09-17).
Le os registos Stage C com as decisoes de verificacao aplicadas em memoria (overlay) e escreve
um longtable LaTeX. Nao escreve nos registos."""
import collections, csv, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "verification_v1"))
from overlay import effective
V = lambda e: e.get("value") if isinstance(e, dict) and "value" in e else e
out = sys.argv[1]
recs = {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(f"{ROOT}/production/stage_c/claude/outputs/rayyan-*.json"))}
recs, _ = effective(recs, os.path.join(os.path.dirname(HERE), "verification_v1/verificacao_modelo/decisoes_2026-09-17.json"))
T = json.load(open(f"{HERE}/tabelas_cap3_2026-09-17.json", encoding="utf-8")); bk = T["bibkey"]
SECT = {"petroleum refining": "refinação", "petrochemicals": "petroquímica", "cement and lime": "cimento e cal",
        "pulp and paper": "pasta e papel", "steel and primary metals (continuous production)": "siderurgia e metais",
        "continuous chemical production": "química contínua", "industrial gases": "gases industriais",
        "glass (continuous melting)": "vidro", "iron and steel": "siderurgia e metais"}
SECT.update({"cement, lime, clinker": "cimento e cal", "pulp & paper": "pasta e papel", "multiple of the above": "vários"})
def sect(s):
    if s in SECT: return SECT[s]
    for k, v in SECT.items():
        if s and s.lower().startswith(k.split(" (")[0]): return v
    return s.replace("&", "\\&")
rows = []
for k, r in recs.items():
    ms = [m for x in r["applications"] for m in x["models"]]
    sectors = sorted({sect(V(x["sector_registered"])) for x in r["applications"]})
    bc = {c["boundary_correspondence"] for m in ms for c in m.get("C5_measurement") or []}
    fr = "exata" if "exact" in bc else ("alocada" if bc & {"allocated by rule", "allocated by estimate"} else ("desvio" if "mismatch acknowledged" in bc else "n.r."))
    reg = {V(m["C6_re_estimation"]["regime"]) for m in ms}
    rg = "declarado" if reg - {"not stated", "fixed, not mentioned", "explicitly none in period", None} else "não"
    env = {V(m["C7_validity_envelope"]["statement"]) for m in ms}
    dm = "numérico" if "stated with numeric bounds" in env else ("qualitativo" if "stated qualitatively" in env else "não")
    oos = {V(m["C8_metrics"]["out_of_sample_validation"]["status"]) for m in ms}
    oo = "reportada" if "reported" in oos else ("n.a." if oos == {"not applicable"} else "não")
    rows.append((bk[k], ", ".join(sectors), len(ms), fr, rg, dm, oo, len(r["mechanisms"]), len(r["adaptations"])))
rows.sort(key=lambda x: x[0].lower())
# 2026-09-22: "Benmakhlouf" escorria da coluna do estudo, e o cabecalho a
# negrito alargou as colunas fixas e agravou o transbordo para 4,9pt. Sem
# efeito: baixar \hyphenpenalty e declarar \hyphenation{Ben-makh-louf} -- o
# nome vem de \textcite e o biblatex nao o deixa cortar. Estreitar a coluna
# do setor para 2,0cm e pior, deixa de caber "petroquimica". Resolve-se com
# \scriptsize, que e o que as tabelas densas do Apendice C ja usam: encolhe
# as colunas fixas e devolve largura a coluna X.
# ANTERIOR (sem efeito, mantido como registo do que ja se tentou):
# NAO RESOLVIDO (2026-09-22): "Benmakhlouf" escorre 2,1pt (0,7mm) da coluna
# do estudo. Tentado e sem efeito: baixar \hyphenpenalty na coluna, e declarar
# \hyphenation{Ben-makh-louf} -- o nome vem de \textcite e o biblatex nao o
# deixa cortar. Estreitar a coluna do setor para 2,0cm e pior: passa a nao
# caber "petroquimica" e o transbordo sobe para 3,7pt. Fica como esta.
L = [r"\ntzebra", r"\begin{xltabular}{\linewidth}{@{}>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}p{2.3cm}rllllrr@{}}",
     r"\caption[Corpus B: características por estudo]{Corpus~B, estudo a estudo (39 registos cartografados). Nível mais forte entre os modelos de cada estudo. Fronteira (C5): exata, alocada, desvio reconhecido ou não reportada; re-estimação (C6): regime declarado ou não; domínio (C7); fora da amostra (C8): validação com resultado reportado. Mec.\ e Adapt.: número de ocorrências. Valores com as decisões de verificação de 2026-09-17 aplicadas e os itens pendentes no valor original.}\label{tab:apB-corpus-b}\\",
     r"\hiderowcolors",
     r"\toprule", r"\textbf{Estudo} & \textbf{Setor} & \textbf{Mod.} & \textbf{Fronteira} & \textbf{Re-est.} & \textbf{Domínio} & \textbf{Fora am.} & \textbf{Mec.} & \textbf{Adapt.} \\", r"\midrule", r"\endfirsthead",
     r"\toprule", r"\textbf{Estudo} & \textbf{Setor} & \textbf{Mod.} & \textbf{Fronteira} & \textbf{Re-est.} & \textbf{Domínio} & \textbf{Fora am.} & \textbf{Mec.} & \textbf{Adapt.} \\", r"\midrule", r"\endhead",
     r"\midrule",
     r"\rowcolor{white}\multicolumn{9}{r}{\emph{continua na página seguinte}}\\",
     r"\endfoot", r"\bottomrule", r"\endlastfoot", r"\showrowcolors"]
for b, s, n, fr, rg, dm, oo, me, ad in rows:
    L.append(f"\\textcite{{{b}}} & {s} & {n} & {fr} & {rg} & {dm} & {oo} & {me} & {ad} \\\\")
L.append(r"\end{xltabular}")
open(out, "w", encoding="utf-8").write("%% Gerado por stage_c/figuras_cap3/tabela_apendice_b.py (2026-09-17). Nao editar a mao.\n"
    "{\\scriptsize\n" + "\n".join(L) + "\n}\n")
c = collections.Counter(x[3] for x in rows); print(len(rows), c, collections.Counter(x[6] for x in rows), sum(x[2] for x in rows), collections.Counter(x[1] for x in rows))
