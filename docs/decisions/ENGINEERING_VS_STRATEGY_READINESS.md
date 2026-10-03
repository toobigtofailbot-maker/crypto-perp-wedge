# Engineering vs Strategy Readiness and Balanced Acceleration

## V2 controlling pointer

`D2-020` and
`docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`
now control bounded-autonomous research authorization and V2 sequencing. This
document's permanent principle is preserved: infrastructure buildability is
not candidate-gated; economic activation is. V2-00 activates no autonomy, and
all research autonomy remains default-off until Stage 5B is implemented,
validated, explicitly activated, and a valid Karl-approved envelope exists.
Candidate promotion, protected execution, paper/live, risk, and capital remain
human-gated.

## Decision status and authority

- Status: **LOCKED / APPROVED**.
- Accepted by: Karl/Main.
- Effective: prospectively after
  `WP-PLANNING-ENGINEERING-STRATEGY-READINESS-LOCK-01` merges.
- Authority: current merged repo truth and a later explicit Karl/Main decision
  may supersede this lock. Chat summaries, planning shorthand, and historical
  package language cannot silently override it.

This is an architecture and operating-model decision. It creates no dispatch,
execution, result, promotion, runtime, paper/live, OMS, reconciliation, risk, or
capital authority.

## Permanent engineering-vs-strategy distinction

> Absence of a profitable candidate blocks only real-capital authorization and deployment. It does not block continued construction or engineering validation of the research lab, autonomous factory, paper/shadow and monitoring layers, or the live-capable stack in disabled/non-capital mode. A designated non-winning dummy hypothesis is authorized for those engineering purposes and remains structurally GO-forbidden.

**Engineering readiness** means that infrastructure behaves correctly,
reproducibly, observably, and safely in its authorized non-capital modes.

**Strategy readiness** means that a candidate has produced the genuine
performance evidence required by its promotion gates.

Engineering readiness may progress without strategy readiness. Strategy
readiness remains mandatory before real-capital authorization or deployment.
Engineering completion never authorizes live trading, capital allocation, or a
promotion that requires genuine strategy-performance evidence.

## Designated dummy-hypothesis rule

H-004-R2 is the designated engineering dummy. It is explicitly non-winning,
non-production, structurally GO-forbidden, and non-promotable.

The dummy may not justify expected profitability, capital allocation, risk
expansion, live promotion, or performance claims. It may be used, under
separately authorized packages and the applicable protected gates, to exercise:

- idea intake, orchestration, research scheduling, and variant mechanics;
- backtests, walk-forward/OOS, robustness, and Monte Carlo machinery;
- ranking, rejection, retention, and recommendation plumbing without treating
  their outputs as genuine performance evidence;
- paper/shadow plumbing, monitoring, dashboards, and reports;
- execution, OMS, reconciliation, and risk-control integration in simulation or
  disabled/non-capital modes; and
- deployment and rollback workflows up to, but not through, real-capital
  authorization.

Using H-004-R2 for engineering proof does not convert that proof into strategy
evidence and cannot make H-004-R2 eligible for GO or promotion.

## Performance-dependent boundary

Genuine strategy-performance evidence is required for real-capital
authorization/deployment and for every promotion gate whose semantics
explicitly require genuine performance evidence. Engineering readiness is not a
substitute for those gates. Protected runtime, capital, paper/live, OMS,
reconciliation, risk, safe-mode, broker/exchange, order, position, and balance
boundaries remain subject to their actual separately authorized gates.

## Balanced Acceleration operating model

Balanced Acceleration applies prospectively:

1. Each work package uses risk-tiered, affected-scope validation. Full
   validation runs at defined milestone/release boundaries and wherever the
   package risk tier or a protected/canonical gate requires it.
2. Conditional runways may cover non-protected, non-canonical work inside a
   pre-approved scope.
3. Work packages should be larger when they remain coherent, reducing
   unnecessary Main/Side/Codex report-back crossings.
4. Exact-head Main/Karl review remains mandatory for protected/canonical
   crossings; it is not mechanically required for every low-risk non-boundary
   package.
5. Automated evidence generation and concise report-backs are encouraged when
   the underlying evidence remains inspectable.
6. Capital safety, protected runtime boundaries, OMS/reconciliation/risk
   controls, canonical integrity, and explicit human approval before
   live-impacting actions are non-negotiable.
7. Package-specific stop conditions and stronger existing protected gates
   always win.

This model does not retroactively change completed or merged history. It does
not let any package exceed its scope, ignore a failed acceptance criterion, or
bypass a human/protected/canonical gate.

## Transition and current sequence

**Current-sequence supersession (2026-09-23):** the numbered sequence below is
preserved as the historical sequence at this decision's lock. The current
migration sequence is controlled by
`docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md` and
begins with CPW-MIG-01 only. BROKER-4/H3-1 continuation and further generic
dispatch/control-plane expansion are not the current roadmap. The permanent
engineering-vs-strategy distinction in this document remains controlling:
infrastructure buildability is not candidate-gated; economic activation is.

1. PR #685 / the post-crossing regression package is merged. Its exact
   pre-dispatch boundary remains intact.
2. This repo-lock package makes the readiness and acceleration decisions durable.
3. `WP-TOOLING-DISPATCH-SCOPE-VALIDATION-01` is the next prospective tooling
   package and requires separate execution and review.
4. The dispatch-record/KDAUTH-consumption crossing remains separately
   Karl-gated after the tooling package merges. This decision does not authorize
   it.
5. Stage B plus execution assembly is planned as one coherent future Balanced
   package, with the Stage-B gate retained.
6. `RP-0007` creation remains a future canonical crossing with exact-head review.
7. Evaluation plus advisory work is planned as one coherent future
   non-protected package with milestone validation.
8. M2/M3/M4 factory, paper/shadow, monitoring, dashboards, and
   live-capable-disabled engineering may be built using the designated dummy,
   subject to their real protected gates. They are not blocked solely because
   the dummy is non-winning.

This sequence is planning truth, not downstream execution authority.

## Historical exception: PR #685

> PR #685 acceptance exception (exact-head, package-specific). For PR #685 at head `ff4b3901a4f1ead2fb5f4bce77ae46187e236f97` only: the full-release orchestration's nonzero exit is caused solely by `diff_scope_summary.py` lacking a `dispatch-authorization-crossing` authorized scope and lacking a base-to-head diff mode — a tooling-capability gap, not a test, semantic, or integrity failure. The acceptance property the allowlist check exists to guarantee — that exactly the five authorized files changed, with the full suite passing and integrity intact — is independently established at this exact head by direct five-file scope proof, cached diff check, clean worktree, 48/48 shards (160/160 files) passing, 240 protected-contract tests passing, 25/25 registry validators, clean integrity views (excepting the previously locked STRAT-SPEC-0007 legacy row), 8/8 standard verifier, and immutable-identity reproof of all five durable hashes. On that basis the machine-recognized package-allowlist portion of the acceptance criterion is waived for this PR/head only. This exception is not a general bypass: it does not waive full-suite success, integrity-view cleanliness, exact-file-scope proof, or exact-head review for any future canonical crossing. Future dispatch/KDAUTH crossings require the scope-validation capability to exist unless separately and explicitly excepted.

`WP-TOOLING-DISPATCH-SCOPE-VALIDATION-01` is the prospective package that
closes this capability gap. The exception does not authorize tooling changes in
PR #685 or in this decision package.
