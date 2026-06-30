# WP-LAB-VISUAL-COCKPIT-STATIC-01

Status: complete

Base commit: `b2e8e66261e08b98de11fad6a5738fc49dfe3728`

Implemented a dependency-free, static, read-only lab visual cockpit under `tools/lab_visual_cockpit`. The cockpit consumes existing audit dashboard projections, event-tape and replay artifacts, Side 12 readiness evidence, report replay artifacts, and committed result populations.

Follow-up `WP-LAB-VISUAL-COCKPIT-STATIC-01-FOLLOWUP-CAPABILITY-MAP-01` fixes capability completion parsing so the cockpit consumes the 23 entries under `side12_operating_readiness_map.json.capabilities` instead of rendering top-level metadata keys as cards. Generated cockpit data now preserves each Side 12 `event_tape_audit_status`, proof basis, remaining condition, and read-only authority flags on the capability cards.

Boundary: no audit dashboard semantic change, no server/backend, no live fetch, no dependency changes, no candidate/crossing/paper-live/runtime authority, no protected-path behavior change, and no fabricated missing metrics.

Validation evidence is recorded in `scratch/WP-LAB-VISUAL-COCKPIT-STATIC-01/validation_summary.txt`.
