# Repo Truth Discovery

Package: `WP-LAB-RUN-REGISTRY-PROVENANCE-HARDEN-01`

Base commit: `cbbca34fa62dabcb17c81bbf25c264f0dcb64b56`.

Preflight:

- `origin/main` fetched and `main` fast-forward checked: already up to date.
- No local or remote `lab/run-registry-provenance-harden-01` branch existed before package branch creation.
- Open PR search for this package returned none.
- Pre-existing untracked `build/` was present before package work and left untouched / unstaged.

PR #583-#587 artifacts observed:

- PR #583: `docs/status_entries/WP-LAB-BASELINE-PAYLOAD-DEFINE-01.md`, `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json`.
- PR #584: `docs/status_entries/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01.md`, `scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/baseline_gate_expectations.json`.
- PR #585: `docs/status_entries/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01.md`, `scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/guard_validation_summary.json`.
- PR #586: `docs/status_entries/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01.md`, `scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/baseline_loop_result.json`.
- PR #587: `docs/status_entries/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01.md`, `docs/research/LAB_COMPLETION_MAP.md`, `scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/completion_state_update.json`, `scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/held_boundary_map.json`.

Existing registry/result-store/lab-state surfaces:

- `tools/lab_registry/build_lab_run_registry.py` and `tools/lab_registry/validate_lab_run_registry.py` already build and validate a read-only lab registry over committed Result Populations.
- `tools/lab_state/`, `tools/lab_dashboard/`, and `tools/lab_reporting/` provide read-only operator state/reporting projections.
- `tools/research_query/` provides read-only query views.
- `tools/registry/validate_result_populations.py` and `tools/registry/validate_candidate_registry.py` validate canonical artifact stores.

Current canonical artifact inventories:

- Result Populations observed: RP-2134, RP-2592, RP-3731, RP-4492, RP-6236, RP-6688, RP-7134, RP-7520.
- Candidate registry observed: `research/candidate_registry.jsonl` with current H-001..H-012 entries inspected read-only.

Current scratch/status inventories relevant to lab runs:

- Funding-fade NO-GO synthesis and Stage-1 triage artifacts under `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md` and `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/`.
- Baseline construction sequence artifacts under `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/`, `scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/`, `scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/`, `scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/`, and `scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/`.
- Price-only/data-derived frontier index under `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/evidence_index.json`.

Selected registry hardening route:

- Package-local scratch index and status entry only.
- Existing `tools/lab_registry` builder was used to create `existing_lab_run_registry_snapshot.json`; no helper/schema/code changes were needed.

Files intentionally left unchanged:

- `research/result_populations/**`
- `research/candidate_registry.jsonl`
- `tools/research_runner/**`
- `tools/registry/**`
- `tools/candidate_lifecycle/**`
- `lib/**`
- `configs/**`
- `data/**`
- requirements/dependency files
- runtime, paper/live, OMS, risk, reconciliation, broker, exchange, order, capital paths

Explicit non-authority statement:

This registry/index is read-only and non-authoritative. It records provenance, lineage, validation status, blockers, terminal states, and caveats over existing artifacts only. It creates no candidate authority, no ranking/recommendation authority, no promotion/readiness authority, no canonical crossing authority, and no paper/live/runtime authority.
