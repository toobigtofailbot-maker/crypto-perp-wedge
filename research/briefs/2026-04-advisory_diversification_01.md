# Advisory Diversification 01 Production Record

**Date:** 2026-04-22
**Package:** WP-7n
**Scope:** Second deterministic upstream advisory artifact set for additive advisory-input diversification.
**Does not introduce:** Production code changes, schema changes, validator changes, query-layer changes, helper changes, overlay-input diversification, shadow-log entries, scheduler infrastructure, or runtime wiring.
**Does not encode:** Policy inference, runtime influence, OMS influence, risk influence, sizing authority, or execution authority.

## 1. Purpose

This record documents the additive creation of a second deterministic advisory upstream artifact set so committed advisory state is no longer structurally constant at the mapper and `MACRO_AWARE_FLOOR` pre-gate surfaces.

This file is a production record only. It is not a diagnostic brief, not a policy recommendation, and not a runtime instruction.

## 2. Additive Fixtures Created

- `tests/fixtures/regime_scoring_market_fixture_02.json`
- `tests/fixtures/macro_narrative_input_fixture_02.json`

The regime fixture was selected to remain deterministic while producing a lower-stress score profile than `AOUT-0001`. The macro fixture was selected to remain deterministic while setting `macro_event_window_active = false`.

## 3. Production Commands Used

`AOUT-0002` used the approved execution-only fallback path because the committed `tools.agents.regime_scoring_stub` CLI does not expose an output-id argument.

```powershell
@'
from pathlib import Path
import json
from tools.agents import regime_scoring_stub as stub

fixture_path = Path("tests/fixtures/regime_scoring_market_fixture_02.json")
output_path = Path("research/agent_outputs/AOUT-0002.agent_output.json")
original_id = stub.AGENT_OUTPUT_ID

try:
    stub.AGENT_OUTPUT_ID = "AOUT-0002"
    payload = stub.build_agent_output(fixture_path=fixture_path)
finally:
    stub.AGENT_OUTPUT_ID = original_id

output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {output_path}")
'@ | .\.venv\Scripts\python.exe -
```

```powershell
.\.venv\Scripts\python.exe -m tools.agents.macro_narrative_stub --fixture tests\fixtures\macro_narrative_input_fixture_02.json --output research\macro_window_agent_outputs\MOUT-0002.macro_window_agent_output.json --macro-window-agent-output-id MOUT-0002
```

```powershell
.\.venv\Scripts\python.exe -m tools.mappers.score_bucket_mapper --source research\agent_outputs\AOUT-0002.agent_output.json --output research\bucket_mappings\BMAP-0002.bucket_mapping.json --bucket-mapping-id BMAP-0002
```

```powershell
.\.venv\Scripts\python.exe -m tools.support.build_pre_gate_advisory_snapshot --agent-output research\agent_outputs\AOUT-0002.agent_output.json --bucket-mapping research\bucket_mappings\BMAP-0002.bucket_mapping.json --macro-window-agent-output research\macro_window_agent_outputs\MOUT-0002.macro_window_agent_output.json --output research\pre_gate_advisory_snapshots\PGAS-0003.pre_gate_advisory_snapshot.json --pre-gate-advisory-snapshot-id PGAS-0003 --combination-rule-applied MACRO_AWARE_FLOOR
```

## 4. Produced Artifact Mapping

| Artifact | Source / outcome |
|---|---|
| `AOUT-0002` | Fixture-backed `REGIME_SCORING` advisory output from `tests/fixtures/regime_scoring_market_fixture_02.json` |
| `BMAP-0002` | Deterministic mapping of `AOUT-0002` |
| `MOUT-0002` | Fixture-backed macro-window advisory output from `tests/fixtures/macro_narrative_input_fixture_02.json` |
| `PGAS-0003` | `MACRO_AWARE_FLOOR` snapshot over `AOUT-0002`, `BMAP-0002`, and `MOUT-0002` |

Exact outcome chain:

- `AOUT-0002.setup_score = 95.31`
- `AOUT-0002.confidence = 0.978`
- `BMAP-0002.mapped_bucket = ALLOW`
- `MOUT-0002.macro_window_flag = false`
- `PGAS-0003.combined_bucket = ALLOW`

## 5. Preferred Target Result

The preferred target was achieved exactly:

- `BMAP-0002.mapped_bucket = ALLOW`
- `MOUT-0002.macro_window_flag = false`
- `PGAS-0003.combined_bucket = ALLOW`

This creates a second truthful committed advisory state that differs structurally from the existing `ALLOW_REDUCED` path and prepares the advisory corpus for later accumulation work.

## 6. Boundary Statement

This package added fixtures, artifacts, current-state test maintenance, and this production record only. It did not modify production code, schemas, validators, query-layer runtime code, helpers, runtime paths, overlay behavior, or policy state. It is preparatory advisory-side variety injection for later accumulation and is not a diagnostic brief.
