# Repo Truth Discovery

Package: `WP-LABPROD-PAPER-HANDOFF-BOUNDARY-DEFINE-01`

Base inspected: `origin/main` / `126d9aaeaad2e5bd67e5163548f1223e6e78df13`

## Preflight

- Root checkout `C:\GitHub\crypto-perp-wedge` was clean on `main`.
- `git fetch --prune origin` completed.
- `git pull --ff-only origin main` reported already up to date.
- `gh pr list --state open --json number,title,headRefName,baseRefName,updatedAt,files` returned `[]`.
- Package worktree created at
  `C:\GitHub\crypto-perp-wedge-worktrees\labprod-paper-handoff-boundary-define-01`.

## Required Source Mapping

- Startup anchors:
  - `docs/project_status.md`
  - `CLAUDE_START_HERE.md`
  - `docs/runbook.md`
  - `AGENTS.md`
- Lab completion and lab productization:
  - `docs/research/LAB_COMPLETION_MAP.md`
  - `docs/research_pipeline/2026-06-strategy_research_lab_target_operating_model.md`
  - `docs/research_pipeline/2026-06-strategy_research_lab_design_consolidation_roadmap.md`
  - `docs/research/LAB_COORDINATOR_STATE_MODEL.md`
  - `docs/research/LAB_APPROVAL_QUEUE_SURFACE.md`
- Gate and approval/readiness boundaries:
  - `docs/onboarding/PHASE2_BASELINE.md` for D2-006, D2-007, and D2-011
  - `docs/research_pipeline/2026-04-rec_d2_006_gates_methodology.md`
  - `docs/research_pipeline/2026-04-rec5_floor_gap_stability.md`
  - `docs/research_pipeline/2026-04-phase9_decision_record.md`
  - `docs/research_pipeline/2026-05-approval_readiness_criteria_locking_decision.md`
  - `docs/research_pipeline/2026-05-scope6_packaging_locking_decision.md`
  - `docs/research_pipeline/2026-05-research_to_shadow_readiness_criteria_sketch.md`
  - `docs/research_pipeline/2026-05-shadow_to_paper_readiness_criteria_sketch.md`
- Candidate lifecycle and crossing surfaces:
  - `docs/architecture/candidate_lifecycle_design.md`
  - `docs/architecture/2026-06-agent_canonical_crossing_design.md`
- OOS/robustness/full-denominator sources:
  - `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md`
  - `docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md`
  - `docs/research_pipeline/2026-06-result_population_storage_design.md`
- Paper/shadow/live and human-gate boundaries:
  - `docs/architecture/paper_shadow_chassis_design.md`
  - `docs/architecture/2026-06-paper_bot_scaffolding_design.md`
  - `docs/architecture/LONG_TERM_SCOPE.md`
- Workflow/report-back guidance:
  - `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`
  - `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md`

## Facts

- The current lab completion map says the no-edge research lab is complete for
  known-payload proof, event-tape readiness, and bounded real-traffic
  acceptance evidence, but not unqualified production autonomy, real candidate
  admission, first real crossing, paper/live/runtime authority, or always-on
  factory completion.
- D2-006 defines eight locked promotion gates for any strategy candidate going
  from research to shadow.
- D2-007 defines shadow mode as the sole bridge from research backtester to
  paper runtime, with at least 14 calendar days of shadow and parity thresholds
  of PnL deviation no more than 10% and trade-count deviation no more than 5%.
- D2-011 gives agents research/evaluation/monitoring roles but no execution,
  gate approval, live-system access, risk-parameter, exchange-API, or protected
  execution authority.
- REC-5 requires at least 3 reconciliations per exact
  `candidate_id / outcome_kind / pipeline_version / expectation_source_type`
  segment before segment-level inference; current floor-gap docs reject pooled
  or cross-segment inference.
- Approval/readiness criteria are locked as human-review gates only. They do
  not create automatic transition, readiness, promotion, demotion, lifecycle,
  paper, live, risk-change, kill, runtime, or Tier 4 authority.
- Scope 6 locks future R2S approval-record, shadow-evidence retention, and S2P
  approval-record required-content shapes while preserving that records document
  human decisions and do not implement transitions.
- Candidate lifecycle and canonical crossing designs are docs-only and require
  separate future approval and implementation before any canonical writes.
- OOS and robustness contracts are non-authoritative review inputs; pass/fail or
  advisory outputs do not approve candidates or create readiness.
- Paper/shadow chassis and paper-bot scaffolding docs are design-only and do not
  authorize implementation, provider/API, credentials, broker/exchange/order, or
  protected runtime contact.

## Inferences

- A future GO-like lab output can surface only as an evidence packet or
  human-review prompt unless a later package explicitly authorizes candidate
  admission or canonical crossing.
- Any future paper/shadow discussion must first preserve D2-006, D2-007,
  REC-5, Phase 9/D2-011, Scope 6, and permanent human-gate boundaries.
- Missing robustness, OOS, PSR/DSR/MinTRL, per-trade, funding-stress, or
  simulator-realism support must be disclosed as unsupported, not converted into
  pass language.

## Decisions In This Package

- Add a single boundary document at
  `docs/research/LAB_RESEARCH_TO_PAPER_HANDOFF_BOUNDARY.md`.
- Add package-local scratch evidence and a status entry only.
- Do not edit `docs/project_status.md` or `docs/research/LAB_COMPLETION_MAP.md`.

## Open Questions

- The exact future artifact/schema path for any real candidate crossing remains
  unresolved in current repo truth.
- The exact future paper/shadow implementation path remains separately
  unauthorized.
- Exact future backtest-realism thresholds remain a future lock item.

## Future Options

- A later package may define an evidence-packet schema or review surface.
- A later Karl/Main-authorized package may define or execute a candidate
  crossing.
- A later protected-boundary package may design or implement paper/shadow only
  after explicit authorization.
