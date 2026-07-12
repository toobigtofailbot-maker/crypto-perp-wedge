# Repo-truth discovery — WP-CANON-FIRST-GATE-C-CROSSING-GATED-02C Phase A

## Branch and base facts

- Branch: `codex/wp-canon-first-gate-c-crossing-gated-02c`.
- Starting `origin/main` and HEAD: `0a4f1a22fb9f2a9c1fdf66aad4024e631672358f`.
- The worktree was created as a clean isolated sibling worktree after fetching origin.
- The base is merge commit PR #652. The required writer, eligibility validator, and inbox review service exist.

## Canonical corpus facts

- Six Strategy Specs exist: `STRAT-SPEC-0001` through `STRAT-SPEC-0006`.
- Six Variant Manifests exist: `VM-0001` through `VM-0006`.
- Six Sweep Plans exist: `SWEEP-PLAN-0001` through `SWEEP-PLAN-0006`.
- These existing artifacts predate the append-only Gate-C writer flow and cannot be reused retroactively: `spec_writer.py` requires a new target and rejects an existing Strategy Spec ID/path.
- `research/canonical_crossing_audit/` is absent; therefore `strategy_spec_writes.jsonl` is also absent and no writer-recorded real Gate-C crossing exists.
- Existing canonical IDs are forbidden for this first crossing. Any later approved crossing must allocate a new unused ID (currently the next numerical candidate would be `STRAT-SPEC-0007`, subject to re-verification at freeze time).

## Candidate, registry, and result facts

- The authoritative draft directory contains exactly one committed packet: `AIDRAFT-8DEEE634E62CD560`.
- `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/sample_draft_packet.json` is additional sample evidence, not a second authoritative packet in the required `drafts/<draft_id>.draft_packet.json` location.
- The candidate registry contains concluded NO-GO families H-001 through H-010 and H-012, plus reserved draft H-011. These registry entries are not Agent Inbox draft packets and cannot substitute for one.
- Eight Result Populations exist (`RP-2134`, `RP-2592`, `RP-3731`, `RP-4492`, `RP-6236`, `RP-6688`, `RP-7134`, `RP-7520`). They are prior research evidence, not valid Gate-C source drafts.

## Sole authoritative draft facts

- Draft ID/title: `AIDRAFT-8DEEE634E62CD560` / “EMA momentum continuation”.
- Submitter: `codex-sample`; client ID: `sample-draft-001`.
- Provenance is explicitly `fake-rule-v1`, `fake_offline`, `deterministic_fake`, and `fake_offline_packet_only`.
- The packet's `fabricated` boolean is false, but that does not override its explicit fake/sample provenance.
- It is scratch-only and non-authoritative across canonical, candidate, execution, queue, runtime, and paper/live boundaries.
- It has no review-event trail: zero events and no latest review state.
- Its committed eligibility report is advisory-only with status `needs_clarification`, no rejection reasons, and no Gate-C authority.
- It carries the blocker: “no validated draft adapter exists for this exact primitive family”.
- Its only open packet question asks human review to decide whether to revise, discard, or later promote it.

## Duplicate and near-duplicate assessment

- The committed eligibility validator found zero normalized duplicate/near-duplicate matches and zero concluded-family freshness matches.
- That automated result does not establish material differentiation. The sample's exact EMA computation, trigger, direction, exits, and parameter meanings are absent or internally unclear, while canonical/research history already includes SMA crossover momentum (`STRAT-SPEC-0005` and `0006`), hourly MACD momentum (H-005), premium-confirmed momentum (H-008), and 15m trend following (H-012).
- Consequently there is no proven exact duplicate, but near-duplicate differentiation remains a material human decision after exact semantics are supplied.

## Blockers and unresolved human decisions

- No genuine intended-research Agent Inbox draft exists.
- Karl must select/supply a genuine idea or explicitly accept the fake/sample packet as a canonical canary.
- For any selected idea, every semantic item in `karl_candidate_and_clarification_decision.md` must be resolved without Codex inventing economic logic.
- The selected idea must resolve any adapter/data/implementation blocker and explain differentiation from existing canonical and concluded families.

## Decision

Fact: no valid first-crossing candidate currently exists.

Inference: a legitimate Gate-C crossing cannot safely enter Phase B from current repo truth.

Decision: stop after the Phase-A packet. Do not append review state, rerun/overwrite eligibility, freeze a Strategy Spec, prepare a Gate-C approval, or write canonical/audit artifacts.

Future option: Karl may supply a new genuine idea through the response template, or explicitly designate the existing sample as a canonical canary with full provenance acknowledgement and complete clarifications.

