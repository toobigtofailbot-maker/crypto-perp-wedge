# CPW-NAUTILUS-N1-02 — Bounded parity proofs and pinned-engine limitations

**PARTIAL / N1 PROMOTION BLOCKED.** No engine promotion or execution authority.

- Authorization: Karl's attached WP and explicit execution request.
- Class: bounded T2 adapter/test implementation.
- Branch: codex/cpw-nautilus-n1-02-parity-01.
- Base: 547a411994ddfc80edbf0181c6633783e1a7fab5.
- Tested code: bf8648ae36d50c86e43e2a684621bafd51b0805e.
- Worktree: C:\Users\dersu\.codex\worktrees\cpw-nautilus-n1-02-lane-b\crypto-perp-wedge
- Environment: CPython 3.12.10 / Nautilus 1.231.0; committed lock versions all verified. Existing dedicated proof environment has additional packages; no mutation.
- Repo discovery: #717 and Lane A #740 merged; no competing open PR. Nautilus baseline blobs unchanged.

Changed files:

1. tools/nautilus_adapter/research.py — closed private probes reuse existing engine/strategy and real fills; actual Decimal commission, position/funding events, margin observations.
2. tests/test_nautilus_n1_02_parity.py — repeated physical scenarios, unchanged CPW oracles, fail-closed negatives, legacy guard.
3. tests/test_nautilus_n1_acceptance.py — adds historical scientific hash assertion; no weakened checks.
4. docs/status_entries/CPW-NAUTILUS-N1-02.md — this fragment.

| Gap | Verdict | CPW reference | Native evidence / limit |
| --- | --- | --- | --- |
| fee_slippage_split | PROVEN_NATIVE_DIFFERENCE | 100->100 q=1: fee .08, slip .02, equity 9999.90; 100->200 fee .12, equity 10099.85 | Actual displaced fills 100.01/99.99 and commission .08; variable-price fee .119996, equity 10099.850004 |
| nonzero_funding | UNSUPPORTED_IN_PINNED_ENGINE | q=1 at100, signed rate +/- .01, long/short: one held event pays/receives 1; flat events pay 0 | Three timestamp-aligned rate callbacks, net quantities 0,+/-1,0; all balances10000; no native cash settlement |
| quantity_precision | PROVEN_PARITY | Explicit probe floor quantum 2/3/6/8 dp gives1.23/1.234/1.234567/1.23456789; CPW compares fixed quantized order_size | Exact quantities/notionals on native fill events; exact minimum fills, sub-minimum rejects; non-step floors |
| direct_flip | PROVEN_PARITY | Fixedq1: three closed trades, long-short-long and inverse with 100/110/90/95 next opens; unchanged targets do not submit | Four orders, fillqty1/2/2/1; native PositionClosed then PositionOpened at reversals; matching equity/fees |
| zero_equity_liquidation | UNSUPPORTED_IN_PINNED_ENGINE | Short100@100, close200 or250: zero-floor liquidation at bar2, final0, no surviving position | Equity0 or-5000, one open short100, only entry fill/PositionOpened, no automatic forced close |
| maintenance_margin | UNSUPPORTED_IN_PINNED_ENGINE | Short100@100, close195: equity500<=975maintenance, liquidation atbar2, final0 | Native close-price calculator975; stored entry-price margin500; equity500; position survives |

Interpretation and tolerances:

- fee_slippage_split: Native fee uses actual execution price, CPW uses reference open. Variable-price delta +.000004; no economic-policy repair. Tolerance: Exact Decimal fill/commission; CPW float 1e-9 USD equity, 1e-12 fees; rel=0. Tests: test_real_fee_and_adverse_execution_split, test_fee_basis_native_difference_is_not_allocated_parity.
- nonzero_funding: Rate delivery is available; built-in perpetual funding settlement is absent in inspected backtest/accounting route. No custom cash override. Tolerance: Exact Decimal balances/rates/timestamps/quantity; CPW float 1e-9 USD equity, 1e-12 funding; rel=0. Tests: test_signed_funding_delivered_without_native_settlement.
- quantity_precision: Bounded quantity mapping only; floor is adapter probe policy, not a new CPW sizing policy. Native money six decimals. Tolerance: Exact Decimal quantity/notional; 1e-6 USD settlement equity vs CPW float, rel=0. Tests: test_precision_quantum_minimum_and_exact_notional, test_exact_minimum_step_is_filled.
- direct_flip: Bounded fixed-quantity NETTING proof only; no generalized dynamic reversal sizing or public routing promotion. Tolerance: Exact event quantities, order counts, timestamps, closed realized PnL sum; 1e-9 USD equity,1e-12 fees vs CPW; rel=0. Tests: test_direct_and_repeated_reversals_use_native_netting, test_unchanged_target_does_not_duplicate_orders_and_has_no_lookahead.
- zero_equity_liquidation: Native automatic close and CPW zero-floor parity absent; no manual clamp. Tolerance: Exact Decimal stress equity and event counts; CPW floor0 exact. Tests: test_zero_and_negative_equity_do_not_force_native_liquidation, test_installed_margin_bypass_and_absent_native_liquidation_route.
- maintenance_margin: Calculation proven separately; stored margin differs and automatic enforcement is absent in pinned route. Tolerance: Exact Decimal 975,500,500 and event counts; CPW margin975/floor0 exact. Tests: test_margin_calculation_and_missing_enforcement_are_separate, test_installed_margin_bypass_and_absent_native_liquidation_route.

