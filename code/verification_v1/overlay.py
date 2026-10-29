"""Applies the decisions of the September 2026 model verification
(data/05-extraction-corpus-b/model-reread-2026-09/verifier/decisoes_*.json) to the Corpus B records, in memory.
Never writes to the records. States: confirmado (confirmed) · corrigido (corrected) · retirado (removed) ·
mantido (retained) · pendente_* (original value kept).
"""
import copy, json, re

TOK = re.compile(r"([A-Za-z0-9_]+)(?:\[(\d+)\])?")


def _walk(rec, path):
    parts = path.split(".")
    parent, key = None, None
    o = rec
    for p in parts:
        m = TOK.fullmatch(p)
        name, idx = m.group(1), m.group(2)
        parent, key = o, name
        o = o[name]
        if idx is not None:
            parent, key = o, int(idx)
            o = o[int(idx)]
    return parent, key, o


def effective(records, decisions_path):
    D = json.load(open(decisions_path, encoding="utf-8"))
    recs = copy.deepcopy(records)
    drop = {}
    stats = {}
    for it in D["itens"].values():
        k = it["key"]
        stats[it["estado"]] = stats.get(it["estado"], 0) + 1
        if k not in recs:
            continue
        if not it.get("keep", True):
            m = TOK.fullmatch(it["path"])
            drop.setdefault(k, []).append((m.group(1), int(m.group(2))))
            continue
        for field, (old, new) in (it.get("changes") or {}).items():
            parent, key, obj = _walk(recs[k], it["path"])
            if it["type"] in ("MEC", "ADP"):
                obj[field] = new if new not in ("",) else None
            elif isinstance(obj, dict) and "value" in obj:
                obj["value"] = new
            else:
                parent[key] = new
    for k, lst in drop.items():
        for name, idx in sorted(lst, key=lambda x: -x[1]):
            del recs[k][name][idx]
    return recs, stats
