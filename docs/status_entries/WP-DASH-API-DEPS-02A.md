# WP-DASH-API-DEPS-02A Branch State

## Scope Summary

Adds the minimal dependency declarations needed to unblock the future local-first read-only dashboard API package's FastAPI import and TestClient smoke path. This package performs dependency enablement only and implements no API endpoint, frontend, server process, Agent Inbox, deployment, auth, monitoring, scheduler, runtime, paper/live, provider/API, broker/exchange, or protected-path behavior.

## Repo Truth Discovery

Dependency discovery is recorded in `scratch/WP-DASH-API-DEPS-02A/dependency_discovery.md`. Current repo truth uses `requirements.txt` as the direct dependency surface and `requirements.lock.txt` as the pinned lock surface; `pyproject.toml` carries metadata/tooling only. The future dashboard architecture lock names FastAPI as the backend direction for a local-first read-only artifact-reader API, while preserving all no-implementation and no-runtime boundaries.

## Dependency Decision

`requirements.txt` now declares:

- `fastapi`
- `httpx`

`requirements.lock.txt` preserves its existing UTF-16 LE lockfile format and adds the pinned FastAPI/TestClient stack rows for `fastapi==0.139.0`, `starlette==1.3.1`, `httpx==0.28.1`, Pydantic, AnyIO, and their narrow transitive support packages.

`uvicorn` is deferred because this package does not authorize a server runner, deployment, or local run-command surface.

## Evidence Artifacts

- `scratch/WP-DASH-API-DEPS-02A/dependency_discovery.md`
- `scratch/WP-DASH-API-DEPS-02A/dependency_decision.md`
- `scratch/WP-DASH-API-DEPS-02A/non_authority_assertions.json`
- `scratch/WP-DASH-API-DEPS-02A/validation_summary.txt`

## Validation Status

- Default `python` import probe: `fastapi False`, `starlette False`, `pydantic True`; the unrelated global/default interpreter was not mutated.
- Repo `.venv` import probe after dependency install: `fastapi True`, `starlette True`, `pydantic True`.
- FastAPI/TestClient smoke: PASS, `fastapi_testclient_ok`; Starlette emitted a deprecation warning about the current httpx-based TestClient path, but the test passed.
- `non_authority_assertions.json` JSON validation: PASS.
- Query view listing: PASS, 124 views listed.
- Result-population validator: PASS.
- Candidate-registry validator: PASS.
- Diff-scope summary: PASS; only package-authorized dependency files matched forbidden-pattern terms.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `.venv` `pip check`: PASS.

Full pytest was not run because the active package validation list did not require it for this dependency-enable-only package and the package-specific import, TestClient, registry, query, compatibility, and diff checks passed.

## Boundary Summary

Dependency enablement only. No dashboard API implementation, frontend, Agent Inbox, server deployment, hosting, auth, monitoring, scheduler/autonomy, notification firing, provider/API, credentials, broker/exchange, paper/live/runtime, OMS, reconciliation, risk, overlay, safe-mode, canonical evidence, candidate lifecycle, crossing, promotion, readiness, schema, validator, query-layer behavior, data, or protected-path change is created.

## Unblock Statement

`WP-DASH-READONLY-API-02` is unblocked for repo-standard `.venv` execution after installing from the updated dependency files. The default/global Python environment remains outside repo authority.
