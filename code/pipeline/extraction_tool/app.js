// §13.2 extraction tool — schema-driven form renderer.
"use strict";

let SCHEMA = null, PAPERS = [], current = null;
let dirty = false, saving = false, saveTimer = null, editRevision = 0;
let loadedSavedAt = null;
const AUTOSAVE_MS = 750;
const widgets = {};  // widgets[block][name] = () => value
const evidenceWidgets = {};  // evidenceWidgets[block.field] = () => {mode,quote,page,rule}
const PHASE_ICONS = { blind: "🔵", verification: "🟡", ai_blind_test: "🧪" };
const PHASE_LABELS = { blind: "blind", verification: "verification", ai_blind_test: "AI test" };

const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (v != null) n.setAttribute(k, v);
  }
  for (const c of kids) if (c != null) n.append(c.nodeType ? c : document.createTextNode(c));
  return n;
};

// ----------------------------------------------------------------- widgets
function triState(value) {
  // null / true / false
  let val = value;
  const wrap = el("div", { class: "tri" });
  const opts = [["—", null], ["Yes", true], ["No", false]];
  const btns = opts.map(([lab, v]) => {
    const b = el("button", { type: "button", onclick: () => { val = v; paint(); fire(); } }, lab);
    return b;
  });
  function paint() { btns.forEach((b, i) => b.classList.toggle("on", opts[i][1] === val)); }
  function fire() { wrap.dispatchEvent(new Event("change", { bubbles: true })); }
  wrap.append(...btns); paint();
  wrap._get = () => val;
  return wrap;
}

function enumSelect(options, value) {
  const s = el("select");
  s.append(el("option", { value: "" }, "—"));
  options.forEach((o, i) => s.append(el("option", { value: String(i) }, String(o))));
  const selected = options.findIndex(o => o === value);
  s.value = selected < 0 ? "" : String(selected);
  s._get = () => (s.value === "" ? null : options[Number(s.value)]);
  return s;
}

function multiEnum(field, value) {
  const vals = Array.isArray(value) ? value.slice() : [];
  const known = new Set(field.options);
  const otherVal = vals.find(v => typeof v === "string" && v.startsWith("other-named:"));
  const wrap = el("div", { class: "checks" });
  const boxes = field.options.map(o => {
    const cb = el("input", { type: "checkbox" });
    cb.checked = vals.includes(o);
    cb._opt = o;
    return el("label", {}, cb, o);
  });
  wrap.append(...boxes);
  let otherInput = null;
  if (field.other) {
    otherInput = el("input", { type: "text", placeholder: "other-named: …",
      style: "flex-basis:100%" });
    if (otherVal) otherInput.value = otherVal.replace(/^other-named:\s*/, "");
    wrap.append(otherInput);
  }
  wrap._get = () => {
    const out = boxes.map(b => $("input", b)).filter(c => c.checked).map(c => c._opt);
    if (otherInput && otherInput.value.trim()) out.push("other-named: " + otherInput.value.trim());
    return out;
  };
  return wrap;
}

function listStr(value) {
  const vals = Array.isArray(value) ? value.slice() : [];
  const box = el("div");
  const rows = el("div");
  function addRow(v = "") {
    const inp = el("input", { type: "text", value: v });
    const rm = el("button", { class: "ghost", type: "button",
      onclick: () => { row.remove(); box.dispatchEvent(new Event("change", { bubbles: true })); } }, "✕");
    const row = el("div", { class: "row" }, inp, rm);
    rows.append(row);
  }
  vals.forEach(addRow);
  const add = el("button", { class: "ghost", type: "button",
    onclick: () => { addRow(""); box.dispatchEvent(new Event("change", { bubbles: true })); } }, "+ add");
  box.append(rows, add);
  box._get = () => [...rows.querySelectorAll(".row input")]
    .map(i => i.value.trim()).filter(Boolean);
  return box;
}

