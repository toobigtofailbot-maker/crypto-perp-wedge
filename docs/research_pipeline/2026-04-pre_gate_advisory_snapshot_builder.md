# Pre-Gate Advisory Snapshot Builder

## Why These Packages Are Next

WP-7a proved the first deterministic Regime / Scoring advisory lane. WP-6j
proved the first deterministic bucket-mapping consumer of that lane. WP-7f
proved a parallel Macro / Narrative advisory lane. WP-7g is the narrow next
step because the repo now needs one shared read-only surface that can expose the
current advisory picture without deciding how those lanes should interact.
WP-7h then adds the narrow first deterministic rule for reviewing a combined
bucket while keeping all runtime boundaries closed.

## Historical Bundle-Only State

The repo does not yet contain an approved upstream policy for combining
Regime / Scoring and Macro / Narrative advisory inputs. The first builder
therefore stops at structural bundling: it assembles committed evidence into a
single snapshot and explicitly records that no combination rule has been
applied. `PGAS-0001` remains unchanged with
`combination_rule_applied = NONE_BUNDLE_ONLY`.

## MACRO_AWARE_FLOOR v1

WP-7h adds `MACRO_AWARE_FLOOR`, the first non-NONE pre-gate advisory
combination rule. It consumes the already-committed BMAP and MOUT state only:

- If `macro_window_flag = true`, combined bucket = the more restrictive of the
  BMAP bucket and `ALLOW_REDUCED`.
- If `macro_window_flag = false`, combined bucket = BMAP bucket unchanged.
- Restrictiveness ordering is `BLOCK` > `ALLOW_REDUCED` > `ALLOW`.

The rule does not recompute BMAP from AOUT score or confidence. AOUT remains
copied provenance in PGAS.

## What Source Artifacts Are Bundled

The builder consumes exactly these committed upstream artifacts:

- `research/agent_outputs/AOUT-0001.agent_output.json`
- `research/bucket_mappings/BMAP-0001.bucket_mapping.json`
- `research/macro_window_agent_outputs/MOUT-0001.macro_window_agent_output.json`

It copies the source values needed for review into deterministic PGAS payloads
and derives `generated_at` / `as_of_timestamp` as the latest timestamps across
the three sources. `PGAS-0002` references the same committed inputs as
`PGAS-0001` and records `combined_bucket = ALLOW_REDUCED` under
`MACRO_AWARE_FLOOR`.

## Why This Remains Advisory-Only

The builder and combiner are small stdlib-only research utilities. They read
committed source artifacts, write committed snapshot artifacts, and do not
import overlay, OMS, risk, sizing, or execution paths. `MACRO_AWARE_FLOOR`
creates no final gate decision, no policy recommendation, no runtime influence,
and no overlay, OMS, risk, or execution authority.
