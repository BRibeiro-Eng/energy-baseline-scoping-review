#!/usr/bin/env python3
"""Detector (c) triage builder — §3-Step-4 closure.

Partitions the 394 detector-(c) responses into the reviewer's work:
  Stratum I   — eligible, outside Corpus B, signal present, strong application,
                AND the signal names a §5.3 registered sector  -> full read
  Exploratory — same but the continuous-flow sector is NOT on the §5.3 list
                -> declared exploratory cases, never counted silently (§5.3)
  Stratum II  — signal present but application_strength in {mentioned_only, none}
                -> §5.3 excludes these by its own wording; verified sample only
  Out of A    — ineligible papers with signals; cannot enter Corpus B without
                reopening eligibility. Listed for the record.

Writes to output/fn_census/detector_c/triage/.
"""
import json, glob, os, random, sys, re, datetime
sys.path.insert(0, "output")
from corpus_profile import rosters, _get, SECTOR_RX

ROOT = os.getcwd()
D = "output/fn_census/detector_c"
T = f"{D}/triage"
os.makedirs(T, exist_ok=True)
STRONG = {"applied", "validated", "demonstrated"}
SEED_II_A, SEED_II_B = 46, 47
N_II_A, N_II_B = 25, 8

R = rosters(); C, G = R["C"], R["G"]
A, B = set(R["corpus_a"]), set(R["corpus_b"])
recs = {}
for p in glob.glob(f"{D}/responses_claude/rayyan-*.json"):
    d = json.load(open(p, encoding="utf-8")); recs[d["key"]] = d
assert len(recs) == 394, len(recs)

def page_text(key, page):
    b = json.load(open(f"output/stage0/{key}.json", encoding="utf-8"))
    for pg in b["pdf"]["pages"]:
        if pg.get("page") == page:
            return pg.get("text") or ""
    return ""

def window(key, quote, page, pad=420):
    """Surrounding source text, so the reviewer judges the signal in context."""
    txt = page_text(key, page)
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", s or "")).strip()
    nt, nq = norm(txt), norm(quote)
    i = nt.lower().find(nq.lower()[:60])
    if i < 0:
        return "[nao localizado no texto extraido desta pagina]"
    return ("…" if i > pad else "") + nt[max(0, i-pad): i+len(nq)+pad] + "…"

def meta(key):
    c, g = C.get(key, {}), G.get(key, {})
    return {
        "a8_claude": _get(c, "stage2", "sector_of_activity"),
        "a8_chatgpt": _get(g, "stage2", "sector_of_activity"),
        "a9": _get(c, "stage2", "type_of_organisation") or _get(g, "stage2", "type_of_organisation"),
        "paper_type": _get(c, "stage1", "paper_type") or _get(g, "stage1", "paper_type"),
        "level_3b_models": [_get(c, "stage1", "level_3b"), _get(g, "stage1", "level_3b")],
    }

sig = {k: d for k, d in recs.items() if (d.get("listed_sector_signals") or d.get("other_continuous_flow_signals"))}
in_a_out_b = [k for k in sig if k in A and k not in B]
strong = [k for k in in_a_out_b if recs[k].get("application_strength") in STRONG]
s1        = sorted(k for k in strong if recs[k].get("listed_sector_signals"))
explor    = sorted(k for k in strong if not recs[k].get("listed_sector_signals"))
s2        = sorted(k for k in in_a_out_b if k not in strong)
s2_listed = sorted(k for k in s2 if recs[k].get("listed_sector_signals"))
s2_other  = sorted(k for k in s2 if not recs[k].get("listed_sector_signals"))
out_of_a  = sorted(k for k in sig if k not in A)

samp_a = sorted(random.Random(SEED_II_A).sample(s2_listed, min(N_II_A, len(s2_listed))))
samp_b = sorted(random.Random(SEED_II_B).sample(s2_other,  min(N_II_B, len(s2_other))))

def clopper_upper(n, conf=0.95):
    """One-sided upper bound for x=0 successes in n: 1 - (1-conf)**(1/n)."""
    return 1 - (1 - conf) ** (1.0 / n) if n else 1.0

