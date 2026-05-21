# Stage 2c Workflow Efficiency Operating-Model Lock

## Scope

This is a documentation-only operating-model lock. It records accepted Stage 2c workflow-efficiency decisions and does not create implementation authority, evidence authority, runtime authority, or downstream decision authority.

Repo truth and active package scope still outrank this lock. Package-specific forbidden scope also overrides the general tier model below.

## Current state at lock

Latest merged runway package: WP-12bh / WP-S2c-25.

Current H-005 state:

- H-005 / research_oos / pre_wp_5b / d2_006_gates count = 2
- H-005 / research_oos / pre_wp_5b / exp_success_criteria count = 1

Next strict H-005 runway package remains WP-S2c-26 unless this lock package is inserted first.

WP-S2c-25a is an inserted workflow-lock package. It does not replace WP-S2c-26 and does not change the H-005 runway sequence.

## Tiered workflow model

Tier 0 - Strategy / boundary decisions:

- Authorization: Karl/Main.
- Typical package size: variable, because these decisions set boundaries.
- Validation posture: decision-specific, with repo-truth inspection and explicit stop-condition handling.
- Main/Karl re-engagement: always required for boundary unlocks, methodology changes, protected-path implications, and unresolved authority questions.

Tier 1 - Safe documentation / planning packages:

- Authorization: Karl/Main may authorize bounded documentation and planning locks inside existing boundaries.
- Typical package size: small and mergeable.
- Validation posture: refreshed-main preflight, exact changed-file scope checks, integrity views, registry validators where repo convention requires them, and full pytest unless a future repo-approved validation-tier document changes that rule.
- Main/Karl re-engagement: required when documentation would change authority, sequencing, methodology, or protected boundaries.

Tier 2 - Research artifacts / query packages:

- Authorization: approved work package scope.
- Typical package size: narrow artifact append or bounded query-layer package.
- Validation posture: artifact/schema/query integrity, registry validators, scoped regression, full pytest, and exact-scope diff checks as package class requires.
- Main/Karl re-engagement: required on integrity drift, validation failure, evidence/authority tension, stop triggers, or package scope conflict.

Tier 3 - Local automation infrastructure:

- Authorization: explicit package authority.
- Typical package size: bounded local helper or automation surface, with dry-run/default-safe behavior where applicable.
- Validation posture: prove local boundedness, corpus/schema compatibility where relevant, no runtime influence, and no protected-path contact.
- Main/Karl re-engagement: required before scheduler, trigger, runtime, paper/live, policy, or protected-path implications.

Tier 4 - Runtime / paper / live / OMS / risk / protected paths:

- Authorization: strict Karl/Main boundary authority only.
- Typical package size: narrow and separately authorized.
- Validation posture: strongest applicable runtime, safety, reconciliation, and regression evidence.
- Main/Karl re-engagement: always required.

Tier 4 remains strict and cannot be accelerated by this operating-model lock.

## Main / Side / Codex authority split

Main/Karl sets strategy, unlocks boundaries, approves methodology changes, and resolves Tier 0 / Tier 4 decisions.

Side may draft packages inside approved envelopes without asking Main for every micro-step. Side must still inspect repo truth before drafting or reviewing and must stop on boundary conflict.

Codex executes only the active work package from refreshed `main` within exact scope. Codex does not decide policy, methodology, lifecycle, promotion/demotion, scoring/ranking, runtime, paper/live, or downstream authority.

Future chats must use current merged repo truth first.

## Project-status overlap guardrail

No simultaneous open PRs may modify `docs/project_status.md` unless the later PR is refreshed or rebased after the earlier PR merges.

Operational rules:

- Every new work package that edits `docs/project_status.md` must start from refreshed `main`.
- Before opening a PR that edits `docs/project_status.md`, Codex must check for open PRs touching that file when feasible.
- If another open PR already touches `docs/project_status.md`, Codex must stop and report rather than creating a competing status-edit PR.
- This is a merge-control rule, not a Main authorization gate.

## Standing efficiency authorization