function listObj(field, value) {
  const vals = Array.isArray(value) ? value.slice() : [];
  const box = el("div");
  const rows = el("div");
  function addObj(obj = {}) {
    const getters = {};
    const card = el("div", { class: "obj" });
    for (const f of field.item_fields) {
      let w;
      if (f.type === "enum") w = enumSelect(f.options, obj[f.name]);
      else { w = el("input", { type: "text", value: obj[f.name] == null ? "" : obj[f.name] });
             w._get = () => (w.value.trim() || null); }
      getters[f.name] = w._get;
      card.append(el("div", { class: "gr" }, el("span", {}, f.name), w));
    }
    const rm = el("button", { class: "ghost", type: "button",
      onclick: () => { card.remove(); box.dispatchEvent(new Event("change", { bubbles: true })); } }, "✕ remove");
    card.append(rm);
    card._get = () => {
      const o = {}; for (const [k, g] of Object.entries(getters)) o[k] = g();
      return o;
    };
    rows.append(card);
  }
  vals.forEach(addObj);
  const add = el("button", { class: "ghost", type: "button",
    onclick: () => { addObj({}); box.dispatchEvent(new Event("change", { bubbles: true })); } }, "+ add metric");
  box.append(rows, add);
  box._get = () => [...rows.querySelectorAll(".obj")].map(c => c._get())
    .filter(o => Object.values(o).some(v => v != null && v !== ""));
  return box;
}

function makeWidget(field, value) {
  switch (field.type) {
    case "bool": return triState(value);
    case "enum": return enumSelect(field.options, value);
    case "multienum": return multiEnum(field, value);
    case "list_str": return listStr(value);
    case "list_obj": return listObj(field, value);
    case "textarea": { const t = el("textarea", {}, value == null ? "" : value);
      t._get = () => (t.value.trim() || null); return t; }
    default: { const i = el("input", { type: "text", value: value == null ? "" : value });
      i._get = () => (i.value.trim() || null); return i; }
  }
}

// ----------------------------------------------------------------- render
function fmtVal(v) {
  if (v == null) return "—";
  if (typeof v === "boolean") return v ? "true" : "false";
  if (Array.isArray(v)) return v.length
    ? v.map(x => (typeof x === "object" ? JSON.stringify(x) : x)).join("; ") : "—";
  return String(v);
}

function renderForm(tpl) {
  for (const k of Object.keys(widgets)) delete widgets[k];
  for (const k of Object.keys(evidenceWidgets)) delete evidenceWidgets[k];
  const ai = tpl._ai && Object.keys(tpl._ai).length ? tpl._ai : null;
  const required = new Set(tpl._review_fields || []);
  const form = $("#form"); form.innerHTML = "";
  for (const [block, spec] of Object.entries(SCHEMA)) {
    widgets[block] = {};
    const sec = el("div", { class: "section", id: "sec-" + block });
    sec.append(el("h2", {}, spec.title));
    for (const f of spec.fields) {
      const fq = block + "." + f.name;
      const w = makeWidget(f, (tpl[block] || {})[f.name]);
      widgets[block][f.name] = w._get;
      const priorEvidence = (tpl.reviewer_evidence || {})[fq] || {};
      const mode = enumSelect(
        ["quoted", "not_reported_after_full_text_review"],
        priorEvidence.mode || "quoted");
      const quote = el("textarea", { placeholder: "Literal supporting quote" }, priorEvidence.quote || "");
      const page = el("input", { type: "number", min: "1", placeholder: "Physical page" });
      page.value = priorEvidence.page == null ? "" : String(priorEvidence.page);
      const rule = el("input", { type: "text", placeholder: "Decision rule / rationale" });
      rule.value = priorEvidence.rule || "";
      function paintEvidenceMode() {
        const absence = mode._get() === "not_reported_after_full_text_review";
        quote.disabled = absence;
        page.disabled = absence;
        quote.closest(".quoted-evidence").classList.toggle("hidden", absence);
      }
      mode.addEventListener("change", paintEvidenceMode);
      evidenceWidgets[fq] = () => {
        const selectedMode = mode._get() || "quoted";
        return {
        mode: selectedMode,
        quote: selectedMode === "quoted" ? quote.value.trim() || null : null,
        page: selectedMode === "quoted" && page.value !== "" ? Number(page.value) : null,
        rule: rule.value.trim() || null,
      }; };
      const main = el("div", { class: "fmain" },
        el("label", {}, f.label),
        f.help ? el("div", { class: "help" }, f.help) : null,
        w);
      if (required.has(fq)) {
        const quoted = el("div", { class: "quoted-evidence" },
          quote, el("div", { class: "evidence-row" }, page, rule));
        main.append(el("div", { class: "evidence" },
          el("div", { class: "evidence-title" }, "Required human evidence"),
          el("label", { class: "evidence-mode" }, "Evidence mode", mode),
          el("div", { class: "absence-help" },
            "Use “not reported…” only for false, null, empty-list, or registered absence values; give the decision rationale."),
          quoted));
        paintEvidenceMode();
      }
      const field = el("div", { class: "field" }, main);
      if (ai) {  // post-commit comparison column (read-only model outputs)
        const col = el("div", { class: "aicol" });
        for (const [m, out] of Object.entries(ai)) {
          col.append(el("div", { class: "aival" },
            el("span", { class: "aim" }, m + " "), fmtVal((out[block] || {})[f.name])));
        }
        field.classList.add("cmp");
        field.append(col);
      }
      sec.append(field);
    }
    form.append(sec);
  }
  // reviewer notes
  const notes = el("textarea", {}, tpl.reviewer_notes || "");
  notes.id = "notes";
  form.append(el("div", { class: "section" },
    el("h2", {}, "Reviewer notes (free text)"),
    el("div", { class: "field" }, notes)));
  form.addEventListener("change", () => { updateDim(); markDirty(); });
  form.addEventListener("input", () => { updateDim(); markDirty(); });
  updateDim();
}

