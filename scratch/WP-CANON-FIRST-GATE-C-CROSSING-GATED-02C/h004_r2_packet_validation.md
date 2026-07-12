# H-004-R2 packet validation — preview stop

Expected deterministic ID verification passed: `sha256("h004-r2-daily-ema-pullback-atr-time-v1")[:16].upper()` yields `AIDRAFT-2B5725C1A8349863`.

The mandatory non-writing preview did not pass:

- formalizer status: `rejected`;
- rejection: `protected trading-control action requested`;
- blocked action: `risk_control`, target `src/risk`;
- research object: null;
- capability assessment: null, so EMA/ATR/OHLCV detection and testability assertions were not reached;
- provider mode: `fake_offline`;
- provider ID: `fake-rule-v1`;
- API call made: false;
- captured scratch paths existed only in the in-memory packet-only formalizer.

The exact approved title ends with “risk control”. Current formalizer guard logic interprets that phrase as a request for protected risk-control action despite the request's review-only and no-execution language. This is more than the expected packet-only adapter limitation.

Per the package stop condition and no-retry rule, `create_intake_draft` was not called. No `AIDRAFT-2B5725C1A8349863` authoritative packet exists. A separate correction must authorize exact alternative wording or a separately scoped formalizer change; this package may do neither.

