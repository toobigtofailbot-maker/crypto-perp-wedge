# WP-LAB-COORDINATOR-STATE-MODEL-01 — Repo-Truth Discovery

## Method

Read-only inspection of merged `origin/main` after PRs #564–#567. No edits made
during discovery. Searched docs, tools, tests, research, and scratch for the
status vocabularies already in repo truth, then read the canonical contracts and
status entries that define each lab stage.

## Base

- Branch base already contains PRs #564, #565, #566, #567.
- Recent commits: replay normalization contract (#565), walk-forward OOS gate
  (#567), generic robustness review reach (#566), funding fade conclude (#564).

## Existing stage vocabularies found in repo truth

The lab already defines per-stage vocabularies. The coordinator state model must
re-use these rather than invent parallel names.

### Idea intake / formalization
- `docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md`
- `docs/status_entries/WP-AGENT-IDEA-FORMALIZER-01.md`
- Hypothesis identity convention: `H-...-01` (e.g.
  `H-FUNDING-RATE-POSITIONING-FADE-01`).

### Experiment run / Result Populations
- `tools/registry/validate_result_populations.py`
- Result Population identity: `RP-####`, denominator manifest with
  planned/complete/failed/invalid/blocked/pruned counts; "denominator shrinkage
  forbidden".
- Funding fixture: `RP-2009`, `RP-7592` (scratch, non-canonical, NO-GO).

### Replay normalization (#565)
- `docs/research/RP_REPLAY_NORMALIZATION_CONTRACT.md`
- `tools/research_replay/normalization.py`
- States: a replay either normalizes successfully (raw + normalized stable
  hash) or fails closed. Match/no-match is equivalence, **not** approval.
- Fixture: `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/replay_fixture_summary.json`.

### Walk-forward / OOS gate (#567)
- `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md`
- `tools/oos_gate/evaluate.py`
- `gate_decision` enum (repo truth): `pass` | `fail` | `blocked` |
  `advisory_only`.
- Fixture: `scratch/WP-LAB-WALKFORWARD-OOS-GATE-01/fixture_gate_summary.json`
  (`gate_decision=fail`, RP-2592 / WF-RUN-40BB0B209274054B).

### Robustness + candidate-review reach (#566)
- `docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md`
- Output fields (repo truth): `candidate_review_packet_created`,
  `no_candidate_review_packet_reason`, `blocked_review_reason`,
  `advisory_only_summary`.
- Reason-code families (repo truth): `NO_GO_*` (no-packet), `BLOCKED_*`
  (blocked), `UNAVAILABLE_*` (withheld stats).
- Fixture: `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json`.

### Candidate lifecycle (downstream, human-gated — out of scope to mutate)
- `tools/candidate_lifecycle/lifecycle_engine.py`
- `LIFECYCLE_STATES`: proposed, in_research, research_concluded,
  paper_eligible, paper_active, paper_concluded, live_eligible, live_active,
  halted, archived.
- `HUMAN_GATED_TO_STATES` and `FORBIDDEN_TO_STATES` enforce a human operator
  gate before paper/live. This is the downstream consumer of the coordinator
  state model's `operator_gate_pending` / `candidate_ready_for_human_review`.

### Reporting
- `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`
- `docs/status_entries/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01.md` +
  `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json`.

### Read-only query / dashboard surfaces (future consumers)
- `tools/research_query/run.py --list-views` (DuckDB read-only views).
- `tools/dashboard/collector.py` (only dashboard component that reads repo
  artifacts; produces `dashboard_data.v1`).

## Mapping decision

The WP §5 candidate state list maps cleanly onto existing repo vocabulary:

| Coordinator state | Repo-truth source |
| --- | --- |
| `not_started` / `formalized` | idea-intake / formalization status entries |
| `experiment_complete` / `no_go` | Result Population denominator + conclusion |
| `replay_checked` | replay normalization contract |
| `oos_gate_pass` / `oos_gate_fail` / `oos_gate_blocked` | OOS `gate_decision` enum |
| `robustness_advisory` | generic robustness reach `advisory_only_summary` |
| `candidate_review_blocked` | `blocked_review_reason` (`BLOCKED_*`) |
| `candidate_review_not_created` | `no_candidate_review_packet_reason` (`NO_GO_*`) |
| `candidate_ready_for_human_review` | `candidate_review_packet_created=true` |
| `reported` | synthesis doc / status entry / conclusion traceability |
| `operator_gate_pending` | lifecycle `HUMAN_GATED_TO_STATES` boundary |

The coordinator model therefore introduces **no new status names**; it composes
existing per-stage vocabularies into one ordered pipeline and one read-only
snapshot.

## Funding end-to-end binding (primary fixture)

`H-FUNDING-RATE-POSITIONING-FADE-01` provides a complete real binding across all
stages:

- formalized (idea-intake/formalizer),
- experiment_complete (RP-2009 / RP-7592, denominator 36/36 preserved),
- replay_checked (both normalize; do not match each other — expected),
- OOS dry-run-only with deferred purge/embargo → `oos_gate_blocked`,
- robustness_advisory (PSR/DSR/MinTRL withheld, per-trade MC blocked),
- candidate_review_not_created (`NO_GO_PRIMARY_RISK_SCREEN_FAILED`),
- reported (synthesis + conclusion traceability),
- overall: `no_go`; operator gate not pending (no candidate produced).

The standalone OOS gate fixture (RP-2592, WF-RUN-40BB0B209274054B,
`gate_decision=fail`) provides a second binding exercising `oos_gate_fail`.

## Boundary confirmation

No transition execution, strategy run, edge-search, canonical write, candidate
lifecycle mutation, or protected-path change is required to build this model.
The resolver only reads committed JSON/markdown artifacts.
