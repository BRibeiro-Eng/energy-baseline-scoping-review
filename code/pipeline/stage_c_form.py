#!/usr/bin/env python3
"""Render a Stage C record as a readable extraction form — one markdown file per paper.

  /usr/local/bin/python3 output/stage_c_form.py --surface claude --all

WHY. The record is JSON and the dossier is prose; neither is the thing you keep open while
writing a results paragraph. This is that thing: every extracted cell laid out in reading order,
each with its value, its evidence quote, its page, how the extractor says it knows
(`support_class`), and the triage priority of the cell. Nothing is computed here and nothing is
re-judged — it is the record, rendered.

Every form carries the verification level in its header, because a form that does not say what
level it is invites being read as verified.
"""
import argparse, csv, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT + "/output")
OUT = "output/forms"


def val(x):
    return x.get("value") if isinstance(x, dict) else x


def ev(o, indent="  "):
    """value · support_class · p.N + the quote, for one envelope object."""
    if not isinstance(o, dict):
        return f"{indent}- {o!r}"
    v = o.get("value")
    # An object with no `value` key at all is not an empty value -- mechanisms and adaptations
    # carry their meaning in the axes, printed by the caller. Saying "(vazio)" there invented an
    # emptiness the record does not contain.
    bits = []
    if "value" in o:
        bits.append(f"**{v}**" if v not in (None, "") else "*(vazio)*")
    if o.get("support_class"):
        bits.append(str(o["support_class"]))
    if o.get("absence_basis"):
        bits.append("ausência: " + str(o["absence_basis"]))
    if o.get("page") is not None:
        p = f"p.{o['page']}"
        if o.get("locator_corrected"):
            p += f" (corrigida de p.{o.get('page_as_recorded')})"
        bits.append(p)
    for extra in ("other_verbatim", "cause_other_verbatim", "effect_other_verbatim",
                  "adaptation_other_verbatim", "energy_vector_other_verbatim"):
        if o.get(extra):
            bits.append(f'{extra}: "{o[extra]}"')
    line = (indent + " · ".join(bits)) if bits else indent.rstrip()
    q = o.get("evidence_quote")
    if q:
        q = " ".join(str(q).split())
        line += f'\n{indent}  > "{q}"'
    return line


def item(prefix, obj):
    """One bullet whose quote line is indented to sit inside the bullet, not beside it."""
    body = ev(obj, "").lstrip()
    pad = " " * len(prefix)
    return prefix + body.replace("\n  > ", "\n" + pad + "> ")


def block(title, obj, keys=None, indent="  "):
    if obj is None:
        return []
    L = [f"{indent}**{title}**"]
    items = obj.items() if isinstance(obj, dict) else []
    for k, v in items:
        if keys and k not in keys:
            continue
        if isinstance(v, dict) and ("value" in v or "evidence_quote" in v):
            L.append(item(f"{indent}- `{k}` ", v))
        elif isinstance(v, list):
            for i, it in enumerate(v):
                L.append(item(f"{indent}- `{k}[{i}]` ", it)
                         if isinstance(it, dict) else f"{indent}- `{k}[{i}]` {it}")
        elif v not in (None, "", [], {}):
            L.append(f"{indent}- `{k}`: {v}")
    return L if len(L) > 1 else []


def priorities(key):
    """path -> priority, from the triage worklist, so the form shows where reading was due."""
    out = {}
    p = "production/stage_c/claude/triage_worklist.csv"
    if not os.path.isfile(p):
        return out
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if r.get("paper") == key:
            out[r["path"]] = r["priority"]
    return out


HEADER = """> **Nível de verificação deste formulário.** Extracção de superfície única
> (Claude Code CLI, prompt v2.3.0-C, esquema congelado
> `d855254b73a8640b4e13255876a3021ae9da699e1bf04bb4db3d5b2444e883ff`), com **todas as citações
> ancoradas à página** pelo verificador do protocolo. **Não houve verificação humana
> independente da codificação** (V1/V2/V3 não executados — ver §9 do protocolo). Os valores
> abaixo são a leitura do extractor com a prova à vista, não propriedades verificadas da
> literatura. Cita a citação, não a célula."""


