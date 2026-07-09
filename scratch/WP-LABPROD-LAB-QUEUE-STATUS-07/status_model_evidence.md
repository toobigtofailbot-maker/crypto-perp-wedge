# Status Model Evidence

## Implemented Surface

- Module: `tools.lab_pipeline.queue_status`
- Builder: `build_queue_status`
- Markdown renderer: `render_markdown`
- Schema: `lab_product_queue_status_v1`

## Allowed States

- `queued`
- `running`
- `awaiting_prereg_approval`
- `awaiting_execute_approval`
- `blocked`
- `complete`
- `failed`
- `advisory_packet_ready`

## Current Committed Projection

`build_queue_status()` over committed repo fixtures produced:

```json
{
  "advisory_packet_ready_count": 0,
  "approval_needed_count": 2,
  "blocked_count": 1,
  "by_status": {
    "advisory_packet_ready": 0,
    "awaiting_execute_approval": 1,
    "awaiting_prereg_approval": 1,
    "blocked": 1,
    "complete": 0,
    "failed": 0,
    "queued": 0,
    "running": 0
  },
  "failed_count": 0,
  "run_count": 3
}
```

Run-level projection:

- `LPIPE-0508a68667a87ce9`: `awaiting_execute_approval`
- `LPIPE-2201304f65ac6f79`: `awaiting_prereg_approval`
- `LPIPE-e7d1a256221a28aa`: `blocked`

## Focused Test Evidence

`tests/test_lab_pipeline_queue_status.py` verifies:

- current committed fixture projection;
- full allowed state vocabulary and zero-count buckets;
- prereg approval and execute approval are distinct;
- blocked, running, complete, failed, and advisory packet ready states;
- advisory packet availability comes from `advisory_review_packet.json`;
- notification fields are dry-run only;
- Markdown rendering has no executable controls.
