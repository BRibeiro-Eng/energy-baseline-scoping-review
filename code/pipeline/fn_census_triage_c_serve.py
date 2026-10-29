#!/usr/bin/env python3
"""Detector (c) triage server — §3-Step-4.

    /usr/local/bin/python3 output/fn_census_triage_c_serve.py     # http://127.0.0.1:5053

Three queues, built by output/fn_census_triage_c_build.py:

  I            2 papers, full read, Corpus-B membership verdict under PROTOCOL.md §5.3
  exploratory 12 papers, unlisted continuous-flow sector — ONE collective decision
  II          33 sampled papers, one binary each: own application vs citation/mention

Anti-mass-click guards, all enforced SERVER-side (the client cannot fake them):
  * dwell is measured from the moment the server hands out the paper
  * Stratum I   : dwell >= 60 s, justification >= 40 chars, verbatim quote >= 20 chars, page int
  * Stratum II  : dwell >= 15 s; a "false negative" verdict additionally needs a note >= 20 chars
  * no bulk action, no keyboard shortcut, one paper at a time, no verdict without a decision
  * every verdict stores its own dwell; the header shows the running median so a
    collapsing attention profile is visible while it happens, not afterwards
"""
import json, os, glob, datetime, statistics, re
from flask import Flask, jsonify, request, Response

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "output/fn_census/detector_c")
T = os.path.join(D, "triage")
V = os.path.join(T, "verdicts")
os.makedirs(V, exist_ok=True)

MIN_DWELL = {"I": 60, "II": 15}
app = Flask(__name__)
SERVED = {}          # key -> datetime the server handed the paper out


def summary():
    return json.load(open(os.path.join(T, "SUMMARY.json"), encoding="utf-8"))


