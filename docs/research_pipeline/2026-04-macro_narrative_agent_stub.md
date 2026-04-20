# Macro/Narrative Agent Stub

## Why This Package Is Next

WP-7a proved the first deterministic advisory agent lane for Regime/Scoring.
WP-7f proves a second Z2 support lane for human-authored macro/narrative
context while keeping the output candidate-agnostic, deterministic, and outside
execution paths.

## Why A Committed Fixture Was Chosen

The first macro/narrative input is a committed synthetic fixture:

```text
tests/fixtures/macro_narrative_input_fixture.json
```

This keeps the first output reproducible from repo contents alone. It avoids
runtime config, environment variables, manual prompts, live feeds, and ignored
local files.

## Why A Parallel Schema Family Was Chosen

The existing WP-7a `agent_output` schema is intentionally specialized to
Regime/Scoring semantics such as setup score, confidence, and scoring method
components. WP-7f adds a dedicated macro-window family instead of widening that
schema and coupling unrelated advisory lanes.

## Frozen Boolean Derivation Rule

`tools/agents/macro_narrative_stub.py` applies one deterministic rule:

```text
macro_window_flag = bool(fixture["macro_event_window_active"])
```

The first fixture sets `macro_event_window_active` to true, so `MOUT-0001`
records `macro_window_flag` as true.

## Why Live Human-Input Plumbing Is Deferred

Live/manual human-input plumbing would introduce operator workflow, timing,
authorship, provenance, and runtime boundary decisions. WP-7f intentionally
proves only the artifact family, deterministic derivation, validation, and
read-only query exposure.

## Candidate-Agnostic And Advisory-Only Boundary

The stub does not reference a candidate, strategy, H-011, position, sizing
rule, overlay bucket, OMS instruction, risk rule, or execution policy. Its
output is stored only under `research/macro_window_agent_outputs/` and exposed
through the read-only query layer.
