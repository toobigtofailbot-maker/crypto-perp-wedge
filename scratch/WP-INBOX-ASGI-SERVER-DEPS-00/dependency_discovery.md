# WP-INBOX-ASGI-SERVER-DEPS-00 Dependency Discovery

## Repo truth

- Branch base: refreshed `main` / `origin/main` at `42cd688c2fc55a82adc03e4e8b0f1d592af2da6c`.
- `requirements.txt` is the direct dependency declaration surface.
- `requirements.lock.txt` is the pinned dependency surface and retains UTF-16 LE with CRLF line endings.
- `pyproject.toml` contains project metadata and Ruff configuration, not runtime dependencies.
- `fastapi` and `httpx` were already declared; no ASGI server was declared or importable in the repo `.venv`.
- Prior package evidence in `scratch/WP-DASH-API-DEPS-02A/dependency_decision.md` explicitly deferred `uvicorn` because that package did not authorize a server runner or local run command.
- No Hypercorn, Granian, Waitress, FastAPI CLI, or other preferred ASGI server standard was found.

## Dependency decision

Minimal `uvicorn` is the repo-consistent ASGI server dependency. `requirements.txt` declares unpinned direct dependencies, so it now adds plain `uvicorn`, not `uvicorn[standard]`. The resolver selected:

- `uvicorn==0.51.0`
- `click==8.4.2`
- `colorama==0.4.6` on Windows

The existing `h11==0.16.0` row already satisfies Uvicorn's remaining runtime requirement. A resolver dry run with `--ignore-installed` confirmed that no other transitive rows are required.

## Install path

The repo `.venv` was synchronized through the existing direct dependency surface:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No wholesale `pip freeze` was used because the repo lockfile is maintained as a narrow pinned surface and the local `.venv` contains unrelated package history.

## ASGI app discovery

`tools/agent_inbox_intake/app.py` exports the module-level `app = create_app()` object. The exact ASGI import path is therefore:

```text
tools.agent_inbox_intake.app:app
```

No service code change is required to start it.