function readBlock(block) {
  const o = {};
  for (const [name, get] of Object.entries(widgets[block] || {})) o[name] = get();
  return o;
}

function readEvidence() {
  const out = {};
  for (const [field, get] of Object.entries(evidenceWidgets)) {
    const item = get();
    if (item.mode !== "quoted" || item.quote != null || item.page != null || item.rule != null) {
      out[field] = item;
    }
  }
  return out;
}

function updateDim() {
  const elig = readBlock("eligibility");
  $("#sec-level_a").classList.toggle("dim", elig.methodological_eligibility === false);
  $("#sec-level_b").classList.toggle("dim", elig.level_3b !== true);
}

function renderMeta(tpl) {
  const m = tpl.metadata;
  $("#meta").innerHTML =
    `<div style="font-weight:600">${m.title}</div>
     <div style="color:var(--muted);font-size:12px">${m.authors} · ${m.year} · ${m.source}
     · Rayyan: ${m.rayyan_decision} · <span class="pill ${tpl._phase}">${tpl._phase}</span></div>`;
}

// ------------------------------------------------- blind-first state banner
const STATE_LABELS = {
  blind: "BLIND — model outputs withheld until you commit",
  revealed: "REVEALED — model outputs shown; every edit is logged",
  finalised: "FINALISED — locked",
};

function renderBanner(tpl) {
  const st = tpl._state || "blind";
  const bar = $("#modebar");
  bar.className = "modebar " + st;
  bar.innerHTML = "";
  bar.append(el("span", { class: "modelabel" }, STATE_LABELS[st] || st));
  bar.append(el("span", { class: "sp" }));
  if (st === "blind") {
    bar.append(el("button", { onclick: commit }, "Commit blind answers"));
  } else if (st === "revealed") {
    bar.append(el("button", { onclick: finalise }, "Finalise"));
  }
  $("#save").disabled = st === "finalised";
  $("#done").disabled = st === "finalised";
}

async function commit() {
  if (!current) return;
  if (!confirm("This freezes your blind answers and reveals model outputs — irreversible. Continue?")) return;
  if (!(await flushSave({ reason: "commit" }))) return;
  const r = await (await fetch("/api/commit/" + current, { method: "POST" })).json();
  if (!r.ok) { $("#status").textContent = "✗ " + (r.error || "commit failed"); return; }
  const p = PAPERS.find(x => x.key === current); if (p) p.state = r.state;
  loadPaper(current);  // refetch: server now attaches model outputs
}

