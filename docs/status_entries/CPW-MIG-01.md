# CPW-MIG-01 — Domain Extraction & Active Storage

## Branch, PR, and package identity

- Work package: `CPW-MIG-01`
- Branch: `codex/cpw-mig-01-domain-extraction-active-storage`
- PR: [#714 — CPW-MIG-01: Extract CPW domain seams and active storage](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/714)
- Package class: FOUNDATION / MIGRATION BASE / DOMAIN CONTRACT + NONCANONICAL STORAGE SEAM
- Validation tier: T2, with the package-mandated full-release run
- Exact base: `114028afbbf341e94d6c85d68bd25c0d586721da`
- Implementation and accepted full-release head: `ade295a3b0af68937258132158473288251f3326`
- Final head: the commit containing this status-only evidence tail; its immutable SHA is recorded in the PR body and coding-agent exact-head report because a Git commit cannot contain its own object ID.
- Merge status: open, non-draft PR held for Side exact-head review; not merged and no auto-merge or self-merge requested.

## Scope and result

This package extracts the minimum locked CPW-owned formalization,
preregistration/approval, and scientific-accounting semantics into pure
framework-neutral modules. The allowlisted legacy research-agent and lab-pipeline
consumers delegate to those modules while preserving their existing import
paths, outward exception/error behavior, output paths, and scientific results.

It also adds a contained repo-local storage resolver for `.cpw/active/` and
`.cpw/ephemeral/`. The entire `.cpw/` tree is gitignored and has no canonical,
candidate, execution, promotion, runtime, or economic authority. Existing
`scratch/` consumers, defaults, historical evidence, and ToolContext permissions
remain unchanged.

## Exact changed files

Created:

1. `tools/research_domain/__init__.py`
2. `tools/research_domain/contracts.py`
3. `tools/research_domain/formalization.py`
4. `tools/research_domain/preregistration.py`
5. `tools/research_domain/scientific_accounting.py`
6. `tools/research_storage/__init__.py`
7. `tools/research_storage/workspace.py`
8. `tests/test_research_domain.py`
9. `tests/test_research_storage.py`
10. `docs/architecture/2026-09-domain_extraction_active_storage_contract.md`
11. `docs/status_entries/CPW-MIG-01.md`

Modified:

12. `.gitignore`
13. `tools/research_agents/idea_formalizer_agent.py`
14. `tools/research_agents/experiment_runner_agent.py`
15. `tools/research_agents/formalizer_runner_bridge.py`
16. `tools/lab_pipeline/model.py`
17. `tools/lab_pipeline/orchestrator.py`
18. `tools/lab_pipeline/adapters.py`
19. `tools/lab_pipeline/gate_actions.py`
20. `docs/project_status.md`

The final tracked base-to-head set is exactly these 20 allowlisted paths. There
are no renames, deletions, tracked `.cpw/` files, or changes to an existing
legacy oracle test.

## Locked domain and storage surface

`tools.research_domain.contracts` owns the exact locked timeframe, trial-status,
preregistration schema/scope/statement/field, and lab/prereg non-authority
constants. `tools.research_domain.formalization` exposes `detect_features`,
`assess_capabilities`, and `build_strategy_spec`.
`tools.research_domain.preregistration` exposes
`build_preregistration_packet`, `build_approval_requirement`,
`build_approval_template`, `validate_bound_requirement`,
`validate_prereg_approval`, and `build_approval_marker`.
`tools.research_domain.scientific_accounting` exposes
`validate_declared_trials`, `validate_trial_denominator`,
`build_bridge_ledger_rows`, `validate_variant_denominator`, and
`compare_result_populations`.

`tools.research_storage.workspace` exposes the exact
`ACTIVE_WORKSPACE_RELATIVE_ROOT`, `EPHEMERAL_WORKSPACE_RELATIVE_ROOT`, and
`resolve_workspace_path` surface. Resolution accepts only the locked storage
classes, safe relative namespaces/artifact paths, and an optional contained
parent-creation step. Absolute, drive-qualified, empty/dot, traversal, and
existing symlink/junction escapes fail closed with `ValueError`-compatible
behavior.

## Semantic oracle and focused validation

The exact immutable legacy oracle command was run before and after mutation:

```text
python -m pytest tests/test_agent_idea_formalizer.py tests/test_agent_experiment_runner.py tests/test_agent_formalizer_runner_bridge.py tests/test_lab_pipeline_orchestrator.py tests/test_lab_pipeline_agent_adapters.py tests/test_lab_pipeline_gate_actions.py tests/test_lab_cockpit_pipeline_state.py tests/test_lab_pipeline_runner_adapter.py -q
```

- Pre-mutation base: `242 passed` in 29.98 seconds.
- Post-mutation implementation: `242 passed` in 24.98 seconds.
- Post-format confirmation: `242 passed` in 25.16 seconds.
- Parity: exact pass-count parity; no oracle file was edited.
- New focused tests: `30 passed, 2 skipped` in 3.29 seconds. Both skips are the
  Windows environment's inability to create the symlink fixtures; every
  non-symlink containment case passed.
- Required adjacent blast radius: `459 passed`, 24 warnings, in 97.24 seconds.
- The six wrapper-focused legacy subsets also passed independently: `188 passed`.
- Python compilation completed successfully for the changed Python modules.

## Full-release evidence

The exact mandatory command ran on the clean implementation head
`ade295a3b0af68937258132158473288251f3326` and exited zero:

```text
python tools/dev/verify.py --validation-preset full-release --full-pytest-sharded --pytest-shard-profile full-release-balanced-v1 --json
```

Profile `full-release-balanced-v1` version 1 used 48 shards, 4 workers, and the
locked 1,800-second per-shard timeout. All 180 discovered tracked test files
were assigned and executed exactly once: 180 discovered, 180 assigned, 180
unique, zero missing, duplicate, untracked, incomplete, not-run, or timed-out
assignments. All 48 shards passed and `all_shards_passed=true`. Collection
contained 3,928 nodes; the accepted environment result was 3,883 passed and 45
explicitly gated skips. The skip-bearing files were rerun under the same
environment to recover the aggregate omitted by UI output truncation: 461
passed and the same 45 skips. The slowest full-release shard was shard 41 at
1,143.515 seconds.

The validation-only 1d and funding datasets were copied from the root checkout
into their exact gitignored worktree paths after source/destination hash checks.
They remained ignored, untracked, and outside package truth. The 45 skips are
environment disclosures only: absent optional local fixtures, Windows
symlink/junction privilege limitations, unset PostgreSQL integration-test DSNs,
and one deployment-host-only proof. No required shard failed or timed out.

Only this status fragment changed after the accepted full-release head. Final
head focused/oracle/import/gitignore/scope/diff checks are the publication
evidence; every code, test, storage, architecture, and project-status blob is
byte-identical to the accepted full-release head.

## Isolation, dependency, and boundary proof

- `.gitignore` contains `/.cpw/`, so both storage classes and any future child
  are ignored as a whole root. Git ignore checks pass for representative active
  and ephemeral paths; no `.cpw` path is tracked, staged, or required as repo
  truth.
- Storage tests prove active/ephemeral separation, deterministic contained
  resolution, optional parent creation, storage-class validation, absolute and
  drive-path rejection, traversal rejection, and existing-link escape
  rejection where Windows permits link creation.
- Direct import inspection of `tools/research_domain/**` and
  `tools/research_storage/**` finds no Pydantic AI, Hermes, Prefect,
  NautilusTrader, ToolContext/agent-sandbox, lab orchestration/scheduler/state,
  research automation, canon-intake, `lib.backtest`, network client, or
  protected runtime/paper/live/OMS/risk/reconciliation/exchange/order/capital
  dependency.
- Search Governor, compiler/backtester, Research Memory, robustness, WFO/OOS,
  candidate lifecycle/promotion, schemas, validators, query views, canonical
  artifacts/writers, dependencies, runtime safety, OMS, risk, overlay,
  reconciliation, exchange/order, credentials, and capital behavior are
  unchanged.
- No Prefect, Hermes, or Nautilus ownership transfer, adoption, cutover, or
  retirement occurs. No final canonical `RunRequest` or `ResultEnvelope` is
  introduced.

## Active-WP Requirement Traceability

| Requirement | Disposition | Evidence |
|---|---|---|
| Framework-neutral domain package | Satisfied | Pure `tools/research_domain` modules with forbidden-import proof |
| Locked minimum public API surface | Satisfied | Exact constants/functions listed above and re-exported without a service/framework layer |
| Formalization extraction | Satisfied | Pure detection/capability/spec functions; idea-formalizer delegates |
| Preregistration/approval extraction | Satisfied | Pure packet, requirement, template, validation, and marker functions |
| `gate_actions` semantic-owner consolidation | Satisfied | File/path/preview I/O remains local; bound-requirement, operator, and marker semantics delegate to the domain owner |
| Scientific-accounting extraction | Satisfied | Trial validation, denominators, bridge rows, and result comparison moved to pure functions |
| Legacy wrapper delegation | Satisfied | Seven allowlisted legacy consumer modules delegate while preserving old public paths and outward behavior |
| Unchanged legacy oracle tests | Satisfied | Same immutable eight-file oracle: 242 passed before and after; zero oracle edits |
| `.cpw/active` active/provisional root | Satisfied | Locked constant and contained resolver |
| `.cpw/ephemeral` root | Satisfied | Locked constant and contained resolver |
| Whole `.cpw` root gitignored | Satisfied | `/.cpw/` rule plus representative `git check-ignore` proof |
| No legacy scratch migration | Satisfied | Historical scratch and existing defaults remain untouched |
| No ToolContext permission change | Satisfied | Agent-sandbox files and `WRITE_SCRATCH` behavior unchanged |
| No Prefect/Hermes/Nautilus dependency | Satisfied | Dependency files unchanged; direct import proof clean |
| No canonical `RunRequest`/`ResultEnvelope` | Satisfied | No such contract or canonical crossing implementation added |
| No protected/runtime authority change | Satisfied | Exact allowlist excludes all protected/runtime/economic paths |
| Required full-release evidence | Satisfied | Exact command passed all 48 shards over 180/180 unique files |
| Exact changed-file scope | Satisfied | Exactly 20 authorized paths, with this file as the sole docs tail |
| No later-package authorization | Satisfied | Later lanes are only technically eligible after merge and still require separate drafting and authorization |

## Runway after merge

After Karl merges this exact reviewed head, CPW-PREFECT-01,
CPW-HERMES-01, CPW-NAUTILUS-N1-01, CPW-CANON-01, and CPW-RESEARCH-02 become
technically eligible for separate drafting. Eligibility is not execution
authority. This package starts none of those lanes and grants no later package,
framework, canonical, paper/live, or capital authority.
