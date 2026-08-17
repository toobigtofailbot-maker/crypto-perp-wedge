# WP-HERMES-H2-PROPOSE-01

## Package State

- Branch: `codex/wp-hermes-h2-propose-01`
- Refreshed base: `6115753fd623bcec668ec9a3dd814c52182f088a` (merged PR #706)
- Live-acceptance implementation head: `02d8c8133d3892bc5e649ed24b427a2c18f00e1d`
- Package class: T2 typed, evidence-anchored, non-authoritative proposal surface
- Result: H2 PROPOSE complete; H2.5, H3, and H4 not started

## Delivered Contract

`tools/hermes/proposals/models.py` defines the exact external proposal identities:

1. `StrategyProposal`
2. `StrategyAdjustmentProposal`
3. `BugFixProposal`
4. `LabImprovementProposal`
5. `DataAcquisitionProposal`
6. `DependencyUpgradeProposal`
7. `InvestigationProposal`

Every proposal requires schema/type/title, exact repo and Hermes-session identity,
ordered evidence refs plus resolved path/hash anchors, FACT/INFERENCE/OPEN QUESTION,
rationale/benefit/confidence, affected scope/domains, A0/A1/A2 class, cost/compute/time,
requested authority, approval, validation, rollback/stop, and immutable non-authority
fields. Type-specific Pydantic bodies forbid missing or extra fields.

The only permitted requested-authority kind is human review for a separate work
package. Self-approval, direct execution, and standing authority are false;
`approval_required=true`, `not_authority=true`, `review_required=true`, and
`automatic_consumers=[]` are mandatory for every class.

## Deterministic Classification and Evidence Resolution

The closed affected-domain enum mechanically requires A0 for canonical evidence
writes, Result Population or authoritative Strategy Spec mutation, promotion/GO,
dispatch/KDAUTH, OMS, reconciliation, hard risk, safe mode/kill switch, live
strategy parameters, paper/live runtime, exchange/order/capital, private
credentials, Search Governor bypass, and ambiguous protected scope. A2 is limited
to the explicitly low-risk lab-process, bounded-investigation, documentation, and
test-only-tooling domains. All H2 classes remain proposal-only.

Before persistence, Project-Evidence re-reads every `project://` or `evidence://`
resource or reruns every allowlisted `query://` identity at the proposal repo SHA.
Declared paths/hashes must exactly equal the returned identities and every FACT and
typed body evidence ref must resolve to an envelope anchor. Research Memory remains
an index/hint and cannot directly anchor an H2 FACT.

The existing `submit_proposal` tool remains the seventh and only proposal write
tool. The outbox remains one fixed gitignored root with symlink/traversal denial,
exclusive create, no overwrite, durable fsync, repo/session/evidence lineage, and
no reader or automatic consumer. It now persists `hermes_proposal_outbox_v2` with
the complete validated typed object.

## Real Model-Backed Acceptance

The deployed pinned Hermes v2026.8.13 path used the sole `openai-codex` OAuth
credential labeled `second-account`, model `gpt-5.6-luna`, and the live
Project-Evidence MCP at exact repo SHA
`02d8c8133d3892bc5e649ed24b427a2c18f00e1d`.

| Type | Class | Proposal ID | Exact evidence ref |
| --- | --- | --- | --- |
| `InvestigationProposal` | A2 | `HERMES-PROP-20260817T162438Z-9b3ec5fa4bf247aa` | `project://status` |
| `StrategyProposal` | A1 | `HERMES-PROP-20260817T162650Z-ea955486d4604e07` | `evidence://experiment-report/REP-0032` |
| `StrategyAdjustmentProposal` | A0 | `HERMES-PROP-20260817T162754Z-3686372350454c61` | `evidence://experiment-report/REP-0032` |
| `BugFixProposal` | A1 | `HERMES-PROP-20260817T162854Z-3ff32af378864387` | `evidence://experiment-report/REP-0032` |
| `LabImprovementProposal` | A1 | `HERMES-PROP-20260817T163007Z-b7c699e786cc4cbc` | `evidence://experiment-report/REP-0032` |
| `DataAcquisitionProposal` | A1 | `HERMES-PROP-20260817T163116Z-3cf8990d32e14f91` | `evidence://experiment-report/REP-0032` |
| `DependencyUpgradeProposal` | A1 | `HERMES-PROP-20260817T163237Z-6a03bda175a44e14` | `project://status` |

The exact live evidence identities were:

- `docs/project_status.md`, SHA-256
  `5e18d0f7cfd5ce3017dd2679178293401b44ef77e3ca97ff058a6fe6bc271852`;
- `research/experiments/REP-0032.report.json`, SHA-256
  `1b397c15ecb2b4d48fdb8b55fafbd8bdb8dea52114511a6d735e8d558e2d1085`.

The A0 example proposes only a future lab comparison for H-012, but declares
`strategy_spec_authority_mutation` because any later authoritative Strategy Spec
change is permanently protected. It has `approval_required=true`. The deployed
validator rejected exact copies relabeled A1 and A2 and left the outbox at seven.
The Strategy proposal is legitimate A1 research; the bounded status-gap
investigation is legitimate A2 and still requests no standing authority.

An initial live investigation attempt could not see a trailing status hash after
large content. It submitted a zero placeholder; validation rejected it and created
no file. Project-Evidence now serializes identity/hash before large content, after
which all seven live types passed without relaxing validation.

## Validation and Boundary Proof

- Focused H2 plus existing Project-Evidence/outbox/deployment contracts: 75 passed.
- Candidate/Result Population, Pydantic reasoning, and Research Memory adjacency:
  113 passed, 3 environment-dependent PostgreSQL tests skipped.
- All 20 required adversarial cases pass, including both A0 misclassifications,
  direct action/authority variants, missing/unallowlisted/fabricated evidence,
  non-authority flag violations, duplicate create, symlink traversal, and malformed
  typed bodies. Additional A2-domain and query-hash tamper cases also pass.
- Live MCP discovery: exactly seven tools; no new tool or action surface.
- Ruff check/format, compileall, JSON/YAML parsing, Compose config, and
  `git diff --check`: pass.
- Runtime/control-root search found no outbox/type consumer. Physical mounts retain
  read-only project evidence and skills/config; `/outbox` is the sole project-facing
  writable mount. The repository stayed clean throughout live generation because
  proposal files are local and gitignored.

## Authority Boundary

H2 reads evidence, reasons, validates, and writes inert review proposals only.
There is no executable payload, broker, approval token, dispatcher, automatic
consumer, project/canonical writer, dependency installer, data hydrator, issue/PR
creator, shell, arbitrary filesystem/SQL, runtime, paper/live, exchange, order,
capital, OMS, reconciliation, risk, safe mode, kill switch, promotion/GO,
dispatch/KDAUTH, or Search Governor authority. H2 adds no trading, runtime, or
scientific authority. H2.5 PREPARE, H3 ask-and-act, and H4 standing authority are
not started.
