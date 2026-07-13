# WP-LAB-STATE-SUPPLEMENTAL-ROLE-CONTRACT-RECONCILE-01

## Status

READY FOR PR REVIEW. The exact supplemental-role mismatch is fixed and exhaustive deterministic sharded validation introduces no new repository failure.

## Base / head

- Base: `bfc15567850dd143dd064f688a0fa99fbeec9eff` (`origin/main`).
- Branch before commit: base plus the package-scoped production, test, status, and evidence changes listed below.

## Defect and correction

The coordinator emits `riskmanaged_conclusion_evidence` for `funding_fade_riskmanaged_no_go`, while the coverage auditor rejected that exact role. The correction adds an immutable exact-role allowlist containing only `riskmanaged_conclusion_evidence`. Existing prefixes and coordinator/resolver output are unchanged; `made_up_role`, `riskmanaged_unknown`, and `riskmanaged_conclusion_evidence_extra` remain fail-closed.

## Changed-file scope

- `tools/lab_state_coverage_audit/audit.py`
- `tests/test_lab_state_coverage_audit.py`
- `docs/status_entries/WP-LAB-STATE-SUPPLEMENTAL-ROLE-CONTRACT-RECONCILE-01.md`
- `scratch/WP-LAB-STATE-SUPPLEMENTAL-ROLE-CONTRACT-RECONCILE-01/**`

## Validation

- Original monolithic pytest: timed out after 5,404 seconds; partial JUnit captured 2,002 cases. It is not treated as a pass.
- Deterministic collection: two identical inventories, 2,848 nodes across 157 files; normalized inventory SHA-256 `e785f8add24c57f09225779b6c1fc3a605fd30083226c212d82a73f8b553f296`.
- Eight completed terminal shards: 2,836 passed, 6 failed, 6 skipped, 0 errors, 0 internal errors, 0 final timeouts; every collected node executed exactly once.
- Failure union: exactly the six source-hash-bound pre-existing unrelated nodes. The repository baseline remains red.
- All 15 formerly affected lab-state nodes pass.
- Focused: 27 passed.
- Adjacent: 108 passed plus only the known stale operator-surface node.
- Coverage CLI observed 2,109 discovered artifacts at the current PR head. The 59 tracked package-evidence files explain the increase from the earlier 2,049 observation. The stable test invariant requires the total to equal inventory length and exceed 1,000; exact contract counts remain 123 covered, 119 surface-visible, 0 gaps, and 0 malformed. All 15 risk-managed paths are covered and require no follow-up.
- Preservation: all 71 read-only hashes and frozen production/test hashes unchanged; `py_compile`, JSON/JUnit parsing, `git diff --check`, and forbidden-path scan pass.

Two preliminary shard attempts are preserved but excluded from terminal reconciliation: S01 used an absent in-repo basetemp parent; S03 used an in-repo basetemp that correctly triggered path guards. Their corrected terminal reruns completed successfully.

## Boundary

No coordinator output, resolver/model, operator/dashboard/cockpit code or fixture, canonical, queue, execution, result, candidate, runtime, paper/live, OMS, risk, reconciliation, dependency, or configuration change was made. No unrelated baseline repair is included.

The production role-contract correction remains byte-identical in the narrow PR follow-up.
