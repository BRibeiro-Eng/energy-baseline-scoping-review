#!/usr/bin/env python3
"""Generate §11 (skeleton) and §12 (closed lists) of the extraction prompt FROM the schema.

  /usr/local/bin/python3 output/stage_c_prompt_build.py [--check]

The prompt and the schema drifted twice: the schema split `mechanism` into two axes and §11
still showed the old single enum, so the surfaces were being told to return a shape the
validator rejects. Hand-maintaining both is not viable — §11 and §12 are now derived, and
stage_c/PROMPT_HEADER.md (§1-§10) is the only hand-written part. `--check` exits non-zero if
the file on disk is not what the current schema produces, so preflight catches the drift.
"""
import argparse, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SC = "stage_c"
SCHEMA = json.load(open(f"{SC}/schema.json", encoding="utf-8"))

def deref(node, seen=()):
    """Resolve $ref and flatten allOf. The schema composes every enveloped value as
    allOf[ {$ref: env}, {value: {enum: [...]}} ]; a renderer that does not flatten that
    shows an empty object and the surface returns a shape the validator rejects."""
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        ref = node["$ref"]
        if ref in seen:
            return {"type": "object", "properties": {}}
        tgt = SCHEMA
        for part in ref.lstrip("#/").split("/"):
            tgt = tgt[part]
        merged = deref(tgt, seen + (ref,))
        rest = {k: v for k, v in node.items() if k != "$ref"}
        return _merge(merged, deref(rest, seen + (ref,))) if rest else merged
    if "allOf" in node:
        out = {k: v for k, v in node.items() if k != "allOf"}
        for sub in node["allOf"]:
            out = _merge(out, deref(sub, seen))
        return out
    return node


def _merge(a, b):
    """Shallow schema merge; `properties` merges key by key, `required` unions."""
    # `"value": true` in $defs/env means 'any'; a later allOf member narrows it to an enum.
    if a is True or not isinstance(a, dict):
        return b if isinstance(b, dict) else {}
    if b is True or not isinstance(b, dict):
        return a
    out = dict(a)
    for k, v in (b or {}).items():
        if k == "properties":
            props = dict(out.get("properties") or {})
            for pk, pv in v.items():
                props[pk] = _merge(deref(props.get(pk) or {}), deref(pv)) if pk in props else pv
            out["properties"] = props
        elif k == "required":
            out["required"] = sorted(set(out.get("required") or []) | set(v))
        else:
            out[k] = v
    return out


# An envelope's bookkeeping keys are rendered as instructions, not as types.
def override(k, node):
    """Render the two bookkeeping keys as instructions. Nullable only where the schema allows
    null: in `mechanisms` the quote is required and non-null, and telling the surface it may
    be null there invites an unevidenced mechanism."""
    t = deref(node).get("type")
    nullable = isinstance(t, list) and "null" in t
    if k == "evidence_quote":
        return "<verbatim" + (", or null only for an absence>" if nullable else ">")
    return "<int" + (", or null only for an absence>" if nullable else ">")

# Optional envelope bookkeeping keys. The envelope appears ~50 times in the skeleton, so
# printing these inside each one adds 9 KB of noise. `confidence` is worse than noise: a
# self-reported number invites an invented one, and nothing in the analysis consumes it.
# They are legal and are documented once in the §11 preamble instead.
HIDE = {"non_contiguous_evidence", "searched_terms"}


def _lit(x):
    return "null" if x is None else str(x)


def scalar(node):
    node = deref(node)
    if "const" in node:
        return _lit(node["const"])
    if "enum" in node:
        return " | ".join(_lit(x) for x in node["enum"])
    t = node.get("type")
    if isinstance(t, list):
        return f"<{t}>"
    if t == "integer":
        return "<integer>"
    if t == "number":
        return "<number>"
    if t == "boolean":
        return "<boolean>"
    return "<string>"


