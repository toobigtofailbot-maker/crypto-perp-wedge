# H-004-R2 exact Gate-C review packet

R1 `AIDRAFT-C1F03B240EC9C27E` remains rejected for missing an explicit causal mechanism and is preserved at SHA-256 `1e8fb845356e95952ab3ec3bcaaaa455670b7d1f0ea0bc82195b406799a55a07`. The failed R2 preview remains preserved: protected wording triggered `risk_control`, no API call occurred, and no authoritative packet was created.

Corrected draft: `AIDRAFT-2B5725C1A8349863`, `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/AIDRAFT-2B5725C1A8349863.draft_packet.json`, SHA-256 `7c4e53c5cceefc23dc2c242102c0a5c744355d7fafff4ebd892944cf13c5193a`. It is accepted with EMA/ATR/OHLCV, fake-offline provider, no API call, and only the expected packet-only adapter limitation.

Review trail: `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews/AIDRAFT-2B5725C1A8349863.review_events.jsonl`, event `AIREVIEW-8050D437553B2B93`, SHA-256 `a0e3174758316a18ff0f4f207886d2cb1704eaad609e397fd1aee1e0f4339230`.

Eligibility: `scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports/AIDRAFT-2B5725C1A8349863.eligibility_report.json`, SHA-256 `76a0654144d215d62932568b5627d6838f3613e36238bebccaac25d55b873dd9`, advisory status `ineligible`. All eight non-duplicate checks pass. The two failed advisory scans are one intentional H-004 concluded-family near-match at similarity `0.024691`, overlapping only `daily` and `trend`; no exact or unrelated material duplicate exists.

Material difference: H-004 is dual-SMA plus realized-volatility percentile continuous trend exposure. H-004-R2 uses an EMA trend regime and a new pullback-recovery cross entry, permits later distinct pullback entries after cooldown, removes the volatility filter, and adds ATR/time exits with four new parameter roles. H-004 remains NO-GO.

Frozen spec: `STRAT-SPEC-0007`, `scratch/WP-CANON-FIRST-GATE-C-CROSSING-GATED-02C/frozen_strategy_spec.json`, target `research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json`, SHA-256 `b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c`. Schema and compile-only validation pass.

Frozen Gate-C artifact: `GATE-C-H004-R2-0001`, `scratch/WP-CANON-FIRST-GATE-C-CROSSING-GATED-02C/frozen_gate_c_approval.json`, intended authoritative path `scratch/WP-CANON-FIRST-GATE-C-CROSSING-GATED-02C/approvals/GATE-C-H004-R2-0001.gate_c_approval.json`, SHA-256 `b05753fe01cc99aa2c4f0e419fca88f4f843154f12843f01aae775eb1e4e68cd`.

Warnings: the formalizer adapter limitation and advisory duplicate/freshness failures remain fully disclosed. These artifacts grant no Gate Q, queue, execution, scheduler, candidate, promotion/readiness, notification, runtime, paper, or live authority.

## Exact approval statement

I approve Gate C GATE-C-H004-R2-0001 for exactly one append-only canonical Strategy
Spec write.

I reviewed and approve the exact H-004-R2 Strategy Spec bytes with SHA-256:
b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c

for target:
research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json

I approve the exact Gate-C approval artifact bytes with SHA-256:
b05753fe01cc99aa2c4f0e419fca88f4f843154f12843f01aae775eb1e4e68cd

at:
scratch/WP-CANON-FIRST-GATE-C-CROSSING-GATED-02C/approvals/GATE-C-H004-R2-0001.gate_c_approval.json

The approved source draft is:
AIDRAFT-2B5725C1A8349863
scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/AIDRAFT-2B5725C1A8349863.draft_packet.json
7c4e53c5cceefc23dc2c242102c0a5c744355d7fafff4ebd892944cf13c5193a

I acknowledge the disclosed advisory duplicate findings and confirm that
H-004-R2 is materially distinct from H-004 through its EMA trend regime,
pullback-recovery entry event, cooldown, ATR exit, and maximum holding exit.
H-004 remains a concluded NO-GO.

This approval authorizes only the canonical Strategy Spec write. It does not
authorize Gate Q, queue admission, research execution, scheduling, candidate
registration or promotion, notifications, runtime, paper trading, or live
trading.

AWAITING KARL GATE-C APPROVAL
