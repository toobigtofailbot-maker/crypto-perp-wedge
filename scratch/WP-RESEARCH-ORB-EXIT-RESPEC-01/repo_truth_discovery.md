# WP-RESEARCH-ORB-EXIT-RESPEC-01 Repo-Truth Discovery

## Fact

- Local `main` was refreshed to `2d054df` (`Merge pull request #552 from toobigtofailbot-maker/agent/canonical-crossing-build-01`) before this worktree was created.
- The isolated branch/worktree is `research/orb-exit-respec-01` at `C:\GitHub\crypto-perp-wedge-worktrees\research-orb-exit-respec-01`.
- Committed ORB/opening-range artifacts do exist in repo truth:
  - `docs/research_pipeline/2026-06-online_orb_15m_prereg_01.md`
  - `docs/status_entries/WP-ONLINE-ORB-15M-PREREG-01.md`
  - `docs/research_pipeline/2026-06-online_ohlcv_runner_perf_01.md`
  - `docs/status_entries/WP-ONLINE-OHLCV-RUNNER-PERF-01.md`
  - `docs/research_pipeline/2026-06-online_ohlcv_surface_integration_01.md`
  - `docs/status_entries/WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01.md`
- The current Strategy Spec grammar and validator include ORB-related declarations: `session_window`, `opening_range`, `opening_range_breakout`, `opening_range_retest`, `time_exit.session_end`, `opening_range_opposite_side`, and `fixed_R_target`.
- The current compiler includes implementation paths and tests for those ORB/session/exit primitives in `tools/research_runner/spec_signal_compiler.py` and `tests/test_spec_signal_compiler.py`.
- The committed ORB 15m preregistration record reports one scratch dry-run surface with denominator 8, 8 successful rows, no Result Population write, and all rows net-negative with high drawdown.
- The scratch Strategy Spec / VM / Sweep artifacts from prior ORB packages are intentionally uncommitted and are absent in this refreshed worktree.
- The current `tools/research_agents/idea_formalizer_agent.py` only has a validated draft adapter for the exact `STRAT-SPEC-0003` SMA/stddev mean-reversion family.
- The current `tools/research_agents/formalizer_runner_bridge.py` explicitly supports only accepted BTCUSDT 15m formalizer outputs with `sma` and `stddev` features and a produced draft Strategy Spec from that adapter.
- A bounded formalizer run for this ORB re-spec accepted the idea as scratch-only and detected `atr` plus `ohlcv`, but produced no draft Strategy Spec because `no validated draft adapter exists for this exact primitive family`.
- Current committed Result Population rows expose aggregate row metrics such as return, Sharpe, drawdown, trade count, fees, funding, slippage, exposure, and win rate. They do not expose `MFE`, `MAE`, `exit_reason`, or real per-trade rows for the ORB dry-run family.
- Repo search found no committed support for the operator-provided `+1.1R median MFE` claim. That claim remains operator context only.
- BTCUSDT 15m D4A data is locally available at `C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`.

## Inference

- ORB can be expressed by lower-level Strategy Spec grammar and compiled by the offline runner when scratch artifacts are manually constructed.
- ORB cannot currently be run through the completed formalizer-to-bridge-to-robustness-to-candidate-review agent chain because the formalizer and bridge do not support producing or consuming ORB Strategy Spec / VM / Sweep artifacts.
- The specific exit re-spec question cannot be answered honestly with MFE/MAE/exit-reason diagnostics because those diagnostics are not present in current runner outputs or committed result rows.
- A fresh manual scratch ORB spec/VM/sweep re-creation could be possible from prior docs, but doing so would bypass the completed formalizer/bridge path selected by this package and would risk substituting a different workflow for the authorized machine path.

## Decision

- Stop at the earliest honest machine boundary after the formalizer output.
- Do not create scratch Strategy Spec / Variant Manifest / Sweep Plan artifacts for this WP because the existing formalizer did not produce a draft and the existing bridge only supports the SMA/stddev family.
- Do not run the bridge, robustness diagnostician, or candidate-review packet agent without bridge outputs.
- Classify the outcome as `BLOCKED` with `FOLLOW-UP NEEDED` for a narrow ORB formalizer/bridge adapter or an explicitly authorized manual scratch ORB rerun path.

## Open Questions

- Should a future package add a validated ORB draft adapter to the idea formalizer and bridge, or should ORB use a separate explicitly authorized manual scratch-run path?
- Should future runner/result-population instrumentation expose real per-trade rows, MFE, MAE, and exit reason before further ORB exit analysis?
- Should the prior ORB 15m negative scratch economics be treated as sufficient to move on, or should the operator-provided MFE context justify one instrumentation-first exit-analysis package?

## Future Options

- Add a narrow ORB agent adapter that maps the existing ORB grammar into scratch Strategy Spec / VM / Sweep artifacts, then rerun the completed bridge path.
- Add result instrumentation for per-trade rows, MFE, MAE, and exit reason under a separately authorized runner/schema package before any ORB exit re-spec evidence claim.
- If Main/Karl want no more ORB work, close this thread as blocked/no-go and move to a fresh archetype queue item without promotion, ranking, or canonical authority.