def render(node, ind):
    """Return the rendered VALUE for a schema node, at indent `ind`."""
    node = deref(node)
    if node is True or node == {}:
        return '"<any>"'
    t = node.get("type")
    if t == "object" or "properties" in node:
        req = set(node.get("required") or [])
        props = node.get("properties") or {}
        lines = ["{"]
        items = sorted(props.items(), key=lambda kv: (kv[0] not in req, list(props).index(kv[0])))
        items = list(props.items())                      # schema order, not sorted
        if "support_class" in props:
            items = [(k, v) for k, v in items if k not in HIDE]
        for i, (k, v) in enumerate(items):
            name = k if k in req else k + "?"
            if k in ("evidence_quote", "page"):
                body = '"' + override(k, v) + '"'
            else:
                body = render(v, ind + 2)
            comma = "," if i < len(items) - 1 else ""
            lines.append(f'{" " * (ind + 2)}"{name}": {body}{comma}')
        lines.append(" " * ind + "}")
        return "\n".join(lines)
    if t == "array":
        inner = render(node.get("items") or {}, ind + 2)
        return "[\n" + " " * (ind + 2) + inner + "\n" + " " * ind + "]"
    return '"' + scalar(node) + '"'


def enums(node, path="", out=None):
    out = {} if out is None else out
    if not isinstance(node, dict):
        return out
    node = deref(node)
    if not isinstance(node, dict):
        return out
    if "enum" in node and path:
        out[path] = [str(x) for x in node["enum"]]
    for k, v in (node.get("properties") or {}).items():
        enums(v, f"{path}.{k}" if path else k, out)
    if node.get("items"):
        enums(node["items"], path, out)
    for sub in node.get("allOf") or []:
        enums(sub, path, out)
    return out


SKIP_IN_APPENDIX = {"support_class", "absence_basis", "record_type", "schema_version"}


def build():
    head = open(f"{SC}/PROMPT_HEADER.md", encoding="utf-8").read().rstrip() + "\n"
    body = [head, "## 11. The exact shape — copy this skeleton\n",
            "Generated from the schema. Key names are exact; a `?` marks an optional key and is "
            "not part\nof the name. Enum fields show **all** their legal values.\n",
            "`C1_dependent_variable` is an OBJECT with sub-fields, not keys on the model. "
            "`mechanisms`,\n`adaptations`, `study_limitations`, `implementation_barriers`, "
            "`absence_declarations` and\n`C13_reproducibility` live at **paper level**, never "
            "inside a model.\n",
            "Two optional keys are omitted from the skeleton to keep it readable, and both are "
            "legal on\nEVERY object that carries evidence: `searched_terms` (array of strings, "
            "useful on an absence)\nand `non_contiguous_evidence` (boolean, when the quote is "
            "assembled from two places on the\npage). There is no `confidence` field: a "
            "self-assigned number is not evidence, nothing in the\nanalysis reads it, and it is "
            "not accepted anywhere.\n",
            "**`absence_declarations` is required.** An empty `mechanisms` array asserts nothing "
            "unless\nyou also declare that you searched; a paper that genuinely identifies no "
            "model limitation is\na finding, and a finding needs a basis.\n",
            "```json", render(SCHEMA, 0), "```\n", "---\n",
            "## 12. Appendix — every closed list, generated from the schema\n",
            "The only legal values. Copy them character for character.\n",
            "Every envelope also accepts `support_class`: `direct statement` | `requires "
            "inference` |\n`absence checked`, and `absence_basis`: `searched full text` | "
            "`section absent` |\n`explicitly stated absent` | `field meaningless here`. Not "
            "repeated below.\n"]
    ap = enums(SCHEMA)
    for p in sorted(ap):
        if p.rsplit(".", 1)[-1] in SKIP_IN_APPENDIX:
            continue
        body.append(f"- `{p}`: " + " · ".join(f"`{v}`" for v in ap[p]))
    return "\n".join(body) + "\n"


def main():
    a = argparse.ArgumentParser(); a.add_argument("--check", action="store_true")
    a = a.parse_args()
    new = build()
    p = f"{SC}/PROMPT_EXTRACTION.md"
    old = open(p, encoding="utf-8").read() if os.path.isfile(p) else ""
    if a.check:
        same = old == new
        print(("prompt: IN SYNC with the schema" if same else
               "prompt: STALE — regenerate with output/stage_c_prompt_build.py")
              + f"  (schema {hashlib.sha256(json.dumps(SCHEMA, sort_keys=True).encode()).hexdigest()[:12]})")
        sys.exit(0 if same else 1)
    open(p, "w", encoding="utf-8").write(new)
    n_enums = sum(1 for k in enums(SCHEMA) if k.rsplit('.', 1)[-1] not in SKIP_IN_APPENDIX)
    print(f"wrote {p}: {len(new)} bytes, {n_enums} closed lists"
          + ("" if old else " (new)") + ("" if old == new else "  [CHANGED]"))


if __name__ == "__main__":
    main()
