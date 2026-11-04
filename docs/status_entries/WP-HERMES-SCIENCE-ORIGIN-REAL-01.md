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
