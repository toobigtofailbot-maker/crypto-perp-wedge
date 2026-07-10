# WP-DASH-AGENT-INBOX-WRITE-01A Repo Truth Discovery

Base branch: `main`

Base SHA: `b01d15e616cd56a849c0483275ed195464abc759`

Working branch: `codex/wp-dash-agent-inbox-write-01a`

## Preflight Facts

- `WP-DASH-PANELS-04` is merged in refreshed `main`.
- Local branch was created from refreshed `main`.
- `git branch --list codex/wp-dash-agent-inbox-write-01a`: no collision before creation.
- `git ls-remote --heads origin codex/wp-dash-agent-inbox-write-01a`: no remote branch before creation.
- `gh pr list --state open --limit 100 --json number,title,headRefName,baseRefName,files,url`: returned `[]`; no open Agent Inbox write path PR or dashboard API PR was found.

## Dashboard API Boundary

Inspected:

- `tools/operator_dashboard_api/app.py`
- `tools/operator_dashboard_api/readers.py`
- `tools/operator_dashboard_api/models.py`
- `tools/operator_dashboard_api/README.md`
- `tests/test_operator_dashboard_api.py`

Current API routes are all `GET`:

- `/api/dashboard/summary`
- `/api/research/jobs`
- `/api/research/result-populations`
- `/api/research/result-populations/{id}`
- `/api/strategies`
- `/api/strategies/{id}`
- `/api/candidates/funnel`
- `/api/reports/daily`
- `/api/reports/weekly`
- `/api/system/data-health`
- `/api/agent/intake-schema`

Read-only assertion is explicit in README and tests. `POST /api/agent/intake-draft` is intentionally absent from `tools.operator_dashboard_api`.

Decision: the Agent Inbox intake write service must live outside `tools/operator_dashboard_api`.

## Existing Agent Inbox Placeholder

Inspected:

- `operator_dashboard_frontend/src/app/agent-inbox/page.tsx`
- `operator_dashboard_frontend/src/lib/fixtures/agent_intake_schema.json`
- `operator_dashboard_frontend/src/lib/apiClient.ts`
- `operator_dashboard_frontend/README.md`

Frontend currently displays a read-only schema preview and says `/api/agent/intake-draft` is intentionally not implemented. This package does not modify frontend files.

## Formalizer / Fake-Offline Path

Inspected:

- `tools/research_agents/idea_formalizer_agent.py`
- `tools/research_agents/reasoning_providers.py`
- `tests/test_agent_idea_formalizer.py`

Repo truth:

- `IdeaFormalizerAgent` supports provider mode `fake_offline`.
- `FakeOfflineProvider` is deterministic and makes no network or credential call.
- Formalizer writes are routed through `ToolContext`.
- Formalizer reads indicator and availability catalogs under `research/`.
- The normal formalizer can emit scratch draft Strategy Spec files for supported primitive families.

Answer: the formalizer can be safely invoked for draft-only Agent Inbox output only through a package-local packet-only wrapper that:

- uses `IdeaFormalizerAgent` and `FakeOfflineProvider`;
- uses `ToolContext(wp_id="WP-DASH-AGENT-INBOX-WRITE-01A", role="idea_formalizer")`;
- captures formalizer write attempts in memory;
- disables formalizer Strategy Spec emission by making every primitive family unsupported for spec production;
- persists only the Agent Inbox draft packet.

## ToolContext / Scratch Pattern

Inspected:

- `tools/agent_sandbox/__init__.py`
- `tools/agent_sandbox/tool_context.py`
- `tools/agent_sandbox/permissions.py`
- `tools/agent_sandbox/audit.py`

Repo truth:

- `idea_formalizer` allows `READ_NON_SECRET`, `WRITE_SCRATCH`, and `RUN_READ_ONLY_VALIDATION`.
- `WRITE_SCRATCH` is limited to `scratch/<wp_id>/`.
- canonical write prefixes under `research/strategy_specs`, `research/variant_manifests`, `research/sweep_plans`, and `research/result_populations` are hard blocked.
- candidate registry, dependency paths, protected paths, network/provider/credential actions, runtime/paper/live/order/risk/OMS/reconciliation actions, promotion/freezing/registration, backtest/sweep execution, and evidence suppression/deletion actions are hard blocked.

Safe scratch root for this package:

- `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/`

Persisted draft root:

- `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`

## Approval / Prereg / Bridge / Runner Boundaries

Inspected by targeted search and tests:

- `tools/research_agents/formalizer_runner_bridge.py`
- `tools/research_runner/run_offline_sweep.py`
- `tools/lab_pipeline/runner_adapter.py`
- `tools/lab_pipeline/bridge_adapter.py`
- `tools/lab_pipeline/gates_adapter.py`
- `tools/candidate_lifecycle/canonical_crossing_build.py`
- `tests/test_agent_formalizer_runner_bridge.py`
- `tests/test_lab_pipeline_runner_adapter.py`
- `tests/test_lab_pipeline_bridge_adapter.py`
- `tests/test_lab_pipeline_gates_adapter.py`

The new service imports none of these modules and does not invoke their action types.

## Safest Namespace

Chosen namespace:

- `tools/agent_inbox_intake`

Reason: it is separate from `tools/operator_dashboard_api`, package-local, and names the isolated Agent Inbox write path directly.

## Forbidden Imports / Modules

The new service must not import:

- `tools.operator_dashboard_api`
- `operator_dashboard_frontend`
- `tools.research_runner.*`
- `tools.research_agents.formalizer_runner_bridge`
- `tools.lab_pipeline.runner_adapter`
- `tools.lab_pipeline.bridge_adapter`
- `tools.lab_pipeline.gates_adapter`
- `tools.candidate_lifecycle.*`
- `src.*`
- `lib.*`
- `configs.*`
- provider/network/credential modules such as `requests`, `urllib`, or `socket`

## Tests Proving Isolation

Implemented in `tests/test_agent_inbox_intake.py`:

- valid intake produces one scratch draft packet;
- invalid empty/unbounded input fails closed;
- output root must remain package scratch;
- audit contains no forbidden authorized action;
- no forbidden runner/bridge/gates/candidate modules are imported during intake;
- execution/promotion smuggling is rejected and remains non-authoritative;
- isolated FastAPI app owns `POST /api/agent/intake-draft`;
- dashboard API remains GET-only and does not contain the intake draft route;
- service source does not import forbidden execution surfaces.
