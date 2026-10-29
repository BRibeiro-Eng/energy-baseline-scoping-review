# C-2.3 Reviewer Extraction Tool

Local form-with-PDF for blind-first human charting without editing raw JSON.
Enum fields are dropdowns/checkboxes, so saved values are schema-valid by construction.

## Run

```bash
cd production/reviewer_workspace
python3 extraction_tool/serve.py \
  --canonical-root ../.. \
  --data-root reviews
# open http://127.0.0.1:5051
```

Needs Flask (`pip install flask` — already present in this env).

## Use

- **Picker** (top): all queued review papers. 🔵 = blind, 🟡 = verification. ✓ = marked done.
- **Left:** the PDF. **Right:** the form (Eligibility → Level A → Level B → notes).
- Level A dims when you mark the paper ineligible; Level B dims unless Level 3B = true. (Dimming is a guide, not a lock.)
- Every edit is copied immediately to browser-local recovery storage and
  autosaved to disk after a short pause. **⌘S** (or Save) forces an immediate save.
- The footer distinguishes `Unsaved changes`, `Saving…`, `Saved to disk`,
  `Recovered local draft`, and `Save failed`. A newer local draft is restored
  automatically after a refresh or browser/app interruption.
- Changing paper first flushes the current form; navigation is cancelled if the
  disk save fails. Closing/reloading with a dirty or in-flight form triggers the
  browser's unsaved-work warning.
- Required human evidence has two registered modes:
  `quoted` requires a literal quote and physical page;
  `not_reported_after_full_text_review` is restricted to absence-like values
  (false, null, an empty list, or a registered absence label), forbids a
  fabricated quote/page, and requires a decision rationale.
- `Commit blind answers` freezes the pre-reveal values before model outputs appear.
- `Finalise` first saves the form and only locks it when `mark done` is enabled.

## Blind-first gate

1. Chart the paper while model values are withheld.
2. Save, then commit the blind answers. This transition is irreversible.
3. Compare with the revealed model values; every changed field is logged.
4. Enable `mark done` and finalise to lock the record.

## Files

- `serve.py` — Flask app (API + PDF serving + save)
- `schema.py` — v2.2.1 field definitions (single source of truth, mirrors PROTOCOL.md §6)
- `index.html`, `app.js` — UI

Saved data lives below the configured reviewer `data-root`.
The tool only writes `eligibility`, `level_a`, `level_b`, `reviewer_notes`,
`reviewer_evidence`, `_done`, and the server `saved_at` receipt.
It listens only on `127.0.0.1` and makes no network calls.
