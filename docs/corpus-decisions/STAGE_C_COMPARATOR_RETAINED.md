# output/stage_c_compare.py — retained, out of the executed pipeline

Reviewer decision 2026-09-12: Stage C extracts on one surface, so there is no second extraction
to compare. This module and `stage_c/test_compare.py` (27 assertions) are **kept and not
deleted**, for two reasons:

- they encode nine measured comparator defects — discarded occurrence multiplicity, fields absent
  from the pairing keys (`normative_framing`, `addresses_mechanism`, `also_constrains_model`),
  silently overwritten repeated C3 variables and C5 vectors, an invisible `support_class` flip,
  and the same value grounded in two different sentences counted as agreement. That is the record
  of what a naive comparator gets wrong, and it cost real work to find;
- if a second extraction surface is ever added, they are ready.

They produce nothing for this review. `preflight.sh` runs the suite so the code cannot rot
silently, and labels it retained. No figure in the thesis comes from this module.
