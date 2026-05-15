# Automation Build Operating Model (WP-12a)

## Package Metadata

- Package label: WP-12a / AUTO-00.
- Package title: Automation Build Operating Model.
- Package class: documentation-only operating-model package.
- Effective base: refreshed `main` after merged WP-11c.
- Created artifact: this operating-model document only.
- Modified status surface: `docs/project_status.md` only.

WP-12a creates no automation code, runner, scheduler, parameter sweep, Monte
Carlo engine, dashboard, agent, paper/live bridge, implementation artifact,
research evidence artifact, schema, validator, query-layer change, test change,
runtime behavior, config change, dependency change, data change, or
protected-path change.

## Purpose

WP-12a transitions the project from manual micro-WP governance into a tiered
automation-build operating model.

The model is intended to improve package flow for the automation-build phase
without weakening repo-truth discipline, validation discipline, changed-file
scope discipline, or protected-boundary discipline.

This document is an operating model, not an automation implementation. It
becomes guidance for future WP drafting, Codex execution, and Side review.

## Why The Workflow Changes Now

WP-11c locked the Stage 2 first sub-stage complete-as-executed through:

```text
WP-10q -> WP-10r -> WP-10s -> WP-10t -> WP-10w -> WP-10x -> WP-10y -> WP-11a
```

That lock records the selected exact segment:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

It records REC-5 crossing for that exact segment only through `REC-0022`,
`REC-0023`, and `REC-0024`, and records WP-11a as the first descriptive
consumer brief over that floor-crossed exact segment.

The prior micro-WP pattern was appropriate for proving evidence-pipeline
guardrails. The next project phase needs automation architecture and
implementation, which requires larger coherent tracks and controlled vertical
slices rather than repeated tiny permission packages.

Runtime, paper/live, OMS, risk, safe-mode, execution, deployment, config,
dependency, data, schema, validator, query-layer, test, and protected-path
boundaries remain strict.

## Operating Principles

- Repo truth wins over memory, summaries, and assumptions.
- Current merged `main` wins over stale local state.
- Every future WP starts from refreshed local `main`.
- Exact changed-file sets remain required.
- Protected paths remain protected unless explicitly authorized.
- Main 3.0 approves strategy tracks and boundary crossings.
- Side 3.0 may draft packages inside approved tracks.
- Codex executes only scoped packages.
- Larger packages are allowed only when risk is lower or the track envelope is
  already approved.
- Runtime, paper/live, OMS, risk, safe-mode, execution, and deployment remain
  Tier 4 and always require explicit Main 3.0 approval.
- Automation is built in vertical slices.
- Agents come after stable runners, result stores, and dashboard surfaces.

## Tiered Execution Model

### Tier 0 - Strategic Direction

Used for choosing major tracks, authorizing automation-build mode, authorizing
paper/live or runtime-adjacent work, changing protected boundaries, and choosing
whether to enter Stage 2 second-sub-stage, Path B, cohort, or additional floor
crossing.

Authority: Main 3.0 / user strategy authority required.

Output: direction decision docs or strategy capsules.

Validation: documentation validation if committed; no implementation.

### Tier 1 - Safe Documentation / Planning

Used for architecture notes, operating models, roadmaps, implementation plans,
stability locks, and non-authoritative design docs.

Authority: Side 3.0 may draft without new Main confirmation when inside an
approved track and not changing boundaries.

Validation: refreshed-main preflight, exact changed-file check, `git diff
--check`, standard validators/integrity views as repo convention, and
targeted/full pytest where current repo convention requires.

### Tier 2 - Research Artifacts / Briefs / Query Bundles

Used for REP / OL / REC artifacts, research briefs, package-local query
bundles, output JSON, and read-only consumers over committed artifacts.

Authority: Side 3.0 may draft if the artifact or brief sequence is already
authorized by a locked direction. Main 3.0 is required if creating a new
evidence direction, new candidate/cohort, Path B, or any new scope boundary.

Validation: artifact validators, all registry validators as applicable,
integrity views, targeted pytest, full pytest, semantic scope scans, and exact
changed-file checks.

