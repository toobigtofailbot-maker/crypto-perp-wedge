# Strategy Research Lab Target Operating Model Design Opening

## 1. Scope

WP-S2c-146 / WP-12fs is a Tier 1 documentation-only design-opening package.

It opens the Strategy Research Lab target-operating-model design. It creates
only this document, updates `docs/research_pipeline/README.md` with one
additive index entry, and updates `docs/project_status.md`.

It creates no implementation, schema, artifact, query, runtime, strategy
authority, approval authority, promotion authority, readiness authority,
transition authority, or ranking authority.

## 2. Authorization basis

Main 4.0 authorized the Strategy Research Lab design tranche in external
package-routing output. WP-S2c-146 opens that tranche.

WP-S2c-147 is the next sequential lab package after WP-S2c-146. Later locking
moments remain external authorization context for sequencing, not repo-truth
facts until committed by later packages.

All packages before later locking points remain design-only unless separately
authorized. Permanent human gates and protected runtime boundaries remain
absolute.

## 3. Pivot context

Manual one-candidate-per-tranche testing has proven the locked research
discipline, but it exposes throughput as the current constraint.

Current repo truth records eleven concluded candidates as `NO-GO`: H-001
through H-010 plus H-012. H-012 confirmed that the locked artifact chain works
end-to-end through candidate registration context, EXP, REP, trial-log, OL,
REC, and DEC evidence.

WP-S2c-139 records a possible second manual Path B surface and then pauses
Track 3. WP-S2c-140 onward is deferred, not rescinded.

The next architectural direction is to design the lab that can generate and
evaluate many strategy variants under locked discipline.

## 4. Current architecture basis

The Strategy Research Lab must consume, not replace, the current research and
evidence architecture:

- candidate registry and candidate-registry schema;
- EXP / REP artifacts and the append-only trial log;
- OL / REC / DEC evidence and decision surfaces;
- D2-006 promotion gates;
- D2-007 shadow discipline;
- REC-5 exact-segment floor and no cross-segment inference below floor;
- Phase 9 / D2-011 pre-registration discipline;
- Scope 6 approval/shadow-evidence schemas and query views;
- read-only query layer and integrity views;
- parameter-sweep, batch-runner, local-run-registry, local-sweep-result, and
  AUTO bridge precedent docs;
- permanent human gates;
- protected runtime boundaries.

Those surfaces remain repo-truth inputs. The lab opening does not mutate them
and does not create parallel authority.

## 5. Target operating model thesis

The Strategy Research Lab is an automation layer above the locked research
architecture.

The lab should convert user, paper, and online strategy ideas into reviewed
concepts, reviewed specs, pre-registered variant populations, controlled
sweeps, robustness-filtered results, and advisory ranked outputs.

The lab should increase research throughput without creating promotion,
transition, paper, live, runtime, or human-gate authority. It should make it
easier to find robust strategy setups while reducing overfitting risk.

## 6. Lab operating envelope

At target-operating-model level, the lab may conceptually support:

- ingesting ideas into concept documents;
- converting approved concepts into structured strategy specs;
- generating bounded variant populations from specs;
- pre-registering variant populations before execution;
- running controlled sweeps through existing backtest and evaluation surfaces
  when later implementation authorizes it;
- filtering pathological variants;
- computing DSR-aware population-level metrics;
- producing advisory rankings for human review;
- preserving all artifact and provenance links.

Outside-envelope activities are:

- no automatic R2S, S2P, paper, or live promotion;
- no runtime or execution-core changes;
- no broker, exchange, or order API contact;
- no automatic human-gate satisfaction;
- no weakening D2-006, D2-007, REC-5, Phase 9, or Scope 6.

## 7. Human-gated authority model

The lab proposes. Karl approves.

Spec approval is human-gated. Variant population pre-registration approval is
human-gated at least in initial lab maturity.

Research-to-shadow, shadow-to-paper, paper/live movement, risk parameter
changes, kill decisions, and novel strategy-family introductions remain
human-gated.

Advisory ranking is not promotion authority.

## 8. Lab artifact-flow sketch

The conceptual lab flow is:

```text
Idea source
-> concept record
-> human-reviewed strategy spec
-> hash-pinned variant population
-> sweep execution
-> trial / EXP / REP outputs
-> OL / REC aggregation
-> advisory ranking brief
-> human review
-> possible later Scope 6 approval path
```

