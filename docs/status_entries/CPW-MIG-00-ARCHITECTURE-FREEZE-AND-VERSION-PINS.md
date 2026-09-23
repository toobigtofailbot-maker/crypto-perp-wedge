# CPW-MIG-00 — Architecture Freeze & Version Pins

## Package identity

- Branch: `codex/cpw-mig-00-architecture-freeze-version-pins`
- Pull request: pre-publication validation state
- Base: `08abff2ac2f368f603f217cce7867eb78a4dfa8b`
- Package class: T0 documentation / status / process policy

## Scope summary

CPW-MIG-00 freezes the approved adoption-first ownership model, proof gates,
version targets, supersession rules, storage classes, compatibility and
retirement policy, and migration sequence. It creates architecture/governance
truth only. Infrastructure buildability is not candidate-gated; economic
activation is. The package unlocks CPW-MIG-01 only.

## Changed files

Created:

- `docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md`
- `docs/status_entries/CPW-MIG-00-ARCHITECTURE-FREEZE-AND-VERSION-PINS.md`

Modified:

- `AGENTS.md`
- `CLAUDE_START_HERE.md`
- `docs/project_status.md`
- `docs/architecture/LONG_TERM_SCOPE.md`
- `docs/architecture/RESEARCH_MACHINE_DIRECTION.md`
- `docs/architecture/2026-06-external_repo_adoption_decision.md`
- `docs/architecture/2026-06-side12-external-adoption-pilot-plan.md`
- `docs/decisions/ENGINEERING_VS_STRATEGY_READINESS.md`
- `docs/research/LAB_COMPLETION_MAP.md`
- `docs/onboarding/PHASE2_BASELINE.md`
- `docs/decisions.md`

No code, dependency, configuration, test, schema, query, data, artifact,
runtime, paper/live, OMS, reconciliation, risk, overlay, broker, exchange,
order, or capital surface changes.

## Decision summary

- Hermes is the future generic reasoning/runtime owner.
- Prefect is the future generic orchestration owner.
- Nautilus is the future generic trading-mechanics owner only after applicable
  N1/N2/N3 proof and later ownership transfer.
- CPW retains differentiated scientific, canonical, safety, and approval
  semantics; humans retain economic authority.
- Reconciliation ownership is decided: Nautilus may own ordinary mechanics
  after proof, while CPW retains trust, ambiguity, fail-closed escalation,
  safe-flatten, duplicate-effect, and human recovery policy.
- Canonical authority is engine-neutral and remains CPW-controlled.

## Supersession summary

Prospectively superseded as current direction: BROKER-4/H3 expansion; PR #712
H3-1 continuation; permanent H2.5 prepared-plan growth; custom generic
scheduler/run-state and duplicate Pydantic runtime growth; major new legacy
backtester, PaperBroker/accounting, and bespoke OMS/reconciliation mechanics;
generic offline canon control-plane expansion; and the Nautilus GO/paper-first
trigger. Historical evidence remains valid and readable.

## Version and environment summary

- Hermes control: `v2026.8.13` / `v0.20.1`, digest
  `sha256:68e15ae2a6d894d0ccbd9f8aacbbe13d4d28fa5dc9b6a303970b67bb2499b1a6`.
- Hermes future canary: `v2026.9.21` / `v0.21.4`.
- Prefect future proof target: `3.8.6`; not installed.
- Nautilus historical isolated spike: `1.221.0`.
- Nautilus future proof target: `1.231.0` on Python 3.12; not installed.
- Repo Python remains `>=3.11`; Project-Evidence remains Python 3.11.9.

## Validation summary

- Pre-publication `python tools/dev/verify.py --validation-preset docs-only
  --json`: PASS (6/6 required commands).
- `git diff --check`: PASS.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no
  forbidden-path matches.
- Revised closed allowlist: PASS; exactly 13 authorized documentation paths.
- Internal reference and version/dependency checks: PASS.
- Focused current-direction search: 7 material legacy-phrase hits classified
  A=2 updated, B=5 historical-retained, C=0 intentionally-current, D=0
  out-of-allowlist conflict.

Full pytest: NOT RUN - T0 docs/process policy; not used as merge evidence

## Boundary summary

No framework was installed or upgraded; no runtime migration or legacy deletion
occurred; no canonical writer, scientific, promotion, execution, risk, live, or
capital authority changed; no human gate was weakened; permanent dual authority
was expressly forbidden.

## Merge status

Pre-publication validation passed; PR creation and final committed-head checks
remain in the original one-shot publication sequence. Never self-merge or
enable auto-merge.

## Next dependency

After merge, CPW-MIG-01 — Domain Extraction & Active Storage — is the only
package unlocked. No other migration lane is authorized by CPW-MIG-00.

## Active-WP Requirement Traceability

| Requirement | WP source section | Evidence location | Status |
|---|---|---|---|
| Docs-only / non-authority objective | Original WP §§1, 15, 17 | Architecture record: Non-authority statement; changed-file list above | satisfied |
| Ownership matrix | Original WP §§3, 14.1 | Architecture record: Ownership matrix | satisfied |
| Prospective supersession register | Original WP §5 | Architecture record: Prospective supersession register | satisfied |
| Prefect/Hermes/Nautilus/Canon proof gates | Original WP §6 | Architecture record: Proof-gate register | satisfied |
| Version/environment pin ledger | Original WP §7 | Architecture record: Version and environment pin ledger | satisfied |
| No-dual-authority rule | Original WP §8 | Architecture record: No-dual-authority rule | satisfied |
| Shim ownership and deletion triggers | Original WP §9 | Architecture record: Compatibility shims and boundary adapters | satisfied |
| Retirement criteria | Original WP §10 | Architecture record: Retirement criteria | satisfied |
| Storage-class meanings | Original WP §11 | Architecture record: Storage-class freeze | satisfied |
| Research during migration | Original WP §4.4 | Architecture record: Research during migration | satisfied |
| Human/economic gates unchanged | Original WP §§3.5, 4.1 | Architecture record: Controlling principle and ownership matrix | satisfied |
| CPW-MIG-01 is the only next package unlocked | Original WP §12 | Architecture record: Next authority; project-status runway | satisfied |
| D2-019 and Phase 2 baseline reconciliation | Continuation §§2–3 | `docs/decisions.md`; `docs/onboarding/PHASE2_BASELINE.md` | satisfied |
| No runtime/dependency/code/test/schema/data changes | Original WP §§1, 15, 19.7 | Changed-file list and final scope validation | satisfied |
| Required T0 validation | Original WP §19; continuation §6 | Validation summary in this fragment | satisfied |
