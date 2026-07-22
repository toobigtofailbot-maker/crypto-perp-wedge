# Repo-truth discovery

- Initial execution base: `origin/main` at `621d760abdf5826282f1fd476781aa75bbb99ebf` (merged PR #666); merged PR #665 was also present. After validation, the branch was refreshed to `94ba623830655d2e20af2cd96e37ef019b082382`, which adds the unrelated merged funding-provenance PR #667 with no changed-path overlap.
- Package branch: `codex/wp-canon-spec0007-external-content-readiness-01`.
- Open-PR preflight: PR #667 was initially the only open PR and was unrelated funding-provenance work; no overlapping readiness implementation PR existed. PR #667 merged during validation, and the final pre-push check found no open PRs.
- `STRAT-SPEC-0007` remained exactly 19,880 bytes, raw SHA-256 `sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c`, full `repo_canonical_json_v1` SHA-256 `sha256:8b6f7dd7a3e12b934c1038ae113aa25aa79f0b3cc6a336b25bd58164f5cc92db`, and Git blob `ac5a493cb5b7d1a5de3647df07bd3151a8e4a440`.
- The embedded legacy state remained `hash_status=not_computed`, `canonical_spec_hash=null`, and `hash_scope_version=strategy_spec_hash_scope_v1`.
- VM-0007 parent hash exactly equaled the full canonical Strategy Spec hash. VM-0007, SWEEP-PLAN-0007, QI-20260717-H004R2B1, GATE-Q-H004-R2-04B-0001, and the queue-admission audit remained byte-identical to the preservation manifest.
- The production fact root and retained Git history contained no prior readiness fact before the protected crossing.
- The pre-package query layer exposed 58 `v_integrity_*` views. Its sole nonempty row was `v_integrity_strategy_spec_hash_readiness` for STRAT-SPEC-0007 legacy `not_computed` state.
- Consumer discovery found only the active SQL definition, tests, and historical documentation/evidence. No merged runtime, dispatch, runner, or other active consumer required a compatibility alias, so the old surface could be replaced by the two locked surfaces without creating a third active view.
- `docs/project_status.md` is explicitly excluded from this package and was not modified.
