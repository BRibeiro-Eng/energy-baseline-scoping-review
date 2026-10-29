#!/usr/bin/env python3
"""Visualizador de triagem do censo FN — Validation Protocol C-2.3 §3-Step-4.

    /usr/local/bin/python3 output/fn_census/triage/serve_triage.py
    http://127.0.0.1:5052

Mostra o paper ao lado dos excertos que o puseram na lista. Grava veredictos no
mesmo formato do verdict.py. Nao decide nada: os botoes sao teus.
"""
import datetime, json, re, sys
from pathlib import Path
from flask import Flask, jsonify, request, send_file, Response

T = Path(__file__).resolve().parent
O = T.parent.parent
ROOT = O.parent
sys.path.insert(0, str(O))
from fn_hunt import _compile, CONTINUOUS_PROCESS_TERMS

STRONG = {"refinery", "refining", "petrochemical", "clinker", "blast furnace",
          "steelmaking", "pulp and paper", "paper mill", "ammonia", "ethylene",
          "olefin", "sulfuric acid", "sulphuric acid", "chlor-alkali",
          "industrial gases", "air separation", "glass furnace", "glass melting", "kiln"}
SECTORS = ["petroleum refining", "petrochemicals", "cement/lime/clinker",
           "pulp and paper", "steel/primary metals", "continuous chemicals",
           "industrial gases", "glass", "continuous-unlisted"]
KEY_RE = re.compile(r"rayyan-\d+")
app = Flask(__name__)

SERVED = {}          # key -> instante em que o paper foi servido (para dwell_seconds)

def sample_keys():
    """Modo amostra: quando SAMPLE.json existe, a fila e' so' a amostra sorteada."""
    p = T / "SAMPLE.json"
    return set(json.loads(p.read_text())["keys"]) if p.is_file() else None


def queue():
    out = []
    for tier in ("B", "A"):                      # skims primeiro
        for c in json.loads((T / f"QUEUE_{tier}.json").read_text()):
            c["tier"] = c.get("tier", tier)
            out.append(c)
    seen, uniq = set(), []
    for c in out:
        if c["key"] not in seen:
            seen.add(c["key"]); uniq.append(c)
    sk = sample_keys()
    if sk is not None:
        uniq = [c for c in uniq if c["key"] in sk]
    return uniq


def verdict_of(key):
    p = T / "verdicts" / f"{key}.json"
    return json.loads(p.read_text()) if p.is_file() else None


def bundle(key):
    p = O / "stage0" / f"{key}.json"
    return json.loads(p.read_text()) if p.is_file() else {}


def contexts(key, terms):
    pages = (bundle(key).get("pdf") or {}).get("pages") or []
    pats = _compile(terms or CONTINUOUS_PROCESS_TERMS)
    out = {}
    for pg in pages:
        n, text = pg.get("page"), pg.get("text") or ""
        for term, pat in pats:
            for m in pat.finditer(text):
                hits = out.setdefault(term, [])
                if len(hits) >= 4:
                    break
                s, e = max(0, m.start() - 220), min(len(text), m.end() + 220)
                hits.append({"page": n,
                             "before": re.sub(r"\s+", " ", text[s:m.start()]),
                             "hit": text[m.start():m.end()],
                             "after": re.sub(r"\s+", " ", text[m.end():e])})
    return [{"term": t, "strong": t in STRONG, "hits": h}
            for t, h in sorted(out.items(), key=lambda kv: (kv[0] not in STRONG, kv[0]))]


def ground(quote, page, pages):
    try:
        from grounding import ground_quote
        return ground_quote(quote, page, pages), "canonico"
    except ImportError:
        norm = lambda s: re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", s or "")).strip().lower()
        tgt = next((p.get("text") for p in pages if p.get("page") == page), "")
        return {"grounded": norm(quote) in norm(tgt)}, "reduzido (sem rapidfuzz)"


@app.route("/api/queue")
def api_queue():
    rows = []
    for c in queue():
        v = verdict_of(c["key"])
        rows.append({"key": c["key"], "tier": c["tier"], "year": c.get("year"),
                     "title": c.get("title"), "terms": c.get("terms") or [],
                     "flags": c.get("model_flag_reasons") or [],
                     "verdict": v["verdict"] if v else None})
    return jsonify({"rows": rows, "sectors": SECTORS,
                    "mode": "amostra n=%d (seed 45)" % len(rows) if sample_keys() else "censo completo"})