Main has standing authorization to surface credible workload-reduction ideas.

Ideas must be classified as:

- safe to adopt now;
- needs design first;
- risky / not recommended.

Safe reductions may be adopted only if they do not weaken validation, repo truth, stop triggers, protected boundaries, or package-specific scope.

Design-first reductions require a Tier 1 design package and Karl/Main approval before application.

Risky reductions must not be adopted without explicit future reversal.

## Adopted low-risk efficiencies

Status-entry brevity standardization:

- `docs/project_status.md` entries should be concise when full detail exists in the package artifact, document, or PR body.
- The status entry must still record package identity, created/modified files, core boundary, and next-step authority.
- Brevity does not permit omitting material authority or boundary facts.

Stable integrity-view report brevity:

- If the integrity view count is stable and all discovered views were actually run, report-backs may summarize as `v_integrity_*: clean (N)`.
- This changes reporting only, not validation.
- The underlying integrity views must still be listed, discovered, and run.

## Authorized design tranches

WP-S2c-21b is the paired-source reuse methodology design tranche.

WP-S2c-21c is the batched REP+OL+REC cycle methodology design tranche.

WP-S2c-21b drafts from refreshed `main` after clean merge of whichever package is in flight. WP-S2c-21c drafts only after WP-S2c-21b merges.

Mandatory Main re-engagement is required after WP-S2c-21c report-back to approve R1/R2 before implementation use.

R1/R2 apply to H-006 onward only unless Main explicitly changes that later.

R1/R2 are not implementation-authorized by this operating-model lock.

## H-005 runway preservation

H-005 continues under the already-authorized strict exact-segment pattern.

H-005 is not changed mid-runway by R1/R2 design work.

WP-S2c-26 through WP-S2c-34 remain sequential under existing authorization unless a stop trigger fires or Main explicitly revises sequencing.

No paired-source reuse or batched-cycle implementation may be applied to H-005 unless separately authorized.

## Validation discipline

Refreshed-main preflight remains mandatory.

Integrity views remain mandatory.

Registry validators remain mandatory where repo convention requires them.

Full pytest remains mandatory unless a future repo-approved validation-tier document changes that rule.

No validation reduction is authorized by this lock.

E8 and E9 remain not adopted:

- do not skip refreshed-main preflight;
- do not skip full pytest merely because a package is documentation-only.

## Reporting and handoff expectations

Default concise report-back shape:

```text
A. Scope
B. Changed files
C. Validation
D. Boundary check
E. Decision: merge-ready / follow-up / blocked
```

Longer report sections are still required for Tier 2/3/4, artifact packages, stop triggers, nontrivial validation failures, or when the active work package requires them.

Future chat handoffs must state current merged WP, active next WP, open PR conflicts, current protected boundaries, and whether a package touches `docs/project_status.md`.

Reviews must inspect actual changed files, not only PR summaries.

## What is not authorized

This operating-model lock does not authorize REP, OL, REC, EXP, LCH, schema, validator, query-layer, implementation, config, dependency, data, runtime, paper/live, OMS, risk, safe mode, Path B, H-006 implementation, paired-source reuse implementation, batched-cycle implementation, AUTO successor work, policy/scoring/ranking/recommendation, approval, promotion/demotion, readiness, lifecycle, or downstream authority.

## Stop conditions

Stop if the operating-model lock would require code, schema, validator, or query-layer changes.

Stop if the document cannot preserve H-005 runway unchanged.

Stop if the document implies R1/R2 are approved for implementation.

Stop if the document weakens refreshed-main, integrity-view, registry-validator, or full-pytest discipline.

Stop if another open PR touches `docs/project_status.md`.

Stop if changed files exceed the allowed set.

## Future review points

Mandatory Main re-engagement is required after WP-S2c-21c to approve or reject R1/R2.

H-005 checkpoint at WP-S2c-34 remains a Main re-engagement point.

H-006 runway sizing depends on the R1/R2 approval state.

Standing efficiency ideas should continue to be surfaced in report-backs, batched where practical.
