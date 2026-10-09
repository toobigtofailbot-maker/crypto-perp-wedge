# Validation Policy

This document records the repo-local validation tiers for coding-agent work. It
is workflow guidance only; current merged repo truth and the active work package
still win. Main, Karl, or an active package may always require stronger
validation. A lower tier never weakens an explicit protected, canonical,
milestone, release, or exact-head requirement.

## T0-T4 validation tiers by blast radius

Classify the changed semantics and their blast radius, not merely the number of
files. If a package crosses tiers, use the highest applicable tier.

| Tier | Typical changed surface | Required validation posture |
| --- | --- | --- |
| T0 | Documentation, status, or comments only | Scope, changed-file, docs render/lint/link checks where supported, and `git diff --check`; no pytest by default. |
| T1 | Tests only; read-only query additions that do not change production query semantics; exact-artifact persistence; non-canonical research automation | Mandatory focused and adjacent blast-radius tests plus relevant validators and integrity views; no full suite by default. |
| T2 | Schema, validator, contract, query-SQL, or broadly used production-code changes | Focused and adjacent tests, every affected contract suite, and relevant validators/integrity views; full suite when the dependency graph or blast radius is broad enough to require it. |
| T3 | Canonical crossing logic, execution writers, dispatch authorization, or other protected writers | Full rigor, full-release/full-suite evidence, and exact-head review. |
| T4 | Runtime, OMS, reconciliation, risk, capital, or paper/live paths | Maximum rigor, Karl gate, and preservation of every protected control. |

T0 applies only when the committed diff is limited to documentation, status, or
comments and changes no schema, validator, query-layer behavior, tooling code,
test, research artifact, result population, data, runner/backtester behavior,
runtime, paper/live trading path, OMS, reconciliation, risk, broker/exchange,
credential, or capital control. Report skipped full pytest as:

```text
full pytest: NOT RUN - T0 docs/process policy; not used as merge evidence
```

Do not report a timeout as a policy skip. Use:

```text
full pytest: TIMED OUT after <seconds>; not a pass
```

## Blast-radius test selection

Every work package must name the smallest sufficient focused, adjacent,
affected-contract, validator/integrity checks and explain whether broad/full
validation is required. Select checks by distinct actual behaviors, direct
consumers, and credible failure modes, not test counts. Cover each material
contract and failure class; do not multiply equivalent negative matrices or
repeat the same assertion without additional risk coverage. Mark inapplicable
checks with a reason; this cannot waive a tier floor or active-WP stronger gate.

The selection must follow affected semantics and direct consumers, including
append-only growth. Tests over append-only registries, ledgers, streams, or
artifact corpora should assert dynamic membership, uniqueness, denominators,
ordering, and preserved historical identities where those are the contract.
They should not require a valid future append to extend a brittle snapshot of
the entire corpus unless the snapshot itself is the authorized contract.

Any future dependency-map or blast-radius selector is separate T1 tooling work.
This policy does not implement one.

## Readiness before broad validation

Use this order:

1. Confirm the exact branch, base, and worktree.
2. Confirm the named validation profile and environment prerequisites.
3. Record known baseline disclosures.
4. Prove the changed-file and scope allowlist.
5. Run focused tests.
6. Run adjacent tests.
7. Run relevant validators and integrity views.
8. Run a broad/full suite only when the tier or active package requires it.
9. Complete the final base/mergeability gate and exact-head evidence.

Never start a long full suite merely to discover a missing known gitignored
dataset or an already-recorded baseline disclosure. A focused failure returns
to focused correction. After a small correction, rerun broad validation only
when that correction invalidates the prior broad evidence.

## Reusable validation evidence

A reusable broad-validation record must identify:

- exact base and head;
- changed surface covered;
- test and validator profile;
- environment and validation profile;
- known disclosures;
- result and duration.

A subsequent package may cite that evidence only after proving that its changed
files and semantics are outside the reused evidence's invalidated blast radius,
and after running the focused and adjacent delta required for its own change.
Full-suite evidence is therefore not automatically invalidated by every later
file-disjoint, low-blast-radius package. Reuse is evidence, not authority, and
does not waive a tier, milestone, release, protected, or package-specific gate.

Non-normative example: broad query-semantic evidence from PR #695 supported the
focused exact-artifact-persistence delta in PR #694 because the later package
proved its bounded delta; that sequence does not create a general exemption.

## Full-release evidence

Full pytest and the full-release profile are integration and protected-boundary
tools, not the routine inner loop. Require them for T3/protected gates, explicit
WP/release/milestone requirements, or genuinely broad integration risk supported
by the affected dependency graph. T4 retains maximum rigor and all applicable
protected/full-release floors. T0-T2 do not automatically require full release.
Prefer one broad run on the stable candidate; repeat only when changed semantics
invalidate the covered evidence, while preserving stronger exact-head gates.

When a package requires
full-suite evidence, `tools/dev/verify.py --full-pytest-sharded --pytest-shards
N` may be used only when all required shards pass. A failed or timed-out shard
fails the overall verification.

The repo-owned `full-release-balanced-v1` profile is the bounded default for
release-gated full-suite evidence when a package requires sharding:

```powershell
python tools/dev/verify.py --validation-preset full-release `
  --full-pytest-sharded `
  --pytest-shard-profile full-release-balanced-v1 `
  --json
```

The profile discovers the sorted tracked `tests/test*.py` file set from Git,
places `tests/test_research_query.py` alone in a dedicated shard, executes that
isolated shard exclusively, then distributes all remaining files
deterministically across the other shards with up to four parallel workers.
Before pytest, the verifier fails closed unless the assignment proves exact,
unique coverage of every discovered file. Its JSON and Markdown summaries
include the profile version, assignment-manifest SHA-256, coverage counts,
per-shard assignments and completion/timing state, and the slowest shard. The
profile preserves the 1,800-second per-shard limit; a failed, timed-out,
unselected, or incomplete shard is not complete full-suite evidence. An
exclusive-shard failure stops before the parallel phase so the verifier emits
decisive failure evidence without starting unrelated tests.

Raw `--pytest-shards N` index-modulo mode remains available. A named profile
cannot be combined with `--pytest-shards`; ambiguous combinations are rejected.
`--pytest-shard-index` remains available for deterministic diagnostics, but a
selected-shard run is not complete full-suite evidence.

## Local-first validation and future hosted checks

Run the required local checks first. Before selecting minimal hosted exact-head
validation in a later authorized package, inspect the actual ruleset, branch
protection, and trusted classification. This guidance designs or implements no
CI and cannot waive required hosted or protected checks.

## Protected-core invariants

Acceleration is faster where protected-level cost is unnecessary and unchanged
where protected controls require it. No tier, profile, or reused evidence may
weaken exact-content canonical crossings, irreversible-execution authorization,
full-denominator accounting, append-only integrity, protected writers, human
promotion gates, runtime, paper/live, OMS, reconciliation, hard risk, capital,
or exact-head review where T3/T4 requires it.

The tier model is not an exemption from semantic review, direct changed-file
inspection, forbidden-scope checks, protected-boundary review, validators named
by the package, or any active work-package requirement.
