# Rendering Evidence — WP-LABPROD-COCKPIT-REALRUN-REFRESH-08

Built with `python -m tools.lab_cockpit.run --out-dir
scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/build` (byte-identical across runs).
DOM inspection of the rendered `cockpit.html` confirmed section order, 8 cards, 3
SVGs, and **no horizontal overflow**.

## Product pipeline · real runs panel

- KPIs: Product runs = 1, Advisory packet ready = 1, Real runner invoked = 1,
  Blocked / failed = 0.
- State vocabulary chips render all six honest states: **No run**, **Awaiting
  execute approval**, **Prepared (bridge prepare-only)**, **Executed (runner
  Result Population)**, **Advisory packet ready**, **Blocked / failed**.
- Run card `LGATE-ad8b6d62f772e9d8`:
  - provenance chips: pipeline `PIPELINE-PRODUCT-BRIDGE-0001`, bridge
    `239624c28e8e64a6`, runner `LRUN-cbbdb839a2a7badf`, gates
    `LGATE-ad8b6d62f772e9d8`.
  - stage ladder: all five stages reached (idea_formalized → bridge_prepared →
    execute_approval_consumed → runner_executed → advisory_packet_ready).
  - "Real runner executed" callout: `runner_invoked = True`; denominator
    `completed 8 · failed 0 · invalid 0 · blocked 0 · pruned 0`. **No spine-only
    banner** on this real run.
  - Withheld/missing statistics table: WFO/OOS gate status `blocked`
    (`withheld_missing_walkforward_oos_inputs`); sections `wfo_oos`,
    `oos_walkforward`, `per_trade`, `funding_stress` each shown with an explicit
    status and `fabricated = false`.
  - Robustness diagnostics: 7 completed chips + 3 skipped with honest reasons
    (missing_fold_inputs, QUEUE_PER_TRADE_INSTRUMENTATION,
    not_applicable_funding_mode_off).
  - Candidate review (advisory): status `completed`, 0 blockers, 3 evidence
    gaps, recommendation `None`.
  - Advisory surface routing callout: status `needs_more_evidence` — review
    routing only; candidate lifecycle written `False`; auto admission / crossing
    / promotion `False / False / False`.

## Product candidate funnel

| stage | count |
| --- | ---: |
| Runner rows preserved (full denominator) | 8 |
| Completed runner rows | 8 |
| Advisory review packets ready | 1 |
| Routed hold-for-review (advisory only) | 0 |
| Candidates admitted | **0** |

## Missing / withheld handling

Withheld statistics are surfaced as explicit status strings with
`fabricated = false`; none are rendered as `0`. WFO/OOS shows as a **blocked /
withheld** gate, not a zero pass.

## Legacy spine-only panel supersession

The pre-existing pipeline run-state panel keeps its honest per-run spine-only
labels, and now additionally shows the supersession note: *"the real product
runner + gates adapter flow is now complete; see the product pipeline real-run
panel …"* — obsolete "flow not yet complete" framing is corrected only because
committed real-run evidence now exists.
