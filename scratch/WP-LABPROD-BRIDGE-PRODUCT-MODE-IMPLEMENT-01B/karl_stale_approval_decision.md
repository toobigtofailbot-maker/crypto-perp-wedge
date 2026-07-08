Karl decision:
A product bridge-preparation approval is valid only for the exact frozen source/product/formalizer/stage/output-root content it hashes and identifies. It does not expire by wall-clock time in this package. Missing or malformed timestamps fail closed. Mismatched hashes, paths, run IDs, stage identity, output root, signer, scope, approval statement, or authority flags fail closed.

Implementation note:
For this package, stale approval rejection is content-bound rather than wall-clock-bound. A timestamp is required for audit, but expiry is determined by exact hash/path/run/stage/authority-field binding, not elapsed time.
