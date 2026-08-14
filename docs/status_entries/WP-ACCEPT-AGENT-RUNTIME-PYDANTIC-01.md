# WP-ACCEPT-AGENT-RUNTIME-PYDANTIC-01

## Package State

- Branch: `codex/wp-accept-agent-runtime-pydantic-01`
- Base: `6994e9000aa6dcf56a7f1a4a08712ba778ea8bbe`
- Implementation commit: `dd95f343e7a3be9a3718524a17fdfcf8611945ee`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/698
- Package class: T2 bounded research-agent contract/runtime integration
- Result: PASS; non-draft and ready for review

## Scope Summary

Pydantic AI is integrated as an offline-only implementation of the existing
repo-owned `ReasoningProvider` seam. It is not a second agent architecture,
ToolContext, truth store, authority system, promotion system, or trading
runtime.

The adapter exposes zero project tools to Pydantic. It accepts only injected
Pydantic `TestModel` or `FunctionModel` instances. All repository reads and
writes remain in the existing `IdeaFormalizerAgent` and continue through the
existing `ToolContext` permission/audit boundary.

## Dependency and Integration Seam

- Direct package: `pydantic-ai-slim==2.30.0` in `requirements.lock.txt`.
- Direct requirement name: `pydantic-ai-slim` in `requirements.txt`.
- Adapter: `PydanticReasoningProvider(BaseProvider)` behind the existing
  `ReasoningProvider` protocol.
- Existing response contract: additive `run_metadata` and `provenance` fields
  on `ProviderResponse`; existing providers default both fields to `None`.
- Typed output: `PydanticProviderPayload` mirrors the existing
  `agent_idea_draft_v1` schema and is revalidated by the existing
  `BaseProvider.parse_response` path.
- Tool surface: zero Pydantic function tools; the Pydantic output tool is typed.
- Provider status: offline/test only; external provider calls are not
  implemented or enabled.

The narrow compatible lock addition preserves all prior pins and adds only:

- `pydantic-ai-slim==2.30.0`
- `pydantic-graph==2.30.0`
- `genai-prices==0.1.2`
- `griffelib==2.1.0`
- `httpx2==2.3.0`
- `httpcore2==2.3.0`
- `logfire-api==4.40.0`
- `opentelemetry-api==1.44.0`
- `truststore==0.10.4`

## Run Metadata, Provenance, and Instrumentation

Every completed Pydantic response records:

- exact provider and model identity from the selected injected model;
- `CHEAP`, `STANDARD`, or `FRONTIER` reasoning tier;
- exact tier reasoning configuration;
- `pydantic-ai-slim` runtime distribution and installed version;
- adapter version and usage counters;
- explicit offline-only, no-provider-API-call, and zero-project-tool facts;
- SHA-256 identities for canonicalized request context and response payload;
- the existing ToolContext boundary name and a non-authority statement.

`ProviderTraceSink` is the local instrumentation seam. The focused harness
uses `MemoryProviderTraceSink` and proves `started`, `completed`, `timed_out`,
`cancelled`, `blocked`, and `invalid_output` outcomes without requiring an OTel
Collector, Grafana, or backend. P3 may adapt the protocol to OTel later without
changing this package's authority model.

## Acceptance Matrix

| Requirement | Evidence | Result |
| --- | --- | --- |
| Existing provider seam, no duplicate architecture | `PydanticReasoningProvider(BaseProvider)` plus end-to-end `IdeaFormalizerAgent` test | PASS |
| Typed outputs and fail-closed malformed output | Three tier runs validate `PydanticProviderPayload`; extra authority field is rejected | PASS |
| Existing ToolContext remains the project-action gate | Pydantic function-tool list is empty; real formalizer reads/writes are ToolContext-audited | PASS |
| CHEAP / STANDARD / FRONTIER | Exact three-profile catalog and parameterized acceptance runs | PASS |
| Exact runtime/model/config metadata | Provider, model, tier config, adapter, runtime distribution/version, usage assertions | PASS |
| Timeout and cancellation | Slow injected `FunctionModel` is cancelled on timeout and caller cancellation | PASS |
| Provenance | Request/response SHA-256, source, ToolContext boundary, non-authority metadata | PASS |
| Local instrumentation seam | `ProviderTraceSink` and deterministic memory sink outcome assertions | PASS |
| No authority leakage | 21 adversarial ToolContext attempts fail before their operation runs and emit blocked audits | PASS |
| Existing non-Pydantic compatibility | Existing provider/formalizer and all directly affected research-agent tests pass | PASS |
| Provider connectivity default-safe | Non-test/function model factory is rejected before any model request | PASS |

