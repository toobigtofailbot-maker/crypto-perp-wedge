# WP-INBOX-ASGI-SERVER-DEPS-00 Branch State

## Scope

Enables local startup of the existing isolated Agent Inbox intake service by adding minimal `uvicorn` to the repo dependency surfaces. `WP-INBOX-LOCAL-RUNBOOK-01` had correctly stopped because FastAPI was declared but no ASGI server was available.

## Delivered change

- `requirements.txt` adds unpinned direct dependency `uvicorn`, matching repo convention.
- `requirements.lock.txt` adds `uvicorn==0.51.0` and required resolver rows `click==8.4.2` and `colorama==0.4.6`; existing `h11==0.16.0` is reused.
- Dependency discovery and live socket evidence are recorded under `scratch/WP-INBOX-ASGI-SERVER-DEPS-00/`.

The validated start command is:

```powershell
.\.venv\Scripts\python.exe -m uvicorn tools.agent_inbox_intake.app:app --host 127.0.0.1 --port 8765
```

OpenAPI and docs returned HTTP 200. A valid request returned `AIDRAFT-45754E9CE36DE17F`; an invalid ETHUSDT request remained rejected with HTTP 400. The created validation packet and server process were cleaned up.

## Boundary

Dependency enablement only. No runbook, UI, CORS, service behavior, canonicalization, candidate, queue, runner, bridge, gates, pipeline, scheduler, notification, hosted deployment/auth, provider/exchange, runtime, OMS, reconciliation, risk, safe-mode, credential, or paper/live functionality is added. `WP-INBOX-LOCAL-RUNBOOK-01` may now be rerun as a separate package.
