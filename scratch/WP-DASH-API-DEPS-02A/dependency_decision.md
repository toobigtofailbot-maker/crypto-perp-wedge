# WP-DASH-API-DEPS-02A Dependency Decision

Decision: add the minimal dashboard API dependencies allowed by repo truth.

## What Changed

- Added `fastapi` to `requirements.txt`.
- Added `httpx` to `requirements.txt` for local `fastapi.testclient.TestClient` support.
- Deferred `uvicorn` because no server runner, deployment, or documented run command is authorized by this package.
- Left `starlette` and `pydantic` as transitive/runtime lock entries rather than direct declarations.
- Updated `requirements.lock.txt` by preserving its UTF-16 LE format and adding the minimal pinned rows associated with the FastAPI/TestClient stack:
  - `annotated-doc==0.0.4`
  - `annotated-types==0.7.0`
  - `anyio==4.14.0`
  - `fastapi==0.139.0`
  - `h11==0.16.0`
  - `httpcore==1.0.9`
  - `httpx==0.28.1`
  - `pydantic==2.13.4`
  - `pydantic_core==2.46.4`
  - `starlette==1.3.1`
  - `typing-inspection==0.4.2`

## What Did Not Change

- No dashboard API implementation.
- No frontend app.
- No Agent Inbox endpoint.
- No server deployment, Docker, systemd, reverse proxy, VPS, hosting, auth, secrets, `.env`, CI, monitoring, scheduler, notification, provider/API, broker/exchange, paper/live, runtime, OMS, reconciliation, risk, overlay, safe-mode, canonical evidence, candidate lifecycle, crossing, promotion, or readiness change.
- No `pyproject.toml` change because repo truth uses `requirements.txt` / `requirements.lock.txt` for dependencies.

## Decision Basis

Fact: The future dashboard architecture lock names FastAPI as the backend direction for a local-first read-only artifact-reader API.

Fact: The active package authorizes dependency enablement only.

Fact: `fastapi` and `starlette` were absent from both default `python` and the repo `.venv` before the local install.

Fact: `httpx` was already present in both interpreters, but it was not declared in repo dependency files.

Inference: `httpx` should be declared directly because the package objective includes local TestClient tests, and Starlette's TestClient imports an httpx client layer.

Decision: Add `fastapi` and `httpx` as direct dependencies; lock the resolved FastAPI/TestClient stack; do not add `uvicorn`.

## Unblock Statement

`WP-DASH-READONLY-API-02` is unblocked for repo-standard `.venv` execution after installing from the updated dependency files. The unrelated global/default `python` environment was not mutated and still is not treated as repo authority.