This is a conceptual flow only. This package creates no artifact schemas,
artifact instances, variant population files, sweep outputs, ranking artifacts,
or approval records.

## 9. Design questions for WP-S2c-147

WP-S2c-147 should answer the substantive operating-model questions:

- What exactly is the lab lifecycle from idea to advisory ranked output?
- What are the minimum human gates before sweep execution?
- How does the lab avoid overfit and multiple-testing drift?
- What surfaces should be concept, spec, variant, sweep, and ranking artifacts
  versus existing EXP, REP, OL, and REC artifacts?
- How much of the AUTO bridge can be reused as precedent without reactivating
  it?
- What is the initial maturity level for autonomous operation?
- What is the maximum safe autonomy before implementation locks?
- What are the stop conditions for moving from design to implementation?

## 10. Dependencies on later lab tranche packages

The authorized design tree is sequencing context only at this opening stage:

- WP-S2c-147: operating model substance.
- WP-S2c-148 through WP-S2c-151: Strategy DSL design, consolidation, and
  Karl-gated locking.
- WP-S2c-152 through WP-S2c-153: concept ingestion and spec authoring/approval
  discipline.
- WP-S2c-154 through WP-S2c-158: variant generation, sweep orchestration,
  storage design, consolidation, and Karl-gated storage locking.
- WP-S2c-159 through WP-S2c-160: anti-overfit/DSR population design and
  advisory ranking artifact design.
- WP-S2c-161 through WP-S2c-162: Scope 6 integration and lab agent roles.
- WP-S2c-163 through WP-S2c-164: lab design consolidation/roadmap and
  Karl-gated lab-design/implementation authorization.

This opening does not expand those items into implementation requirements.

## 11. Protected boundaries

This opening preserves:

- Phase 1 paper runtime;
- D-0001 hard risk caps;
- D2-008 overlay semantics;
- OMS, reconciliation, kill-switch, and safe-mode boundaries;
- `SignalProvider` Protocol;
- Tier 4 boundaries;
- `lib/`, `src/`, `configs/`, `.claude/`, `data/`, and other protected paths;
- AUTO bridge frozen status unless a later Karl decision reactivates it;
- A2C-003 and Path B C/F deferred/rejected states;
- permanent human gates.

## 12. What this opening does not decide

This opening decides no:

- Strategy DSL fields;
- concept schema;
- variant schema;
- storage option lock;
- ranking formula;
- DSR implementation detail;
- code path;
- implementation tranche;
- paper bridge;
- candidate registration;
- Track 3 reactivation.

## 13. WP-S2c-147 handoff

WP-S2c-147 should draft the substantive operating model.

It should convert this opening into a concrete target operating model with
lifecycle stages, actor responsibilities, artifact surfaces, authority
boundaries, and pre-implementation stop criteria.

WP-S2c-147 should remain Tier 1 documentation-only.

## 14. Validation posture

Validation profile: CS12 T1-doc-narrow.

Validation should confirm exact changed-file scope, integrity views and
validators per doc-narrow convention, and no implementation or authority
creation. Full pytest is not required unless repo-local convention or
validation issues require it.

## 15. Stop conditions

Stop if:

- any part of the opening requires implementation;
- any part creates or modifies schemas, artifacts, query views, tools, tests,
  or code;
- any part weakens pre-registration, REC-5, D2-006, D2-007, Scope 6, or human
  gates;
- any part implies ranking, promotion, readiness, or transition authority;
- any part attempts to reactivate AUTO bridge or Track 3 execution;
- any part touches runtime or protected paths;
- validation fails.

## 16. Non-authority boundary

This design opening creates no strategy authority, promotion authority,
approval authority, runtime authority, paper/live authority, route-selection
authority, ranking authority, scoring authority, recommendation authority, or
human-gate execution authority.

It is planning structure only.

## 17. Next-package posture

After merge, Side may draft WP-S2c-147 under Main lab-tranche authorization
after refreshed-main preflight and no stop trigger.

Do not draft WP-S2c-148, WP-S2c-152, WP-S2c-154, WP-S2c-159, WP-S2c-161, or
WP-S2c-162 before deciding sequencing unless Main's multi-track lab
authorization is intentionally used. The default sequential path is
WP-S2c-147.
