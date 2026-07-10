# Agent Inbox local runtime

## Purpose and boundary

This runbook starts the local operator dashboard and the separate isolated Agent
Inbox intake service. The dashboard UI is not sufficient by itself: the intake
service must be running, and `AGENT_INBOX_SERVICE_ORIGIN` must be present in the
dashboard process before that process starts.

The intake service writes one review-only, noncanonical packet per successful
submission under:

```text
scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/AIDRAFT-*.draft_packet.json
```

It does not create a Strategy Spec, Variant Manifest, Sweep Plan, Result
Population, candidate, queue entry, runner job, pipeline action, or runtime,
paper, or live action. Keep both services bound to the local machine.

The commands below deliberately use two operator-owned terminals rather than a
background launcher. Stop each service with `Ctrl+C`; terminal output is the
service log. No credentials are required or stored.

## Prerequisites

From the repository root:

- install the locked Python dependencies into `.venv`;
- install the dashboard dependencies in `operator_dashboard_frontend`;
- ensure ports `8765` and `3000` are available.

Windows PowerShell dependency setup:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
Push-Location operator_dashboard_frontend
npm install
Pop-Location
```

POSIX shell dependency setup:

```sh
./.venv/bin/python -m pip install -r requirements.lock.txt
(cd operator_dashboard_frontend && npm install)
```

## Start on Windows PowerShell

Open PowerShell terminal 1 at the repository root and start the isolated intake
service on `127.0.0.1:8765`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn tools.agent_inbox_intake.app:app --host 127.0.0.1 --port 8765
```

Open PowerShell terminal 2 at the same repository root. Set the server-only
origin in the dashboard process, then start Next.js on its existing development
port, `127.0.0.1:3000`:

```powershell
$env:AGENT_INBOX_SERVICE_ORIGIN = "http://127.0.0.1:8765"
npm --prefix operator_dashboard_frontend run dev -- --hostname 127.0.0.1 --port 3000
```

Open `http://127.0.0.1:3000/agent-inbox`.

## Start on POSIX shells

Open terminal 1 at the repository root:

```sh
./.venv/bin/python -m uvicorn tools.agent_inbox_intake.app:app --host 127.0.0.1 --port 8765
```

Open terminal 2 at the repository root:

```sh
AGENT_INBOX_SERVICE_ORIGIN=http://127.0.0.1:8765 \
  npm --prefix operator_dashboard_frontend run dev -- --hostname 127.0.0.1 --port 3000
```

Open `http://127.0.0.1:3000/agent-inbox`.

## Verify the local services

With the intake service running, these endpoints must return HTTP 200:

```powershell
Invoke-WebRequest http://127.0.0.1:8765/openapi.json -UseBasicParsing | Select-Object StatusCode
Invoke-WebRequest http://127.0.0.1:8765/docs -UseBasicParsing | Select-Object StatusCode
```

Equivalent POSIX checks:

```sh
curl --fail --silent --output /dev/null --write-out '%{http_code}\n' http://127.0.0.1:8765/openapi.json
curl --fail --silent --output /dev/null --write-out '%{http_code}\n' http://127.0.0.1:8765/docs
```

Verify the dashboard states independently:

1. **Unconfigured:** start the dashboard without
   `AGENT_INBOX_SERVICE_ORIGIN`. `/agent-inbox` shows `INTAKE SERVICE NOT
   CONFIGURED`, and submission is disabled. Stop that dashboard before the next
   check.
2. **Configured:** set the origin and restart the dashboard as documented. The
   unconfigured message is absent and the form is enabled.
3. **Unreachable:** leave the origin configured but stop the intake service.
   Submission reports that the isolated service could not be reached, and no
   packet is created.
4. **Successful:** restart the intake service, reload `/agent-inbox`, and submit
   the bounded sanity-check idea below. The page returns a real
   `AIDRAFT-<16 uppercase hex characters>` id; it must not display a fabricated
   replacement.

## Submit one bounded sanity-check idea

Enter:

```text
Title: Local Agent Inbox sanity check
Hypothesis: For BTCUSDT on 15m bars, test whether a simple price breakout condition can be represented as a bounded review-only draft; do not run research or create canonical artifacts.
Market: BTCUSDT
Timeframe: 15m
Constraints: Scratch packet only. No candidate, queue, runner, pipeline, paper, live, or runtime action.
Submitter: local-runbook-validation
```

Select **Create scratch draft**. Record the returned draft id, then confirm its
packet exists from the repository root:

```powershell
$draftId = "AIDRAFT-REPLACE_WITH_RETURNED_ID"
$packet = "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/$draftId.draft_packet.json"
Test-Path $packet
Get-Content $packet -Raw | ConvertFrom-Json | Select-Object draft_id, created_at, fabricated
```

The path check must be `True`, `draft_id` must match, and `fabricated` must be
`False`.

## Verify draft history

The history service reads only the scratch packets owned by the isolated intake
service:

```powershell
$history = Invoke-RestMethod http://127.0.0.1:8765/api/agent/drafts
$history | Select-Object status, count, storage_source, scratch_only
$history.drafts | Where-Object draft_id -eq $draftId
Invoke-RestMethod "http://127.0.0.1:8765/api/agent/drafts/$draftId" | Select-Object draft_id, created_at, fabricated
```

POSIX equivalent:

```sh
curl --fail http://127.0.0.1:8765/api/agent/drafts
curl --fail "http://127.0.0.1:8765/api/agent/drafts/$draftId"
```

The list must include the returned id and the detail response must match the
stored JSON packet.

## Clean up the validation packet

After recording the sanity-check result, remove only the exact packet created by
this validation. Do not remove the whole draft directory because it may contain
operator-owned scratch drafts.

PowerShell:

```powershell
Remove-Item -LiteralPath $packet
Test-Path -LiteralPath $packet
```

POSIX shell:

```sh
rm -- "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/$draftId.draft_packet.json"
test ! -e "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/$draftId.draft_packet.json"
```

The final check must show that the one validation packet no longer exists.

## Troubleshooting

- **Environment variable unset:** stop the dashboard, set
  `AGENT_INBOX_SERVICE_ORIGIN` in the same terminal that will start it, and
  restart. Setting it in a different shell does not update an existing process.
- **Service not running / unreachable:** confirm terminal 1 is still running and
  that `http://127.0.0.1:8765/openapi.json` returns 200. An unreachable submit
  returns HTTP 502 through the dashboard and creates no draft.
- **Wrong port:** the origin must exactly match the intake `--host` and `--port`.
  Do not point it at the dashboard or the read-only dashboard API.
- **Stale frontend process after an environment change:** stop Next.js with
  `Ctrl+C` and start it again. The origin is read by the dashboard server
  process, not entered in the browser.
- **Port already in use:** stop the stale process, or choose another local port
  and update both the intake `--port` and dashboard origin consistently. For the
  dashboard, change `--port` and open the matching URL.
- **Missing Python dependency:** run the locked dependency install above and
  verify `.\.venv\Scripts\python.exe -m uvicorn --version` (PowerShell) or
  `./.venv/bin/python -m uvicorn --version` (POSIX). Do not edit dependency files.
- **Dashboard build versus dev:** `npm run build` validates a production build;
  it does not start the dashboard. This runbook uses `npm run dev`. If using
  `npm run start` after a build, set `AGENT_INBOX_SERVICE_ORIGIN` in that start
  process and pass the desired hostname and port there as well.

## Stop

Press `Ctrl+C` once in each owning terminal. Confirm ports `8765` and `3000` are
no longer listening. The runbook starts no scheduler, detached process, or
background automation.
