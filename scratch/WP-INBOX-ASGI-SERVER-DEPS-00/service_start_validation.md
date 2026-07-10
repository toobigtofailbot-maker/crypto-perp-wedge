# WP-INBOX-ASGI-SERVER-DEPS-00 Service Start Validation

## Start command

Validated from the repo root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn tools.agent_inbox_intake.app:app --host 127.0.0.1 --port 8765
```

Uvicorn started successfully with the minimal dependency set and reported application startup complete.

## HTTP validation

- `GET /openapi.json` returned HTTP 200.
- `GET /docs` returned HTTP 200.
- A bounded valid `POST /api/agent/intake-draft` returned `AIDRAFT-45754E9CE36DE17F`.
- The returned packet asserted `scratch_only=true` and `not_execution=true`.
- An invalid request using `market_hint=ETHUSDT` returned HTTP 400 with `market_hint must remain bounded to BTCUSDT`.

The valid request created only:

```text
scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/AIDRAFT-45754E9CE36DE17F.draft_packet.json
```

That validation packet was removed. Draft packet count was 1 before validation, 2 immediately after the valid request, and 1 after cleanup. The Uvicorn process was stopped and its temporary stdout/stderr files were removed.

## Boundary result

The service remained authoritative, wrote only its existing noncanonical scratch packet, and required no application, dashboard, canonicalization, queue, runner, runtime, or paper/live modification.
