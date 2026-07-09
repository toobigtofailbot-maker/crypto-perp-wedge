# WP-DASH-API-DEPS-02A Dependency Discovery

## Fact

- Branch: `codex/wp-dash-api-deps-02a`
- Base: `main` / `origin/main` at `86e72fa7ceddf25dc37680bb87d95597e4f1cd70`
- Startup anchors inspected:
  - `docs/project_status.md`
  - `CLAUDE_START_HERE.md`
  - `docs/runbook.md`
  - `AGENTS.md`
- Package-relevant dependency files found:
  - `pyproject.toml`
  - `requirements.txt`
  - `requirements.lock.txt`
- `pyproject.toml` contains project metadata, Python version, and Ruff config only. It does not declare runtime dependencies.
- `requirements.txt` is the direct dependency declaration surface.
- `requirements.lock.txt` is the pinned dependency surface and is stored as UTF-16 LE with CRLF line endings.
- Current lockfile history shows dependency packages have previously edited both `requirements.txt` and `requirements.lock.txt`.

## Dependency Presence Before Local Install

Default `python`:

```text
fastapi False
starlette False
pydantic True
uvicorn False
httpx True
pytest True
```

Repo `.venv`:

```text
fastapi False
starlette False
pydantic True
uvicorn False
httpx True
pytest True
```

## Resolver Observation

Installing `fastapi` into the repo `.venv` resolved:

```text
fastapi==0.139.0
starlette==1.3.1
annotated-doc==0.0.4
```

Already present in the repo `.venv` and needed by the stack:

```text
pydantic==2.13.4
httpx==0.28.1
anyio==4.14.0
typing-inspection==0.4.2
typing_extensions==4.15.0
```

## Boundary Discovery

- `docs/architecture/operator_dashboard_agent_inbox_architecture_lock.md` selects FastAPI as the future local-first read-only dashboard backend direction.
- The same lock keeps dashboard implementation, Agent Inbox, hosting, auth, monitoring, scheduler, provider/exchange contact, runtime, paper/live, OMS, reconciliation, risk, and protected paths out of scope.
- `docs/dashboard/README.md` describes the existing static dashboard and does not create API-server authority.

## Inference

The active package explicitly authorizes a narrow dependency/config decision. Repo truth supports adding direct dependency declarations in `requirements.txt` plus matching pinned rows in `requirements.lock.txt`, provided no API implementation or protected runtime path is touched.

## Open Question

The repo lockfile is not a clean full freeze of the current local `.venv`; the `.venv` contains unrelated prior-pilot packages. Therefore, the lockfile was not regenerated wholesale from local `pip freeze`.
