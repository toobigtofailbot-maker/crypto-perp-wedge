"""Offline-only ATR parent-spec denominator bundler.

For the frozen Stage-1 funding-riskmanaged triage (H-FUNDING-FADE-RISKMANAGED-01),
three separate parent Strategy Specs are required because exit_logic.atr_stop is a
parent-spec-level field in the current schema.  This utility combines three 36-row
result-population row slices into one 108-row denominator table for comparison,
preserving all rows including failures.

This module is offline-only and writes no canonical result populations.
"""

from __future__ import annotations

from typing import Any


EXPECTED_ROWS_PER_STATE = 36
EXPECTED_TOTAL_ROWS = 108
ATR_STATES = ("no_atr", "atr_20", "atr_30")


class BundlerError(ValueError):
    """Raised when denominator bundling cannot be completed honestly."""


def bundle_atr_denominator(
    no_atr_rows: list[dict[str, Any]],
    atr_20_rows: list[dict[str, Any]],
    atr_30_rows: list[dict[str, Any]],
    *,
    validate_counts: bool = True,
) -> list[dict[str, Any]]:
    """Combine three 36-row result-population slices into a 108-row denominator table.

    Assigns a ``risk_control_state`` label and a prefixed ``composite_row_id`` to
    each row so cross-state variant ID collisions are unambiguous.  All rows are
    preserved — failures, errors, and data-unavailable outcomes remain in the table.

    Args:
        no_atr_rows: 36 rows from the same-window no-ATR parent spec run.
        atr_20_rows: 36 rows from the ATR-2.0 parent spec run.
        atr_30_rows: 36 rows from the ATR-3.0 parent spec run.
        validate_counts: When True (default), fail if any state has != 36 rows.

    Returns:
        108-element list of dicts with original row fields plus
        ``risk_control_state`` and ``composite_row_id``.

    Raises:
        BundlerError: If counts are wrong or composite IDs collide.
    """
    state_slices: list[tuple[str, list[dict[str, Any]]]] = [
        ("no_atr", no_atr_rows),
        ("atr_20", atr_20_rows),
        ("atr_30", atr_30_rows),
    ]
    if validate_counts:
        for label, rows in state_slices:
            if len(rows) != EXPECTED_ROWS_PER_STATE:
                raise BundlerError(
                    f"expected {EXPECTED_ROWS_PER_STATE} rows for state {label!r}, "
                    f"got {len(rows)}"
                )
    combined: list[dict[str, Any]] = []
    seen_composite_ids: set[str] = set()
    for state_label, rows in state_slices:
        for row in rows:
            variant_id = row.get("variant_id", "")
            composite_id = f"{state_label}:{variant_id}"
            if composite_id in seen_composite_ids:
                raise BundlerError(
                    f"duplicate composite_row_id detected: {composite_id!r}"
                )
            seen_composite_ids.add(composite_id)
            combined.append(
                {
                    **row,
                    "risk_control_state": state_label,
                    "composite_row_id": composite_id,
                }
            )
    if validate_counts and len(combined) != EXPECTED_TOTAL_ROWS:
        raise BundlerError(
            f"expected {EXPECTED_TOTAL_ROWS} total rows after bundling, "
            f"got {len(combined)}"
        )
    return combined


def validate_bundle_denominator_integrity(
    bundle: list[dict[str, Any]],
) -> list[str]:
    """Return a list of integrity error strings (empty = OK).

    Checks:
    - Total row count == 108
    - Each state has exactly 36 rows
    - All composite_row_ids are unique
    - No cross-state variant_id collision under the same composite namespace
    """
    errors: list[str] = []
    if len(bundle) != EXPECTED_TOTAL_ROWS:
        errors.append(
            f"bundle has {len(bundle)} rows; expected {EXPECTED_TOTAL_ROWS}"
        )
    state_counts: dict[str, int] = {}
    seen_ids: set[str] = set()
    for row in bundle:
        state = row.get("risk_control_state", "")
        cid = row.get("composite_row_id", "")
        state_counts[state] = state_counts.get(state, 0) + 1
        if cid in seen_ids:
            errors.append(f"duplicate composite_row_id: {cid!r}")
        seen_ids.add(cid)
    for state in ATR_STATES:
        count = state_counts.get(state, 0)
        if count != EXPECTED_ROWS_PER_STATE:
            errors.append(
                f"state {state!r} has {count} rows; expected {EXPECTED_ROWS_PER_STATE}"
            )
    unexpected_states = set(state_counts) - set(ATR_STATES)
    for state in sorted(unexpected_states):
        errors.append(f"unexpected risk_control_state: {state!r}")
    return errors
