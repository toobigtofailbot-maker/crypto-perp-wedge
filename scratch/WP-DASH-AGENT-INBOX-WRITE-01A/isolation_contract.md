# WP-DASH-AGENT-INBOX-WRITE-01A Isolation Contract

The Agent Inbox intake service is isolated at `tools.agent_inbox_intake`.

Allowed behavior:

- accept one bounded intake request;
- use the existing idea formalizer in fake-offline packet-only mode;
- write one noncanonical draft packet under `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`;
- include ToolContext audit records and non-authority flags in the packet.

Disallowed behavior:

- no `tools.operator_dashboard_api` mutation or dependency;
- no frontend mutation;
- no canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population, trial log, candidate registry, or candidate lifecycle write;
- no bridge, runner, gates, pipeline, robustness, candidate-review, crossing, approval, promotion, scheduler, notification, runtime, paper/live, provider, broker, exchange, credential, OMS, risk, reconciliation, safe-mode, or protected-path contact.

Formalizer handling:

- the service uses `IdeaFormalizerAgent` with `FakeOfflineProvider`;
- normal formalizer file writes are captured in memory for packet construction;
- normal formalizer Strategy Spec emission is disabled in the package-local wrapper;
- the persisted service output is the Agent Inbox draft packet only.

The draft packet is review material only. It is not evidence, authority, approval, recommendation, ranking, readiness, promotion, or execution input.
