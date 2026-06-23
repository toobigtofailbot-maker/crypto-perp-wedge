# WP-INFRA-LANGGRAPH-DEPCLEANUP-01 Repo-Truth Discovery

## Scope

This discovery records the current merged repo truth after PR #552 was merged into
local `main` and before cleanup on branch `infra/langgraph-depcleanup-01`.

## Direct LangGraph Dependencies

- `requirements.txt` contained one direct LangGraph dependency: `langgraph`.
- `pyproject.toml` contains only project metadata and Ruff configuration; it had no
  LangGraph, LangChain, or LangSmith dependency.

## Resolver-Required LangGraph / LangChain Transitive Dependencies

`requirements.lock.txt` is UTF-16 LE and was last changed by
`WP-AGENT-LANGGRAPH-PILOT-01` for the LangGraph pilot. Relative to the pre-pilot
lockfile, the LangGraph pilot added:

- `annotated-types==0.7.0`
- `anyio==4.14.0`
- `h11==0.16.0`
- `httpcore==1.0.9`
- `httpx==0.28.1`
- `jsonpatch==1.33`
- `jsonpointer==3.1.1`
- `langchain-core==1.4.8`
- `langchain-protocol==0.0.18`
- `langgraph-checkpoint==4.1.1`
- `langgraph-prebuilt==1.1.0`
- `langgraph-sdk==0.4.2`
- `langgraph==1.2.6`
- `langsmith==0.9.0`
- `orjson==3.11.9`
- `ormsgpack==1.12.2`
- `packaging==26.0`
- `pydantic-core==2.46.4`
- `pydantic==2.13.4`
- `PyYAML==6.0.3`
- `requests-toolbelt==1.0.0`
- `tenacity==9.1.4`
- `typing-inspection==0.4.2`
- `uuid_utils==0.16.2`
- `websockets==15.0.1`
- `xxhash==3.7.0`
- `zstandard==0.25.0`

## Source Imports

- `tools/research_agents/langgraph_pilot.py` imported
  `from langgraph.graph import END, START, StateGraph`.
- `tools/research_agents/__init__.py` exported `LangGraphPilot`,
  `LangGraphPilotConfig`, and `ProhibitedActionProbe` from the pilot module.
- No non-pilot source file imported LangGraph, LangChain, or LangSmith packages.

## Tests

- `tests/test_agent_langgraph_pilot.py` depended on the pilot harness and imported
  `RUN_SCRATCH_LANGGRAPH_PILOT`, `LangGraphPilot`, `LangGraphPilotConfig`, and
  `ProhibitedActionProbe`.
- `tests/test_agent_toolcontext_sandbox.py` listed the pilot role in the
  repo-truth role taxonomy.
- No non-pilot test required LangGraph, LangChain, or LangSmith packages.

## ToolContext Role / Action

- `tools/agent_sandbox/permissions.py` defined pilot action
  `RUN_SCRATCH_LANGGRAPH_PILOT = "run_scratch_langgraph_pilot"`.
- The same file defined role `langgraph_pilot_orchestrator` with
  `READ_DOCS`, `READ_NON_SECRET`, `WRITE_SCRATCH`, and
  `RUN_SCRATCH_LANGGRAPH_PILOT`.
- The action was path-scoped to
  `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/`.

## Pilot Evidence Preservation

- Historical status evidence exists at
  `docs/status_entries/WP-AGENT-LANGGRAPH-PILOT-01.md`.
- Committed scratch evidence exists under `scratch/WP-AGENT-LANGGRAPH-PILOT-01/`,
  including `repo_truth_discovery.md` and output artifacts for run
  `85eaed766d4aa5a2`.
- The evidence can remain as historical non-authoritative docs/scratch evidence
  after removing the runtime harness and dependency weight.

## Non-Pilot Usage

- Repo search found only documentation/status references plus the pilot module,
  pilot test, package export, and ToolContext pilot role/action.
- No non-pilot code depends on LangGraph, LangChain, or LangSmith.

## Cleanup Decision

- Remove `langgraph` from `requirements.txt`.
- Restore `requirements.lock.txt` to the pre-pilot lockfile state to remove
  LangGraph/LangChain/LangSmith resolver weight while preserving the existing
  lockfile format.
- Delete the runtime pilot module and pilot test because retaining them would
  require the direct LangGraph dependency in the main tree.
- Remove the now-unused ToolContext pilot role/action and package exports.
- Preserve `docs/status_entries/WP-AGENT-LANGGRAPH-PILOT-01.md` and
  `scratch/WP-AGENT-LANGGRAPH-PILOT-01/*` as historical non-authoritative pilot
  evidence.
