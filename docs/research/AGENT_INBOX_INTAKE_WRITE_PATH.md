# Agent Inbox Intake Write Path

`tools.agent_inbox_intake` is the isolated scratch-only Agent Inbox intake draft service.

It exposes `POST /api/agent/intake-draft` from its own FastAPI app. This route is not added to `tools.operator_dashboard_api`, which remains read-only and GET-only.

The service accepts a bounded title, hypothesis text, BTCUSDT market hint, locked timeframe hint, optional notes, submitter label, and client draft id. It uses the existing idea formalizer in fake-offline packet-only mode, then writes one draft packet under:

```text
scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/
```

The packet is noncanonical review material only. It does not create Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, candidates, approvals, promotions, runner jobs, pipeline runs, notifications, scheduler behavior, paper/live behavior, runtime contact, provider/API contact, or protected-path authority.

Sample request:

```text
scratch/WP-DASH-AGENT-INBOX-WRITE-01A/sample_intake_request.json
```

Sample packet:

```text
scratch/WP-DASH-AGENT-INBOX-WRITE-01A/sample_draft_packet.json
```

Focused validation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_agent_inbox_intake.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_operator_dashboard_api.py -q
```