## No-Authority-Leakage Evidence

The focused acceptance harness uses the real `ToolContext`, not a replacement or
mock, and proves the operation callback never runs for:

- canonical write;
- candidate registration and promotion;
- dispatch-authorization and KDAUTH contact;
- `docs/project_status.md` mutation;
- runtime, paper, and live control;
- OMS, risk, reconciliation, and safe-mode access;
- exchange, order, capital, and credential access;
- network and provider API calls;
- direct ToolContext bypass;
- protected runtime-path scratch write.

Every attempt produces one deterministic blocked audit record. The Pydantic
model receives no project function tools, so there is no direct project-action
bypass around this boundary.

## Changed Files

- `requirements.txt`
- `requirements.lock.txt`
- `tools/research_agents/reasoning_providers.py`
- `tools/research_agents/pydantic_reasoning_provider.py`
- `tools/research_agents/idea_formalizer_agent.py`
- `tools/research_agents/__init__.py`
- `tests/test_agent_pydantic_reasoning_provider.py`
- `docs/status_entries/WP-ACCEPT-AGENT-RUNTIME-PYDANTIC-01.md`

## Validation

- `python -m pytest tests/test_agent_pydantic_reasoning_provider.py tests/test_agent_toolcontext_sandbox.py tests/test_agent_idea_formalizer.py -q`:
  PASS, 141 passed.
- `python -m pytest tests/test_agent_formalizer_runner_bridge.py tests/test_agent_donchian_adapter.py tests/test_agent_experiment_runner.py tests/test_agent_robustness_diagnostician.py tests/test_agent_candidate_review_packet.py tests/test_agent_canonical_crossing_build.py -q`:
  PASS, 243 passed.
- `python -m pytest tests/test_validate_strategy_specs.py tests/test_validate_result_populations.py -q`:
  PASS, 173 passed with two existing `jsonschema.RefResolver` deprecation warnings.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- Fresh Python 3.11 install from `requirements.lock.txt`: PASS, all 43 pins
  installed, `pip check` clean, `pydantic-ai-slim==2.30.0` import confirmed.
- Ruff check and format check on the new adapter/harness: PASS.
- `python -m compileall -q tools/research_agents tests/test_agent_pydantic_reasoning_provider.py`:
  PASS.
- `git diff --check`: PASS.
- `tools/dev/diff_scope_summary.py`: PASS for the exact intended file set;
  `requirements.txt` and `requirements.lock.txt` are the only forbidden-pattern
  matches and are explicitly authorized dependency-update scope in this WP.
- Full pytest: not run by design; the active package requires focused T2
  validation and says not to run the full suite by default unless the changes
  cross a broader surface.

## Boundary Summary

No canonical artifact, candidate lifecycle/promotion, dispatch/KDAUTH, H004/M1,
Hermes, runtime, paper/live, OMS, risk, reconciliation, safe-mode, exchange,
order, capital, credential, protected-path, config, schema, validator,
query-layer, data, `lib/`, `src/`, or `docs/project_status.md` file changed.

`network_access`, `provider_api_call`, and all other hard prohibitions in
`tools/agent_sandbox/permissions.py` are unchanged. A future real provider call
would require a separate explicit network/credential/provider-authority
decision; this package creates no such activation path.

## Requirement Traceability and Runway

All ten active acceptance criteria are satisfied by the matrix above. The PR is
non-draft, mergeable, and GitHub reported merge state `CLEAN` at final package
inspection. No OpenAI Agents SDK fallback evaluation is indicated because the
Pydantic adapter passed.

This package creates no canonical, evidence, candidate-lifecycle, promotion,
dispatch, execution, runtime, OMS, risk, reconciliation, exchange, order,
capital, credential, provider-network, or downstream automation authority.
