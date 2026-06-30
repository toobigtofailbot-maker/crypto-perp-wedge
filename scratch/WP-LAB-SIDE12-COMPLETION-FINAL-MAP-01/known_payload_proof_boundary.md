# Known-Payload Proof Boundary

Known/non-winning/non-promotable payloads are useful for proving lab machinery
before edge hunting. The repo has already used that principle twice:

- PR #586 proved the single-pipe no-candidate / `reject_by_construction` path
  for `known_losing_baseline`.
- PR #588 proved scale-correct denominator preservation for a 600-row synthetic
  known-property population from the same non-promotable class.

A non-winning / non-promotable strategy and a non-promotable baseline
construction payload are the same class of lab input for current proof purposes.
Both are known-outcome, non-promotable inputs. Both must terminate as
no-candidate / `reject_by_construction`.

Running one more non-promotable strategy through the same path would be
re-proof, not new capability completion. The remaining held-B capabilities
require streams of real research jobs, not one known-outcome payload.

This package does not claim a real edge exists, recommend a strategy family, or
authorize edge-search.