### Tier 3 - Automation Infrastructure

Used for experiment runners, batch runners, parameter sweep systems, Monte
Carlo engines, result stores, schedulers/job queues, dashboard backend/data
surfaces, and agent orchestration scaffolds.

Authority: Main 3.0 must approve the automation track and envelope. After track
approval, Side 3.0 may draft vertical-slice WPs that stay inside the envelope.
Main 3.0 is required again for dependency additions, config changes,
runtime-adjacent behavior, protected paths, or expansion beyond the approved
envelope.

Validation: unit tests, integration dry runs, deterministic manifests/outputs
where applicable, failure-mode checks, full pytest, protected-path drift check,
and no runtime contact unless separately authorized.

### Tier 4 - Runtime / Paper / Live / OMS / Risk

Used for paper trading, live trading, exchange/broker integration, OMS,
position reconciliation, risk caps, safe mode, kill switch, deployment, and
operational monitoring for live/paper.

Authority: explicit Main 3.0 / user approval is required for every package or
tightly defined sub-track. Protected-path review is required.

Validation: full validation, safety tests, failure-mode tests, rollback or
safe-mode checks where applicable, and no shortcutting.

## Main 3.0 Authority Model

Main 3.0 decides:

- major tracks;
- boundary crossings;
- automation-build envelope;
- runtime, paper/live, OMS, risk, safe-mode, execution, and deployment
  transitions;
- protected-path changes;
- dependency or config additions;
- candidate, cohort, Path B, Stage 2 second-sub-stage, and additional
  floor-crossing changes;
- stop/hold decisions at major checkpoints.

Main 3.0 should not be required to confirm every small WP inside an already
approved track.

## Side 3.0 Authority Model

Side 3.0 may:

- draft Codex-ready WPs inside approved tracks;
- group low-risk documentation packages;
- draft Tier 1 docs and Tier 2 packages when the sequence is already
  authorized;
- draft Tier 3 vertical slices inside an approved automation envelope;
- review Codex outputs;
- decide merge-ready / follow-up / blocked based on scope, changed files,
  semantics, validation, and protected boundaries;
- escalate only when a true decision boundary appears.

Side 3.0 must not:

- invent strategic direction;
- override Main sequencing;
- authorize Tier 4 work;
- broaden the automation envelope;
- add dependencies, configs, runtime behavior, or protected-path changes unless
  explicitly authorized.

## Codex Execution Model

Codex must:

- always refresh local `main`;
- verify clean working tree;
- verify target branch absence;
- verify target docs/artifacts absence;
- use `gh` for repo/PR operations where scoped;
- create the branch only after preflight passes;
- follow exact changed-file scope;
- stop on dirty tree or failed fast-forward;
- never auto-reset, stash, discard, or overwrite local changes;
- run validation required by tier;
- return concise report-backs unless risk requires expanded detail.

## Package Sizing Rules

Package size follows risk, not arbitrary WP count.

- Documentation/planning packages may be larger if they remain
  documentation-only and boundary-preserving.
- Research artifacts should remain narrow unless the pattern is mature and the
  package scope explicitly groups them.
- Automation packages should be vertical slices, not isolated abstractions.
- Runtime and protected-path packages should remain very small and explicit.

Old mode: lay one brick, inspect, ask permission again.

New mode: approve the wall section, lay a controlled section, inspect the
section.

## Validation By Tier

- Tier 1 docs: refreshed-main preflight, exact diff, `git diff --check`,
  validators/integrity views, and targeted/full pytest where repo convention
  requires.
- Tier 2 artifacts/briefs: artifact validators, registry validators, integrity
  views, targeted pytest, full pytest, semantic scans, and exact changed-file
  checks.
- Tier 3 automation: unit tests, integration dry run, manifest/output
  verification, full pytest, protected-path drift check, and failure-mode
  checks.
- Tier 4 runtime: full validation, safety tests, failure-mode tests,
  rollback/safe-mode checks, protected-path review, and explicit Main 3.0
  approval.

