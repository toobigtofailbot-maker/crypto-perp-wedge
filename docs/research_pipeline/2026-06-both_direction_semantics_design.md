# Both-Direction Strategy Spec Semantics Design

## Scope And Non-Authority

WP-COMP-BOTHDIR-01a is a docs-only design package.

This document evaluates candidate semantics for closed `direction: "both"` Strategy Spec entries and recommends one candidate for Main 5 review. It implements nothing and does not lock implementation authority by itself.

This document creates no schema, validator, compiler, test, Strategy Spec, variant, sweep, result population, indicator catalog, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path authority. Later packages must stay inside their own explicit scope and current merged repo truth.

## Repo-Truth Basis

Current merged repo truth wins over older summaries, stale handoffs, and prior planning language.

Files inspected for this design:

- `AGENTS.md`
- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md`
- `docs/ai/codex/WP_EXECUTION_REPORT.md`
- `docs/status_entries/README.md`
- `docs/research_pipeline/README.md`
- `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`
- `docs/research_pipeline/2026-06-compiler_indicator_first_block_options.md`
- `docs/research_pipeline/2026-06-plus_parameter_composition_design.md`
- `docs/status_entries/WP-COMP-XOVER-01.md`
- `docs/status_entries/WP-COMP-PLUSCOMP-01c.md`
- `research/schemas/strategy_spec.schema.json`
- `tools/registry/validate_strategy_specs.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_validate_strategy_specs.py`
- `tests/test_spec_signal_compiler.py`

Current expressiveness facts:

- `crosses_above` and `crosses_below` are present in the Strategy Spec operator enum and implemented by the compiler with immediately prior/current bar semantics.
- `scale_by_one_minus_parameter` remains preserved as the closed lower-side composed operand form.
- `scale_by_one_plus_parameter` is present in schema and validator posture and implemented by the compiler as the closed upper-side sibling.
- `entry_logic.direction` currently permits `long`, `short`, and `both`.
- `instruments.directions_allowed` currently permits only `long` and `short` entries in that array surface.
- The Strategy Spec schema currently has one `entry_logic.groups` array. It has no side label on entry groups.
- The current validator walks `entry_logic`, `exit_logic`, and `filters` groups for closed operators, depth, forbidden keys, composed operands, parameter-bound lookbacks, non-authority flags, and host data refs. It does not currently assign side semantics to entry groups.
- The current compiler accepts `long` and `short` direction strings but raises `UnsupportedSpecSignalCompilerFeature` for `direction: "both"`.
- The current compiler emits one position-intent signal stream where `1.0` means long, `-1.0` means short, and `0.0` means flat.
- The current compiler evaluates entries only while flat. Existing single-direction exits are not side-labeled because a single-direction spec has only one possible held side.
- `max_condition_group_depth` is fixed at exactly `3`.
- Current closed grammar forbids executable keys such as expression/code-style payloads and supports only closed operand and operator forms.

Repo truth therefore supports designing `direction: "both"` now, but not implementing it inside this package.

## Problem Statement

`direction: "both"` cannot be implemented safely by simply changing the existing compiler rejection.

Long and short entries need an unambiguous representation. In current single-direction specs, every entry group inherits its side from `entry_logic.direction`. With `direction: "both"`, that inheritance disappears unless the grammar says which entry groups belong to long and which belong to short.

Simultaneous long/short fire also needs a deterministic conflict rule. Without a closed rule, identical input data could be interpreted as long-first, short-first, flip, flat, or undefined by different implementers.

Exits need side association. A long exit should close a long state, and a short exit should close a short state. A condition intended to exit a long should not accidentally exit a short unless the grammar explicitly defines a shared exit concept.

The design must preserve no-lookahead behavior, closed grammar, and `max_condition_group_depth <= 3`. It must not introduce arbitrary expressions, new operators, a new data stream, hidden runtime behavior, or protected execution semantics.

## Options Matrix

### Option 1: Single Group Mirrored By Compiler

Summary:

Use the current `entry_logic.groups` array as a single canonical entry condition set. For `direction: "both"`, the compiler would derive a long interpretation and a short interpretation from the same groups, likely by reversing comparison operators or swapping upper/lower operands.

Repo compatibility:

- Superficially compatible with the current one-array `entry_logic.groups` shape.
- Not actually closed by current repo truth because the mirroring transform is not represented in the Strategy Spec.

Schema implication:

- Could avoid a schema change for entry representation.
- Would need hidden compiler rules for which operators and operands can be mirrored.
- Would likely need schema restrictions to reject non-mirrorable groups, otherwise the compiler would carry semantic burden not visible in the artifact.

Validator implication:

- The validator would need to detect whether every condition is mirrorable under the hidden transform.
- That becomes semantic validation, not just closed grammar validation.

Compiler implication:

- The compiler would need a transformation layer that rewrites long-side conditions into short-side conditions or vice versa.
- Crossover operators, composed operands, equality, inequality, blocking groups, filters, and indicator operands would all need explicit mirror rules.

Determinism/no-lookahead risk:

- Determinism can be implemented, but audit risk is high because the artifact does not show both branches.
- No-lookahead can be preserved if mirroring uses only current closed operands, but hidden rewrites increase test surface.

Auditability:

- Weak. Reviewers would need to infer short-side logic from compiler rules rather than reading it directly.

Effect on depth <= 3 / closed grammar:

- Condition group depth can remain unchanged.
- Closed grammar is weakened in practice because the compiler creates implicit semantics not visible in the JSON grammar.

Failure modes:

- Non-symmetric conditions can be mirrored incorrectly.
- Human reviewers can approve a spec without noticing the derived short side.
- Later additions to operators or operands can accidentally change mirror behavior.

Reason to reject:

- It is the smallest apparent schema change, but the largest hidden-semantics change. That conflicts with the repo's auditability and repo-truth posture.

### Option 2: Separate Explicit Side-Labeled Long/Short Groups

Summary:

For `direction: "both"`, represent long and short entry logic in separate closed side-labeled blocks. A later schema package would define a closed form such as:

```text
entry_logic.direction: both
entry_logic.side_entries.long.groups: [...]
entry_logic.side_entries.short.groups: [...]
```

The exact key names belong to the later schema package, but the semantic requirement is that long and short entry groups are explicit siblings, not compiler-derived mirrors.

Repo compatibility:

- Compatible with the current semantic direction because `entry_logic.direction` already admits `both`.
- Requires a later schema/validator package because the current schema does not have `side_entries` or an equivalent side-labeled entry surface.
- Compatible with current compiler posture because it already fail-closes `both` until semantics are locked.

Schema implication:

- Add a closed side-entry representation for `direction: "both"`.
- Require exactly one long entry block and exactly one short entry block for `direction: "both"`.
- Preserve existing single-direction `entry_logic.groups` behavior for `long` and `short`.
- Keep condition groups themselves under the existing depth-3 grammar.
- Forbid side labels outside the closed long/short set.

Validator implication:

- Enforce that `direction: "both"` uses the side-labeled representation and does not fall back to ambiguous unqualified entry groups.
- Validate both side blocks with the existing closed operator, operand, condition role, composed operand, lookback, and depth rules.
- Enforce that each side has at least one entry group unless Main 5 explicitly accepts a degenerate one-sided form.
- Enforce that side-labeled exits, if added in the same later schema lane, are closed to long and short.

Compiler implication:

- Evaluate long and short entry blocks independently when flat.
- Produce the same single position-intent stream domain: long `1.0`, short `-1.0`, flat `0.0`.
- Apply a deterministic simultaneous-fire rule.
- Apply side-specific exits only to the currently held side.

Determinism/no-lookahead risk:

- Low. Both branches are explicit and can be evaluated using the same existing condition evaluation mechanics.
- No future-bar reads are needed.

Auditability:

- Strong. Reviewers can inspect long and short entries directly and compare symmetry or intentional asymmetry.

Effect on depth <= 3 / closed grammar:

- Condition group depth remains unchanged because each side block reuses the existing condition-group grammar.
- Grammar remains closed because side keys and group arrays are explicit finite structures.
- No expression language is needed.

Failure modes:

- Later schema design could choose awkward key names or allow both old unqualified groups and new side groups at the same time.
- If side-specific exits are not specified alongside entries, exit semantics remain incomplete.
- Specs could be verbose, but the verbosity is useful audit evidence.

Reason to accept:

- This is the clearest design under current repo-truth constraints. It preserves single-stream mutual exclusivity while making both sides reviewable and testable.

### Option 3: Side-Tagged Groups Within Current Structure

Summary:

Keep one `entry_logic.groups` array, but add a required side tag to each group when `direction: "both"`, for example `side: "long"` or `side: "short"`.

Repo compatibility:

- Conceptually close to the current array structure.
- Requires a later schema package because current condition groups have closed properties and no side tag.

Schema implication:

- Add a side property to condition groups, conditionally required for `direction: "both"`.
- Decide whether side tags can appear in nested subgroups.
- Decide how side tags interact with filters and blocking groups.

Validator implication:

- Enforce side tags on all relevant groups for `direction: "both"`.
- Reject mixed or missing side tags.
- Validate whether a parent side flows to subgroups or every subgroup must repeat the side.

Compiler implication:

- Partition one array into long and short groups before evaluation.
- Resolve ambiguity for blocking/filter groups: side-specific, shared, or both.

Determinism/no-lookahead risk:

- Determinism can be preserved.
- Risk is moderate because side inheritance through nested groups can become subtle.

Auditability:

- Better than mirroring, weaker than separate side blocks. Reviewers must scan one mixed array and nested group tree to understand each side.

Effect on depth <= 3 / closed grammar:

- Depth can remain at 3 if side tags do not add condition-group nesting.
- Closed grammar is possible, but conditional side-tag rules add complexity.

Failure modes:

- A missing side tag can make a group ambiguous.
- Shared filters and side-specific filters can be confused.
- Nested subgroup side inheritance can create review drift.

Reason to reject:

- It is workable but less clean than separate side blocks. The current repo favors auditable artifacts over compactness, and a mixed array is easier to misread.

## Recommended Candidate Semantics

Recommend Option 2 for Main 5 lock: explicit side-labeled long and short entry groups for `direction: "both"`, with no compiler mirroring.

Candidate semantics:

- `direction: "both"` means the spec may enter long or short, but may not represent simultaneous long and short position intent.
- Long entry logic and short entry logic are represented as explicit, closed, side-labeled sibling blocks.
- Each side's groups use the existing closed condition-group grammar with depth no greater than 3.
- Long and short entries are evaluated independently only when the compiled state is flat.
- The compiled output remains one deterministic position-intent stream in the existing domain: `1.0`, `-1.0`, `0.0`.
- A long entry sets long state only if long fires and short does not fire on that bar.
- A short entry sets short state only if short fires and long does not fire on that bar.
- If both long and short entries fire on the same bar while flat, the compiler emits flat and records no entry for that bar.
- When already in a position, opposite-side entry conditions do not flip or exit the current side.
- Side-specific exits close only the currently held matching side.

This option is more auditable than compiler mirroring because the Strategy Spec directly shows both sides. A reviewer can see whether the short side is the intended symmetric upper-band condition, a deliberately asymmetric rule, or absent/invalid. That is safer than requiring reviewers to reconstruct hidden compiler transformations.

## Simultaneous-Fire Conflict Rule

Recommended rule: no entry on simultaneous fire.

When flat on a bar:

```text
long_entry = long side entry groups evaluate true
short_entry = short side entry groups evaluate true

