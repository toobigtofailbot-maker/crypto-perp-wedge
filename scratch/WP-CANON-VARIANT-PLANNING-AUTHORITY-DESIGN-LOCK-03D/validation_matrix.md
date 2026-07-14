# Validation and threat matrix

| Threat | Required rejection/protection |
|---|---|
| Stale parent hash or changed Gate-C line | Recompute exact bytes/raw line and reject mismatch |
| Reused approval, VM ID/path, or search family | Scan artifacts and complete audit history; reject permanently |
| Wrong core, axis order/value, population, denominator | Derive core from VM and require exact structural/hash equality |
| Traversal or symlink component | Lexical confinement plus component-wise non-symlink checks before/inside lock |
| Partial approval/audit write | Exclusive creation, fsync, rollback; integrity-critical on rollback failure |
| Lock collision | Fail without write |
| Lock cleanup failure after commit | Integrity-critical; no automatic retry |
| Preflight/lock TOCTOU | Repeat complete validation inside lock |
| Malformed historical audit | Validate/replay every line and fail closed |
| Unsupported legacy artifact | Preserve embedded-approved path; reject unknown modes/statuses |
| Broad authority flag | Schema constants and semantic checks reject |
| Gate Q used as planning evidence | Reject; planning evidence must pre-exist and validate independently |
| Accidental queue/execution action | Writer output allowlist is approval plus audit only |

Approval fields cover every check; audit fields cover historical replay; the full approval hash is held by VM/Gate-Q/audit references, avoiding self-reference.