## Report-Back Format By Tier

Default concise report-back:

```text
A. Scope
B. Changed files
C. Validation
D. Boundary check
E. Decision: merge / follow-up / blocked
```

Expanded report-backs remain appropriate for artifact packages, blocked
packages, Tier 3 automation, Tier 4 runtime, anything touching protected
boundaries, and user-requested detailed review.

## Standard Git/GH Preflight

Every future WP must start with:

```powershell
Set-Location "C:\GitHub\crypto-perp-wedge"
git fetch origin
git checkout main
git pull --ff-only origin main
git status --short
git branch --list <target-branch>
git ls-remote --heads origin <target-branch>
gh auth status
gh repo view toobigtofailbot-maker/crypto-perp-wedge
gh pr status --repo toobigtofailbot-maker/crypto-perp-wedge
git ls-remote origin HEAD
```

Branch creation occurs only after this passes.

If `git pull --ff-only` fails, stop. If the working tree is dirty, stop. If
the branch exists, stop unless explicitly authorized to reuse it. Do not reset,
stash, discard, or overwrite local changes automatically. `gh` auth failures
are operational/auth issues, not repo architecture facts.

## Protected Boundaries

Protected boundaries carry forward:

- no runtime, paper/live, OMS, risk, safe-mode, execution, or deployment work
  without explicit Tier 4 authorization;
- no policy, scoring, ranking, or recommendation authority without explicit
  strategy decision;
- no schema, validator, query-layer, or test change unless package tier/scope
  explicitly allows it;
- no committed artifact mutation unless a backward-compatible correction is
  explicitly scoped;
- no dependency, config, or data changes unless explicitly scoped;
- no protected-path changes in Tier 1, Tier 2, or Tier 3 unless specifically
  authorized.

## Automation-Track Roadmap

The following roadmap labels are non-authoritative planning handles:

- AUTO - Research automation / runner.
- PARAM - Parameter search / sweeps.
- MC - Monte Carlo / robustness testing.
- DASH - Dashboards / monitoring.
- AGENT - Agent orchestration.
- PAPER - paper-trading bridge.
- LIVE - live-trading bridge.

PAPER and LIVE remain Tier 4 and blocked until explicit authorization.

## First Automation MVP Sequence

Proposed first sequence, non-implementation and subject to package-level
validation:

```text
AUTO-01 - Research Automation Architecture Map
AUTO-02 - Experiment Runner Interface Design
AUTO-03 - Local Dry-Run Runner Vertical Slice
AUTO-04 - Batch Manifest Format
AUTO-05 - Parameter Sweep MVP
AUTO-06 - Result Store / Run Registry
AUTO-07 - First Dashboard Data Surface
```

After WP-12a merges, Side 3.0 may draft AUTO-01 as a Tier 1 documentation
package without another Main confirmation, provided AUTO-01 remains inside this
operating model and does not implement code.

WP-12a does not draft AUTO-01.

## Stop / Escalation Rules

Side 3.0 and Codex must stop and escalate to Main 3.0 when:

- a package crosses a tier boundary;
- a package touches Tier 4 scope;
- a package needs dependency, config, data, or protected-path changes;
- a package would change runtime, paper/live, OMS, risk, safe-mode, execution,
  or deployment behavior;
- a package would authorize policy, scoring, ranking, or recommendation;
- a package would create new candidate, cohort, Path B, Stage 2
  second-sub-stage, or additional floor-crossing direction;
- a package would broaden the automation envelope;
- validation fails;
- integrity views return rows;
- changed files exceed scope.

## Non-Claims

WP-12a creates no:

- automation implementation;
- runner;
- scheduler;
- parameter sweep;
- Monte Carlo engine;
- dashboard;
- agent;
- paper/live bridge;
- runtime behavior;
- config, dependency, or data change;
- schema, validator, query-layer, or test change;
- EXP, REP, OL, REC, LCH, or registry artifact;
- research evidence artifact;
- consumer brief;
- strategy recommendation;
- live/paper readiness;
- policy, scoring, ranking, or recommendation authority.