async function finalise() {
  if (!current) return;
  if (!confirm("Finalise this paper? Further edits will be locked.")) return;
  if (!(await flushSave({ reason: "finalise" }))) return;
  const r = await (await fetch("/api/finalise/" + current, { method: "POST" })).json();
  if (!r.ok) { $("#status").textContent = "✗ " + (r.error || "finalise failed"); return; }
  const p = PAPERS.find(x => x.key === current); if (p) p.state = r.state;
  loadPaper(current);
}

// ----------------------------------------------------------------- nav + io
let loadSeq = 0;

function capturePayload() {
  return {
    eligibility: readBlock("eligibility"),
    level_a: readBlock("level_a"),
    level_b: readBlock("level_b"),
    reviewer_notes: $("#notes")?.value.trim() || "",
    reviewer_evidence: readEvidence(),
    _done: !!$("#done")?.checked,
  };
}

function draftKey(key) {
  return `c23-reviewer-draft:${location.pathname}:${key}`;
}

function persistLocalDraft(key, payload) {
  if (!key) return false;
  try {
    localStorage.setItem(draftKey(key), JSON.stringify({
      paper_key: key,
      saved_at: new Date().toISOString(),
      payload,
    }));
    return true;
  } catch (_) {
    return false;
  }
}

function clearLocalDraft(key) {
  if (!key) return;
  try { localStorage.removeItem(draftKey(key)); } catch (_) { /* server receipt remains authoritative */ }
}

function restoreLocalDraft(key, tpl) {
  let draft;
  try {
    draft = JSON.parse(localStorage.getItem(draftKey(key)) || "null");
  } catch (_) {
    localStorage.removeItem(draftKey(key));
    return { tpl, recovered: false };
  }
  if (!draft?.payload || draft.paper_key !== key) return { tpl, recovered: false };
  const localTime = Date.parse(draft.saved_at || "") || 0;
  const diskTime = Date.parse(tpl._saved_at || tpl.saved_at || "") || 0;
  if (localTime <= diskTime) {
    clearLocalDraft(key);
    return { tpl, recovered: false };
  }
  const restored = { ...tpl };
  for (const block of ["eligibility", "level_a", "level_b"]) {
    restored[block] = draft.payload[block] || tpl[block];
  }
  restored.reviewer_notes = draft.payload.reviewer_notes || "";
  restored.reviewer_evidence = draft.payload.reviewer_evidence || {};
  restored._done = !!draft.payload._done;
  return { tpl: restored, recovered: true };
}

function setSaveState(kind, detail = "") {
  const labels = {
    clean: "Saved to disk",
    dirty: "Unsaved changes",
    saving: "Saving…",
    recovered: "Recovered local draft",
    failed: "Save failed — local recovery copy retained",
  };
  const node = $("#save-state");
  node.className = "save-state " + kind;
  node.textContent = labels[kind] + (detail ? " · " + detail : "");
}

function markDirty() {
  if (!current) return;
  dirty = true;
  editRevision += 1;
  persistLocalDraft(current, capturePayload());
  setSaveState("dirty");
  scheduleAutosave();
}

function scheduleAutosave() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => { flushSave({ reason: "autosave" }); }, AUTOSAVE_MS);
}

