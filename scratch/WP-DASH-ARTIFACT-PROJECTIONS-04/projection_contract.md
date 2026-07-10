# Read-only artifact projection contract

Route:
`GET /api/research/result-populations/{id}/artifact-projections`

The route inventories eight artifact classes for one committed Result Population. It
returns real projections only when a committed source is directly linked by Result
Population id or by an exact strategy-spec / variant-manifest / sweep-plan lineage match.

Each projected item includes:

- `artifact_kind`, `data_available`, `source_path`, `source_sha256`, and `source_field`;
- `row_count`, `fold_count`, `path_count`, and `sample_count` where applicable;
- an explicit `linkage` description;
- `data` copied from the named source field without zero filling, interpolation, replay,
  or runner execution.

Each unavailable inventory item includes `data_available: false`, null source metadata,
zero factual path/row/fold counts, and both `withheld_reason` and `unavailable_reason`.
Unavailable inventory items contain no `data` member and therefore provide no empty
chart-friendly stand-in.

The current real projections are:

- all committed `variant_result_rows` arrays as summarized trade diagnostics;
- two committed WFO `fold_results` arrays linked to `RP-2592` by exact lineage;
- the committed seeded Monte Carlo `bootstrap_ci` mapping linked directly to `RP-2592`.

The Monte Carlo projection is deliberately named a robustness **summary**. Raw bootstrap
samples are not committed and remain unavailable even though the report records their
count and checksum.

The route is API projection only. Repo artifacts remain truth. It adds no mutation route,
runner replay, canonical write, validator/schema change, selection, ranking, gate,
promotion, readiness, runtime, paper/live, broker, exchange, OMS, risk, reconciliation,
safe-mode, scheduler, or notification authority.
