# Eligibility contract

`python -m tools.canon_intake.eligibility_validator <draft_id>` reads one scratch draft, its optional review trail, the concluded candidate registry, canonical Strategy Specs, and Result Populations. Every read artifact is SHA-256 hashed.

It deterministically evaluates falsifiability, market/timeframe bounds, feature/data availability, historical testability, parameter bounds, provenance, duplicate proximity, and concluded-family freshness. A check is `pass`, `fail`, or `unknown`; missing evidence is never converted to a pass.

Malformed packets, review trails, registries, specs, or populations fail closed before a report is written. Reports are written only to `scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports/` unless `--no-write` is used.

`eligible_for_gate_c_review` means only that the bounded advisory screen found no failed/unknown check and a reviewed or flagged review state exists. It is not approval, Gate C, canonical-write authority, queue admission, candidate creation, or research execution.
