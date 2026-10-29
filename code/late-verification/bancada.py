#!/usr/bin/env python3
"""bancada.py — interface local para executar a Emenda 3 (verificação tardia).

    python3 verificacao_2026-10/bancada.py            # abre http://127.0.0.1:8765
    python3 verificacao_2026-10/bancada.py --port 8800 --no-browser

Lê tarefas/ (gerado por build_tasks.py) e escreve respostas/<modulo>.jsonl (só acrescenta; nunca reescreve).
Módulos cegos: a decisão é confirmada uma única vez (commit); a referência só é devolvida depois do commit,
e cada revelação fica registada. Só a biblioteca padrão; escuta apenas em 127.0.0.1.
"""
import argparse, ast, json, os, re, sys, threading, time, webbrowser
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("VT_ROOT") or HERE.parent).resolve()  # VT_ROOT só para testes
TASKS = HERE / "tarefas"
ANS = HERE / "respostas"
LOCK = threading.Lock()
KEY_RE = re.compile(r"^rayyan-\d+$")
DOCS = {"stage1": ROOT / "prompts" / "stage1_system.md", "stage2": ROOT / "prompts" / "stage2_system.md",
        "protocol": ROOT / "PROTOCOL.md", "manual": HERE / "MANUAL.md", "emenda": HERE / "lexico_camada_A.json"}


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_module(m):
    p = TASKS / f"{m}.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def load_ref(m):
    p = TASKS / "_ref" / f"{m}.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else {}


def events(m):
    p = ANS / f"{m}.jsonl"
    out = []
    if p.exists():
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return out


def state(m):
    st = {}
    for e in events(m):
        s = st.setdefault(e["task_id"], {})
        if e["phase"] == "reveal":
            s.setdefault("revealed_at", e["ts"])
        else:
            s[e["phase"]] = {"answer": e.get("answer"), "ts": e["ts"]}
            s.setdefault("time_s", 0)
            s["time_s"] += float(e.get("duration_s") or 0)
    return st


def append(m, rec):
    ANS.mkdir(exist_ok=True)
    p = ANS / f"{m}.jsonl"
    line = json.dumps(rec, ensure_ascii=False)
    with LOCK:
        with open(p, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())


def done(mod, s):
    if mod.get("blind"):
        return "final" in s
    return "answer" in s


def parse_cell(v):
    if v is None:
        return None
    v = v.strip()
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


def enrich_ref(m, ref):
    if m == "d10":
        return {f: {**x, "claude_parsed": parse_cell(x.get("claude")), "chatgpt_parsed": parse_cell(x.get("chatgpt"))} for f, x in ref.items()}
    return ref


MODULES = ["d13", "d11", "d11x", "d7a", "d7b", "d10", "d7c"]


class H(BaseHTTPRequestHandler):
    server_version = "bancada/1.0"

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/":
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if u.path == "/api/modules":
            man = TASKS / "MANIFEST.json"
            if not man.exists():
                return self._send(200, {"ready": False, "filed": (HERE / "AMENDMENT_FILED.txt").exists()})
            out = []
            for m in MODULES:
                mod = load_module(m)
                if not mod:
                    continue
                st = state(m)
                out.append({"module": m, "title": mod["title"], "kind": mod["kind"], "blind": bool(mod.get("blind")),
                            "registered": mod.get("registered"), "frame": mod.get("frame"), "n": len(mod["tasks"]),
                            "done": sum(1 for t in mod["tasks"] if done(mod, st.get(t["id"], {}))),
                            "time_s": sum(s.get("time_s", 0) for s in st.values()), "note": mod.get("note")})
            return self._send(200, {"ready": True, "manifest": json.load(open(man, encoding="utf-8")), "modules": out})
        if u.path == "/api/tasks":
            m = q.get("module")
            mod = load_module(m) if m in MODULES else None
            if not mod:
                return self._send(404, {"error": "módulo desconhecido"})
            st = state(m)
            ref = load_ref(m) if mod.get("blind") else {}
            for t in mod["tasks"]:
                s = st.get(t["id"], {})
                t["_state"] = s
                t["_done"] = done(mod, s)
                if mod.get("blind") and s.get("revealed_at") and t["id"] in ref:
                    t["_ref"] = enrich_ref(m, {t["id"]: ref[t["id"]]})[t["id"]]
            return self._send(200, mod)
        m = re.match(r"^/pdf/(rayyan-\d+)\.pdf$", u.path)
        if m:
            p = ROOT / "data" / "pdfs" / f"{m.group(1)}.pdf"
            if not p.exists():
                return self._send(404, {"error": "PDF não encontrado"})
            return self._send(200, p.read_bytes(), "application/pdf", {"Content-Disposition": f'inline; filename="{p.name}"'})
        m = re.match(r"^/doc/(\w+)$", u.path)
        if m and m.group(1) in DOCS and DOCS[m.group(1)].exists():
            return self._send(200, DOCS[m.group(1)].read_text(encoding="utf-8"), "text/plain; charset=utf-8")
        return self._send(404, {"error": "não encontrado"})

    def do_POST(self):
        u = urlparse(self.path)
        try:
            b = self._json()
        except Exception:
            return self._send(400, {"error": "JSON inválido"})
        m, tid = b.get("module"), b.get("id")
        mod = load_module(m) if m in MODULES else None
        if not mod or tid not in {t["id"] for t in mod["tasks"]}:
            return self._send(404, {"error": "tarefa desconhecida"})
        st = state(m).get(tid, {})
        if u.path == "/api/answer":
            phase = b.get("phase")
            allowed = ("commit", "final") if mod.get("blind") else ("answer",)
            if phase not in allowed:
                return self._send(400, {"error": f"fase inválida para {m}: {phase}"})
            if phase == "commit" and "commit" in st:
                return self._send(409, {"error": "decisão cega já confirmada; não se reescreve"})
            if phase == "final" and "commit" not in st:
                return self._send(409, {"error": "confirma primeiro a decisão cega"})
            if phase == "final" and not st.get("revealed_at"):
                return self._send(409, {"error": "revela primeiro a referência"})
            append(m, {"ts": now(), "task_id": tid, "phase": phase, "answer": b.get("answer"),
                       "duration_s": round(float(b.get("duration_s") or 0), 1)})
            return self._send(200, {"ok": True, "state": state(m).get(tid, {})})
        if u.path == "/api/reveal":
            if not mod.get("blind"):
                return self._send(400, {"error": "módulo sem referência oculta"})
            if "commit" not in st:
                return self._send(409, {"error": "sem commit não há revelação"})
            if not st.get("revealed_at"):
                append(m, {"ts": now(), "task_id": tid, "phase": "reveal"})
            ref = load_ref(m).get(tid)
            return self._send(200, {"ok": True, "ref": enrich_ref(m, {tid: ref})[tid]})
        return self._send(404, {"error": "não encontrado"})


