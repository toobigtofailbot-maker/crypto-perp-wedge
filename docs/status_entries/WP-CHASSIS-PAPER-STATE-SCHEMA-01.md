# WP-CHASSIS-PAPER-STATE-SCHEMA-01 - Paper-state schema

- Package class: schema / validator / tests / docs, disconnected chassis package.
- Branch: `feature/chassis-paper-state-schema-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-CHASSIS-PAPER-STATE-SCHEMA-01`.
- Base: `origin/main` at `0d1248d`.
- Repo-truth discovery: `docs/architecture/paper_shadow_chassis_design.md`
  requires a future paper/shadow state artifact family before paper/shadow
  evidence. Existing validator conventions validate schema shape plus narrow
  semantic guardrails, and current candidate lifecycle schema work already
  separates fixture-only examples from real authority.
- Changed files:
  - `research/schemas/paper_state.schema.json`
  - `tools/registry/validate_paper_state.py`
  - `tests/fixtures/paper_state/valid_example.paper_state.json`
  - `tests/test_validate_paper_state.py`
  - `docs/status_entries/WP-CHASSIS-PAPER-STATE-SCHEMA-01.md`
- Schema summary: Defines a snapshot-style paper-state artifact with
  `schema_version`, `paper_state_id`, `snapshot_time_utc`, `mode`,
  `candidate_ref`, `strategy_ref`, `data_context`, `expected_state`,
  `observed_state`, `orders`, `fills`, `account`, `risk_state`, `drift`,
  `non_authority_declaration`, and `validation_summary`.
- State coverage: Captures expected versus observed position, open orders,
  fills, equity/cash/margin, realized and unrealized PnL, funding, fees,
  slippage estimate, freshness, caps, heartbeat, safe-mode/no-new-intent,
  operator halt, drift classification/severity/reason/evidence, and explicit
  non-authority flags.
- Validator behavior: Loads the schema, validates committed paper-state
  fixtures under `tests/fixtures/paper_state` by default, rejects duplicate
  order IDs and fill IDs, rejects fills that reference unknown orders, rejects
  non-none drift without reason/evidence, rejects `halt_required` drift without
  safe-mode/no-new-intent/operator-halt posture, and rejects false
  non-authority flags. It remains validation-only and implements no
  reconciliation engine.
- Fixture status: The only committed paper-state instance is a fake fixture
  under `tests/fixtures/paper_state/valid_example.paper_state.json` using
  fake IDs such as `PAPER-STATE-EXAMPLE-0001`, `ORDER-EXAMPLE-0001`, and
  `FILL-EXAMPLE-0001`; it does not reference a real candidate as paper-running.
- Boundary summary: No real `research/paper_state/` artifact is committed; no
  paper engine, reconciliation engine, OMS, risk engine, order lifecycle
  engine, exchange connector, broker connector, runtime path, paper/live path,
  Strategy Spec, Variant Manifest, Sweep Plan, result population, compiler,
  runner, query layer, `lib/`, data, credentials, or capital path is changed.
- Authority summary: The schema, validator, and fixture create no paper,
  runtime, live, broker/exchange, capital, order-execution, candidate-promotion,
  trading-recommendation, or policy authority.
