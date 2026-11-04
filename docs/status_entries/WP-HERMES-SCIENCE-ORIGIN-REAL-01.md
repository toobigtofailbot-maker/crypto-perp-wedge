# WP-HERMES-SCIENCE-ORIGIN-REAL-01 - Hermes origin to native CPW science chain (software only)

- Package class: T3 (protected runner use-gate hook and new D3-2 historical
  custody gate). Software only; physical execution NOT performed.
- Outcome: PARTIAL_PHYSICAL_PENDING.
- Branch: `claude/wp-hermes-science-origin-real-01`; draft PR, labelled
  PHYSICAL_PENDING. Karl alone merges.
- Base: `origin/main` at `b92d8cd`.
- Scope summary:
  - Opt-in host observation receipt in `tools/hermes/research_turn.ps1`
    (`-HostObservationReceipt`; default behaviour unchanged).
  - Proof-B verifier `tools/hermes/model_origin_receipt.py`: a cohort that
    verifies but has no operator-pinned receipt anchor stays BLOCKED, and a
    test observer is only ever `B_TEST_FIXTURE_ONLY`.
  - Agent Inbox optional closed `original_parent`, carried through
    `source_hashes` into the unchanged Gate C spec writer.
  - Versioned original route (`research_factory_mapping_original_v1`) in the
    mapper, manual loop and evidence. Without `original` the legacy 0003
    route is unchanged.
  - D3-2 `tools/research_autonomy/historical_source_gate.py` reuses the 02J
    custodian/revocation/control/audit owners. It adds no migration. Leases
    run before any historical read: Windows uses share-mode handles on the
    file and its ancestors; Linux requires the immutable flag or refuses.
  - `tools/lab_pipeline/runner_adapter.py` custody hook. An original-route run
    without custody is refused; the runner records a single-use receipt and
    rechecks that the leased bytes are unchanged.
  - Read-only Stage 0-3 projection
    `tools/research_factory/original_study_bridge.py` with stable refusal codes.
- Proof status: A NOT_EXECUTED, B NOT_PROVEN, A+B NOT_PROVEN, C NOT_PROVEN.
  No genuine Hermes run, receipt anchor, custodian designation, attestation,
  Gate C approval, envelope, D4 approval marker or experiment exists for this WP.
- Boundary summary: No `src/**`, `lib/**`, `configs/**`, `research/schemas/**`,
  `tools/registry/**`, migrations, broker, OMS/risk, Stage 5B, trade paths or
  `docs/project_status.md` changes. No Karl approval was generated or signed,
  and no credentials were used.
- Validation summary: See PR body and the Side 24 report ZIP for exact commands
  and results.
- Merge status: not merged; awaiting Side 24 exact-head review and Karl.
- Next dependency (owner actions):
  1. A genuine Hermes run with `-HostObservationReceipt`, with Karl pinning
     the receipt SHA-256.
  2. Custodian designation and attestation of the exact nonholdout D4 objects.
  3. Agent Inbox review and Gate C approval.
  4. Envelope and search.
  5. A fresh `product_runner_execute_approval_v2` marker.

## Side 24 correction continuation (2026-11-04)

- Outcome: **BLOCKED / NOT MERGE READY**, same draft PR #771; do not merge.
  Pre-correction head: `8b5de0294d396564812025db374755fa6a1b4c4d`.
  Dedicated continuation branch: `codex/pr771-side24-followup`. The old Claude
  worktree is preserved.
- F1: role-scoped D4 CSV/catalog/import paths replace the research-only grammar.
- F2: full leased CSV timestamp sequence, count, UTC/end-exclusive range, import
  range and frozen development partition must agree. Derived/transitive source
  eligibility is **not proven** by this primitive three-object interface.
- Custody preread/use/terminal checks now reread durable contract, envelope,
  custodian/designation/attestation validity and revocation. Fake custody objects
  are refused in the adapter and manual loop.
- F3 remains open: the mapper still accepts a four-hash parent without independent
  capture/Gate C semantic ancestry. The bridge's timeframe/parameter comparison
  cannot establish mechanism/entry/exit/filter/risk continuity. No new semantic
  approval record or approval policy was invented.
- F4 remains open: a missing/replaced mapping sidecar can still classify an
  original input as legacy. Existing v2 approval bytes do not identify that route;
  changing approval semantics or excluding legitimate legacy calls needs an
  explicit bounded owner decision.
- F5: source index bytes bind to the captured manifest and observed source turn;
  command hashes bind to the manifest's exact argument vector. The dictionary-only
  report cannot promote A or B. Native durable proof-A projection is still absent.
- F6: added coverage/path/receipt/proof negatives, original population receipt
  refusal and PostgreSQL custody-revocation reconciliation tests. Legacy 0003
  Spec/VM/Sweep/mapping bytes match the pre-correction head (4/4).
- T3 full-release remains **NOT ACCEPTED**. The clean worktree lacks required
  ignored historical inputs; none were copied or read. Readiness, validators,
  integrity results and exact test commands are recorded in the single Side 24
  evidence ZIP. Focused tests cannot waive this floor.
- A NOT_EXECUTED; B, A+B and C NOT_PROVEN. No real Hermes invocation, historical
  experiment, owner signature, Gate C write, Stage 5B, trading or capital action.
- Remaining owner action is a bounded native ancestry/semantic-review and
  route-binding decision plus separately authorized validation-data custody;
  this entry grants none of those permissions.