def response(key):
    p = os.path.join(D, "responses_claude", key + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else {}


def bundle_pages(key):
    p = os.path.join(ROOT, "output/stage0", key + ".json")
    if not os.path.isfile(p):
        return []
    return json.load(open(p, encoding="utf-8")).get("pdf", {}).get("pages", [])


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", s or "")).strip()


def context(key, quote, page, pad=700):
    for pg in bundle_pages(key):
        if pg.get("page") == page:
            nt, nq = norm(pg.get("text")), norm(quote)
            i = nt.lower().find(nq.lower()[:60])
            if i < 0:
                return None
            return {"before": nt[max(0, i - pad):i], "hit": nt[i:i + len(nq)],
                    "after": nt[i + len(nq):i + len(nq) + pad]}
    return None


def verdicts():
    out = {}
    for p in glob.glob(os.path.join(V, "rayyan-*.json")):
        d = json.load(open(p, encoding="utf-8"))
        out[d["key"]] = d
    return out


def queues():
    s = summary()
    return {"I": list(s["stratum_I_listed_sector"]),
            "exploratory": list(s["exploratory_unlisted_sector"]),
            "II": list(s["sample_IIa"]["keys"]) + list(s["sample_IIb"]["keys"]),
            "IIa": set(s["sample_IIa"]["keys"])}


def dwells():
    return [v["dwell_seconds"] for v in verdicts().values()
            if isinstance(v.get("dwell_seconds"), (int, float))]


@app.get("/api/state")
def state():
    q, done = queues(), verdicts()
    ed = os.path.join(V, "_exploratory_decision.json")
    ds = dwells()
    return jsonify({
        "queues": {k: [{"key": x, "done": x in done,
                        "verdict": (done.get(x) or {}).get("verdict")}
                       for x in q[k]] for k in ("I", "II")},
        "exploratory": q["exploratory"],
        "exploratory_decided": json.load(open(ed, encoding="utf-8")) if os.path.isfile(ed) else None,
        "counts": {k: {"n": len(q[k]), "done": sum(1 for x in q[k] if x in done)}
                   for k in ("I", "II")},
        "dwell": {"n": len(ds), "median": round(statistics.median(ds), 1) if ds else None,
                  "min": round(min(ds), 1) if ds else None},
        "min_dwell": MIN_DWELL,
    })


@app.get("/api/paper/<key>")
def paper(key):
    SERVED[key] = datetime.datetime.now()
    r = response(key)
    sigs = []
    for kind in ("listed_sector_signals", "other_continuous_flow_signals"):
        for s in (r.get(kind) or []):
            sigs.append({"kind": kind, "sector": s.get("sector"), "page": s.get("page"),
                         "signal": s.get("signal"), "quote": s.get("quote"),
                         "context": context(key, s.get("quote", ""), s.get("page"))})
    pages = [p.get("page") for p in bundle_pages(key)]
    q = queues()
    return jsonify({"key": key, "one_line": r.get("one_line"),
                    "application_strength": r.get("application_strength"),
                    "signals": sigs, "pages": pages,
                    "stratum": "I" if key in q["I"] else "II",
                    "sub": "IIa" if key in q["IIa"] else ("IIb" if key in q["II"] else None),
                    "served_at": SERVED[key].isoformat(timespec="seconds")})


@app.get("/api/page/<key>/<int:n>")
def page_text(key, n):
    for pg in bundle_pages(key):
        if pg.get("page") == n:
            return jsonify({"page": n, "text": norm(pg.get("text"))})
    return jsonify({"error": "page not in bundle"}), 404


@app.post("/api/verdict")
def verdict():
    b = request.get_json(force=True)
    key = b.get("key", "")
    q = queues()
    stratum = "I" if key in q["I"] else ("II" if key in q["II"] else None)
    if not stratum:
        return jsonify({"error": "key is not in a triage queue"}), 400
    served = SERVED.get(key)
    if not served:
        return jsonify({"error": "this paper was not served by the server in this "
                                 "session — reopen it before deciding"}), 400
    dwell = (datetime.datetime.now() - served).total_seconds()
    need = MIN_DWELL[stratum]
    if dwell < need:
        return jsonify({"error": f"dwell {dwell:.0f}s < minimo {need}s para o estrato "
                                 f"{stratum}. Le a fonte."}), 422
    v = b.get("verdict")
    allowed = ({"corpus_b", "out"} if stratum == "I" else {"citation", "own_application"})
    if v not in allowed:
        return jsonify({"error": f"verdict must be one of {sorted(allowed)}"}), 400
    just, quote, note = (b.get("justification") or "").strip(), (b.get("quote") or "").strip(), (b.get("note") or "").strip()
    if stratum == "I":
        if len(just) < 40:
            return jsonify({"error": "justificacao com menos de 40 caracteres"}), 422
        if len(quote) < 20:
            return jsonify({"error": "falta a citacao verbatim que sustenta o veredicto "
                                     "(>= 20 caracteres)"}), 422
        try:
            page = int(b.get("page"))
        except (TypeError, ValueError):
            return jsonify({"error": "pagina fisica da citacao em falta"}), 422
    else:
        page = b.get("page")
        if v == "own_application" and len(note) < 20:
            return jsonify({"error": "um falso negativo precisa de nota (>= 20 caracteres): "
                                     "onde e que o paper aplica, e em que sector"}), 422
    rec = {"key": key, "stratum": stratum, "sub": ("IIa" if key in q["IIa"] else None),
           "verdict": v, "justification": just or None, "quote": quote or None,
           "page": page, "note": note or None,
           "dwell_seconds": round(dwell, 1),
           "served_at": served.isoformat(timespec="seconds"),
           "decided_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "source": "fn_census_triage_c_serve", "protocol": "C-2.3 §3-Step-4"}
    tmp = os.path.join(V, key + ".json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, ensure_ascii=False)
        fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, os.path.join(V, key + ".json"))
    return jsonify({"ok": True, "dwell_seconds": rec["dwell_seconds"]})


@app.post("/api/exploratory")
def exploratory():
    b = request.get_json(force=True)
    d = b.get("decision")
    if d not in {"keep_out", "expand_list"}:
        return jsonify({"error": "decision must be keep_out or expand_list"}), 400
    rationale = (b.get("rationale") or "").strip()
    sectors = [s.strip() for s in (b.get("sectors") or []) if s.strip()]
    if len(rationale) < 40:
        return jsonify({"error": "a decisao de corpus precisa de fundamentacao (>= 40 caracteres) — "
                                 "vai para o run_metadata e para a emenda OSF"}), 422
    if d == "expand_list" and not sectors:
        return jsonify({"error": "expandir a lista exige nomear os sectores a acrescentar"}), 422
    rec = {"decision": d, "sectors_added": sectors, "rationale": rationale,
           "papers": summary()["exploratory_unlisted_sector"],
           "decided_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "protocol": "PROTOCOL.md §5.3 dated corpus decision",
           "reminder": ("Registar em run_metadata.json e na emenda OSF ANTES de contar "
                        "estes papers em qualquer analise do Corpus B." if d == "expand_list"
                        else "Reportar como casos exploratorios fora do Corpus B principal.")}
    with open(os.path.join(V, "_exploratory_decision.json"), "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, ensure_ascii=False)
    return jsonify({"ok": True})


HTML = r"""<!doctype html><meta charset="utf-8"><title>Triagem detector (c)</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>
:root{--bg:#fbfaf8;--fg:#1c1b19;--mut:#6b6762;--line:#e3dfd9;--card:#fff;
      --ok:#166534;--no:#9a3412;--warn:#92400e;--hl:#fde68a;--acc:#1d4ed8}
@media(prefers-color-scheme:dark){:root{--bg:#17181a;--fg:#e9e7e4;--mut:#9a958e;
      --line:#2e3033;--card:#1f2124;--ok:#4ade80;--no:#fb923c;--warn:#fbbf24;--hl:#78561b;--acc:#7aa2f7}}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
  background:var(--bg);color:var(--fg)}
header{position:sticky;top:0;z-index:9;background:var(--card);border-bottom:1px solid var(--line);
  padding:10px 18px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
header b{font-size:15px}.pill{font:12px/1 ui-monospace,SFMono-Regular,Menlo,monospace;padding:5px 9px;
  border:1px solid var(--line);border-radius:999px;color:var(--mut)}
main{display:grid;grid-template-columns:260px 1fr;gap:0;min-height:calc(100vh - 52px)}
nav{border-right:1px solid var(--line);padding:14px;background:var(--card)}
nav h3{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin:16px 0 7px}
nav button{display:block;width:100%;text-align:left;background:none;border:1px solid transparent;
  color:var(--fg);padding:6px 8px;border-radius:7px;cursor:pointer;font:12px/1.4 ui-monospace,Menlo,monospace}
nav button:hover{background:var(--bg)}nav button.on{border-color:var(--acc)}
nav button .st{float:right;font-size:11px}
section{padding:22px 26px;max-width:880px}
h1{font-size:19px;margin:0 0 4px}.sub{color:var(--mut);font-size:13px;margin-bottom:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:15px 17px;margin:13px 0}
.card h4{margin:0 0 8px;font-size:13px;color:var(--mut);font-weight:600}
.q{font:13px/1.6 ui-monospace,Menlo,monospace;background:var(--bg);border-left:3px solid var(--acc);
  padding:9px 11px;border-radius:0 7px 7px 0;white-space:pre-wrap;overflow-wrap:anywhere}
.ctx{font-size:13.5px;line-height:1.7;color:var(--mut)}.ctx mark{background:var(--hl);color:var(--fg);padding:1px 0}
label{display:block;font-size:12px;color:var(--mut);margin:12px 0 4px}
textarea,input{width:100%;font:13px/1.5 inherit;background:var(--bg);color:var(--fg);
  border:1px solid var(--line);border-radius:7px;padding:8px 10px}
textarea{min-height:74px;resize:vertical}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:14px}
button.go{border:1px solid var(--line);background:var(--card);color:var(--fg);padding:9px 15px;
  border-radius:8px;cursor:pointer;font-size:13.5px}
button.go:hover:not(:disabled){border-color:var(--acc)}
button.go:disabled{opacity:.4;cursor:not-allowed}
button.go.b{border-color:var(--ok);color:var(--ok)}button.go.o{border-color:var(--no);color:var(--no)}
.msg{margin-top:11px;font-size:13px;color:var(--no);white-space:pre-wrap}
.note{font-size:12.5px;color:var(--mut);border-left:2px solid var(--line);padding-left:10px;margin:10px 0}
.gate{font:12px/1 ui-monospace,Menlo,monospace;color:var(--warn)}
.done{color:var(--ok)}.out{color:var(--no)}
ul.x{padding-left:18px}ul.x li{margin:5px 0;font-size:13.5px}
@media(max-width:760px){main{grid-template-columns:1fr}nav{border-right:0;border-bottom:1px solid var(--line)}}
</style>
<header>
  <b>Triagem detector (c)</b>
  <span class=pill id=pI>I …</span><span class=pill id=pII>II …</span>
  <span class=pill id=pE>exploratórios …</span><span class=pill id=pD>dwell …</span>
</header>
<main>
  <nav>
    <h3>Estrato I — leitura integral</h3><div id=navI></div>
    <h3>Casos exploratórios</h3>
    <button id=navE onclick="openExp()">decisão de corpus (12)</button>
    <h3>Estrato II — amostra</h3><div id=navII></div>
  </nav>
  <section id=view></section>
</main>
<script>
const $=s=>document.querySelector(s), esc=s=>(s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
let S=null, cur=null, t0=null, tick=null;

async function load(){
  S=await (await fetch("/api/state")).json();
  $("#pI").textContent=`I ${S.counts.I.done}/${S.counts.I.n}`;
  $("#pII").textContent=`II ${S.counts.II.done}/${S.counts.II.n}`;
  $("#pE").textContent="exploratórios "+(S.exploratory_decided?"decidido":"pendente");
  $("#pD").textContent=S.dwell.median===null?"dwell —":`dwell mediana ${S.dwell.median}s · min ${S.dwell.min}s`;
  for(const [st,el] of [["I","#navI"],["II","#navII"]]){
    $(el).innerHTML=S.queues[st].map(x=>
      `<button class="${cur===x.key?'on':''}" onclick="open_('${x.key}')">${x.key.replace('rayyan-','')}
       <span class="st ${x.done?(x.verdict==='out'||x.verdict==='citation'?'out':'done'):''}">${
         x.done?(x.verdict==='corpus_b'?'B':x.verdict==='out'?'fora':x.verdict==='citation'?'cit':'FN'):'·'}</span></button>`).join("");
  }
  if(S.exploratory_decided) $("#navE").classList.add("on");
}

function gate(){
  const el=$("#gate"); if(!el||!cur) return;
  const need=S.min_dwell[cur.stratum], d=Math.floor((Date.now()-t0)/1000);
  const ok=d>=need;
  el.textContent = ok ? `leitura ${d}s — mínimo cumprido` : `leitura ${d}s / ${need}s mínimos`;
  document.querySelectorAll("button.go[data-v]").forEach(b=>b.disabled=!ok);
}

async function open_(key){
  cur=await (await fetch("/api/paper/"+key)).json(); t0=Date.now();
  clearInterval(tick); tick=setInterval(gate,1000);
  const I=cur.stratum==="I";
  $("#view").innerHTML=`
   <h1>${cur.key}</h1>
   <div class=sub>estrato <b>${cur.stratum}${cur.sub?" · "+cur.sub:""}</b> ·
     <code>application_strength = ${cur.application_strength}</code></div>
   <div class=note>${I
     ? "A pergunta do §5.3: o paper <b>aplica, valida ou demonstra empiricamente</b> o modelo num dos oito sectores registados? Menção, enquadramento teórico ou &ldquo;could be applied to&rdquo; não chega. Decide a partir da fonte."
     : "A pergunta: o sinal é a <b>aplicação do próprio paper</b>, ou uma citação/menção a trabalho de outros? Se for aplicação própria num sector registado, é um falso negativo do filtro e dispara o §6a."}</div>
   <div class=card><h4>contexto segundo o detector</h4>${esc(cur.one_line)}</div>
   ${cur.signals.map((s,i)=>`
     <div class=card>
       <h4>${s.kind==="listed_sector_signals"?"sinal de sector REGISTADO":"sinal de fluxo contínuo não listado"}
           · ${esc(s.sector)} · p.${s.page}</h4>
       <div style="font-size:13.5px;margin-bottom:9px">${esc(s.signal)}</div>
       <div class=q>${esc(s.quote)}</div>
       ${s.context?`<div class=ctx style="margin-top:11px">${esc(s.context.before)}<mark>${esc(s.context.hit)}</mark>${esc(s.context.after)}</div>`
                  :`<div class=ctx style="margin-top:11px"><i>citação não localizada no texto extraído da p.${s.page}</i></div>`}
       <div class=row><button class=go onclick="full(${s.page})">ler a p.${s.page} inteira</button></div>
     </div>`).join("")}
   <div id=pagebox></div>
   <div class=card>
     <h4>veredicto</h4>
     ${I?`<label>justificação (mín. 40 car.) — porque é, ou não é, aplicação empírica num sector registado</label>
          <textarea id=just></textarea>
          <label>citação verbatim que o sustenta (mín. 20 car.)</label><textarea id=quote></textarea>
          <label>página física da citação</label><input id=page inputmode=numeric>`
        :`<label>nota (obrigatória só se for falso negativo, mín. 20 car.)</label><textarea id=note></textarea>`}
     <div class=row>
       ${I?`<button class="go b" data-v=corpus_b onclick="send('corpus_b')">é Corpus B</button>
            <button class="go o" data-v=out onclick="send('out')">fica fora</button>`
          :`<button class="go b" data-v=citation onclick="send('citation')">citação / menção</button>
            <button class="go o" data-v=own_application onclick="send('own_application')">aplicação própria — FN</button>`}
       <span id=gate class=gate></span>
     </div>
     <div class=msg id=msg></div>
   </div>`;
  gate(); load();
}

async function full(n){
  const d=await (await fetch(`/api/page/${cur.key}/${n}`)).json();
  $("#pagebox").innerHTML=`<div class=card><h4>página ${n}, texto extraído completo</h4>
    <div class=ctx style="max-height:420px;overflow:auto">${esc(d.text||d.error)}</div></div>`;
}

async function send(v){
  const b={key:cur.key,verdict:v};
  if(cur.stratum==="I"){b.justification=$("#just").value;b.quote=$("#quote").value;b.page=$("#page").value;}
  else b.note=$("#note").value;
  const r=await fetch("/api/verdict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});
  const j=await r.json();
  if(!r.ok){$("#msg").textContent=j.error;return;}
  clearInterval(tick); await load(); next();
}

function next(){
  const pend=[...S.queues.I,...S.queues.II].filter(x=>!x.done);
  if(pend.length) open_(pend[0].key);
  else{cur=null;$("#view").innerHTML=`<h1>Filas I e II fechadas</h1>
    <div class=sub>${S.counts.I.done}/${S.counts.I.n} + ${S.counts.II.done}/${S.counts.II.n} decididos ·
      dwell mediana ${S.dwell.median}s, mínimo ${S.dwell.min}s</div>
    <div class=note>Falta a decisão de corpus sobre os 12 exploratórios, se ainda não a tomaste.
      Depois disso: zero falsos negativos confirmados fecha a união de candidatos e o roster;
      qualquer confirmado dispara o §6a (expansão de léxico + nova passagem do detector (b)).</div>`;}
}

async function openExp(){
  cur=null; clearInterval(tick);
  const s=await (await fetch("/api/state")).json();
  const d=s.exploratory_decided;
  $("#view").innerHTML=`<h1>Casos exploratórios — 12 papers</h1>
   <div class=sub>sector de fluxo contínuo <b>fora</b> da lista registada §5.3</div>
   <div class=note>O §5.3: um paper num sector de fluxo contínuo não listado é reportado como
     <b>caso exploratório fora do Corpus B principal</b>, a menos que uma <b>decisão de corpus datada e
     documentada</b> acrescente o sector à lista <b>antes</b> de os seus papers serem contados.
     Esta é uma decisão só, não doze.</div>
   <div class=card><h4>papers</h4><ul class=x>${s.exploratory.map(k=>`<li><code>${k}</code></li>`).join("")}</ul>
     <div class=note>Sectores envolvidos, segundo os sinais: ciclo combinado / centrais térmicas ·
       cerâmica (pavimento, tijolo, louça sanitária) · tratamento de águas residuais · açúcar ·
       upstream de petróleo e gás (gathering centres, plataformas offshore) ·
       minerais não-metálicos (calcinação de gesso) · alimentar de produção contínua.
       O detalhe por paper está em <code>EXPLORATORY_CASES.md</code>.</div></div>
   ${d?`<div class=card><h4>já decidido em ${esc(d.decided_at)}</h4>
        <b>${d.decision==="keep_out"?"manter fora do Corpus B principal":"expandir a lista §5.3"}</b>
        ${d.sectors_added.length?"<br>sectores: "+esc(d.sectors_added.join(", ")):""}
        <div class=ctx style="margin-top:9px">${esc(d.rationale)}</div>
        <div class=note>${esc(d.reminder)}</div></div>`:""}
   <div class=card><h4>${d?"substituir a decisão":"decisão"}</h4>
     <label>fundamentação (mín. 40 car.) — vai para o <code>run_metadata.json</code> e para a emenda OSF</label>
     <textarea id=rat></textarea>
     <label>se expandires: sectores a acrescentar, separados por vírgula</label><input id=secs>
     <div class=row>
       <button class="go b" onclick="sendExp('keep_out')">manter todos fora</button>
       <button class="go o" onclick="sendExp('expand_list')">expandir a lista §5.3</button>
     </div><div class=msg id=msg></div></div>`;
}

async function sendExp(dec){
  const r=await fetch("/api/exploratory",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({decision:dec,rationale:$("#rat").value,
      sectors:($("#secs").value||"").split(",")})});
  const j=await r.json();
  if(!r.ok){$("#msg").textContent=j.error;return;}
  await load(); openExp();
}

load().then(()=>{const p=[...S.queues.I,...S.queues.II].filter(x=>!x.done);
  if(p.length) open_(p[0].key); else next();});
</script>"""


@app.get("/")
def index():
    return Response(HTML, mimetype="text/html")


if __name__ == "__main__":
    s = summary()
    print(f"Triagem detector (c) — I={len(s['stratum_I_listed_sector'])} "
          f"exploratorios={len(s['exploratory_unlisted_sector'])} "
          f"II={len(s['sample_IIa']['keys'])+len(s['sample_IIb']['keys'])}")
    print("http://127.0.0.1:5053")
    app.run(host="127.0.0.1", port=5053, debug=False)
