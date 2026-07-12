# H-004-R2 advisory eligibility disposition

Disposition: **PROCEED TO GATE-C PREPARATION WITH DISCLOSURE**.

The report is advisory-only and records `eligibility_status=ineligible`. All eight non-duplicate checks pass: falsifiable hypothesis, bounded market, bounded timeframe, feature availability, data availability, historical testability, parameter bounds, and provenance completeness. The reviewed state is exact, event count is one, and open questions are empty.

Two expected advisory checks fail: `duplicate_near_duplicate_scan` and `concluded_family_freshness_scan`. Both arise from one H-004 candidate-registry match with similarity `0.024691` and normalized overlap only on `daily` and `trend`. H-004 is the intentionally selected concluded source family. No exact duplicate or unrelated material duplicate exists.

Field-level inspection confirms substantive difference in indicator type, trend regime, pullback-recovery entry event, repeated-entry topology, volatility-filter removal, cooldown, ATR exit, maximum-holding exit, and all four parameter roles. The Gate-C packet discloses the advisory status and requires Karl to acknowledge it. H-004 remains a concluded NO-GO.
