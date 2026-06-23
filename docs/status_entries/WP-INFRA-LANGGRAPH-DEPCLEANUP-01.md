# WP-INFRA-LANGGRAPH-DEPCLEANUP-01 Branch State

## Scope Summary

Removes deferred LangGraph pilot dependency weight from the main tree after
`WP-AGENT-LANGGRAPH-PILOT-01` recorded a defer finding and PR #552 was merged
into local `main`.

## Main Authorization

Main authorized cleanup so the deferred pilot does not leave LangGraph,
LangChain, or LangSmith dependency weight in the active repo dependency files.

## Repo-Truth Discovery

Discovery is recorded in
`scratch/WP-INFRA-LANGGRAPH-DEPCLEANUP-01/repo_truth_discovery.md`.

Current repo truth showed one direct `langgraph` dependency, LangGraph/
LangChain/LangSmith resolver entries in `requirements.lock.txt`, one source
import in `tools/research_agents/langgraph_pilot.py`, one focused pilot test,
one package export, and one ToolContext role/action specific to the pilot. No
non-pilot source or test usage was found.

## Dependency Cleanup

`requirements.txt` no longer lists `langgraph`. `requirements.lock.txt` was
restored to the pre-pilot lockfile byte state, removing the LangGraph,
LangChain, LangSmith, and resolver-only transitive dependency entries added by
the deferred pilot while preserving the repo's existing UTF-16 LE lock format.

## Pilot Evidence Preservation

Historical pilot evidence is preserved:

- `docs/status_entries/WP-AGENT-LANGGRAPH-PILOT-01.md`
- `scratch/WP-AGENT-LANGGRAPH-PILOT-01/*`

These files remain historical, non-authoritative evidence of the pilot and its
defer finding.

## Runtime Harness Disposition

The runtime scratch harness `tools/research_agents/langgraph_pilot.py` was
removed because retaining it would require the direct LangGraph dependency in
the main dependency tree. The package export was removed from
`tools/research_agents/__init__.py`.

## ToolContext Cleanup

The pilot-only ToolContext action `run_scratch_langgraph_pilot` and role
`langgraph_pilot_orchestrator` were removed from
`tools/agent_sandbox/permissions.py`. The ToolContext sandbox role taxonomy
test was updated accordingly. Existing non-pilot ToolContext roles and hard
prohibitions remain in place.

## Behavior Preservation

This package does not change idea formalizer, formalizer-runner bridge,
robustness diagnostician, candidate-review packet, canonical crossing,
registry, query, compiler, backtest, runner, runtime, paper/live, OMS, risk,
reconciliation, or capital behavior.

## Validation Status

- Agent regression tests:
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_agent_idea_formalizer.py tests/test_agent_formalizer_runner_bridge.py tests/test_agent_robustness_diagnostician.py tests/test_agent_candidate_review_packet.py tests/test_agent_canonical_crossing_build.py tests/test_agent_toolcontext_sandbox.py -q`
  passed, 247 tests.
- Registry validator tests:
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_validate_candidate_registry.py tests/test_validate_result_populations.py tests/test_validate_data_feature_availability.py -q`
  passed, 88 tests.
- Registry validators:
  `validate_candidate_registry`, `validate_result_populations`, and
  `validate_data_feature_availability` passed.
- Query view listing:
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`
  passed and listed 124 views.
- Dependency search:
  `Select-String -Path requirements*.txt,pyproject.toml,*lock*,*.lock -Pattern "langgraph|langchain|langsmith" -CaseSensitive:$false`
  returned no matches.
- Diff scope summary:
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`
  passed with only authorized dependency-file forbidden-pattern matches.
- `git diff --check`: passed.
- Full pytest:
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`
  timed out after 15 minutes with no emitted failure details; not passing
  evidence.

## Boundary Summary

No formalizer behavior, bridge behavior, robustness diagnostician behavior,
candidate-review packet behavior, canonical crossing behavior, canonical
schema, canonical artifact, paper/live/runtime path, OMS, risk,
reconciliation, capital, private endpoint, credential, provider/API/network
dependency, orchestration replacement, scheduler, Hermes, or reporting
implementation was changed.

## Non-Authority Statement

This cleanup creates no execution, evidence, candidate lifecycle, ranking,
promotion, readiness, paper/live, runtime, trading-signal, capital,
broker/exchange, OMS, reconciliation, risk, provider/API, network, scheduler,
or downstream automation authority. Preserved pilot artifacts remain historical
scratch evidence only.