Pinned feasibility: installed risk/engine.pyx has the margin early return; accounting/manager.pyx comments out the margin-exceeded guard. add_venue has no liquidation option despite config fields. Inspected built-in backtest/accounting route delivers funding updates without perpetual settlement. No custom cash override, manual equity clamp, policy module or version upgrade.

Validation:

- Physical N1-02: python -B -m pytest tests/test_nautilus_n1_02_parity.py -q -s: 39 passed, zero skipped, 3.41s; valid observations repeated identically.
- Adapter, historical spike, CANON, backtest/liquidation, cost-drag and offline funding suites: 140 passed, 2 environmental skips.
- Signal compiler: 261 passed, 3.27s.
- Local CI smoke selection (test_code_index.py + test_diff_scope_summary.py): 109 passed, 85.22s.
- python -B -m tools.registry.validate_result_populations: passed.
- Missing gitignored 4h parquet and unavailable Windows symlink creation explain both skips; reproduced on clean tracked-source snapshot of exact base. No protected test was changed.
- Full repository pytest not required by bounded T2 WP and not claimed.
- Upstream Pandas deprecation warnings disclosed; no dependency repair.

Frozen N1-01 public API/profile/ID, nonzero-funding rejection, historical cost allocation and flat-only behavior remain closed. Probes create no CANON envelope or writer.

Evidence root: C:/Users/dersu/.codex/validation/cpw-nautilus-n1-02.
scenario-matrix.json binds six verdicts, fixture identities, CPW references, actual observations, tolerances and source hashes. source-and-environment.json binds installed sources/binaries, lock and local data. Raw physical/pre-edit logs stay outside tracked repo.

Boundary: only four listed files change. Lane A, docs/project_status.md, protected runtime/trading paths, CANON, backtester, runner, research artifacts, configs, dependencies and CI untouched. No canonical, paper/live or capital activity.

Next: independent Side B exact-head review then Karl merge decision. No merge performed. N1-03 promotion blocked by residual gaps; N2/N3 remain separately gated. Keep pinned v1 plus disclosed residuals unless a separate package authorizes policy/version work.

Frozen physical acceptance: python -B -m pytest tests/test_nautilus_n1_acceptance.py -q -s:
**3 passed, zero skips, 313.36s**, two full RP-2592 executions at the tested code commit.
8 declared / 8 attempted / 8 successful rows, identical outcomes and hashes:
- Request: sha256:179ef4d8e20af186ead25e7b482175b441863070e4a90f4e7f02c0188cd9da01.
- Both evidence runs: sha256:8ca48f07190e7dfc9a03c8fc7e1339884919a58149b2d290d8da1ac71b3cb832.

Replay disclosure: an earlier pre-commit invocation finished successfully but
was excluded from acceptance due to Git provenance. The committed-head
invocation above replaces it; no science or assertion changed.

Skill use: installed pre-draft inspector, readiness preflight, minimum-test-plan,
one-shot review and PR evidence locators were run; checklists applied. Ponytail,
Ponytail review, systematic debugging and verification instructions were read and
applied. Helpers report source location only, not readiness certificates.
Detailed skills-applied.json and requirement-traceability.json are local evidence.
The chat model/effort could not be switched or independently verified by tools.

WP traceability: sections 4/6 isolation and allowlist -> boundary-identities.json;
7/8 feasibility and six cases -> scenario-matrix.json and preflight.log;
8.5/8.7 legacy preservation -> n1-01-committed-head.log and adjacent-committed.log;
9 validation/negative evidence -> parity-committed.log and clean-base-skips.log;
10 skill use -> skills-applied.json; 12 review handoff -> actual PR and final checks.
All implementation requirements satisfied for the expressly permitted PARTIAL
delivery; full six-gap parity and engine promotion remain unproven.

PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/741
Merge state: open, non-draft, not merged. This status-only tail preserves the
validated code bytes; public check and mergeability are reconciled on the final
GitHub head in the execution report. Ready for independent partial-result review;
no merge-ready declaration or engine promotion approval is made.
