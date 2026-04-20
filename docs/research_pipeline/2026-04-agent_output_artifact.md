# Agent Output Artifacts

## Purpose

`agent_output` artifacts record bounded advisory outputs from deterministic
research agents. WP-7a introduces the first family for Regime/Scoring so the
repo can validate, query, and review an advisory-agent output without changing
execution behavior.

The artifact is JSON-first and validates against:

```text
research/schemas/agent_output.schema.json
```

## Directory / Naming Convention

Instances live under:

```text
research/agent_outputs/
```

Future instances use:

```text
AOUT-NNNN.agent_output.json
```

WP-7a creates the first instance:

```text
research/agent_outputs/AOUT-0001.agent_output.json
```

## Schema Summary

The schema records:

- `agent_output_id`: stable `AOUT-NNNN` identifier.
- `agent_type`: bounded advisory family; WP-7a permits only
  `REGIME_SCORING`.
- `generated_at`: deterministic generation timestamp from committed input.
- `input_data_refs`: repo-relative input paths with SHA256 hashes.
- `as_of_timestamp`: latest market observation represented by the output.
- `setup_score`: bounded score from 0 to 100.
- `confidence`: bounded confidence from 0 to 1.
- `scoring_method`: deterministic method ID and normalized components.
- `rationale_summary`: human-readable explanation.
- `deterministic`: required to be true.
- `notes`: boundary notes.

## Validator Command

```powershell
.venv\Scripts\python.exe -m tools.registry.validate_agent_outputs
```

The validator exits successfully when `research/agent_outputs/` is missing or
empty. When files exist, it validates schema shape, duplicate IDs, filename
conventions, repo-relative input references, input existence, and SHA256
matches.

## Deterministic Boundary

WP-7a uses a tiny committed fixture:

```text
tests/fixtures/regime_scoring_market_fixture.json
```

The ignored local `data/processed/*` parquet and csv files are not used as
source-of-truth for the committed output. This correction keeps the first
agent-output instance reproducible from committed repo contents alone.

## No Execution Influence

Agent outputs are advisory research artifacts only. They do not alter overlay
rules, risk caps, OMS state, order routing, paper runtime behavior, position
sizing, kill-switch behavior, candidate status, or promotion state.

## Out Of Scope In WP-7a

- No LLM call.
- No network or live external input.
- No Score Bucket Mapper.
- No macro, news, or narrative input.
- No candidate registration or promotion.
- No execution, OMS, overlay, risk, or order-sizing wiring.
- No modification to existing research artifacts.