if long_entry and not short_entry: signal = 1.0
if short_entry and not long_entry: signal = -1.0
if long_entry and short_entry: signal = 0.0
if neither: signal = 0.0
```

This rejects priority ordering. There is no long-first or short-first tie-break. The result is deterministic, no-lookahead-safe, and easy to audit. It also treats conflict as information loss: if both sides claim entry on the same bar, the closed compiler should not invent a directional preference.

This rule is preferable to alternating priority, last-side priority, volatility priority, random tie-breaks, or expression-based tie-breaks because those alternatives either create hidden policy, need additional state, or widen the grammar.

## Position Mutual Exclusivity

The compiled signal must not represent simultaneous long and short position intent.

Current repo truth has a single compiled signal stream with values `1.0`, `-1.0`, and `0.0`. Under this design, `direction: "both"` remains single-stream and mutually exclusive:

- `1.0` means long position intent.
- `-1.0` means short position intent.
- `0.0` means flat intent.

There is no hedge-mode representation, no two-column long/short output, no simultaneous side inventory, and no runtime/paper/live position model change. If a later requirement needs simultaneous long and short inventory, that exceeds the current closed grammar and must stop for Main/Karl rather than drift through this lane.

## Exit Interaction

For `direction: "both"`, exits should be side-specific at the design level.

Recommended exit posture:

- Long exits are evaluated only while long state is held.
- Short exits are evaluated only while short state is held.
- A long exit never closes a short state unless a later closed grammar explicitly defines a shared exit and Main 5 approves that form.
- A short exit never closes a long state unless a later closed grammar explicitly defines a shared exit and Main 5 approves that form.
- Opposite-side entry while already in a position is ignored for position-state purposes.
- Same-bar exit and opposite-side entry should not create an implicit reversal. If a side-specific exit fires, the bar should resolve to flat and a new entry should wait for a later bar. This keeps reversal semantics explicit and avoids hidden flip behavior.
- `max_holding_period`, if preserved for both-direction specs, should apply to the currently held side's holding duration and should flatten only that state.

A later schema package should decide the exact closed representation for side-specific exits. The cleanest match to Option 2 is an explicit side-labeled exit surface that parallels side-labeled entries, while preserving existing single-direction exit behavior for `direction: "long"` and `direction: "short"`.

This is design-level only. It does not change runner, backtester, runtime, paper/live, OMS, risk, broker, exchange, or protected execution semantics.

## Determinism, No-Lookahead, And Closed Grammar

Any later implementation package should preserve these requirements:

- No future-bar reads.
- Same input Strategy Spec, variant parameters, indicator catalog, and OHLCV frame produce the same output signal.
- No hidden mirroring unless Main 5 explicitly rejects this recommendation and locks a mirrored option.
- No expression language.
- No `eval`, `exec`, lambda, code strings, or formula strings.
- No new operators for this both-direction package.
- No new data stream.
- No condition-group depth greater than 3.
- No nested composed operand expansion.
- No side keys outside the closed long/short domain.
- No multi-output hedge-mode signal.
- No runtime, paper/live, OMS, risk, broker, exchange, or protected-path contact.

## Downstream Implementation Implications

If Main 5 locks this recommendation, the likely later split is:

```text
WP-COMP-BOTHDIR-01b: schema + validator for the locked representation
WP-COMP-BOTHDIR-01c: compiler implementation + tests
```

`WP-COMP-BOTHDIR-01b` would define and validate the closed side-labeled grammar. It would not implement compiler behavior unless separately scoped.

`WP-COMP-BOTHDIR-01c` would compile the locked grammar into the existing single position-intent stream, including simultaneous-fire, mutual-exclusion, side-specific exit, no-lookahead, and determinism tests.

Neither package is authorized by this document. Main 5 must review and lock semantics after this design before any schema, validator, compiler, or test package begins.

## Stop And Escalation Rule

If no coherent both-direction design fits within closed grammar, condition-group depth no greater than 3, no expression language, no new operators, and single-stream mutual exclusivity, the lane must stop for Main/Karl.

Do not implement around ambiguity. Do not widen protected runtime, paper/live, OMS, risk, broker, exchange, data acquisition, dashboard, Strategy Spec artifact, result-population, schema, validator, compiler, or test authority without a later explicit package.
