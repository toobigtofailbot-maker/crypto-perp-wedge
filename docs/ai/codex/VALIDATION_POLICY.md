# Validation Policy

This document records repo-local validation tiers for coding-agent work. It is
workflow guidance only; active work packages and current repo truth still win.

## Docs-only packages

Docs-only packages do not run full pytest by default. A docs-only package is one
whose committed diff is limited to documentation or status fragments and does not
change schemas, validators, query-layer behavior, tooling code, tests, research
artifacts, result populations, data, runner/backtester behavior, runtime, paper
or live trading paths, OMS, reconciliation, risk, broker/exchange, credentials,
or capital controls.

Default docs-only validation should include:

- `git diff --check`
- `git diff --cached --check`
- `git status --short`
- changed-file and scope inspection
- `python tools/dev/diff_scope_summary.py --check-forbidden`
- docs-specific checks if a package names them
- targeted validators only when the docs diff changes artifact indexes,
  references, examples, or validation-relevant generated text

Full pytest remains available for docs-only packages, but it is not required by
default and is not implied by `tools/dev/verify.py --validation-preset docs-only`.

Report wording must distinguish policy decisions from failures:

- `full pytest: NOT RUN - docs-only policy; not used as merge evidence`
- `full pytest: TIMED OUT after <seconds>; not a pass`

## Implementation packages

Implementation, schema, validator, query-layer, compiler, runner, dashboard, or
test-support packages must follow the active work package validation commands.
Use focused tests first, adjacent subsystem tests second, validators and
integrity checks where relevant, then full pytest or sharded full pytest when the
active package requires full-suite evidence.

`tools/dev/verify.py --full-pytest-sharded --pytest-shards N` may be used as
full-suite evidence only when all required shards pass. A failed or timed-out
shard fails the overall verification.

## Non-exemptions

The docs-only policy is not an exemption from semantic review, changed-file
inspection, forbidden-scope checks, protected-boundary review, validators named
by the package, or any active work package requirement.
