# Adapter Run Fixture

## Fixture Input

- `scratch/WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02/adapter_run_fixture.json`

## Generated Adapter Packet

- `scratch/WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02/outputs/LADAPT-8f3015b055116a87/`

## Fixture Status

- `adapter_status`: `awaiting_prereg_approval`
- `approval_consumed`: `false`
- `invoked_real_modules`: `[]`
- `gap_count`: `0`

## Reason

This package cannot self-author a Karl approval marker. The committed fixture
therefore proves the adapter packet fails closed before invoking real modules.
Approved-flow behavior is covered by focused tests using temporary approval
fixtures.
