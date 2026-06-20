# WP-PILOT-NOTIFICATIONS-APPROVALS-01 - Pilot notification and approval plumbing

## WP id / title

- WP id: `WP-PILOT-NOTIFICATIONS-APPROVALS-01`
- Title: Pilot notification and approval plumbing
- Decision: `COMPLETE`

## Branch / worktree

- Branch: `pilot/notifications-approvals-01`
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-worktrees\pilot-notifications-approvals-01`
- Base: `origin/main` at `4da388a`
- Rebase result: existing worktree WIP was preserved, branch was fast-forwarded from `0ca18b9` to refreshed `origin/main`, and the WIP reapplied cleanly.

## Package class

Scratch-only external-tool pilot / adopt-candidate.

## Repo-truth discovery

- `WP-LAB-DASHBOARD-EXPANSION-01` added a read-only Operator Review page with manual approval posture, blockers, warnings, and explicit no-authority framing.
- `dashboard_data.v1` rejects approval/execution authority keys and keeps operator review display-only.
- `WP-LAB-IDEA-INTAKE-FORMALIZATION-01` keeps draft formalization local, deterministic, non-authoritative, and future-human-gated.
- `WP-PLAN-SIDE12-ADOPTION-LOCK-01` is present on this branch and records Apprise plus GitHub IssueOps as a pilot-now adopt-candidate with no dashboard approval/execution controls or runtime authority.
- Existing query/docs surfaces include approval and lifecycle concepts, but this package does not mutate those canonical or query-layer surfaces.

## Scope summary

This package adds a standalone dry-run pilot under `tools/notifications_poc`.
It models one local JSONL notification event, a pending manual approval request,
a dry-run GitHub IssueOps payload, and blocked forbidden action attempts.

The pilot probes whether `apprise` is importable but does not exercise real
delivery because no package-scoped local/no-op Apprise URL is configured.
No GitHub write API is called.

## Changed files

- `tools/notifications_poc/__init__.py`
- `tools/notifications_poc/approval_models.py`
- `tools/notifications_poc/notifier.py`
- `tools/notifications_poc/run_notifications_approvals_poc.py`
- `tests/test_notifications_approvals_poc.py`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/README.md`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/notification_log.jsonl`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/approval_queue_sample.json`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/issueops_dry_run_payload.json`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/blocked_action_report.json`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/recommendation_report.md`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/provenance.json`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/dependency_probe.json`
- `scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01/requirements.poc.txt`
- `docs/status_entries/WP-PILOT-NOTIFICATIONS-APPROVALS-01.md`

## Boundary summary

- Canonical writes: none.
- Candidate lifecycle / promotion authority: none.
- Dashboard approval/execution controls: none.
- Runtime, paper/live, OMS, risk, reconciliation, safe-mode, kill-switch, broker, exchange, order, capital, credential, or API-config paths: not touched.
- GitHub workflow files and dependency files: not touched.
- `docs/project_status.md`: not touched.

## Validation summary

- `python -m pytest tests/test_notifications_approvals_poc.py -q`: PASS, 6 tests.
- `python -m tools.notifications_poc.run_notifications_approvals_poc --output-dir scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01 --dry-run`: PASS.
- `python tools/dev/diff_scope_summary.py`: PASS; no forbidden-path matches.
- `git diff --check`: PASS.
- `python -m pytest tests/test_generate_static_dashboard.py tests/test_validate_dashboard_data.py -q`: PASS, 55 tests.
- `python -m tools.research_query.run --list-views`: PASS.
- Ambient Python 3.14 `python -m pytest -q`: collection failed in 2.46 seconds because the environment lacks `binance`, `pandas`, and `numpy`; no package-specific failure surfaced.
- Repo virtualenv `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: TIMED OUT after 15 minutes with no visible output; not claimed as passing evidence.
- Repo virtualenv `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -vv --maxfail=1`: FAIL in 114.35 seconds, 518 passed / 1 skipped before first failure; first failure was `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` because `fixture["normalized_data_local_exists"]` was `False` in this isolated worktree. This is the known gitignored local normalized-data-file limitation and is not caused by the notification/approval pilot.
