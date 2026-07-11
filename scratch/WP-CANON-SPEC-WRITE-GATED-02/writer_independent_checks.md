# Writer independent checks

The writer does not consume eligibility as authorization. It independently:

- recomputes exact content and source SHA-256 values;
- parses the real Agent Inbox draft packet contract and requires the exact draft identity/path plus exact draft `source_hashes`;
- requires the review trail and eligibility report at their exact authoritative draft-ID-bound paths;
- parses every JSONL review event, enforcing schema, draft identity, sequential append indexes, all seven non-authority flags, and an allowed latest reviewed/flagged state;
- validates eligibility identity, exact draft/review paths and hashes, all advisory/non-authority flags, and exact event-count/latest-state/flagged-state agreement with the actual review trail;
- validates the target directory, filename/ID binding, absence, and symlink safety;
- validates the proposed spec beside all existing specs with the canonical schema and full Strategy Spec validator;
- checks exact BTCUSDT crypto-perpetual scope, locked primary/confirmation timeframes, bounded directions, at most five declared free parameters, and exact path/hash/approval-bound provenance references;
- rejects downstream authority fields and relies on the canonical validator's closed schema and forbidden executable-key checks;
- blocks target/spec/approval reuse using both filesystem state and the append-only audit;
- writes no queue, candidate, Variant Manifest, Sweep Plan, Result Population, runner, paper/live, or runtime output.
