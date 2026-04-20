# Macro Window Agent Output Artifacts

## Purpose

`macro_window_agent_output` artifacts record bounded macro-window advisory
outputs from the first Macro/Narrative support-layer stub. WP-7f introduces
this as a parallel family so macro/narrative context can be validated, queried,
and reviewed without widening the Regime/Scoring `agent_output` schema.

The artifact is JSON-first and validates against:

```text
research/schemas/macro_window_agent_output.schema.json
```

## Directory / Naming Convention

Instances live under:

```text
research/macro_window_agent_outputs/
```

Future instances use:

```text
MOUT-NNNN.macro_window_agent_output.json
```

WP-7f creates exactly one instance:

```text
research/macro_window_agent_outputs/MOUT-0001.macro_window_agent_output.json
```

## Schema Summary

The schema records:

- `macro_window_agent_output_id`: stable `MOUT-NNNN` identifier.
- `generated_at`: deterministic generation timestamp copied from the fixture.
- `as_of_timestamp`: timestamp copied from the fixture.
- `source_fixture_path`: repo-relative committed fixture path.
- `source_fixture_sha256`: SHA256 hash of the committed fixture.
- `macro_window_flag`: boolean advisory flag.
- `event_class` and `event_name`: fixture-provided context labels.
- `deterministic`: required to be true.
- `advisory_only`: required to be true.
- `notes`: boundary notes.

## Validator Command

```powershell
.venv\Scripts\python.exe -m tools.registry.validate_macro_window_agent_outputs
```

The validator exits successfully when `research/macro_window_agent_outputs/` is
missing or empty. When files exist, it validates schema shape, duplicate IDs,
filename conventions, fixture path safety, fixture existence, fixture SHA256,
and consistency with the frozen fixture rule.

## Fixture-Backed Input

WP-7f uses exactly one committed synthetic input fixture:

```text
tests/fixtures/macro_narrative_input_fixture.json
```

The fixture is the sole source of truth for `MOUT-0001`. No live news, runtime
operator prompt, environment variable, external feed, or ignored local data file
is used.

## Advisory-Only Boundary

Macro-window outputs are advisory research artifacts only. They do not alter
overlay rules, risk caps, OMS state, order routing, paper runtime behavior,
position sizing, kill-switch behavior, candidate status, promotion state, or
policy decisions.

## Out Of Scope In WP-7f

- No widening of `agent_output.schema.json`.
- No Regime/Scoring agent changes.
- No LLM call.
- No network or live external input.
- No live/manual operator-input plumbing.
- No mapper, overlay, OMS, risk, sizing, runtime, or execution wiring.
- No candidate-specific logic.
