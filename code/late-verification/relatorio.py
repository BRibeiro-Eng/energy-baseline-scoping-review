#!/usr/bin/env python3
"""relatorio.py — resultados da Emenda 3 a partir de tarefas/ e respostas/.

    python3 verificacao_2026-10/relatorio.py      # escreve RESULTADOS.md e resultados.json

Relata cada instrumento em separado, como a emenda exige: contagens x/n, intervalos exatos de
Clopper–Pearson (bilateral 95%) e o limite superior unilateral 95%. Nunca agrega entre instrumentos
ou campos. O que não está concluído aparece como tal, com o n concluído.
"""
import json, math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS, ANS = HERE / "tarefas", HERE / "respostas"


def binom_cdf(k, n, p):
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _bisect(f, lo=0.0, hi=1.0, it=80):
    for _ in range(it):
        mid = (lo + hi) / 2
        if f(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def cp(x, n, conf=0.95):
    """Clopper–Pearson exato: (lo, hi) bilateral."""
    if n == 0:
        return (None, None)
    a = 1 - conf
    lo = 0.0 if x == 0 else _bisect(lambda p: 1 - binom_cdf(x - 1, n, p) >= a / 2)
    hi = 1.0 if x == n else _bisect(lambda p: binom_cdf(x, n, p) <= a / 2)
    return (lo, hi)


def upper1(x, n, conf=0.95):
    """Limite superior unilateral exato."""
    if n == 0:
        return None
    if x == n:
        return 1.0
    return _bisect(lambda p: binom_cdf(x, n, p) <= 1 - conf)


def pct(v):
    return "—" if v is None else f"{100 * v:.1f}%"


def fmt(x, n):
    lo, hi = cp(x, n)
    return f"{x}/{n} (IC95% {pct(lo)}–{pct(hi)}; sup. unilateral {pct(upper1(x, n))})" if n else "0/0"


def load(m):
    p = TASKS / f"{m}.json"
    mod = json.load(open(p, encoding="utf-8")) if p.exists() else None
    st = defaultdict(dict)
    q = ANS / f"{m}.jsonl"
    if q.exists():
        for line in open(q, encoding="utf-8"):
            if line.strip():
                e = json.loads(line)
                s = st[e["task_id"]]
                if e["phase"] == "reveal":
                    s.setdefault("revealed_at", e["ts"])
                else:
                    s[e["phase"]] = e
                    s["time_s"] = s.get("time_s", 0) + float(e.get("duration_s") or 0)
    return mod, st


def ref(m):
    p = TASKS / "_ref" / f"{m}.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else {}


def parse_cell(v):
    import ast
    v = (v or "").strip()
    if v in ("", "None", "nan"):
        return None
    if v in ("True", "False"):
        return v == "True"
    if v.startswith("["):
        try:
            return ast.literal_eval(v)
        except Exception:
            return v
    return v


def norm_val(ftype, v):
    if ftype == "multienum":
        return tuple(sorted(str(x).strip().lower() for x in (v or [])))
    if v in (None, "", "__null__"):
        return None
    return str(v).strip().lower()


def hours(st):
    return sum(s.get("time_s", 0) for s in st.values()) / 3600


def r_d13():
    mod, st = load("d13")
    if not mod:
        return None
    out = {"frame": mod["frame"]}
    for stratum in ("lexicon", "sample"):
        ts = [t for t in mod["tasks"] if t["stratum"] == stratum]
        ans = [st[t["id"]]["answer"]["answer"] for t in ts if "answer" in st[t["id"]]]
        miss = [t["id"] for t in ts if "answer" in st[t["id"]] and st[t["id"]]["answer"]["answer"]["decision"] == "should_have_proceeded"]
        out[stratum] = {"n_tasks": len(ts), "n_done": len(ans), "should_have_proceeded": miss,
                        "no_abstract_done": sum(1 for t in ts if "answer" in st[t["id"]] and not t.get("abstract"))}
    s = out["sample"]
    out["sample_rate"] = fmt(len(s["should_have_proceeded"]), s["n_done"])
    out["escalation_binding"] = len(s["should_have_proceeded"]) >= 1
    out["hours"] = round(hours(st), 2)
    return out


def r_d11(m="d11"):
    mod, st = load(m)
    if not mod:
        return None
    R = ref(m)
    flips, done, by_field, changes = [], 0, Counter(), []
    for t in mod["tasks"]:
        s = st.get(t["id"], {})
        if "final" in s:
            done += 1
            mine = s["commit"]["answer"].get("value") == "true"
            if mine != (R[t["id"]]["original_final"] is True):
                flips.append({"id": t["id"], "field": t["field"], "final_value": s["final"]["answer"].get("final_value"),
                              "commit_ts": s["commit"]["ts"]})
                by_field[t["field"]] += 1
            fv = s["final"]["answer"].get("final_value")
            if fv is not None and (fv == "true") != (R[t["id"]]["original_final"] is True):
                changes.append({"id": t["id"], "field": t["field"], "original": R[t["id"]]["original_final"], "final": fv == "true"})
    esc = [f for f, c in by_field.items() if c > 1]
    return {"frame": mod["frame"], "n_done": done, "n": len(mod["tasks"]), "flips": len(flips), "flip_list": flips,
            "membership_changes": changes,
            "flips_by_field": dict(by_field), "escalation_fields": esc, "hours": round(hours(st), 2)}


def r_d7a():
    mod, st = load("d7a")
    if not mod:
        return None
    fams = defaultdict(lambda: {"units_with_hits": 0, "done": 0, "a_none": 0, "b_coded": 0, "c_missed": 0, "missed": []})
    for u in mod["auto_no_hit"]:
        fams[u["family"]].setdefault("no_hit", 0)
        fams[u["family"]]["no_hit"] += 1
    for t in mod["tasks"]:
        f = fams[t["family"]]
        f["units_with_hits"] += 1
        s = st.get(t["id"], {})
        if "answer" in s:
            a = s["answer"]["answer"]
            f["done"] += 1
            f[a["decision"]] += 1
            if a["decision"] == "c_missed":
                f["missed"].append({"key": t["key"], "page": a.get("page"), "field": a.get("field_affected"),
                                    "corrected_value": a.get("corrected_value"), "quote": a.get("quote")})
    for fid, f in fams.items():
        f["complete"] = f["done"] == f["units_with_hits"]
    return {"frame": mod["frame"], "families": dict(fams), "hours": round(hours(st), 2)}


def r_d7b():
    mod, st = load("d7b")
    if not mod:
        return None
    c, by_type, errors = Counter(), defaultdict(Counter), []
    for t in mod["tasks"]:
        s = st.get(t["id"], {})
        if "answer" in s:
            d = s["answer"]["answer"]["decision"]
            c[d] += 1
            by_type[t["type"]][d] += 1
            if d == "incorrect":
                errors.append({"id": t["id"], "key": t["key"], "path": t["path"], "current": t["current"],
                               "correct_value": s["answer"]["answer"].get("correct_value")})
    n = c["correct"] + c["incorrect"]
    return {"frame": mod["frame"], "done": sum(c.values()), "counts": dict(c), "rate": fmt(c["incorrect"], n),
            "by_type": {k: dict(v) for k, v in by_type.items()}, "errors": errors, "hours": round(hours(st), 2)}


def r_d7c():
    mod, st = load("d7c")
    if not mod:
        return None
    R = ref("d7c")
    diffs, rc, done, finals = Counter(), Counter(), 0, {}
    for t in mod["tasks"]:
        s = st.get(t["id"], {})
        if "final" in s:
            done += 1
            a = s["final"]["answer"]; c = s["commit"]["answer"]; r = R[t["id"]]
            for fd in t["fields"]:
                f = fd["id"]
                if c.get(f) != r.get(f):
                    diffs[f] += 1
                if a.get(f + "_final") != c.get(f):
                    rc[f] += 1
            finals[t["key"]] = {fd["id"]: a.get(fd["id"] + "_final") for fd in t["fields"]}
    return {"n_done": done, "n": len(mod["tasks"]), "diffs_by_field": dict(diffs), "reveal_changes_by_field": dict(rc),
            "final_map": finals, "hours": round(hours(st), 2)}


def r_d10():
    mod, st = load("d10")
    if not mod:
        return None
    R = ref("d10")
    nv, raw, adj, cls = Counter(), Counter(), Counter(), defaultdict(Counter)
    done_order = []
    for t in mod["tasks"]:  # na ordem do sorteio
        s = st.get(t["id"], {})
        if "final" not in s:
            continue
        done_order.append(t["id"])
        a = s["final"]["answer"]; cm = s["commit"]["answer"]; r = R[t["id"]]
        for fd in t["fields"]:
            f = fd["id"]
            nv[f] += 1
            c = a.get("c_" + f)
            if fd.get("type") in ("enum", "multienum"):
                differs = norm_val(fd["type"], cm.get("v_" + f)) != norm_val(fd["type"], parse_cell(r[f]["claude"]))
            else:
                differs = c not in (None, "same")
            if differs:
                raw[f] += 1
            cls[f][c] += 1
            if c == "extraction_error":
                adj[f] += 1
    # prefixo contíguo do sorteio (a redução registada para 30 só vale para um prefixo)
    order = [t["id"] for t in mod["tasks"]]
    prefix = 0
    for k in order:
        if k in done_order:
            prefix += 1
        else:
            break
    fields = {}
    for f in sorted(nv):
        fields[f] = {"n_v": nv[f], "raw_e_v": raw[f], "raw": fmt(raw[f], nv[f]), "adjudicated_e_v": adj[f],
                     "adjudicated": fmt(adj[f], nv[f]), "classes": dict(cls[f]), "escalation_e_v_ge_3": raw[f] >= 3}
    return {"frame": mod["frame"], "papers_done": len(done_order), "contiguous_prefix": prefix,
            "prefix_is_srs": prefix == len(done_order), "fields": fields, "hours": round(hours(st), 2)}


def md(res):
    L = [f"# Resultados — Emenda 3 (verificação tardia)", "", f"Gerado {datetime.now().isoformat(timespec='minutes')} a partir de `tarefas/` e `respostas/`. Cada instrumento é relatado em separado.", ""]
    d = res.get("d13")
    if d:
        L += ["## D13 · Exclusões no rastreio", f"- Frame: {d['frame']['excluded']} excluídos; resumo disponível em {d['frame']['with_abstract']}.",
              f"- Censo do léxico: {d['lexicon']['n_done']}/{d['lexicon']['n_tasks']} revistos; devia ter seguido: {len(d['lexicon']['should_have_proceeded'])} {d['lexicon']['should_have_proceeded'] or ''}",
              f"- Amostra aleatória: {d['sample']['n_done']}/{d['sample']['n_tasks']} revistos; devia ter seguido: **{d['sample_rate']}** {d['sample']['should_have_proceeded'] or ''}",
              f"- Escalada vinculativa (re-rastreio integral): **{'SIM' if d['escalation_binding'] else 'não'}**", f"- Tempo registado: {d['hours']} h", ""]
    for key, title in (("d11", "## D11 · Teste–reteste"), ("d11x", "## D11·E · Escalada do reteste")):
        d = res.get(key)
        if not d:
            continue
        L += [title, f"- Concluídas: {d['n_done']}/{d['n']}; flips: **{d['flips']}** {d['flips_by_field'] or ''}",
              f"- Campos com escalada (>1 flip): {d['escalation_fields'] or 'nenhum'}",
              f"- Alterações de pertença (valor final ≠ original): {len(d['membership_changes'])} {[c['id'] for c in d['membership_changes']] or ''}",
              f"- Tempo: {d['hours']} h", ""]
        for x in d["flip_list"]:
            L.append(f"  - flip {x['id']} → final {x['final_value']} (commit {x['commit_ts']})")
        L.append("")
    d = res.get("d7a")
    if d:
        L += ["## D7·A · Censo de ausências por léxico", "| Família | unid. c/ ocorrências | sem ocorrência | revistas | (a) | (b) | (c) omissões | completa |", "|---|---|---|---|---|---|---|---|"]
        for f, v in sorted(d["families"].items()):
            L.append(f"| {f} | {v['units_with_hits']} | {v.get('no_hit', 0)} | {v['done']} | {v['a_none']} | {v['b_coded']} | **{v['c_missed']}** | {'sim' if v['complete'] else 'não'} |")
        for f, v in sorted(d["families"].items()):
            for x in v["missed"]:
                L.append(f"- ({f}) {x['key']} p.{x['page']} · {x['field']} → {x['corrected_value']}")
        L += [f"- Tempo: {d['hours']} h", ""]
    d = res.get("d7b")
    if d:
        L += ["## D7·B · Amostra de células", f"- Frame: {d['frame']['kept']} células (de {d['frame']['items_368']}); amostra {d['frame']['n_sample']}; revistas {d['done']}.",
              f"- Incorretas: **{d['rate']}**; não determináveis: {d['counts'].get('undetermined', 0)}.", f"- Por tipo: {d['by_type']}", f"- Tempo: {d['hours']} h", ""]
        for e in d["errors"]:
            L.append(f"  - {e['id']} {e['key']} `{e['path']}` → {e['correct_value']}")
        L.append("")
    d = res.get("d10")
    if d:
        L += ["## D10 · Auditoria Level-A", f"- Relatórios concluídos: {d['papers_done']}/40 (prefixo contíguo do sorteio: {d['contiguous_prefix']}{'' if d['prefix_is_srs'] else ' — ATENÇÃO: há concluídos fora do prefixo; só o prefixo conta como AAS'}).",
              "| Campo | n_v | e_v bruto (métrica registada) | e_v adjudicado | ≥3? |", "|---|---|---|---|---|"]
        for f, v in d["fields"].items():
            L.append(f"| {f} | {v['n_v']} | {v['raw']} | {v['adjudicated']} | {'**sim**' if v['escalation_e_v_ge_3'] else 'não'} |")
        L += [f"- Tempo: {d['hours']} h", ""]
    d = res.get("d7c")
    if d:
        L += ["## D7·C · Mapa de refinação/petroquímica", f"- Concluídos: {d['n_done']}/{d['n']}.",
              f"- Diferenças leitura vs codificado, por campo: {d['diffs_by_field'] or 'nenhuma'}", f"- Alterações após revelação: {d['reveal_changes_by_field'] or 'nenhuma'}", f"- Tempo: {d['hours']} h", ""]
    return "\n".join(L)


def main():
    res = {"d13": r_d13(), "d11": r_d11(), "d11x": r_d11("d11x"), "d7a": r_d7a(), "d7b": r_d7b(), "d10": r_d10(), "d7c": r_d7c()}
    json.dump(res, open(HERE / "resultados.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    (HERE / "RESULTADOS.md").write_text(md(res), encoding="utf-8")
    print(md(res))


if __name__ == "__main__":
    main()
