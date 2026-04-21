# Pre-Gate Advisory Snapshot Builder

## Why This Package Is Next

WP-7a proved the first deterministic Regime / Scoring advisory lane. WP-6j
proved the first deterministic bucket-mapping consumer of that lane. WP-7f
proved a parallel Macro / Narrative advisory lane. WP-7g is the narrow next
step because the repo now needs one shared read-only surface that can expose the
current advisory picture without deciding how those lanes should interact.

## Why Bundle-Only Was Chosen

The repo does not yet contain an approved upstream policy for combining
Regime / Scoring and Macro / Narrative advisory inputs. The first builder
therefore stops at structural bundling: it assembles committed evidence into a
single snapshot and explicitly records that no combination rule has been
applied.

## What Source Artifacts Are Bundled

The builder consumes exactly these committed upstream artifacts:

- `research/agent_outputs/AOUT-0001.agent_output.json`
- `research/bucket_mappings/BMAP-0001.bucket_mapping.json`
- `research/macro_window_agent_outputs/MOUT-0001.macro_window_agent_output.json`

It copies the source values needed for review into one deterministic
`PGAS-0001` payload and derives `generated_at` / `as_of_timestamp` as the latest
timestamps across the three sources.

## Why No Combination Rule Is Applied Yet

Applying a combination rule would require policy choices about precedence,
conflict handling, final bucket semantics, and how macro context should affect
bounded advisory state. WP-7g intentionally does not make those choices. The
snapshot records `combination_rule_applied = NONE_BUNDLE_ONLY` so that later
packages can distinguish structural packaging from any future policy layer.

## Why Runtime / Overlay Influence Is Deferred

The builder is a small stdlib-only research utility. It reads committed source
artifacts, writes a committed snapshot artifact, and does not import overlay,
OMS, risk, sizing, or execution paths. Any runtime-facing influence remains a
later explicitly scoped decision.
