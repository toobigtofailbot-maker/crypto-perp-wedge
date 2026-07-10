# Writer independent checks

The writer does not consume eligibility as authorization. It independently:

- recomputes exact content and source SHA-256 values;
- validates the target directory, filename/ID binding, absence, and symlink safety;
- validates the proposed spec beside all existing specs with the canonical schema and full Strategy Spec validator;
- checks exact BTCUSDT crypto-perpetual scope, locked primary/confirmation timeframes, bounded directions, at most five declared free parameters, and provenance references;
- rejects downstream authority fields and relies on the canonical validator's closed schema and forbidden executable-key checks;
- blocks target/ID reuse using both filesystem state and the append-only audit;
- writes no queue, candidate, Variant Manifest, Sweep Plan, Result Population, runner, paper/live, or runtime output.
