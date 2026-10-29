#!/usr/bin/env bash
# Recompute data/06-late-verification/resultados.json from the released tasks and decision logs.
# relatorio.py expects the working layout of the review (tarefas/, respostas/ next to the script);
# this script recreates it with symbolic links in a temporary folder and compares the output.
set -euo pipefail
PKG="$(cd "$(dirname "$0")/../.." && pwd)"
T="$(mktemp -d)"
mkdir "$T/tarefas"
for f in "$PKG"/data/06-late-verification/tasks/*.json; do ln -s "$f" "$T/tarefas/$(basename "$f")"; done
ln -s "$PKG/data/06-late-verification/tasks/_ref" "$T/tarefas/_ref"
# the released d13 task file has the publisher abstracts redacted; relatorio.py does not read them
ln -sf "$PKG/data/06-late-verification/tasks/d13.redacted.json" "$T/tarefas/d13.json"
ln -s "$PKG/data/06-late-verification/responses" "$T/respostas"
cp "$PKG/code/late-verification/relatorio.py" "$T/"
(cd "$T" && python3 relatorio.py > /dev/null)
python3 - "$T/resultados.json" "$PKG/data/06-late-verification/resultados.json" <<'PY'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:])
bad = [k for k in b if a.get(k) != b.get(k)]
print("modules recomputed:", ", ".join(b))
print("identical to the released resultados.json" if not bad else f"DIFFERENT: {bad}")
sys.exit(1 if bad else 0)
PY
echo "output in $T"
