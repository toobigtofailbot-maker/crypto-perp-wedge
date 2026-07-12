# Intake/formalizer limitation disposition

The draft was created only through `create_intake_draft` in fake-offline mode. No provider or network call occurred.

Generated draft: `AIDRAFT-C1F03B240EC9C27E` at `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/AIDRAFT-C1F03B240EC9C27E.draft_packet.json`, SHA-256 `1e8fb845356e95952ab3ec3bcaaaa455670b7d1f0ea0bc82195b406799a55a07`.

This is not the anticipated adapter-only limitation. The formalizer status is `rejected`, `research_object` is null, and both the blocker and rejection reason are `idea lacks an explicit causal mechanism`. Although the resume packet contains an economic rationale, the exact authorized source request did not satisfy the service's deterministic causal-mechanism check. It would be dishonest to treat this as resolved through later manual schema mapping.

SMA and ATR are catalogued as full-history OHLCV-derived features, and the merged schema/compiler supports the exact closed ATR-stop object and completed-bar/next-open semantics. Those capability facts do not waive the rejected intake result.

Resolution status: **blocking**. A revised source request with an explicit causal `because` mechanism must be separately authorized and submitted through the service. This package does not authorize silently changing Karl's exact request, deleting the rejected packet, or creating a second draft after failure.

