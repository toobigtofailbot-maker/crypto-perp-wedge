# CPW-NAUTILUS-N1-01 — Common Research Engine Adapter

## Package and branch

- Authorization: Karl/Main authorized the exact N1-01 eight-file implementation package.
- Branch: `codex/cpw-nautilus-n1-01-common-research-engine-adapter`
- Worktree: dedicated managed N1-01 worktree
- Base SHA: `88b7602278d915c81ea6c4bd06a3fcfd4c0b4208`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/717
- Implementation HEAD: `c2eb1cf11ca3ffc5bb6fc9f014b1d079a62b899a`
- Final validated semantic HEAD: `c2eb1cf11ca3ffc5bb6fc9f014b1d079a62b899a`
- Final PR tail: this status-only factual finality update; GitHub's exact PR head is authoritative for Side review and is reported with the PR handoff.
- Merge state: open, non-draft, GitHub `MERGEABLE`, not merged; Side exact-head review remains required

## Exact changed files

1. `tools/nautilus_adapter/__init__.py`
2. `tools/nautilus_adapter/research.py`
3. `tools/nautilus_adapter/requirements-win-py312.lock.txt`
4. `tools/simulators/nautilus_mapping_spike.py`
5. `tests/test_nautilus_research_adapter.py`
6. `tests/test_nautilus_n1_acceptance.py`
7. `docs/architecture/2026-09-nautilus_n1_common_engine_adapter.md`
8. `docs/status_entries/CPW-NAUTILUS-N1-01.md`

## Environment and dependency proof

- Python: CPython `3.12.10` x86-64 on Windows.
- NautilusTrader: exactly `1.231.0`.
- Official wheel: `nautilus_trader-1.231.0-cp312-cp312-win_amd64.whl`.
- Wheel SHA-256: `0697f51e9143f9d8d040f75d2e6a45218003cc34f7ea5b0eb2f9cda6935427de` — verified.
- Dedicated lock: `tools/nautilus_adapter/requirements-win-py312.lock.txt`.
- Lock SHA-256: `4d39a0a1460506532671d8d947abf94c1c6a9dd8a61341352f8ae486194784d2`.
- Clean reproduction environment: built successfully from the dedicated lock only; exact-head acceptance passed.

## Acceptance evidence

- Data: 220,128 rows; normalized SHA-256 `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`; exact slice identity verified.
- Micro-proof: repeated exact BUY fill at next open `125.00`, quantity `80.0`, timestamp `1767226500000000001 ns`; PASS.
- Frozen RP-2592: 8 declared / 8 attempted / 8 represented; build-environment proof PASS.
- CANON request hash: `sha256:179ef4d8e20af186ead25e7b482175b441863070e4a90f4e7f02c0188cd9da01`.
- Nautilus run-1 evidence hash: `sha256:8ca48f07190e7dfc9a03c8fc7e1339884919a58149b2d290d8da1ac71b3cb832`.
- Nautilus run-2 evidence hash: `sha256:8ca48f07190e7dfc9a03c8fc7e1339884919a58149b2d290d8da1ac71b3cb832`.
- Repeated-run deterministic equality: PASS.
- Cross-engine evidence-hash equality is not an N1-01 acceptance condition and is not claimed.

| Semantic category | State |
| --- | --- |
| next-bar-open execution | `PROVEN_FOR_N1_01` |
| fee/slippage split | `NOT_PROVEN_IN_N1_01` |
| nonzero funding | `NOT_PROVEN_IN_N1_01` |
| dynamic 1x fixture sizing | `PROVEN_FOR_N1_01_FIXTURE` |
| generalized quantity precision | `NOT_PROVEN_IN_N1_01` |
| direct flip | `NOT_PROVEN_IN_N1_01` |
| zero-equity liquidation | `NOT_PROVEN_IN_N1_01` |
| maintenance margin | `NOT_PROVEN_IN_N1_01` |

## Validation and boundary

- Root adapter tests: 15 passed.
- Historical spike oracle: 4 passed unchanged.
- CANON oracle: 19 passed.
- Isolated build-environment acceptance: 3 passed; no skips; full fixture executed twice.
- Clean-lock reproduction acceptance at implementation HEAD: 3 passed; no skips; full fixture executed twice in 374.06 seconds.
- Backtest/liquidation oracles: 81 passed / 1 skipped.
- Signal compiler oracle: 261 passed.
- Selected runner oracles: 6 passed / 95 deselected.
- Committed Result Population validator: PASS.
- Final rebase: branch already current with `origin/main` at the base SHA; no rewrite.
- Final scope checker: exact eight-file set, `allowed_file_violations=[]`, `forbidden_matches=[]`.
- `git diff --check` and cached/index hygiene checks: PASS; clean tracked/index state.
- Full pytest posture: not required by the bounded T2/high-risk external-adapter package when all required focused and isolated evidence passes.
- Forbidden scope: root dependencies, CANON production code, runner, backtester, compiler, historical RPs, canonical writers/crossings, engine routing, and runtime/paper/live/protected paths are unchanged.

## Runway and authority

N1-01 creates no research-engine or execution authority. N1-02 remains separate
research semantic-parity/stress work. Karl's serialized top-level order proceeds
to HERMES-01 after N1-01 unless Karl/Main changes it. This entry authorizes no
later package and no merge.
