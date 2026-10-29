#!/usr/bin/env python3
"""d14_yield.py — rendimento por string de pesquisa (Emenda 3 §5).

Põe os exports em verificacao_2026-10/dados/d14/ com estes nomes (a extensão pode variar):
    scopus_A.csv  scopus_B.csv     (Scopus → Export → CSV, com "Title", "DOI", "Year")
    wos_A.txt     wos_B.txt        (WoS → Export → Tab delimited file, Full Record; campos TI, DI, PY)
Depois:
    python3 verificacao_2026-10/d14_yield.py
Escreve dados/d14/D14_RESULTADOS.md e d14_resultados.json. Só a biblioteca padrão.
"""
import csv, json, os, re, sys, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("VT_ROOT") or HERE.parent).resolve()  # VT_ROOT só para testes
D = HERE / "dados" / "d14"
csv.field_size_limit(10 ** 8)


def nt(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def nd(d):
    d = (d or "").strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d) or None


def read_export(p):
    enc = "utf-8-sig"
    txt = p.read_text(encoding=enc, errors="replace")
    delim = "\t" if p.suffix.lower() == ".txt" or txt.split("\n", 1)[0].count("\t") > 3 else ","
    rows = list(csv.DictReader(txt.splitlines(), delimiter=delim))
    out = []
    for r in rows:
        title = r.get("Title") or r.get("TI") or r.get("Article Title") or ""
        doi = r.get("DOI") or r.get("DI") or ""
        year = r.get("Year") or r.get("PY") or ""
        out.append({"title": title, "doi": nd(doi), "nt": nt(title), "year": year})
    return out


def main():
    arts = list(csv.DictReader(open(ROOT / "data" / "articles.csv", encoding="utf-8")))
    lab = {}
    for a in arts:
        m = re.search(r'"Bernardo"=>"([A-Za-z]+)"', a.get("notes") or "")
        lab[a["key"]] = m.group(1) if m else None
    A = set()
    for x in csv.DictReader(open(ROOT / "bibliometrics/results/corpus_a_registado/tables/cell_provenance.csv", encoding="utf-8-sig")):
        A.add(x["paper_id"])
    rl = json.load(open(ROOT / "output/fn_census/detector_c/ROSTER_LOCK_2026-09-12.json", encoding="utf-8"))
    B = set(rl["sector_priority_head_25"] + rl["random_sub_sample_15"] + rl["ai_prefill_plus_verification"]) - {"rayyan-472535628", "rayyan-472535750"}
    sets = {"screened": {a["key"] for a in arts}, "sought": {k for k, v in lab.items() if v in ("Included", "Maybe")}, "A": A, "B": B}
    by_doi = {nd(a["doi"]): a["key"] for a in arts if nd(a["doi"])}
    by_t = {}
    for a in arts:
        by_t.setdefault(nt(a["title"]), a["key"])
    files = {}
    for p in sorted(D.glob("*")):
        m = re.match(r"^(scopus|wos)_([AB])\.", p.name, re.I)
        if m:
            files[(m.group(1).lower(), m.group(2).upper())] = p
    if not files:
        sys.exit(f"Sem exports em {D}. Nomes esperados: scopus_A.csv, scopus_B.csv, wos_A.txt, wos_B.txt")
    res, hit_any = {}, set()
    for (db, s), p in sorted(files.items()):
        rows = read_export(p)
        keys, how = set(), {"doi": 0, "title": 0}
        for r in rows:
            k = by_doi.get(r["doi"]) if r["doi"] else None
            if k:
                how["doi"] += 1
            else:
                k = by_t.get(r["nt"])
                if k:
                    how["title"] += 1
            if k:
                keys.add(k)
        hit_any |= keys
        res[f"{db}_{s}"] = {"file": p.name, "exported": len(rows), "matched": how,
                            **{name: len(keys & S) for name, S in sets.items()}, "_keys": sorted(keys)}
    for s in ("A", "B"):
        u = set()
        for (db, ss) in files:
            if ss == s:
                u |= set(res[f"{db}_{ss}"]["_keys"])
        res[f"string_{s}_union"] = {name: len(u & S) for name, S in sets.items()}
    res["unmatched_by_any"] = {name: len(S - hit_any) for name, S in sets.items()}
    res["unmatched_keys_screened"] = sorted(sets["screened"] - hit_any)
    json.dump(res, open(D / "d14_resultados.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# D14 · Rendimento por string", "", "| Export | exportados | ligados por DOI / título | dos 925 | dos 599 | Corpus A | Corpus B |", "|---|---|---|---|---|---|---|"]
    for k, v in res.items():
        if k.startswith(("scopus_", "wos_")):
            L.append(f"| {k} | {v['exported']} | {v['matched']['doi']} / {v['matched']['title']} | {v['screened']} | {v['sought']} | {v['A']} | {v['B']} |")
    for s in ("A", "B"):
        v = res[f"string_{s}_union"]
        L.append(f"| **String {s} (Scopus ∪ WoS)** | | | {v['screened']} | {v['sought']} | {v['A']} | {v['B']} |")
    v = res["unmatched_by_any"]
    L.append(f"| Sem correspondência em nenhum export | | | {v['screened']} | {v['sought']} | {v['A']} | {v['B']} |")
    L += ["", "Registos publicados depois de 24/02/2026 que os exports tragam são ignorados por construção (não existem nos 925)."]
    (D / "D14_RESULTADOS.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