PAGE = r"""<!doctype html>
<html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bancada · Emenda 3</title>
<style>
:root{--ink:#22212b;--mut:#6b6880;--line:#e3e1ec;--bg:#f6f5fa;--card:#fff;--acc:#7E75C2;--acc2:#C8C2EA;--acc3:#efedf8;--warn:#F4B77A;--warn2:#fdf1e4;--ok:#3f8f6b;--ok2:#e6f3ec;--bad:#b4473b;--bad2:#f8e8e6;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,system-ui,sans-serif;color:var(--ink);background:var(--bg)}
header{display:flex;align-items:center;gap:16px;padding:10px 18px;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
header h1{font-size:15px;margin:0;font-weight:650;letter-spacing:.2px}
header .dl{margin-left:auto;font-size:12.5px;color:var(--mut)}
header .dl b{color:var(--ink)}
nav{display:flex;gap:6px;flex-wrap:wrap;padding:10px 18px;background:#fff;border-bottom:1px solid var(--line)}
nav button{border:1px solid var(--line);background:#fff;border-radius:8px;padding:7px 11px;cursor:pointer;font:inherit;font-size:13px;display:flex;flex-direction:column;align-items:flex-start;min-width:150px}
nav button .t{font-weight:600}nav button .s{font-size:11.5px;color:var(--mut)}
nav button.on{border-color:var(--acc);box-shadow:0 0 0 2px var(--acc3) inset;background:var(--acc3)}
nav .bar{height:3px;background:var(--line);border-radius:2px;width:100%;margin-top:5px;overflow:hidden}nav .bar i{display:block;height:100%;background:var(--acc)}
main{display:grid;grid-template-columns:300px 1fr;height:calc(100vh - 128px)}
#list{border-right:1px solid var(--line);overflow:auto;background:#fff}
#list .tools{position:sticky;top:0;background:#fff;padding:8px 10px;border-bottom:1px solid var(--line);display:flex;gap:8px;align-items:center;font-size:12.5px;color:var(--mut)}
#list .it{padding:8px 12px;border-bottom:1px solid #f0eff5;cursor:pointer;display:flex;gap:8px;align-items:flex-start}
#list .it:hover{background:#faf9fd}#list .it.on{background:var(--acc3)}
#list .dot{width:9px;height:9px;border-radius:50%;margin-top:5px;flex:none;border:2px solid var(--acc2)}
#list .dot.c{background:var(--warn);border-color:var(--warn)}#list .dot.d{background:var(--acc);border-color:var(--acc)}
#list .lb{font-size:12.5px;line-height:1.3}#list .lb small{display:block;color:var(--mut)}
#pane{overflow:auto;padding:18px 26px 80px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:14px}
.card h2{font-size:16px;margin:0 0 4px;font-weight:650}.card h3{font-size:13px;margin:0 0 8px;color:var(--mut);text-transform:uppercase;letter-spacing:.6px;font-weight:650}
.meta{color:var(--mut);font-size:12.5px}
.badge{display:inline-block;font-size:11.5px;padding:2px 8px;border-radius:20px;background:var(--acc3);color:#4b4390;margin-right:6px;font-weight:600}
.badge.w{background:var(--warn2);color:#8a5418}.badge.g{background:var(--ok2);color:#245c43}.badge.r{background:var(--bad2);color:var(--bad)}
.btn{border:1px solid var(--acc);background:var(--acc);color:#fff;border-radius:8px;padding:8px 14px;font:inherit;font-weight:600;cursor:pointer}
.btn.sec{background:#fff;color:#4b4390}.btn:disabled{opacity:.45;cursor:not-allowed}
.btn.pdf{background:#fff;color:#4b4390;border-color:var(--acc2);padding:5px 10px;font-size:12.5px}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
label.opt{display:flex;gap:8px;align-items:flex-start;padding:7px 10px;border:1px solid var(--line);border-radius:8px;margin:5px 0;cursor:pointer;background:#fff}
label.opt:hover{border-color:var(--acc2)}label.opt input{margin-top:3px}
input[type=text],input[type=number],textarea,select{font:inherit;border:1px solid #d6d3e3;border-radius:7px;padding:6px 8px;width:100%;background:#fff}
textarea{min-height:56px;resize:vertical}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.hit{border-left:3px solid var(--acc2);padding:6px 10px;margin:6px 0;background:#fcfcfe;font-size:13px}
.hit mark,.ab mark{background:#ffe5c2;padding:0 2px;border-radius:2px}
.kv{font-family:var(--mono);font-size:12.5px;white-space:pre-wrap;background:#faf9fd;border:1px solid var(--line);border-radius:7px;padding:8px 10px}
.quote{border-left:3px solid var(--acc);padding:6px 10px;background:#faf9fd;font-style:italic;white-space:pre-wrap}
.ab{white-space:pre-wrap}
.f{margin:10px 0 14px}.f>.l{font-weight:600;margin-bottom:4px;font-size:13px}
.note{background:var(--warn2);border:1px solid #f1d3ad;border-radius:8px;padding:8px 12px;font-size:12.5px;color:#6b4312;margin-bottom:12px}
table.cmp{border-collapse:collapse;width:100%;font-size:13px}table.cmp th,table.cmp td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
table.cmp th{font-size:11.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px}
.diff{color:var(--bad);font-weight:600}.same{color:var(--ok);font-weight:600}
.empty{color:var(--mut);padding:40px;text-align:center}
.foot{position:fixed;bottom:0;left:300px;right:0;background:#fff;border-top:1px solid var(--line);padding:10px 26px;display:flex;gap:10px;align-items:center}
.foot .msg{color:var(--mut);font-size:12.5px;margin-left:auto}
.chips button{border:1px solid var(--line);background:#fff;border-radius:16px;padding:3px 9px;font:inherit;font-size:12px;cursor:pointer;margin:2px}
.muted{color:var(--mut)}
code{font-family:var(--mono);font-size:12px}
@media (max-width:900px){main{grid-template-columns:1fr}#list{max-height:30vh}.foot{left:0}.grid2{grid-template-columns:1fr}}
</style></head><body>
<header><h1>Bancada de verificação · Emenda 3 ao TDW6C</h1><span id="filed" class="meta"></span><span class="dl" id="dl"></span></header>
<nav id="nav"></nav>
<main><div id="list"></div><div id="pane"><div class="empty">A carregar…</div></div></main>
<div class="foot" id="foot" style="display:none"></div>
<script>
const $=s=>document.querySelector(s);let MODS=[],MOD=null,CUR=null,OPENED=0,ONLYPENDING=false;
const DEADLINE=new Date('2026-10-29T23:59:00');
function esc(s){return String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function fmtT(s){s=Math.round(s||0);const h=Math.floor(s/3600),m=Math.round((s%3600)/60);return h?`${h} h ${m} min`:`${m} min`}
async function api(p,b){const r=await fetch(p,b?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}:{});const j=await r.json();if(!r.ok)throw new Error(j.error||r.status);return j}
function draftKey(){return `bancada:${MOD.module}:${CUR.id}`}
function saveDraft(){try{const f=$('#form');if(!f)return;localStorage.setItem(draftKey(),JSON.stringify(readForm(f)))}catch(e){}}
function loadDraft(){try{return JSON.parse(localStorage.getItem(draftKey())||'null')}catch(e){return null}}
function clearDraft(){try{localStorage.removeItem(draftKey())}catch(e){}}
function readForm(f){const o={};f.querySelectorAll('[name]').forEach(el=>{if(el.type==='radio'){if(el.checked)o[el.name]=el.value}else if(el.type==='checkbox'){(o[el.name]=o[el.name]||[]);if(el.checked)o[el.name].push(el.value)}else o[el.name]=el.value});return o}
function fillForm(f,o){if(!o)return;f.querySelectorAll('[name]').forEach(el=>{const v=o[el.name];if(v===undefined)return;if(el.type==='radio')el.checked=(el.value===v);else if(el.type==='checkbox')el.checked=Array.isArray(v)&&v.includes(el.value);else el.value=v});f.dispatchEvent(new Event('change'))}
function hl(text,terms){let t=esc(text);(terms||[]).forEach(w=>{t=t.replace(new RegExp('\\b('+w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')\\b','gi'),'<mark>$1</mark>')});return t}
function pdf(key,page){return `<a class="btn pdf" target="_blank" href="/pdf/${key}.pdf${page?'#page='+page:''}">PDF${page?' p. '+page:''} ↗</a>`}
function head(t){const doi=t.doi?` · <a target="_blank" href="https://doi.org/${esc(t.doi)}">doi</a>`:'';return `<h2>${esc(t.title||t.key)}</h2><div class="meta">${esc(t.first_author||'')}${t.year?' ('+esc(t.year)+')':''}${t.journal?' · '+esc(t.journal):''}${doi} · <code>${esc(t.key)}</code></div>`}
function radios(name,opts){return opts.map(([v,l])=>`<label class="opt"><input type="radio" name="${name}" value="${esc(v)}"><span>${l}</span></label>`).join('')}
function msg(s,bad){const m=$('#foot .msg');if(m){m.textContent=s;m.style.color=bad?'var(--bad)':'var(--mut)'}}

async function boot(){
  const d=Math.ceil((DEADLINE-new Date())/864e5);$('#dl').innerHTML=`Janela de execução até 29 out · <b>${d} dias</b>`;
  const j=await api('/api/modules');
  if(!j.ready){$('#pane').innerHTML=`<div class="card"><h2>Sem tarefas geradas</h2><p>${j.filed?'O interlock existe mas as tarefas ainda não foram geradas. Corre <code>python3 verificacao_2026-10/build_tasks.py</code>.':'A emenda ainda não está registada como depositada. Segue a etapa 0 do MANUAL.md: depositar no OSF, preencher <code>AMENDMENT_FILED.txt</code>, correr <code>build_tasks.py</code>.'}</p></div>`;return}
  const a=j.manifest.amendment||{};$('#filed').textContent=`Emenda depositada ${a.deposited||'?'} · OSF ${a.osf_file||'?'}`;
  MODS=j.modules;renderNav();const last=(()=>{try{return localStorage.getItem('bancada:mod')}catch(e){return null}})();
  openModule(MODS.find(m=>m.module===last)?last:MODS[0].module)}
function renderNav(){$('#nav').innerHTML=MODS.map(m=>`<button data-m="${m.module}" class="${MOD&&MOD.module===m.module?'on':''}"><span class="t">${esc(m.title.split(' · ')[0])}</span><span class="s">${esc(m.title.split(' · ')[1]||'')}</span><span class="s">${m.done}/${m.n} · ${fmtT(m.time_s)}</span><span class="bar"><i style="width:${m.n?100*m.done/m.n:0}%"></i></span></button>`).join('');
  document.querySelectorAll('#nav button').forEach(b=>b.onclick=()=>openModule(b.dataset.m))}
async function refreshNav(){const j=await api('/api/modules');MODS=j.modules;renderNav()}
async function openModule(m){try{localStorage.setItem('bancada:mod',m)}catch(e){}MOD=await api('/api/tasks?module='+m);renderNav();renderList();
  const first=MOD.tasks.find(t=>!t._done)||MOD.tasks[0];if(first)openTask(first.id);else $('#pane').innerHTML='<div class="empty">Sem tarefas.</div>'}
function label(t){if(MOD.kind==='absence')return `${t.family} · ${t.first_author||''} ${t.year||''}<small>${t.n_hits} ocorrências · ${esc(t.family_name)}</small>`;
  if(MOD.kind==='retest')return `${t.first_author||''} ${t.year||''}<small>${esc(t.field_label)}</small>`;
  if(MOD.kind==='cell')return `${t.id} · ${esc(t.author_year||'')}<small>${esc(t.field||t.path)}</small>`;
  if(MOD.kind==='triage')return `${esc((t.title||'').slice(0,70))}<small>${t.stratum==='lexicon'?'léxico: '+esc(t.lexicon_terms.join(', ')):'amostra'} · ${esc(t.year||'')}</small>`;
  return `${t.first_author||''} ${t.year||''}<small>${esc((t.title||'').slice(0,60))}</small>`}
function renderList(){const ts=MOD.tasks.filter(t=>!ONLYPENDING||!t._done);
  $('#list').innerHTML=`<div class="tools"><label><input type="checkbox" id="op" ${ONLYPENDING?'checked':''}> só pendentes</label><span style="margin-left:auto">${MOD.tasks.filter(t=>t._done).length}/${MOD.tasks.length}</span></div>`+
   ts.map((t,i)=>`<div class="it ${CUR&&CUR.id===t.id?'on':''}" data-id="${esc(t.id)}"><span class="dot ${t._done?'d':(t._state&&t._state.commit?'c':'')}"></span><span class="lb">${label(t)}</span></div>`).join('');
  $('#op').onchange=e=>{ONLYPENDING=e.target.checked;renderList()};document.querySelectorAll('#list .it').forEach(el=>el.onclick=()=>openTask(el.dataset.id))}
function nextPending(){const i=MOD.tasks.findIndex(t=>t.id===CUR.id);const n=MOD.tasks.slice(i+1).find(t=>!t._done)||MOD.tasks.find(t=>!t._done);if(n)openTask(n.id);else{renderList();$('#foot').innerHTML='<span class="msg">Módulo concluído — nada por fazer aqui.</span>'}}
function openTask(id){CUR=MOD.tasks.find(t=>t.id===id);OPENED=Date.now();renderList();const r=RENDER[MOD.kind];$('#pane').innerHTML=r(CUR);$('#pane').scrollTop=0;
  const f=$('#form');if(f){const ans=(CUR._state.answer||CUR._state.commit||{}).answer;if(!CUR._state.commit&&!CUR._state.answer)fillForm(f,loadDraft());else if(ans&&!MOD.blind)fillForm(f,ans);f.addEventListener('input',saveDraft);f.addEventListener('change',saveDraft)}
  if(HOOK[MOD.kind])HOOK[MOD.kind](CUR)}
async function send(phase,answer){const dur=(Date.now()-OPENED)/1000;OPENED=Date.now();
  const r=await api('/api/answer',{module:MOD.module,id:CUR.id,phase,answer,duration_s:dur});CUR._state=r.state;CUR._done=MOD.blind?('final' in r.state):('answer' in r.state);clearDraft();refreshNav();return r}
function foot(html){const f=$('#foot');f.style.display='flex';f.innerHTML=html+'<span class="msg"></span>'}
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key==='Enter'){const b=document.querySelector('#foot .btn:not(:disabled)');if(b){e.preventDefault();b.click()}}});

// ------------------------------------------------------------------ renderers
const RENDER={},HOOK={};
// D13
RENDER.triage=t=>{foot(`<button class="btn" id="go">Guardar e seguinte</button>`);
 return `<div class="card">${head(t)}<div style="margin-top:8px">${t.stratum==='lexicon'?`<span class="badge w">censo do léxico: ${esc(t.lexicon_terms.join(', '))}</span>`:'<span class="badge">amostra aleatória</span>'}<span class="badge">resumo: ${esc(t.abstract_source)}</span></div></div>
 <div class="card"><h3>Resumo</h3><div class="ab">${t.abstract?hl(t.abstract,t.lexicon_terms):'<span class="muted">Sem resumo disponível. Abre pelo DOI ou no Rayyan; se continuar sem resumo, decide pelo título e regista isso no motivo.</span>'}</div></div>
 <form id="form" class="card" onsubmit="return false"><h3>Decisão</h3>
 <p class="meta" style="margin-top:0">Pergunta: à luz dos critérios de rastreio registados, este registo devia ter seguido para avaliação do texto integral?</p>
 ${radios('decision',[['stands','<b>A exclusão mantém-se</b>'],['should_have_proceeded','<b>Devia ter seguido para texto integral</b> <span class="muted">— aciona procura do PDF e avaliação de elegibilidade</span>']])}
 <div class="f"><div class="l">Motivo (uma linha)</div><input type="text" name="reason"><div class="chips" style="margin-top:4px">${['Não trata de indicadores/baselines de desempenho energético','Energia só como contexto; sem modelo EnPI/EnB','Fora do domínio (não industrial/energético)','Gestão de energia genérica, sem modelo caracterizável','Trata de modelação de consumo que pode ser EnB'].map(c=>`<button type="button" onclick="this.closest('form').reason.value='${c}';saveDraft()">${c}</button>`).join('')}</div></div></form>`};
HOOK.triage=t=>{const f=$('#form');if(t._state.answer)fillForm(f,t._state.answer.answer);$('#go').onclick=async()=>{const a=readForm(f);if(!a.decision)return msg('Escolhe a decisão.',1);if(!a.reason||a.reason.trim().length<4)return msg('Falta o motivo.',1);await send('answer',a);nextPending()}};

// D11
RENDER.retest=t=>{const s=t._state;
 return `<div class="card">${head(t)}<div class="row" style="margin-top:10px">${pdf(t.key)}<a class="btn pdf" target="_blank" href="/doc/stage1">Critérios (stage1) ↗</a></div></div>
 <div class="card"><h3>${esc(t.field_label)}</h3><p style="margin:0">${esc(t.question)}</p></div>
 <form id="form" class="card" onsubmit="return false"><h3>Decisão cega${s.commit?' · confirmada '+esc(s.commit.ts):''}</h3>
 ${radios('value',[['true','<b>Sim</b>'],['false','<b>Não</b>']])}
 <div class="f"><div class="l">Evidência</div>${radios('mode',[['quoted','Citação com página'],['not_reported_after_full_text_review','Não reportado após leitura integral']])}</div>
 <div class="grid2"><div class="f"><div class="l">Página</div><input type="number" name="page" min="1"></div><div class="f"><div class="l">Citação ou fundamentação</div><textarea name="evidence"></textarea></div></div></form>
 <div id="rev"></div>`};
HOOK.retest=t=>{const f=$('#form'),s=t._state;
 if(s.commit){fillForm(f,s.commit.answer);f.querySelectorAll('input,textarea').forEach(e=>e.disabled=true)}
 const showRev=(ref)=>{const mine=s.commit.answer.value==='true',orig=ref.original_final===true,flip=mine!==orig;
   $('#rev').innerHTML=`<div class="card"><h3>Decisão original (revelada ${esc(t._state.revealed_at||'agora')})</h3>
   <table class="cmp"><tr><th>Reteste (agora)</th><th>Original final</th><th>Original cega</th><th>Resultado</th></tr>
   <tr><td>${mine?'Sim':'Não'}</td><td>${orig?'Sim':'Não'}</td><td>${ref.original_blind===true?'Sim':'Não'}</td><td>${flip?'<span class="diff">FLIP</span>':'<span class="same">consistente</span>'}</td></tr></table>
   <div class="kv" style="margin-top:8px">${esc(JSON.stringify(ref.evidence,null,1))}</div><p class="meta">Decidido em ${esc(ref.committed_at)} · finalizado em ${esc(ref.finalised_at)}</p>
   ${flip?`<form id="fin" onsubmit="return false"><h3 style="margin-top:12px">Re-adjudicação (obrigatória num flip)</h3>${radios('final_value',[['true','Sim'],['false','Não']])}<div class="f"><div class="l">Página e citação, ou fundamentação</div><textarea name="final_evidence"></textarea></div><div class="f"><div class="l">Porque divergiram?</div><input type="text" name="why"></div></form>`:`<form id="fin" onsubmit="return false"><div class="f"><div class="l">Nota (opcional)</div><input type="text" name="note"></div></form>`}</div>`;
   if(s.final)fillForm($('#fin'),s.final.answer);
   foot(`<button class="btn" id="fz">${s.final?'Atualizar e seguinte':'Concluir e seguinte'}</button>`);
   $('#fz').onclick=async()=>{const a={...readForm($('#fin')),flip};if(flip&&(!a.final_value||!a.final_evidence))return msg('Num flip, a re-adjudicação precisa de valor e evidência.',1);await send('final',a);nextPending()}};
 if(!s.commit){foot(`<button class="btn" id="cm">Confirmar decisão cega (irreversível)</button>`);
   $('#cm').onclick=async()=>{const a=readForm(f);if(!a.value)return msg('Escolhe Sim ou Não.',1);if(!a.mode)return msg('Escolhe o tipo de evidência.',1);if(!a.evidence)return msg('Falta a citação ou fundamentação.',1);if(a.mode==='quoted'&&!a.page)return msg('Falta a página.',1);await send('commit',a);openTask(t.id)}}
 else if(!s.revealed_at){foot(`<button class="btn" id="rv">Revelar decisão original</button>`);$('#rv').onclick=async()=>{const r=await api('/api/reveal',{module:MOD.module,id:t.id});t._ref=r.ref;t._state.revealed_at='agora';showRev(r.ref);$('#rev').scrollIntoView({behavior:'smooth'})}}
 else showRev(t._ref)};

// D7 A
RENDER.absence=t=>{foot(`<button class="btn" id="go">Guardar e seguinte</button>`);
 const pages={};t.hits.forEach(h=>(pages[h.page]=pages[h.page]||[]).push(h));
 return `<div class="card">${head(t)}<div style="margin-top:8px"><span class="badge">${t.family} · ${esc(t.family_name)}</span><span class="badge ${t.priority==='core'?'':'w'}">${t.priority==='core'?'núcleo':'2.ª prioridade'}</span><span class="badge">${t.n_hits} ocorrências em ${Object.keys(pages).length} páginas</span></div>
 <p style="margin:10px 0 0"><b>Relevante se:</b> ${esc(t.relevant_if)}</p><div class="row" style="margin-top:8px">${pdf(t.key)}</div></div>
 <div class="grid2"><div class="card"><h3>Codificado na extração (${esc(t.field)})</h3><div class="kv">${esc(t.coded.join('\n'))}</div></div>
 <div class="card" style="max-height:60vh;overflow:auto"><h3>Ocorrências do léxico</h3>${Object.entries(pages).map(([p,hs])=>`<div style="margin:10px 0 4px" class="row"><b>p. ${p}</b> ${pdf(t.key,p)}</div>`+hs.map(h=>`<div class="hit">…${esc(h.before.slice(-140))}<mark>${esc(h.match)}</mark>${esc(h.after.slice(0,140))}…</div>`).join('')).join('')}</div></div>
 <form id="form" class="card" onsubmit="return false"><h3>Decisão para esta família neste relatório</h3>
 ${radios('decision',[['a_none','<b>(a) Nenhuma ocorrência relevante</b>'],['b_coded','<b>(b) Relevante e já codificada</b>'],['c_missed','<b>(c) Relevante e NÃO codificada</b> <span class="muted">— corrige o dataset</span>']])}
 <div id="cx" style="display:none"><div class="grid2"><div class="f"><div class="l">Página</div><input type="number" name="page" min="1"></div><div class="f"><div class="l">Campo afetado (modelo/aplicação)</div><input type="text" name="field_affected" value="${esc(t.field)}"></div></div>
 <div class="f"><div class="l">Citação</div><textarea name="quote"></textarea></div><div class="f"><div class="l">Valor corrigido</div><input type="text" name="corrected_value"></div></div>
 <div class="f"><div class="l">Nota</div><input type="text" name="note"></div></form>`};
HOOK.absence=t=>{const f=$('#form');if(t._state.answer)fillForm(f,t._state.answer.answer);const tog=()=>{$('#cx').style.display=(readForm(f).decision==='c_missed')?'block':'none'};f.addEventListener('change',tog);tog();
 $('#go').onclick=async()=>{const a=readForm(f);if(!a.decision)return msg('Escolhe (a), (b) ou (c).',1);if(a.decision==='c_missed'&&(!a.page||!a.quote||!a.corrected_value))return msg('Em (c) faltam página, citação e valor corrigido.',1);await send('answer',a);nextPending()}};

// D7 B
RENDER.cell=t=>{foot(`<button class="btn" id="go">Guardar e seguinte</button>`);
 const cur=Object.entries(t.current||{}).map(([k,v])=>`${k}: ${typeof v==='object'?JSON.stringify(v):v}`).join('\n');
 return `<div class="card">${head(t)}<div style="margin-top:8px"><span class="badge">${esc(t.type)}</span><span class="badge">${esc(t.id)}</span>${t.state_sept?`<span class="badge w">set.: ${esc(t.state_sept)}</span>`:''}<span class="badge">${esc(t.support_class||'')}</span></div>
 <p class="meta" style="margin:8px 0 0"><code>${esc(t.path)}</code>${t.refers_to?' · refere-se a '+esc(t.refers_to):''}</p></div>
 <div class="card"><h3>Valor atual (após a releitura de setembro)</h3><div class="kv">${esc(cur)}</div>${t.extra?`<p class="meta">${esc(t.extra)}</p>`:''}</div>
 <div class="card"><h3>Citação</h3><div class="quote">${esc(t.quote||'(sem citação)')}</div><div class="row" style="margin-top:8px">${pdf(t.key,t.page)}${t.page_as_recorded?`<span class="meta">página corrigida pelo verificador (o extrator escreveu ${esc(t.page_as_recorded)})</span>`:''}</div></div>
 <form id="form" class="card" onsubmit="return false"><h3>Decisão</h3>
 ${radios('decision',[['correct','<b>Correto</b>'],['incorrect','<b>Incorreto</b> <span class="muted">— indica o valor correto</span>'],['undetermined','<b>Não determinável</b> <span class="muted">— diz porquê</span>']])}
 <div class="f" id="cv" style="display:none"><div class="l">Valor correto</div><input type="text" name="correct_value"></div><div class="f"><div class="l">Nota</div><input type="text" name="note"></div></form>`};
HOOK.cell=t=>{const f=$('#form');if(t._state.answer)fillForm(f,t._state.answer.answer);const tog=()=>{$('#cv').style.display=readForm(f).decision==='incorrect'?'block':'none'};f.addEventListener('change',tog);tog();
 $('#go').onclick=async()=>{const a=readForm(f);if(!a.decision)return msg('Escolhe a decisão.',1);if(a.decision==='incorrect'&&!a.correct_value)return msg('Falta o valor correto.',1);if(a.decision==='undetermined'&&!a.note)return msg('Diz porque não é determinável.',1);await send('answer',a);nextPending()}};

// D7 C
RENDER.refmap=t=>{return `<div class="note">${esc(MOD.note||'')}</div><div class="card">${head(t)}<div class="row" style="margin-top:10px">${pdf(t.key)}</div></div>
 <form id="form" class="card" onsubmit="return false"><h3>Leitura integral${t._state.commit?' · confirmada '+esc(t._state.commit.ts):''}</h3>
 ${t.fields.map(fd=>`<div class="f"><div class="l">${esc(fd.label)}</div><select name="${fd.id}"><option value="">—</option>${fd.options.map(o=>`<option>${esc(o)}</option>`).join('')}</select>
 <div class="grid2" style="margin-top:4px"><input type="number" min="1" name="${fd.id}_page" placeholder="página"><input type="text" name="${fd.id}_ev" placeholder="citação ou «não reportado após leitura integral»"></div></div>`).join('')}</form><div id="rev"></div>`};
HOOK.refmap=t=>{const f=$('#form'),s=t._state;if(s.commit){fillForm(f,s.commit.answer);f.querySelectorAll('select,input').forEach(e=>e.disabled=true)}
 const showRev=ref=>{const mine=s.commit.answer;$('#rev').innerHTML=`<div class="card"><h3>Comparação com o codificado</h3><form id="fin" onsubmit="return false"><table class="cmp"><tr><th>Campo</th><th>Leitura</th><th>Codificado</th><th></th><th>Valor final</th><th>Razão</th></tr>
  ${t.fields.map(fd=>{const d=mine[fd.id]!==ref[fd.id];return `<tr><td>${esc(fd.label)}</td><td>${esc(mine[fd.id])}</td><td>${esc(ref[fd.id])}</td><td>${d?'<span class="diff">≠</span>':'<span class="same">=</span>'}</td><td><select name="${fd.id}_final">${fd.options.map(o=>`<option ${o===mine[fd.id]?'selected':''}>${esc(o)}</option>`).join('')}</select></td><td><input type="text" name="${fd.id}_why" placeholder="${d?'obrigatória se ≠':''}"></td></tr>`}).join('')}</table></form></div>`;
  if(s.final)fillForm($('#fin'),s.final.answer);foot(`<button class="btn" id="fz">${s.final?'Atualizar e seguinte':'Concluir e seguinte'}</button>`);
  $('#fz').onclick=async()=>{const a=readForm($('#fin'));for(const fd of t.fields){if((mine[fd.id]!==ref[fd.id]||a[fd.id+'_final']!==mine[fd.id])&&!a[fd.id+'_why'])return msg('Falta a razão em '+fd.label,1)}a.diffs=t.fields.filter(fd=>mine[fd.id]!==ref[fd.id]).map(fd=>fd.id);a.reveal_changes=t.fields.filter(fd=>a[fd.id+'_final']!==mine[fd.id]).map(fd=>fd.id);await send('final',a);nextPending()}};
 if(!s.commit){foot(`<button class="btn" id="cm">Confirmar leitura (irreversível)</button>`);$('#cm').onclick=async()=>{const a=readForm(f);for(const fd of t.fields){if(!a[fd.id])return msg('Falta: '+fd.label,1);if(!a[fd.id+'_ev'])return msg('Falta a evidência em '+fd.label,1)}await send('commit',a);openTask(t.id)}}
 else if(!s.revealed_at){foot(`<button class="btn" id="rv">Revelar valores codificados</button>`);$('#rv').onclick=async()=>{const r=await api('/api/reveal',{module:MOD.module,id:t.id});t._ref=r.ref;t._state.revealed_at='agora';showRev(r.ref);$('#rev').scrollIntoView({behavior:'smooth'})}}
 else showRev(t._ref)};

// D10
function inputFor(fd){const n='v_'+fd.id;if(fd.type==='multienum')return fd.options.map(o=>`<label class="opt" style="display:inline-flex;margin:3px 6px 3px 0"><input type="checkbox" name="${n}" value="${esc(o)}"><span>${esc(o)}</span></label>`).join('');
 if(fd.type==='enum')return `<select name="${n}"><option value="">—</option><option value="__null__">(sem valor no texto)</option>${fd.options.map(o=>`<option value="${esc(String(o))}">${esc(String(o))}</option>`).join('')}</select>`;
 return `<input type="text" name="${n}" placeholder="texto; vazio = sem valor no texto">`}
function normv(fd,v){if(fd.type==='multienum')return JSON.stringify([...(v||[])].map(x=>String(x).trim().toLowerCase()).sort());if(v==='__null__'||v===''||v==null)return 'null';return String(v).trim().toLowerCase().replace(/\s+/g,' ')}
RENDER.audit=t=>{const na=Object.entries(t.not_auditable||{});
 return `<div class="card">${head(t)}<div class="row" style="margin-top:10px">${pdf(t.key)}<a class="btn pdf" target="_blank" href="/doc/stage2">Definições (stage2) ↗</a><a class="btn pdf" target="_blank" href="/doc/stage1">Tipo de artigo (stage1) ↗</a></div>
 ${na.length?`<p class="meta" style="margin:8px 0 0">Fora da auditoria (sem concordância): ${na.map(([f,s])=>esc(f)+' — '+esc(s)).join(' · ')}</p>`:''}</div>
 <form id="form" class="card" onsubmit="return false"><h3>Extração cega${t._state.commit?' · confirmada '+esc(t._state.commit.ts):''} · ${t.fields.length} campos</h3>
 ${t.fields.map(fd=>`<div class="f"><div class="l">${esc(fd.id)}</div>${inputFor(fd)}<input type="text" name="p_${fd.id}" placeholder="página/citação (opcional)" style="margin-top:4px"></div>`).join('')}</form><div id="rev"></div>`};
HOOK.audit=t=>{const f=$('#form'),s=t._state;if(s.commit){fillForm(f,s.commit.answer);f.querySelectorAll('select,input').forEach(e=>e.disabled=true)}
 const showRev=ref=>{const mine=s.commit.answer;
  $('#rev').innerHTML=`<div class="card"><h3>Comparação com o valor concordante</h3><form id="fin" onsubmit="return false"><table class="cmp"><tr><th>Campo</th><th>Leitura cega</th><th>Claude</th><th>ChatGPT</th><th>Bruto</th><th>Classificação</th></tr>
  ${t.fields.map(fd=>{const r=ref[fd.id]||{};const mv=mine['v_'+fd.id];const cv=r.claude_parsed;const auto=fd.type==='text'?null:(normv(fd,mv)!==normv(fd,cv===null?'__null__':cv));
   const opts=[['same',fd.type==='text'?'sem diferença substantiva':'igual'],['extraction_error','diferente — erro da extração'],['reviewer_error','diferente — erro meu (extração certa)'],['equivalent','diferente — equivalente após normalização']];
   return `<tr><td>${esc(fd.id)}</td><td>${esc(Array.isArray(mv)?mv.join(', '):(mv==='__null__'?'(sem valor)':mv))}</td><td>${esc(r.claude)}</td><td>${esc(r.chatgpt)}</td><td>${auto===null?'<span class="muted">juízo</span>':auto?'<span class="diff">≠</span>':'<span class="same">=</span>'}</td>
   <td><select name="c_${fd.id}" data-auto="${auto}"><option value="">—</option>${opts.filter(o=>auto===false?o[0]==='same':(auto===true?o[0]!=='same':true)).map(o=>`<option value="${o[0]}">${o[1]}</option>`).join('')}</select><input type="text" name="n_${fd.id}" placeholder="nota" style="margin-top:4px"></td></tr>`}).join('')}</table></form></div>`;
  const fin=$('#fin');fin.querySelectorAll('select[data-auto="false"]').forEach(x=>x.value='same');if(s.final)fillForm(fin,s.final.answer);
  foot(`<button class="btn" id="fz">${s.final?'Atualizar e seguinte':'Concluir e seguinte'}</button>`);
  $('#fz').onclick=async()=>{const a=readForm(fin);for(const fd of t.fields){if(!a['c_'+fd.id])return msg('Classifica '+fd.id,1);if(fd.type==='text'&&a['c_'+fd.id]!=='same'&&!a['n_'+fd.id])return msg('Texto livre: justifica a diferença em '+fd.id,1)}
   a.raw_diff=t.fields.filter(fd=>{const x=fin.querySelector(`[name="c_${fd.id}"]`).dataset.auto;return x==='true'||(x==='null'&&a['c_'+fd.id]!=='same')}).map(fd=>fd.id);await send('final',a);nextPending()}};
 if(!s.commit){foot(`<button class="btn" id="cm">Confirmar extração cega (irreversível)</button>`);$('#cm').onclick=async()=>{const a=readForm(f);for(const fd of t.fields){if(fd.type==='enum'&&!a['v_'+fd.id])return msg('Falta '+fd.id+' (usa «sem valor no texto» se for o caso)',1);if(fd.type==='multienum'&&!(a['v_'+fd.id]||[]).length)return msg('Falta '+fd.id+' (marca «none» se nenhum)',1)}await send('commit',a);openTask(t.id)}}
 else if(!s.revealed_at){foot(`<button class="btn" id="rv">Revelar valores concordantes</button>`);$('#rv').onclick=async()=>{const r=await api('/api/reveal',{module:MOD.module,id:t.id});t._ref=r.ref;t._state.revealed_at='agora';showRev(r.ref);$('#rev').scrollIntoView({behavior:'smooth'})}}
 else showRev(t._ref)};
boot().catch(e=>{$('#pane').innerHTML='<div class="card"><h2>Erro</h2><p>'+esc(e.message)+'</p></div>'});
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    url = f"http://127.0.0.1:{a.port}/"
    print(f"Bancada em {url}  (Ctrl+C para parar; as respostas ficam em {ANS})")
    if not a.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nParado.")


if __name__ == "__main__":
    main()
