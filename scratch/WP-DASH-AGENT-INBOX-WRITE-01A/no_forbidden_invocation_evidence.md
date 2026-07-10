# No Forbidden Invocation Evidence

Evidence source:

- `tests/test_agent_inbox_intake.py`
- `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/sample_draft_packet.json`

Assertions implemented:

- no `tools.operator_dashboard_api` import in the intake service;
- no `tools.research_runner.run_offline_sweep` import during intake;
- no `tools.research_agents.formalizer_runner_bridge` import during intake;
- no `tools.lab_pipeline.runner_adapter`, `bridge_adapter`, or `gates_adapter` import during intake;
- no `tools.candidate_lifecycle.canonical_crossing_build` import during intake;
- allowed ToolContext actions are limited to `read_non_secret_files` and `write_scratch`;
- allowed ToolContext targets do not start with canonical artifact, candidate, runner, pipeline, dashboard API, `src/`, `lib/`, `configs/`, or `data/` prefixes;
- execution/promotion/gate-bypass language is rejected by the formalizer boundary scanner and recorded as blocked in the draft packet;
- dashboard API route inspection remains GET-only and does not include `/api/agent/intake-draft`.

Sample packet audit summary:

- read: `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- read: `research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`
- captured scratch write authorization: formalized idea path under package scratch
- captured scratch write authorization: human review packet path under package scratch
- persisted write: one Agent Inbox draft packet under `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`

No canonical, candidate, runner, bridge, gates, pipeline, runtime, paper/live, provider, credential, scheduler, or notification action is invoked.