async function flushSave({ reason = "manual" } = {}) {
  if (!current) return false;
  clearTimeout(saveTimer);
  saveTimer = null;
  const keyAtStart = current;
  const revisionAtStart = editRevision;
  const payload = capturePayload();
  persistLocalDraft(keyAtStart, payload);
  saving = true;
  setSaveState("saving", reason === "autosave" ? "autosave" : "");
  let r;
  try {
    const response = await fetch("/api/save/" + keyAtStart, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    r = await response.json();
    if (!response.ok || !r.ok) throw new Error(r.error || "save failed");
  } catch (error) {
    saving = false;
    dirty = true;
    setSaveState("failed", error.message);
    $("#status").textContent = "✗ " + error.message;
    return false;
  }
  saving = false;
  loadedSavedAt = r.saved_at;
  const p = PAPERS.find(x => x.key === keyAtStart); if (p) p.done = r.done;
  refreshPicker();
  if (current === keyAtStart && editRevision === revisionAtStart) {
    dirty = false;
    clearLocalDraft(keyAtStart);
    setSaveState("clean", new Date().toLocaleTimeString());
    $("#status").textContent = "";
  } else if (current === keyAtStart) {
    dirty = true;
    persistLocalDraft(keyAtStart, capturePayload());
    setSaveState("dirty");
    scheduleAutosave();
  }
  return true;
}

async function loadPaper(key) {
  const seq = ++loadSeq;
  const diskTpl = await (await fetch("/api/paper/" + key)).json();
  if (seq !== loadSeq) return false;
  clearTimeout(saveTimer);
  saveTimer = null;
  const restored = restoreLocalDraft(key, diskTpl);
  const tpl = restored.tpl;
  current = key;
  loadedSavedAt = diskTpl._saved_at || null;
  editRevision = 0;
  dirty = restored.recovered;
  saving = false;
  $("#pdf").src = "/pdf/" + key;
  renderMeta(tpl);
  renderBanner(tpl);
  renderForm(tpl);
  $("#done").checked = !!tpl._done;
  $("#picker").value = key;
  $("#status").textContent = "";
  if (restored.recovered) {
    setSaveState("recovered");
    editRevision = 1;
    scheduleAutosave();
  } else {
    setSaveState("clean", loadedSavedAt ? "disk receipt " + loadedSavedAt : "");
  }
  const idx = PAPERS.findIndex(p => p.key === key);
  $("#prev").disabled = idx <= 0;
  $("#next").disabled = idx >= PAPERS.length - 1;
  return true;
}

async function navigateTo(key) {
  if (!key || key === current) return true;
  if (current && (dirty || saving)) {
    const previous = current;
    if (!(await flushSave({ reason: "navigation" }))) {
      $("#picker").value = previous;
      return false;
    }
  }
  return loadPaper(key);
}

async function save() {
  return flushSave({ reason: "manual" });
}

function refreshPicker() {
  const phase = PAPERS[0]?.phase || "blind";
  const done = PAPERS.filter(p => p.phase === phase && p.done).length;
  const total = PAPERS.filter(p => p.phase === phase).length;
  $("#progress").textContent = `${PHASE_LABELS[phase] || phase} ${done}/${total}`;
  const pk = $("#picker");
  pk.innerHTML = "";
  for (const p of PAPERS) {
    const tag = PHASE_ICONS[p.phase] || "○";
    const lock = p.state === "finalised" ? "🔒 " : p.state === "revealed" || p.state === "committed" ? "👁 " : "";
    pk.append(el("option", { value: p.key },
      `${p.done ? "✓ " : "○ "}${tag} ${lock}${p.key.replace("rayyan-", "")} — ${p.title.slice(0, 48)}`));
  }
  if (current) pk.value = current;
}

async function step(d) {
  const idx = PAPERS.findIndex(p => p.key === current);
  const ni = idx + d;
  if (ni >= 0 && ni < PAPERS.length) await navigateTo(PAPERS[ni].key);
}

async function init() {
  SCHEMA = await (await fetch("/api/schema")).json();
  PAPERS = await (await fetch("/api/papers")).json();
  refreshPicker();
  $("#picker").addEventListener("change", e => navigateTo(e.target.value));
  $("#prev").addEventListener("click", () => step(-1));
  $("#next").addEventListener("click", () => step(1));
  $("#save").addEventListener("click", save);
  $("#done").addEventListener("change", markDirty);
  document.addEventListener("keydown", e => {
    if ((e.metaKey || e.ctrlKey) && e.key === "s") { e.preventDefault(); save(); }
  });
  window.addEventListener("beforeunload", e => {
    if (!dirty && !saving) return;
    persistLocalDraft(current, capturePayload());
    e.preventDefault();
    e.returnValue = "";
  });
  if (PAPERS.length) loadPaper(PAPERS[0].key);
}

init();
