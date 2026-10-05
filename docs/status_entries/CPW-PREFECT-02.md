# CPW-PREFECT-02 — First Real Research-Consumer Orchestration Cutover

- Branch: `codex/cpw-prefect-02-real-consumer-cutover`
- Pull request: not opened during pre-PR validation
- Locked start base: `d4d16278ed68bdfa65c7a85bc778981291f60030`
- Implementation/physical-proof head: `2e60093165e069dff6449610d0355cbc8bb28473`
- Full-release validation head: `c479df73b636907f3ac99e06e32c449bbfbf45ac`,
  based on the unchanged implementation/test blobs from the physical-proof head
- Package class: T2; mandatory full-release
- Self-merge: no

## Exact scope and owner transfer

Changed files are limited to:

1. `tools/prefect_integration/local_json_sweep_consumer.py`
2. `tests/test_prefect_local_json_sweep_consumer.py`
3. `docs/architecture/2026-10-prefect_local_json_sweep_consumer_cutover.md`
4. `docs/status_entries/CPW-PREFECT-02.md`
5. `tools/prefect_integration/__init__.py`
6. `docs/project_status.md`

The selected consumer is
`tools.research_automation.local_json_sweep_spec_loader.run_local_json_parameter_sweep`.
After accepted merge, Prefect owns supported top-level operational invocation,
queue/worker execution, flow state, and run history for this selected consumer
only. Existing CPW helpers continue to own JSON parsing, sweep/point identity,
batch/dry-run/registry behavior, artifacts, and research meaning.

No schedule, trigger, autonomous dispatch, task-level fan-out, or automatic
retry exists. Prefect receives no scientific, denominator, holdout, leakage,
WFO/OOS, robustness, Search Governor, canonical, approval, promotion, runtime,
paper/live, risk, trading, or capital authority.

## Physical validation profile and results

- Host: Windows / PowerShell; Python `3.11.9`; Prefect `3.8.6`.
- Worktree: `C:\GitHub\worktrees\cpw-prefect-02-real-consumer-cutover`.
- Tested implementation head: `2e60093165e069dff6449610d0355cbc8bb28473`.
- Prefect API: loopback `127.0.0.1:14200`; no API key; no Cloud.
- Backend: self-hosted single-server Prefect API with official PostgreSQL
  `17.10` Windows binaries and isolated database
  `cpw_prefect_02_validation` on loopback port `15432`.
- `PREFECT_HOME`: package-owned OS temporary validation directory outside the repo.
- Work pool: `cpw-research-local-process`, type `process`, concurrency limit `1`.
- Worker: `cpw-prefect-02-validation-worker`, process worker limit `1`, observed online.
- Deployment: `cpw-local-json-sweep/cpw-local-json-sweep-v1`, version exactly
  `2e60093165e069dff6449610d0355cbc8bb28473`, explicit worktree pull step,
  zero schedules, zero automations/triggers.
- Fixture: `.cpw/active/cpw-prefect-02/specs/parity.json`, ignored validation
  material, SHA-256
  `f98fa84915c8edf32c1370195a0a3dd743208aa711c54557693384dcb56b4252`.

Direct-helper baseline and Case A each produced 22 files for four points. The
recursive relative file sets and every SHA-256 were equal, with no extra file.
Sweep ID, ordered point IDs, batch ID, registry record IDs, counts, and boundary
flags were equal. The completed flow run used `run_count=1`; Prefect IDs were
not added to CPW artifacts.

Case B remained `Scheduled` with no output namespace while the worker was off.
After worker restart it completed once with `run_count=1` and one 22-file
namespace. Case C restarted only the Prefect server against the same PostgreSQL
database; the exact deployment and both completed histories remained visible,
and PostgreSQL retained one deployment and two completed flow runs.

Case D invalid JSON finished `Failed` with an operational input-validation
exception and no final sweep summary. Case E duplicate namespace finished
`Failed` before helper invocation; the prior 22-file tree remained byte-for-byte
equal to the direct baseline. The proof ended with four total flow runs:
two `Completed`, invalid-spec `Failed`, duplicate-namespace `Failed`, all with
`run_count=1`. Package-owned services were stopped and both proof ports closed.

## Validation

- Focused consumer tests: `21 passed, 1 skipped`; the skip is unavailable
  Windows symlink creation privilege, already covered by the existing resolver suite.
- CPW-PREFECT-01 regression: `12 passed`.
- Local sweep/storage adjacency: `126 passed, 2 skipped`; skips are the same
  unavailable Windows symlink/junction capability.
- Domain/scheduler/operator non-coupling adjacency: `61 passed`.
- Physical self-hosted acceptance: passed all five required cases.
- Direct-vs-Prefect artifact difference count: `0`.
- Integrity profile `h004-clean`: 61 clean views plus exactly the two expected
  disclosures for the missing H004 execution stream and the scoped legacy
  `STRAT-SPEC-0007` hash; zero unexpected rows.
- Mandatory `full-release-balanced-v1`: overall `pass`; 48/48 shards completed
  and passed; 188/188 tracked test files assigned exactly once; 3,875 passed,
  49 accepted environment/capability skips; zero failed, timed-out, incomplete,
  missing, duplicate, or untracked shard assignments.
- Validation continuation fixture: the ignored D4A CSV was copied from the
  primary checkout at 29,300,290 bytes with SHA-256
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.
  The previously failing exact test passed (`1 passed`), the mandatory full
  release passed, and the ignored copy was removed without staging or commit.

## Forbidden-scope result and next dependency

Dependency files, existing research automation, research domain/storage,
scientific runner, canonical/query/schema surfaces, and every protected runtime,
OMS, reconciliation, risk, safe-mode, overlay, broker/order, paper/live, and
capital path are unchanged. No `.cpw` proof material is committed.

After accepted merge, Side/Main must decide whether a remaining Prefect consumer
or legacy-retirement assessment is required before the Hermes + Research Memory
+ Search Governor/Optuna lane. This package pre-authorizes neither route.
