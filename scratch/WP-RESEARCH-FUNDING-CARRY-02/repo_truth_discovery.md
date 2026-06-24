# Repo-Truth Discovery

- PR #562 is merged at base `d08da05` and provides `rolling_empirical_percentile_v1` plus parameter-bound maximum hold.
- PR #560 funding input was locally staged with SHA256 `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`.
- The formalizer and bridge previously supported SMA/stddev and Donchian only. This WP adds one closed `funding_rate_positioning_fade_v1` family.
- Exact frozen semantics require two validated Strategy Specs because existing closed grammar does not parameter-toggle exit groups: 18 midline-or-max-hold rows and 18 fixed-max-hold rows.
- The runner already preserves declared `funding_rate`; no runner, backtester, schema, validator, query, or funding-accounting semantic change was needed.
- Existing walk-forward dry-run and seeded advisory Monte Carlo hooks were used. Per-trade Monte Carlo remains unavailable because Result Population rows contain aggregate metrics only.
- Candidate review is not triggered because every full-history row fails the primary 20% drawdown screen.
- Determinism is proven through bridge/direct reconciliation for both 18-row populations and pinned byte/stable-metric hashes.
- Forbidden files remain runtime, paper/live, OMS, risk, reconciliation, capital, canonical artifacts, candidate lifecycle, crossing, funding-P&L, provider/API/network, and external adoption surfaces.