def render(key, surface):
    rec = json.load(open(f"production/stage_c/{surface}/outputs/{key}.json", encoding="utf-8"))
    pri = priorities(key)
    npri = {}
    for path, p in pri.items():
        npri[p] = npri.get(p, 0) + 1
    L = [f"# Formulário de extracção — {key}", "", HEADER, "",
         "Células por prioridade de triagem: "
         + (", ".join(f"{k} {npri[k]}" for k in sorted(npri)) or "—"),
         "", "---", ""]

    apps = rec.get("applications") or []
    L += [f"## Applications ({len(apps)})", ""]
    for ai, a in enumerate(apps):
        L += [f"### A{ai+1} — {val(a.get('sector_registered'))}", ""]
        for f in ("sector_verbatim", "sector_registered", "refinery_or_petrochemical_case",
                  "scale_of_application", "scope_description", "country_region",
                  "baseline_period_start", "baseline_period_end"):
            if a.get(f) is not None:
                L.append(item(f"- `{f}` ", a[f]))
        L.append("")
        for mi, m in enumerate(a.get("models") or []):
            L += [f"#### Modelo M{mi+1}" + (f" — {m.get('model_id')}" if m.get("model_id") else ""), ""]
            for cname in ("C1_dependent_variable", "C2_model_form", "C3_variables",
                          "C3_variables_absence", "C4_data", "C5_measurement",
                          "C6_re_estimation", "C7_validity_envelope", "C8_metrics",
                          "C9_uncertainty", "C10_normalisation", "C11_aggregation",
                          "C12_data_requirements"):
                if cname not in m:
                    continue
                v = m[cname]
                if isinstance(v, list):
                    if not v:
                        continue
                    L.append(f"  **{cname}** ({len(v)})")
                    for i, it in enumerate(v):
                        if isinstance(it, dict) and ("value" in it or "evidence_quote" in it):
                            L.append(item(f"  - [{i}] ", it))
                        elif isinstance(it, dict):
                            L += block(f"[{i}]", it, indent="    ")
                        else:
                            L.append(f"  - [{i}] {it}")
                    L.append("")
                elif isinstance(v, dict):
                    if "value" in v or "evidence_quote" in v:
                        L += [item(f"  **{cname}** ", v), ""]
                    else:
                        b = block(cname, v)
                        if b:
                            L += b + [""]
            L.append("")

    for name, title in (("mechanisms", "Mecanismos"), ("adaptations", "Adaptações"),
                        ("implementation_barriers", "Barreiras de implementação"),
                        ("study_limitations", "Limitações declaradas pelo estudo")):
        items = [x for x in (rec.get(name) or []) if isinstance(x, dict)]
        L += [f"## {title} ({len(items)})", ""]
        for i, it in enumerate(items):
            head = []
            for k in ("mechanism_cause", "mechanism_effect_on_model", "adaptation",
                      "limitation", "claim_status", "normative_framing", "status",
                      "addresses_mechanism", "also_constrains_model", "refers_to"):
                if it.get(k) is not None:
                    head.append(f"`{k}`={val(it[k])}")
            L.append(f"**{i+1}.** " + " · ".join(head))
            for k in ("value", "evidence_quote", "page", "support_class"):
                pass
            L.append(item("  ", it) if ("evidence_quote" in it or "value" in it) else "")
            # Only the free-text companions, and only when there are any: an empty key list
            # used to fall through the `if keys` guard and dump the whole object back.
            ks = [k for k in it if k.endswith("_verbatim") or k == "searched_terms"]
            if ks:
                L += ["  " + ", ".join(f"`{k}`: \"{it[k]}\"" for k in ks if it.get(k))]
            L.append("")
        L.append("")

    c13 = rec.get("C13_reproducibility") or {}
    if c13:
        L += ["## C13 — reprodutibilidade", ""]
        for k, v in c13.items():
            L.append(item(f"- `{k}` ", v) if isinstance(v, dict) else f"- `{k}`: {v}")
        L.append("")
    ad = rec.get("absence_declarations") or {}
    if ad:
        L += ["## Declarações de ausência", ""]
        for k, v in ad.items():
            L.append(f"- `{k}`: {json.dumps(v, ensure_ascii=False)}")
        L.append("")
    L += ["---", "",
          f"Dossier deste paper: `output/dossiers/{key}.md` · "
          f"registo: `production/stage_c/{surface}/outputs/{key}.json`"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", required=True)
    ap.add_argument("--key")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    keys = ([a.key] if a.key else
            sorted(os.path.basename(p)[:-5]
                   for p in glob.glob(f"production/stage_c/{a.surface}/outputs/rayyan-*.json")))
    idx = ["# Formulários de extracção — Stage C", "", HEADER, "",
           "| paper | applications | modelos | mecanismos | adaptações | formulário | dossier |",
           "|---|---|---|---|---|---|---|"]
    for k in keys:
        txt = render(k, a.surface)
        open(f"{OUT}/{k}.md", "w", encoding="utf-8").write(txt)
        rec = json.load(open(f"production/stage_c/{a.surface}/outputs/{k}.json", encoding="utf-8"))
        apps = rec.get("applications") or []
        nm = sum(len(x.get("models") or []) for x in apps)
        dp = f"output/dossiers/{k}.md"
        idx.append(f"| `{k}` | {len(apps)} | {nm} | {len(rec.get('mechanisms') or [])} | "
                   f"{len(rec.get('adaptations') or [])} | [form]({k}.md) | "
                   + (f"[dossier](../dossiers/{k}.md)" if os.path.isfile(dp) else "—") + " |")
        print(k)
    open(f"{OUT}/INDEX.md", "w", encoding="utf-8").write("\n".join(idx) + "\n")
    print(f"\n{len(keys)} formulários em {OUT}")


if __name__ == "__main__":
    main()