stamp = datetime.datetime.now().strftime("%Y-%m-%d")
summary = {
    "generated": stamp, "responses": len(recs),
    "with_any_signal": len(sig), "eligible_outside_B": len(in_a_out_b),
    "stratum_I_listed_sector": s1, "exploratory_unlisted_sector": explor,
    "stratum_II_n": len(s2), "stratum_IIa_listed_sector_n": len(s2_listed),
    "stratum_IIb_other_n": len(s2_other),
    "sample_IIa": {"seed": SEED_II_A, "n": len(samp_a), "keys": samp_a,
                   "upper_bound_if_zero": round(clopper_upper(len(samp_a)), 4)},
    "sample_IIb": {"seed": SEED_II_B, "n": len(samp_b), "keys": samp_b,
                   "upper_bound_if_zero": round(clopper_upper(len(samp_b)), 4)},
    "signals_in_ineligible_papers": out_of_a,
}
json.dump(summary, open(f"{T}/SUMMARY.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

def sig_block(k, fh):
    d = recs[k]
    for kind in ("listed_sector_signals", "other_continuous_flow_signals"):
        for s in (d.get(kind) or []):
            fh.write(f"\n**{kind}** — sector apontado: *{s.get('sector')}*  · p.{s.get('page')}\n\n")
            fh.write(f"> {s.get('signal')}\n\n")
            fh.write(f"Citação: `{s.get('quote')}`\n\n")
            fh.write("Contexto na fonte:\n\n```\n" + window(k, s.get('quote',''), s.get('page')) + "\n```\n")

with open(f"{T}/STRATUM_I.md", "w", encoding="utf-8") as fh:
    fh.write(f"# Estrato I — leitura integral ({len(s1)} papers)\n\n")
    fh.write("Elegíveis, fora do Corpus B, com sinal de **sector da lista registada §5.3**\n"
             "e `application_strength` em {applied, validated, demonstrated}.\n\n"
             "Para cada um, a decisão é a do §5.3: o paper **aplica, valida ou demonstra\n"
             "empiricamente** o modelo nesse sector? Menção, contexto teórico ou\n"
             "\"could be applied to\" não chega. Decide a partir da fonte, não do one-liner.\n\n---\n")
    for k in s1:
        m = meta(k); d = recs[k]
        fh.write(f"\n## {k}\n\n")
        fh.write(f"- `application_strength`: **{d.get('application_strength')}**\n")
        fh.write(f"- A8 (claude / chatgpt): {m['a8_claude']!r} / {m['a8_chatgpt']!r}\n")
        fh.write(f"- A9: {m['a9']!r} · paper_type: {m['paper_type']!r}\n")
        fh.write(f"- `level_3b` dos modelos: {m['level_3b_models']}\n")
        fh.write(f"- Contexto segundo o detector: {d.get('one_line')}\n")
        sig_block(k, fh)
        fh.write("\n**Veredicto do revisor:** `[ ] Corpus B`  `[ ] fora`  — justificação e citação:\n\n---\n")

with open(f"{T}/EXPLORATORY_CASES.md", "w", encoding="utf-8") as fh:
    fh.write(f"# Casos exploratórios — sector de fluxo contínuo FORA da lista §5.3 ({len(explor)} papers)\n\n")
    fh.write("O §5.3 é explícito: *\"Unlisted sector that appears continuous-flow? Do NOT\n"
             "self-classify\"*, e um paper num sector de fluxo contínuo não listado é\n"
             "reportado como **caso exploratório fora do Corpus B principal**, a menos que\n"
             "uma decisão de corpus datada e documentada acrescente o sector à lista\n"
             "**antes** de os seus papers serem contados.\n\n"
             "Estes papers têm aplicação empírica forte mas em sectores não registados.\n"
             "Ficam aqui declarados. Nenhum entra no Corpus B sem decisão datada.\n\n---\n")
    for k in explor:
        m = meta(k); d = recs[k]
        secs = sorted({(s.get("sector") or "?") for s in (d.get("other_continuous_flow_signals") or [])})
        fh.write(f"\n## {k} — {d.get('application_strength')}\n\n")
        fh.write(f"- Sectores sinalizados: {', '.join(secs)}\n")
        fh.write(f"- A8: {m['a8_claude']!r} · A9: {m['a9']!r} · paper_type: {m['paper_type']!r}\n")
        fh.write(f"- {d.get('one_line')}\n")
    fh.write("\n---\n\n## Decisão pendente do revisor\n\n"
             "`[ ] manter todos fora do Corpus B principal, reportar como exploratórios` (recomendado)\n\n"
             "`[ ] acrescentar sector(es) à lista §5.3 por decisão datada` — indicar quais e "
             "registar em `run_metadata.json` + emenda OSF **antes** de contar os papers\n")

with open(f"{T}/STRATUM_II_SAMPLE.md", "w", encoding="utf-8") as fh:
    fh.write("# Estrato II — amostra verificada\n\n")
    fh.write(f"O Estrato II são os {len(s2)} papers elegíveis, fora do Corpus B, com sinal mas com\n"
             "`application_strength` em {{mentioned_only, none}}. O §5.3 exclui-os pela sua própria\n"
             "redacção — *\"the paper must apply, validate, or empirically demonstrate\"* — pelo que o\n"
             "filtro não é uma conveniência, é o critério registado. A amostra serve para **limitar o\n"
             "erro do filtro**, não para decidir pertenças.\n\n")
    fh.write(f"Sub-estratificado por risco: IIa tem sinal de sector da lista §5.3 (mais arriscado), IIb não.\n\n")
    fh.write(f"| Sub-estrato | N | n | seed | limite sup. 95% se 0/n |\n|---|---|---|---|---|\n")
    fh.write(f"| IIa — sector §5.3 | {len(s2_listed)} | {len(samp_a)} | {SEED_II_A} | {100*clopper_upper(len(samp_a)):.1f}% |\n")
    fh.write(f"| IIb — outro sinal | {len(s2_other)} | {len(samp_b)} | {SEED_II_B} | {100*clopper_upper(len(samp_b)):.1f}% |\n\n")
    fh.write("Para cada paper da amostra: o sinal é a aplicação do próprio paper, ou uma citação /\n"
             "menção? Se for aplicação própria num sector §5.3, é um falso negativo do filtro e\n"
             "dispara o §6a (expansão de léxico + nova passagem do detector (b)).\n\n---\n")
    for label, keys in (("IIa", samp_a), ("IIb", samp_b)):
        fh.write(f"\n## Amostra {label}\n")
        for k in keys:
            d = recs[k]; m = meta(k)
            secs = sorted({(s.get("sector") or "?") for s in
                           (d.get("listed_sector_signals") or []) + (d.get("other_continuous_flow_signals") or [])})
            fh.write(f"\n### {k} — `{d.get('application_strength')}`\n")
            fh.write(f"- sectores sinalizados: {', '.join(secs) or '—'}\n")
            fh.write(f"- A8: {m['a8_claude']!r} · A9: {m['a9']!r}\n- {d.get('one_line')}\n")
            for s in (d.get("listed_sector_signals") or [])[:2]:
                fh.write(f"- p.{s.get('page')}: `{(s.get('quote') or '')[:180]}`\n")
            fh.write("- veredicto: `[ ] citação/menção (filtro correcto)`  `[ ] aplicação própria (FALSO NEGATIVO)`\n")

with open(f"{T}/INELIGIBLE_WITH_SIGNALS.md", "w", encoding="utf-8") as fh:
    fh.write(f"# Sinais em papers inelegíveis ({len(out_of_a)})\n\n"
             "Papers fora do Corpus A (falharam a elegibilidade metodológica) onde o detector (c)\n"
             "encontrou sinal de fluxo contínuo. **Não podem entrar no Corpus B**: o Corpus B é um\n"
             "subconjunto do Corpus A. Ficam registados porque um sinal não registado não pode ser\n"
             "revisitado, e porque a elegibilidade de qualquer um deles pode ser reaberta se o\n"
             "revisor quiser — nesse caso o paper volta ao Tier-1, não ao Corpus B directamente.\n\n")
    for k in out_of_a:
        d = recs[k]
        fh.write(f"- `{k}` — {d.get('application_strength')} — "
                 f"listed={len(d.get('listed_sector_signals') or [])} "
                 f"other={len(d.get('other_continuous_flow_signals') or [])} — {d.get('one_line','')[:120]}\n")

print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in summary.items()}, indent=1, ensure_ascii=False))
print("\nEstrato I:", s1)
print("Exploratorios:", len(explor))
print("escrito em", T)