@app.route("/api/paper/<key>")
def api_paper(key):
    if not KEY_RE.fullmatch(key):
        return jsonify({"error": "bad key"}), 404
    c = next((x for x in queue() if x["key"] == key), None)
    if not c:
        return jsonify({"error": "not in queue"}), 404
    b = bundle(key)
    SERVED[key] = datetime.datetime.now()
    return jsonify({**c, "n_pages": (b.get("pdf") or {}).get("n_pages"),
                    "contexts": contexts(key, c.get("terms")),
                    "verdict": verdict_of(key)})


@app.route("/pdf/<key>")
def pdf(key):
    if not KEY_RE.fullmatch(key):
        return Response(status=404)
    rel = (bundle(key).get("pdf") or {}).get("path")
    full = (ROOT / rel).resolve() if rel else None
    if not full or not full.is_file():
        return Response(status=404)
    return send_file(full, mimetype="application/pdf")


@app.route("/api/verdict/<key>", methods=["POST"])
def api_verdict(key):
    if not KEY_RE.fullmatch(key):
        return jsonify({"error": "bad key"}), 404
    c = next((x for x in queue() if x["key"] == key), None)
    if not c:
        return jsonify({"error": "not in queue"}), 404
    d = request.get_json(force=True)
    v, reason = d.get("verdict"), (d.get("reason") or "").strip()
    served = SERVED.get(key)
    dwell = round((datetime.datetime.now() - served).total_seconds(), 1) if served else None
    rec = {"key": key, "tier": c["tier"],
           "ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "detectors": c.get("detectors"), "terms": c.get("terms"),
           "source": "serve_triage", "dwell_seconds": dwell,
           "sample_mode": sample_keys() is not None}

    if v == "promoted_to_A":
        if c["tier"] != "B":
            return jsonify({"error": "promover so faz sentido em Tier-B"}), 400
        if len(reason) < 10:
            return jsonify({"error": "justifica a promocao numa linha"}), 400
        rec.update({"verdict": v, "reason": reason})
        qa = json.loads((T / "QUEUE_A.json").read_text())
        if not any(x["key"] == key for x in qa):
            e = {k: val for k, val in c.items() if k != "tier"}
            e.update({"tier": "A", "promoted_from_B": True})
            qa.append(e)
            (T / "QUEUE_A.json").write_text(json.dumps(qa, indent=1, ensure_ascii=False))
    elif v == "confirmed_fn":
        sector, quote, page = d.get("sector"), (d.get("quote") or "").strip(), d.get("page")
        if sector not in SECTORS or not quote or not page:
            return jsonify({"error": "confirmed_fn exige setor, citacao e pagina"}), 400
        pages = (bundle(key).get("pdf") or {}).get("pages") or []
        g, mode = ground(quote, int(page), pages)
        if not g.get("grounded"):
            return jsonify({"error": f"citacao nao verificada na p.{page} (modo {mode}). "
                                     "Corrige a pagina ou a transcricao — nada foi gravado."}), 422
        rec.update({"verdict": v, "sector": sector, "quote": quote, "page": int(page),
                    "grounded": True, "grounding_mode": mode, "reason": reason})
    elif v == "not_fn":
        if len(reason) < 10:
            return jsonify({"error": "not_fn exige uma razao real"}), 400
        rec.update({"verdict": v, "reason": reason})
    else:
        return jsonify({"error": "veredicto invalido"}), 400

    out = T / "verdicts" / f"{key}.json"
    if out.exists():
        sup = T / "verdicts" / "_superseded"; sup.mkdir(exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        out.rename(sup / f"{key}.{stamp}.json")
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    total = len(queue())
    done = len(list((T / "verdicts").glob("rayyan-*.json")))
    return jsonify({"ok": True, "verdict": rec, "done": done, "total": total})


@app.route("/")
def index():
    return send_file(T / "triage.html")


if __name__ == "__main__":
    print("triagem em http://127.0.0.1:5052")
    app.run(host="127.0.0.1", port=5052, debug=False)
