# No-Controls Evidence — WP-LABPROD-COCKPIT-REALRUN-REFRESH-08

The refreshed cockpit remains a static, read-only visualization. The product
real-run panel and product candidate funnel add **no** executable control.

## Renderer constraints (unchanged)

`tools/lab_cockpit/render.py` emits hand-generated HTML/CSS/SVG only. Automated
assertions (in `tests/test_lab_cockpit_product_runs.py`) confirm the rendered
page contains none of:

```
<script   <button   <form   <input   onclick
http-equiv="refresh"   http://   https://   fetch(
xmlhttprequest   ws://   setinterval   settimeout
```

- `test_product_panel_has_no_controls_or_network` — asserts every token above is
  absent from the full rendered page (product panel included).

## Non-authority declaration (data model)

`build_cockpit_data(...)["non_authority_declaration"]` inherits every dashboard
guarantee and adds product-panel keys, all asserted false / read-only by
`test_no_product_run_or_execute_controls_declared`:

```
reads_product_run_state_only        = true
invokes_product_runner_adapter      = false
invokes_product_gates_adapter       = false
writes_advisory_review_packet       = false
records_candidate_surface_decision  = false
admits_candidate                    = false
```

## Boundary behavior surfaced (not exercised)

- The advisory surface routing status (`needs_more_evidence` here) is displayed
  as a **review-routing value only**; `candidate_lifecycle_written`,
  `go_auto_admission`, `go_auto_crossing`, `go_auto_promotion` are all shown as
  `false`, and the product candidate funnel terminates at
  `Candidates admitted = 0`.
- The panel reads committed advisory packets; it never calls the bridge, runner
  adapter, or gates adapter. The fixture generator is a separate, explicitly-run
  scratch script — not part of the cockpit runtime.
