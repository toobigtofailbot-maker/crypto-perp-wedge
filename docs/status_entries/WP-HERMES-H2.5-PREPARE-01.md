# WP-HERMES-H2.5-PREPARE-01

## Package State

- Branch: `codex/wp-hermes-h2-5-prepare-01`
- Refreshed base: `e67fe2773a64adce7947a98ea940ad3f58b14480` (merged PR #707)
- Live-acceptance implementation head: `c4c3a0189d8e61a1d07e2e3390db73ffcb5b638e`
- Pull request: [#708](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/708)
- Package class: T2 typed contract, validation, exact persistence, and MCP seam
- Result: H2.5 PREPARE complete; H3 and H4 not started

## Stable Prepared Identities

`tools/hermes/prepare/models.py` defines exactly these external identities:

1. `StrategyLabPreparedPayload`
2. `SearchGovernorCampaignPreparedPayload`
3. `CodexWorkPackagePreparedPayload`
4. `PrefectWorkflowPreparedPayload`
5. `BoundedDiagnosticPreparedPayload`
6. `DataHydrationPreparedPayload`
7. `DependencyMaintenancePreparedPayload`

Every type has the common envelope fields `schema_version`,
`prepared_payload_type`, exact prepared `repo_sha`, `source_session_id`,
`source_proposal_id`, `source_proposal_type`,
`source_proposal_content_sha256`, `source_proposal_repo_sha`,
`source_authority_class`, ordered `evidence_refs` and `evidence_anchors`,
FACT/INFERENCE/OPEN QUESTION separation, `future_action_type`, exact `target`,
`scope`, and `parameters`, applicable `count_or_quantity_bound`, exact hard
`budget_bound`, exact hard `timeout`, `expected_outputs`, `validation_plan`,
`rollback_or_stop_conditions`, and class-preserving `authority_class`.

All payloads require `human_review_required=true`, `not_authority=true`,
`automatic_consumers=[]`, and false `self_approval`, `direct_execution`,
`standing_authority`, `approval_token_eligible`, `broker_eligible`, and
`dispatch_eligible`. A0 additionally and mechanically requires
`permanent_non_executable=true` and `protected_human_gate_only=true`. A1/A2
remain non-executable classifications in H2.5 and receive no current broker or
standing-authority encoding.

## Closed Source Compatibility

| Prepared type | Accepted H2 proposal types |
| --- | --- |
| Strategy Lab | Strategy, Strategy Adjustment |
| Search Governor Campaign | Strategy, Strategy Adjustment, Investigation; additionally restricted to non-A0 bounded non-protected research domains |
| Codex Work Package | Bug Fix, Lab Improvement, Dependency Upgrade, Investigation; Strategy/Strategy Adjustment only with explicit non-A0 non-protected research-tooling scope |
| Prefect Workflow | Lab Improvement, Investigation, Data Acquisition |
| Bounded Diagnostic | Bug Fix, Lab Improvement, Investigation, Dependency Upgrade |
| Data Hydration | Data Acquisition |
| Dependency Maintenance | Dependency Upgrade |

All other pairings reject before prepared-record creation.

## Parent Lineage and Canonical Bytes

`PreparedPayloadValidator.load_source_proposal()` resolves only
`<fixed-outbox>/<proposal_id>.proposal.json`, rejects missing, oversized,
non-regular, symlinked, or escaped inputs, requires an H2 outbox-v2 outer record,
and validates the nested object as `TypedProposal`. Outer ID/type/title/source,
evidence-reference, and non-authority fields must agree with the nested object.
Caller hashes are declarations only.

`source_proposal_content_sha256` is SHA-256 over
`canonical_json_bytes(validated_nested_typed_proposal)`. It does not hash the
filename, timestamp, H2 outer record, or its formatting. H2 had no prior
declared proposal-content hash, so no historical identity required rebasing and
no conflicting historical hash semantic was found.

`tools/hermes/prepare/serialization.py::canonical_json_bytes()` emits sorted,
compact canonical JSON with UTF-8 encoding, `ensure_ascii=false`, finite numbers
only, platform-independent LF, and exactly one trailing newline. Prepared
parameters reject floats and use exact integers/strings where numeric identity
matters. H2's already-validated finite confidence floats serialize through the
same deterministic local function. The implementation does not import or modify
the protected canonical-intake/KDAUTH helpers.

The outer `hermes_prepared_outbox_v1` record is itself canonical JSON and stores
the nested prepared object, `prepared_payload_sha256`, source/outbox metadata,
canonicalization metadata, and inert authority flags. The prepared hash covers
only the canonical bytes of the nested validated prepared payload and therefore
does not hash itself; changing outer metadata does not change it.

## Persistence and MCP Boundary

Prepared records exclusive-create beside their H2 parents in the existing
physical `scratch/hermes_proposal_outbox/` root as
`HERMES-PREP-<UTC>-<token>.prepared.json`. The same fixed-root, symlink/traversal
denial, no-overwrite, file flush/fsync, gitignored/local, and no-consumer posture
is preserved. `submit_proposal` is unchanged.

Exactly one MCP tool was added: `submit_prepared_payload`. Live discovery found
exactly eight tools:

1. `project_evidence_manifest`
2. `list_project_resources`
3. `read_project_resource`
4. `run_evidence_query`
5. `lookup_research_memory`
6. `check_dependency_security_watch`
7. `submit_proposal`
8. `submit_prepared_payload`

The new tool validates and exclusive-creates one inert prepared record only. It
cannot approve, mint a token, call a broker, dispatch, invoke Search Governor,
Prefect, Codex, or network services, write repository/canonical evidence, run a
diagnostic, hydrate data, update a dependency, or execute anything.

## Real Model-Backed Acceptance

Pinned Hermes `v2026.8.13` used the existing sole `openai-codex` credential
labeled `second-account`, model `gpt-5.6-luna`, reasoning `high`, live
Project-Evidence MCP, and exact implementation SHA
`c4c3a0189d8e61a1d07e2e3390db73ffcb5b638e`.

| Prepared type | Class | Prepared record | Parent proposal | Parent content SHA-256 | Prepared SHA-256 |
| --- | --- | --- | --- | --- | --- |
| Bounded Diagnostic | A2 | `HERMES-PREP-20260817T214348Z-f8882dcab86e4ea0` | `HERMES-PROP-20260817T162438Z-9b3ec5fa4bf247aa` | `4e16956823dcc212180135ccacefa945db7f0cb2631d6f0d50aa092b7588cee3` | `39f07782a6fe20533e55f8ed3a222a7630d3b6143b3d651a3fd16038aa69bfe5` |
| Strategy Lab | A0 | `HERMES-PREP-20260817T214502Z-c9c9507e279b45e6` | `HERMES-PROP-20260817T162754Z-3686372350454c61` | `5e3311c6464cf5e26593ff4c85da217522d62e2a1414cf369a0c6a1e7602eae0` | `31227263d464e6763a1e56c965f06671ec770b1cffddae764c41152279d25e16` |
| Search Governor Campaign | A1 | `HERMES-PREP-20260817T214611Z-b5f0b4de396147fa` | `HERMES-PROP-20260817T162650Z-ea955486d4604e07` | `c4354c14fe80176f4d278ebfbe9e1f5131a39b465e727557c9a126adbf4f541d` | `9d613bc8407ccc890c19ea0b638cc793ed79a305cfc10506462d05d3c807d6a3` |
| Codex Work Package | A1 | `HERMES-PREP-20260817T214725Z-10c2aebef1ec4d57` | `HERMES-PROP-20260817T162854Z-3ff32af378864387` | `ace5c0810eb9475c171f7c4ef33dfd3bc5abd41162e3af08ecb29e428451d60a` | `2764956f3d60779d90054658d302e5cc6b7688862da955a09f5459da6323109e` |
| Prefect Workflow | A1 | `HERMES-PREP-20260817T214846Z-38c751117a6144c6` | `HERMES-PROP-20260817T163007Z-b7c699e786cc4cbc` | `400afaacd30070cc76e49f32581f83b5fb330fa3c079f7670ba5daecd82ecc1d` | `b0e4dafcb8160387f713720bc8b6fb5f5625d2a104e6848ba62c9dafe2d1c15d` |
| Data Hydration | A1 | `HERMES-PREP-20260817T215001Z-2672a2dcc14041d8` | `HERMES-PROP-20260817T163116Z-3cf8990d32e14f91` | `411b6b342b83592513847fad8b70af77d41ddf33bb7fc70392d5b367de18225f` | `bb7e9ffbccba8f9bd160cbf6e1edb1f24c19cb6ea86b0ad3834e52096c88c597` |
| Dependency Maintenance | A1 | `HERMES-PREP-20260817T215121Z-48f23f082efb4bb9` | `HERMES-PROP-20260817T163237Z-6a03bda175a44e14` | `6d59c675ff3ab59c44416faff1d0ec50154d81a408eed6084656ea0866407f2e` | `08aa95c2f207f05083a5cd1dc8a9c16f68360c92e474055d463a6e6ff267b647` |

The current prepared evidence identities at the live head were:

- `project://status` -> `docs/project_status.md`, SHA-256
  `5065d9e926edec015763833f2bfae9f041f36283cc69f6f176666403b2ae8c23`;
- `evidence://experiment-report/REP-0032` ->
  `research/experiments/REP-0032.report.json`, SHA-256
  `1b397c15ecb2b4d48fdb8b55fafbd8bdb8dea52114511a6d735e8d558e2d1085`.

The server independently reopened all seven parents, recomputed every parent and
prepared hash, re-resolved every evidence anchor, reproduced every canonical
outer byte sequence, and retained exactly seven prepared records. One initial
A2 model attempt incorrectly supplied A0-only fields; validation rejected it and
created no record before the corrected A2 submission.

The real A0 parent remained A0 with both permanence flags true. Deployed tamper
attempts to relabel it A1/A2, set either permanence gate false, or enable approval
token, broker, or dispatch eligibility all rejected; the outbox count stayed
seven. Real A1 and A2 cases are present, so no class was fabricated or omitted.

## Evidence and Option-B Watch Proof

Prepared FACTs accept only `project://`, `evidence://`, or `query://` anchors and
are re-resolved at the exact prepared repo SHA. Prepared refs must exactly equal
the H2 parent's ordered refs. Research Memory may remain an index/hint but is
mechanically rejected as a direct prepared FACT anchor. `watch://` is absent
from the evidence-ref grammar; live dependency/security watch observations are
not FACT evidence. The live Dependency Maintenance case deliberately did not
call the watch, used `project://status`, kept the target `UNKNOWN`, and set
`transient_watch_fact=false` and `install_or_update=false`.

## Actual-Path No-Consumer / No-Dispatch Proof

The test and repo-wide searches used current paths, not assumed names:

- Search Governor: `tools/research_search/`;
- dispatch/KDAUTH and canonical writers: `tools/canon_intake/`, including the
  dispatch authorization/manifest/writer, execution-event/writer/adapter,
  queue-admission, spec-writer, and scratch-persistence modules;
- offline runner: `tools/research_runner/`;
- execution, runtime, paper, overlay, and event-log surfaces: `src/execution/`,
  `src/runtime/`, `src/paper/`, `src/overlay/`, and `src/logging/event_writer.py`;
- canonical control-plane records: `research/queue/`.

None contains `.prepared.json`, a prepared type, `submit_prepared_payload`, or
`HERMES-PREP`. No dedicated Prefect implementation and no Codex-dispatch
implementation exists outside the new inert Hermes definition/model/skill
surface; both absences were confirmed by repo-wide implementation search.
Dedicated OMS, risk, reconciliation, and safe-mode runtime modules are also
absent; the actual protected paper/runtime/execution surfaces above were searched
instead. No automatic Hermes consumer was discovered.

## Validation and Boundary Result

- Focused H2.5/H2/Project-Evidence/deployment: 127 passed, 1 host-dependent
  Docker test skipped in the Python run; Docker Compose and the live deployment
  were separately green.
- Candidate/Result Population, Pydantic reasoning, Research Memory, Search
  Governor, and execution-runner adjacency: 165 passed, 3 environment-dependent
  PostgreSQL tests skipped.
- H2.5 focused file: 53 passed, including all 20 accepted matrix pairs, seven
  stable identities, determinism, and 30 explicit rejection variants covering
  the package's 22 minimum adversarial cases.
- Deployed MCP discovery: exactly 8 tools.
- Ruff check/format, compileall, JSON/YAML parsing, Compose validation,
  `git diff --check`, exact changed-file inspection, and protected-path diff:
  pass.
- Broad full-repo pytest was not run, as Tier T2 calls for focused and adjacent
  validation unless actual blast radius requires more.

No protected canonical/KDAUTH, Search Governor legality/holdout/budget, Result
Population, Strategy Spec scientific, execution writer, runtime, paper/live,
OMS, risk, reconciliation, safe mode, exchange, order, capital, dependency, or
data path changed. H2.5 adds zero broker, approval-token, dispatch, runtime,
trading, or scientific authority. Prepared artifacts are inert, hash-stable,
H2-proposal-lineaged human-review plans. H3/H4 are not started.
