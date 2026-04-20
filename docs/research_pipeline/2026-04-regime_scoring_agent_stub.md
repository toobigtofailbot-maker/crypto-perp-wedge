# Regime/Scoring Agent Stub

## Why Regime/Scoring Is First

Regime/Scoring is the narrowest useful first advisory agent family because its
output can be bounded to `setup_score` and `confidence`. That shape proves the
schema, validator, deterministic generation, and query-layer pattern without
introducing promotion authority or execution influence.

## Real Inputs Used From Repo Truth

Repo truth surfaced an important reproducibility constraint: processed parquet
and csv market-data files exist locally under `data/processed/`, but they are
ignored by git and therefore cannot be used as committed source-of-truth for the
first output instance.

WP-7a therefore uses exactly one tiny committed input fixture:

```text
tests/fixtures/regime_scoring_market_fixture.json
```

The fixture contains eight hourly observations with close price, funding rate,
and spread-bps proxy values. `AOUT-0001` records the fixture path and SHA256 so
the output can be regenerated and audited from committed contents alone.

## What The Stub Computes

`tools/agents/regime_scoring_stub.py` is a deterministic stdlib-only module. It
sorts fixture observations by timestamp, computes close-to-close returns, then
derives:

- realized volatility from population standard deviation of returns
- normalized volatility stress
- normalized mean absolute funding stress
- normalized mean spread-bps stress
- weighted stress score
- bounded `setup_score`
- bounded `confidence`

The first fixture-backed output is:

- `agent_output_id`: `AOUT-0001`
- `agent_type`: `REGIME_SCORING`
- `setup_score`: `72.95`
- `confidence`: `0.891`

## What It Does NOT Do

- It does not read ignored local processed market-data files.
- It does not call network APIs or external services.
- It does not call an LLM.
- It does not interpret news, narrative, or macro calendars.
- It does not create vetoes, multipliers, sizing outputs, or candidate
  recommendations.
- It does not touch execution, OMS, overlay, risk, or paper-runtime paths.

## Why It Remains Advisory-Only

The output is stored only as a research artifact under `research/agent_outputs/`
and exposed through the read-only query layer. No runtime path imports it, no
execution-facing file is written, and no decision or release artifact is
authored by this package.

## Future Score Bucket Mapper Preparation

The artifact shape gives a later Score Bucket Mapper a stable, schema-validated
input surface: `agent_type`, `setup_score`, `confidence`, deterministic method
metadata, and input provenance. WP-7a intentionally stops before building that
consumer layer.
