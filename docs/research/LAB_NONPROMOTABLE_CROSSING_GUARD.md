# Lab Non-Promotable Crossing Guard

This document records the repo-native guard added by `WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01`.

The guard applies inside the fixture-only candidate crossing builder and rejects construction or non-promotable payloads before fixture crossing authorization. It exists to prevent PR #583 baseline construction payloads, or payloads that carry equivalent non-promotable semantics, from becoming candidate, crossing, promotion, readiness, paper/live, or operator-GO inputs.

Rejected payloads use `reason_code=reject_by_construction` and preserve these outcomes:

- no candidate lifecycle write
- no canonical crossing write
- no promotion or readiness creation
- no paper/live eligibility
- no operator gate pending state
- no edge claim allowed

This guard is not a real candidate lifecycle transition. It creates no edge evidence, no ranking, no recommendation, no promotion authority, no paper/live/runtime authority, and no OMS, risk, reconciliation, order, broker, or exchange authority.

